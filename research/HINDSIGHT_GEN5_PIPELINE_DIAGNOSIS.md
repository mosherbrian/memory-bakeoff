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

The primary cause is the per-process descriptor limit, not the macOS TCP PCB
counter. This host's inherited soft `RLIMIT_NOFILE` was 256 (hard limit
unlimited): a confirming test failed after 253 listener sockets with
`EMFILE`/"Too many open files", while raising that shell's soft limit to 8192
allowed 2,000 listeners. The wildly fluctuating `net.inet.tcp.pcbcount` cannot
represent live user sockets—its reported values exceeded `kern.num_files` by
orders of magnitude—and must not be used as a resource-leak diagnosis.

The launcher now raises its own soft `nofile` limit to 8192 before it starts
pg0 or Hindsight and records the effective value in `hindsight_runtime.json`.
The Codex tool-runner still intermittently reports `ENOBUFS` for localhost
connections even after that raise; this is an execution-environment limitation
of the tool-runner, distinct from the normal Mac shell reproduction. Complete
the driver matrix from a regular terminal with `ulimit -n 8192` before treating
the earlier blank `psycopg2` `OperationalError` as a separate driver defect.
Starting pg0 inside the restricted sandbox also hangs.

The launcher starts the same uniquely named pg0 backend explicitly before
Hindsight and passes its ready PostgreSQL URI to the service, avoiding the
separate pg0-start race. No benchmark has been run on the partially initialized
databases.

## Preserved invalid artifacts

`results/hindsight_gen5_candidate_flow_r1/` was captured before the stale
listener was discovered. Its `INVALIDATED.md` sidecar forbids using it as
candidate-generation or reranking evidence.

## Next safe action

From a regular terminal, run the disposable driver matrix with `ulimit -n 8192`
first. If `psycopg2` then connects, run a new fresh RRF stress reference;
otherwise diagnose the driver separately. Capture native candidate flow from
that exact bank, followed by native `min_scores` strategy-isolation calls
(where validated by traces) and the local learned-reranker arm. Do not reuse
any generation-4 or invalid candidate-flow values.
