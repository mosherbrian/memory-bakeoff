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

Fresh pg0 PostgreSQL 18.1 instances start normally and the bundled `psql` can
authenticate to their generated `postgresql://hindsight:...` URIs. In this
environment, however, Python 3.13's installed `psycopg2` fails to connect to
the same URI with an otherwise empty `OperationalError`. Hindsight therefore
fails during migrations before its health endpoint becomes ready. Starting pg0
inside the restricted sandbox also hangs; outside it, pg0 starts successfully.

The launcher now starts the same uniquely named pg0 backend explicitly before
Hindsight and passes its ready PostgreSQL URI to the service, avoiding the
separate pg0-start race. That does not bypass the `psycopg2` failure, so no
benchmark has been run on the partially initialized databases.

## Preserved invalid artifacts

`results/hindsight_gen5_candidate_flow_r1/` was captured before the stale
listener was discovered. Its `INVALIDATED.md` sidecar forbids using it as
candidate-generation or reranking evidence.

## Next safe action

Repair or replace the local Python/PostgreSQL driver stack, then run a new
fresh RRF stress reference first. Capture native candidate flow from that exact
bank, followed by native `min_scores` strategy-isolation calls (where validated
by traces) and the local learned-reranker arm. Do not reuse any generation-4 or
invalid candidate-flow values.
