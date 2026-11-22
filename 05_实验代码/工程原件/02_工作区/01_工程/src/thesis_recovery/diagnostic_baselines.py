"""Offline Who&When request/receipt adapter. No API client or evaluator labels.

Author prompts are pinned to the project's MIT-licensed copy. Adaptations: remove
the answer line, retain original role/content rendering and zero-based boundaries,
reject ambiguous output instead of the author's random fallback. A submitted call
must be reconciled before another request. Sessions have a single writer.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import tempfile
import time

AUTHOR_SOURCE = "https://github.com/mingyin1/Agents_Failure_Attribution/blob/b2bae5c5b06d681d04ea5e9b63b7a30525c04925/Automated_FA/Lib/utils.py"
PROMPT_PATH = "01_实验/历史结论与经验/实验/实验132_论文驱动三案归因对比/literature/prompts/who_prompts.py"
PROMPT_SHA256 = "f47a5b45264610a71ae166299e00017fa4011e1d8c124602c78ed73ef153ae16"
PROTOCOL = {"id": "who_when_no_answer_strict_v1", "author_source": AUTHOR_SOURCE,
            "prompt_path": PROMPT_PATH, "prompt_sha256": PROMPT_SHA256,
            "adaptations": ["remove answer line", "reject ambiguous output instead of random fallback"],
            "step_boundary": "one supplied record per candidate, zero-based",
            "rendering": "original role: content lines in supplied order",
            "time_budget": "cumulative request elapsed time, excluding pauses",
            "output": "single step, no complete ranking"}


class PendingRequestError(RuntimeError):
    pass


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _prompts():
    path = Path(__file__).resolve().parents[4] / PROMPT_PATH
    if hashlib.sha256(path.read_bytes()).hexdigest() != PROMPT_SHA256:
        raise ValueError("Pinned prompt changed; review protocol first")
    spec = importlib.util.spec_from_file_location("thesis_who_when_prompts", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _binding(sample, method, config):
    if method not in ("all_at_once", "binary_search"):
        raise ValueError("Unknown method")
    if set(sample) != {"sample_id", "task", "steps"}:
        raise ValueError("Public sample contains exactly sample_id, task, steps; no labels")
    if not isinstance(sample["sample_id"], str) or not sample["sample_id"] or not isinstance(sample["task"], str):
        raise ValueError("Nonempty sample_id and task text required")
    if not isinstance(sample["steps"], list) or not sample["steps"]:
        raise ValueError("Nonempty ordered steps required")
    for step in sample["steps"]:
        if not isinstance(step, dict) or set(step) != {"role", "content"} or not all(isinstance(v, str) for v in step.values()) or not step["role"]:
            raise ValueError("Each step has exactly text role and content; preserve original boundaries")
    if set(config) != {"backend", "max_requests", "max_output_tokens", "max_model_seconds"}:
        raise ValueError("Config requires backend, max_requests, max_output_tokens, max_model_seconds")
    backend = config["backend"]
    if backend != "deepseek-flash" and not (isinstance(backend, str) and backend.startswith("local:") and len(backend) > 6):
        raise ValueError("Use deepseek-flash or an existing named local: model")
    for key in ("max_requests", "max_output_tokens"):
        if type(config[key]) is not int or config[key] < 1:
            raise ValueError(key + " must be a positive integer")
    _elapsed(config["max_model_seconds"])
    if config["max_model_seconds"] == 0:
        raise ValueError("Time budget must be positive")
    _prompts()
    return copy.deepcopy({"sample": sample, "method": method, "config": config, "protocol": PROTOCOL,
                          "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})


def _elapsed(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("Finite nonnegative elapsed_seconds required")


def _parse(text, method, sample):
    if method == "binary_search":
        choice = text.strip().lower()
        if choice not in ("upper half", "lower half"):
            raise ValueError("binary_ambiguous_half")
        return {"choice": choice}
    fields = {}
    for name in ("Agent Name", "Step Number", "Reason for Mistake"):
        pattern = r"(?:^|\n)\s*" + re.escape(name) + r"\s*:\s*(.*?)(?=\n\s*(?:Agent Name|Step Number|Reason for Mistake)\s*:|\Z)"
        matches = re.findall(pattern, text, flags=re.I | re.S)
        if len(matches) != 1:
            raise ValueError("missing_or_duplicate_official_fields")
        fields[name] = matches[0].strip()
    if not re.fullmatch(r"\(?\s*\d+\s*\)?", fields["Step Number"]):
        raise ValueError("step_not_integer")
    step = int(fields["Step Number"].strip("() "))
    role = fields["Agent Name"].strip("() \"'")
    if not 0 <= step < len(sample["steps"]):
        raise ValueError("step_out_of_bounds")
    if role not in {s["role"] for s in sample["steps"]} or not fields["Reason for Mistake"]:
        raise ValueError("unknown_role_or_empty_reason")
    return {"predicted_step": step, "predicted_role": role, "reason": fields["Reason for Mistake"],
            "agent_output_origin": "native_model_output",
            "role_matches_selected_step": role == sample["steps"][step]["role"]}


class DiagnosticSession:
    """Prepare once, mark submitted before external send, reconcile its receipt.

    Pass request_id as the remote idempotency key when supported. The local guard
    cannot guarantee remote idempotency. Only external clients submit requests.
    Resumption rejects changes to input, code, prompts, method or budget.
    """
    def __init__(self, path, state):
        self.path, self._state = Path(path), state

    @classmethod
    def create(cls, path, sample, method, config):
        binding = _binding(sample, method, config)
        if Path(path).exists():
            raise FileExistsError("Resume existing journal; never overwrite")
        state = {"schema": "rq1.diagnostic_session.v1", "binding": binding,
                 "binding_sha256": _digest(binding), "status": "ready", "low": 0,
                 "high": len(sample["steps"]) - 1, "calls": [], "result": None}
        session = cls(path, state)
        if method == "binary_search" and len(sample["steps"]) == 1:
            session._finish({"predicted_step": 0, "predicted_role": sample["steps"][0]["role"],
                             "agent_output_origin": "derived_from_selected_step"})
        session._save()
        return session

    @classmethod
    def resume(cls, path, sample, method, config):
        expected = _binding(sample, method, config)
        state = json.loads(Path(path).read_text(encoding="utf-8"))
        checksum = state.pop("state_sha256", None)
        if checksum != _digest(state):
            raise ValueError("Journal integrity mismatch")
        if state["binding_sha256"] != _digest(expected) or state["binding"] != expected:
            raise ValueError("Input/method/config/protocol/code changed; create separate session")
        return cls(path, state)

    @property
    def state(self):
        return copy.deepcopy(self._state)

    def _save(self):
        payload = copy.deepcopy(self._state)
        payload["state_sha256"] = _digest(payload)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=self.path.name + ".", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def totals(self):
        submitted = [c for c in self._state["calls"] if c["status"] != "prepared"]
        usage = [c.get("response", {}).get("usage") for c in submitted]
        known = all(isinstance(u, dict) and all(type(u.get(k)) is int and u[k] >= 0 for k in
                    ("prompt_tokens", "completion_tokens")) for u in usage)
        return {"submitted_requests": len(submitted),
                "model_elapsed_seconds": sum(c.get("elapsed_seconds", 0) for c in submitted),
                "prompt_tokens": sum(u["prompt_tokens"] for u in usage) if known else None,
                "completion_tokens": sum(u["completion_tokens"] for u in usage) if known else None,
                "usage_complete": known}

    def _finish(self, result):
        result.update(ranking=None, scores=None, output_kind="single_step")
        self._state.update(status="completed", result=result)

    def next_request(self):
        state = self._state
        if state["status"] in ("completed", "budget_exhausted"):
            return None
        if state["status"] in ("invalid_output", "request_failed"):
            raise ValueError("Explicit retry_invalid required; prior calls remain charged")
        if state["calls"]:
            last = state["calls"][-1]
            if last["status"] == "submitted":
                raise PendingRequestError("Reconcile submitted request " + last["request"]["request_id"])
            if last["status"] == "prepared":
                return copy.deepcopy(last["request"])
        config, sample, method = (state["binding"][k] for k in ("config", "sample", "method"))
        totals = self.totals()
        if totals["submitted_requests"] >= config["max_requests"] or totals["model_elapsed_seconds"] >= config["max_model_seconds"]:
            state["status"] = "budget_exhausted"
            self._save()
            return None
        low, high = state["low"], state["high"]
        middle = low + (high - low) // 2
        content = "\n".join(s["role"] + ": " + s["content"] for s in sample["steps"][low:high + 1])
        prompts = _prompts()
        if method == "all_at_once":
            system, prompt = prompts.ALL_AT_ONCE_SYSTEM, prompts.all_at_once_prompt(sample["task"], content)
        else:
            system = prompts.BINARY_SEARCH_SYSTEM
            prompt = prompts.binary_search_prompt(sample["task"], content, f"from step {low} to step {high}",
                                                  f"from step {low} to step {middle}", f"from step {middle + 1} to step {high}")
        request = {"request_id": _digest([state["binding_sha256"], len(state["calls"])]),
                   "backend": config["backend"], "sample_id": sample["sample_id"], "method": method,
                   "range": [low, high], "mid": middle,
                   "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                   "max_tokens": config["max_output_tokens"],
                   "remaining_model_seconds": config["max_model_seconds"] - totals["model_elapsed_seconds"]}
        state["calls"].append({"status": "prepared", "request": request})
        self._save()
        return copy.deepcopy(request)

    def _last(self, request_id):
        if not self._state["calls"] or self._state["calls"][-1]["request"]["request_id"] != request_id:
            raise ValueError("Receipt is not for current request")
        return self._state["calls"][-1]

    def mark_submitted(self, request_id):
        call = self._last(request_id)
        if call["status"] != "prepared":
            raise PendingRequestError("Already submitted; do not resubmit")
        call.update(status="submitted", submitted_at_unix=time.time())
        self._state["status"] = "waiting_for_receipt"
        self._save()

    def record_response(self, request_id, response, elapsed_seconds):
        _elapsed(elapsed_seconds)
        call = self._last(request_id)
        if call["status"] == "responded":
            if call["response"] == response and call["elapsed_seconds"] == elapsed_seconds:
                return self.state
            raise ValueError("Conflicting duplicate receipt")
        if call["status"] != "submitted" or not isinstance(response, dict) or not isinstance(response.get("text"), str):
            raise ValueError("Submitted request and full response receipt with text required")
        call.update(status="responded", response=copy.deepcopy(response), elapsed_seconds=elapsed_seconds)
        state = self._state
        try:
            if elapsed_seconds > call["request"]["remaining_model_seconds"]:
                raise ValueError("response_after_model_time_budget")
            if response.get("finish_reason") in ("length", "content_filter"):
                raise ValueError("incomplete_generation")
            parsed = _parse(response["text"], state["binding"]["method"], state["binding"]["sample"])
            call["parsed"] = parsed
            if state["binding"]["method"] == "all_at_once":
                self._finish(parsed)
            else:
                if parsed["choice"] == "upper half":
                    state["high"] = call["request"]["mid"]
                else:
                    state["low"] = call["request"]["mid"] + 1
                state["status"] = "ready"
                if state["low"] == state["high"]:
                    step = state["low"]
                    self._finish({"predicted_step": step,
                                  "predicted_role": state["binding"]["sample"]["steps"][step]["role"],
                                  "agent_output_origin": "derived_from_selected_step"})
        except ValueError as exc:
            call["parse_error"], state["status"] = str(exc), "invalid_output"
        self._save()
        return self.state

    def record_failure(self, request_id, error, elapsed_seconds):
        _elapsed(elapsed_seconds)
        call = self._last(request_id)
        if call["status"] != "submitted" or not isinstance(error, str) or not error:
            raise ValueError("Close submitted request with a nonempty error receipt")
        call.update(status="failed", error=error, elapsed_seconds=elapsed_seconds)
        self._state["status"] = "request_failed"
        self._save()

    def retry_invalid(self):
        if self._state["status"] not in ("invalid_output", "request_failed"):
            raise ValueError("Only closed invalid/failed requests can be retried")
        self._state["status"] = "ready"
        self._save()
