# Generation 15: frozen reader sidecar transport

Generation 15 adds a fail-closed bridge between the committed Gen14 frozen
reader requests and an interactive ChatGPT-sidecar responder.  It does not run
agentmemory, reconstruct retrieval, alter ranked context, or generate reader
answers.

## Export artifact

The complete deterministic export is
`results/agentmemory_raw_product_gen15_sidecar_transport/pending_requests.json`.
It contains 28 requests in the Gen14 manifest order: 14 core followed by 14
stress.  For each request it records condition, held-out case ID, stable request
ID, frozen fingerprint, exact OpenAI messages, model field (`chatgpt-sidecar`),
temperature (0.0), and source request path.  The request-set SHA-256 is:

```text
9e2dd8955ca9d0eb044f415594b1a9c8e83543de1f58a9955c1c671e2bf6ea5d
```

The artifact also defines the only accepted response-bundle schema.  The
interactive responder must supply every request exactly once with its matching
fingerprint and this normal sidecar response envelope:

```json
{
  "protocol_version": 1,
  "request_id": "...",
  "fingerprint": "...",
  "content": "...",
  "model": "chatgpt-sidecar",
  "finish_reason": "stop",
  "usage": {},
  "tool_calls": []
}
```

The complete bundle must be wrapped as
`memory-bakeoff-sidecar-response-bundle` schema version 1 and carry the
request-set hash above.  It is intentionally not enough to provide a subset or
to answer only selected high-risk cases.

## Validation and import

`scripts/agentmemory_gen15_sidecar_transport.py` supports:

```bash
.venv/bin/python scripts/agentmemory_gen15_sidecar_transport.py export
.venv/bin/python scripts/agentmemory_gen15_sidecar_transport.py import RESPONSE_BUNDLE.json
.venv/bin/python scripts/agentmemory_gen15_sidecar_transport.py grade
```

The importer loads the frozen local Gen14 request files as authority and
rejects a changed request set, duplicate/missing/unexpected IDs, mismatched
fingerprints, malformed envelopes, or any pre-existing response file.  It
validates the entire bundle before writing a single normal sidecar response.
The grader then consumes those normal response paths and calls the existing
`memory_bakeoff.reader_eval.score_answer` unchanged.  It reports core and
stress separately, retaining per-case exact contexts/answers/grades plus
prohibited/stale, wrong-scope, harmful-conversion, and harmful-context-ignored
classifications.

## Current state

No response bundle was present in the repository or control-plane mailbox at
execution time, and the Gen14 response directories remain empty.  Therefore
there is no downstream answer, answer-success, abstention, prohibited/stale
answer, wrong-scope answer, or harmful-context-conversion result yet.  This is
an intentional fail-closed state, not an inference that harmful context will
or will not be propagated.

When responses are available, the resulting reader report must remain beside
Gen13 stress retrieval (Hit@5 1.000 / all-relevant@5 0.958) **and** lifecycle
loss (82/500 live memories; 418/450 false supersessions, 92.9%).  Reader
success cannot turn destructive deletion of valid memories into a memory
quality win.
