# Hindsight generation-5 pipeline diagnosis

## Status

No generation-5 retrieval score is published. The work correctly invalidated
generation 4 and verified the native trace shape plus local learned-reranker
availability, but the fresh-service benchmark is blocked before ingestion by a
host Python/PostgreSQL-driver failure.

## What was verified

- The launcher now refuses to run if port 8891 is already listening and uses
  the required ONNX file path:
  `.../snapshots/614241f622f53c4eeff9890bdc4f31cfecc418b3/onnx/model.onnx`.
- A clean Hindsight process loaded the pinned E5-small ONNX model and initialized
  the normal local cross-encoder
  `cross-encoder/ms-marco-MiniLM-L-6-v2` on CPU. A four-record sentinel recall
  returned non-null reranker scores, so the learned-reranker arm is viable once
  database connectivity is repaired.
- Hindsight's native `trace=True` response exposes per-strategy candidate ranks,
  RRF fusion ranks/source ranks, reranker rank changes, and final results. The
  new `scripts/collect_hindsight_candidate_flow.py` records those native trace
  fields and maps them through returned Hindsight `document_id` values rather
  than text matching.

## Blocker

The inherited soft `RLIMIT_NOFILE=256` is a real configuration defect, not the
complete pg0 blocker. A confirming test failed after 253 listener sockets with
`EMFILE`/"Too many open files", while raising that shell's soft limit to 8192
allowed 2,000 listeners. However, an immediate pg0 retry in a regular Terminal
at 8192 still failed while PostgreSQL created its first IPv4/IPv6 listeners
with `ENOBUFS`/"No buffer space available". The wildly fluctuating
`net.inet.tcp.pcbcount` cannot represent live user sockets—its reported values
exceeded `kern.num_files` by orders of magnitude—and must not be used as a
resource-leak diagnosis. The remaining `ENOBUFS` cause is unresolved.

The launcher raises its own soft `nofile` limit to 8192 before it starts pg0 or
Hindsight and records the effective value in `hindsight_runtime.json`. This
prevents the known descriptor ceiling but does not resolve the remaining
PostgreSQL listener error, which reproduces in a normal Mac shell as well as
the Codex tool-runner. Diagnose that listener error before treating the earlier
blank `psycopg2` `OperationalError` as a separate driver defect. Starting pg0
inside the restricted sandbox also hangs.

The launcher starts the same uniquely named pg0 backend explicitly before
Hindsight and passes its ready PostgreSQL URI to the service, avoiding the
separate pg0-start race. No benchmark has been run on the partially initialized
databases.

## Preserved invalid artifacts

`results/hindsight_gen5_candidate_flow_r1/` was captured before the stale
listener was discovered. Its `INVALIDATED.md` sidecar forbids using it as
candidate-generation or reranking evidence.

## Next safe action

First compare a Python listener using PostgreSQL's effective listen backlog
with the failed pg0 start, then collect a syscall trace of PostgreSQL's failing
`socket`/`setsockopt`/`bind`/`listen` path. Only after pg0 starts cleanly in a
regular terminal should the disposable Python driver matrix run. Then run a new
fresh RRF stress reference, capture native candidate flow from that exact bank,
and proceed to strategy isolation and the local learned-reranker arm. Do not
reuse any generation-4 or invalid candidate-flow values.
