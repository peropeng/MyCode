"""Export/reconcile offline Who&When requests. This tool never sends requests.

Sample JSON: {sample_id, task, steps: [{role, content}, ...]}.
Config JSON: {backend, max_requests, max_output_tokens, max_model_seconds}.
Response JSON: {request_id, response: {text, usage, finish_reason, ...}, elapsed_seconds}.
Fix endpoint/model revision and generation parameters in the external client
before scientific execution; this tool is only a request/receipt adapter.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from thesis_recovery.diagnostic_baselines import DiagnosticSession


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "next", "mark-submitted", "response", "failure", "retry"])
    parser.add_argument("--session", required=True)
    parser.add_argument("--sample")
    parser.add_argument("--config")
    parser.add_argument("--method", choices=["all_at_once", "binary_search"])
    parser.add_argument("--request-id")
    parser.add_argument("--receipt")
    args = parser.parse_args()
    if args.action == "prepare":
        if not all((args.sample, args.config, args.method)):
            parser.error("prepare requires --sample, --config and --method")
        session = DiagnosticSession.create(args.session, read(args.sample), args.method, read(args.config))
    else:
        binding = read(args.session)["binding"]
        session = DiagnosticSession.resume(args.session, binding["sample"], binding["method"], binding["config"])
    if args.action in ("prepare", "next"):
        result = {"request": session.next_request(), "state": session.state["status"], "totals": session.totals()}
    elif args.action == "mark-submitted":
        if not args.request_id:
            parser.error("mark-submitted requires --request-id")
        session.mark_submitted(args.request_id)
        result = {"state": session.state["status"], "totals": session.totals()}
    elif args.action in ("response", "failure"):
        if not args.receipt:
            parser.error(args.action + " requires --receipt")
        receipt = read(args.receipt)
        if args.action == "response":
            session.record_response(receipt["request_id"], receipt["response"], receipt["elapsed_seconds"])
        else:
            session.record_failure(receipt["request_id"], receipt["error"], receipt["elapsed_seconds"])
        result = {"state": session.state["status"], "result": session.state["result"], "totals": session.totals()}
    else:
        session.retry_invalid()
        result = {"state": session.state["status"], "totals": session.totals()}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
