# AgentIssue-Bench Gate1 qualification report

## Decision

`CONDITIONAL_ASSET_BLOCKED` with blocking reason `HARNESS_CONTRACT_INVALID`.

This is an asset/harness qualification result, not a scientific method failure and not a chapter GO. The preregistered Phase A all-five rule failed, so Phase B was not run.

## Phase A metadata-only summary

| index | requested platform | inspect arch/OS/digest | non-empty diff | unique commit pair | buggy marker replay | fixed marker replay | status |
|---:|---|---|---|---|---|---|---|
| 29 | linux/amd64 | yes | yes | yes | missing/missing | missing/missing | blocked |
| 15 | linux/amd64 | yes | yes | yes | missing/missing | missing/missing | blocked |
| 19 | linux/amd64 | yes | yes | yes | missing/missing | missing/missing | blocked |
| 48 | linux/arm64 | yes | yes (header only) | no | missing/missing | missing/missing | blocked |
| 28 | linux/amd64 | yes | yes | yes | missing/missing | missing/missing | blocked |

All five pulls and all 25 allowed single-tag container runs completed without timeout. The raw streams are retained only under ignored `runtime/logs/`; committed results contain hashes, enums, counts, exit codes, durations, architecture and digest metadata.

The standard marker contract was `Test script failed (exit code …)` or `Test script executed successfully`. No replay emitted either exact marker. Some streams used other wording or stopped before a marker; those observations are intentionally represented as `missing`, not reinterpreted with sample-specific regexes. The arm64 control also did not expose a unique commit/diff pair. Consequently no sample meets the strict fail-to-pass rule.

## Scope and safety

The runner used only sequential exact single-tag `docker pull`, `docker image inspect`, and `docker run --rm --network none --platform …`; the image ENTRYPOINT was preserved. The forbidden official runners, image deletion, host mounts, secret/API-key injection, model calls and uploads were not used. Images remain locally because deletion was forbidden by protocol.

This outcome does not establish that the AgentIssue research direction is scientifically impossible. It establishes that these frozen public images do not provide the required uniform executable test marker/commit chain for the planned asset-qualified experiment.
