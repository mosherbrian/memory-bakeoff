# Tool-loop RPC sidecar

The benchmark sandbox may be intentionally unable to reach the public Internet while the
interactive ChatGPT tool layer can access narrow, audited capabilities such as GitHub and
public Web search. `memory_bakeoff.tool_rpc` bridges those worlds without pretending that the
sandbox has a network connection.

## Model

```text
sandbox benchmark
      |
      | atomic JSON request(s)
      v
.rpc/requests/
      |
      | ChatGPT explicitly services the batch
      | via GitHub / Web / other approved tools
      v
.rpc/responses/
      |
      v
blocked benchmark resumes
```

This is **cooperative pseudo-egress**, not a SOCKS/HTTP proxy. The Python process cannot wake
ChatGPT or invoke connectors itself. A ChatGPT orchestration turn must observe pending files,
perform the corresponding tool calls, and atomically write response envelopes.

## Contract

A request contains:

- `method`: namespaced capability such as `github.fetch_file` or `web.search`
- `params`: JSON parameters for that capability
- `fingerprint`: SHA-256 of method + params, excluding run metadata
- `batch_id` / `batch_index`: lets the worker service related calls together
- `metadata`: audit/run annotations that do not affect the fingerprint

A response contains `ok`, either `result` or structured `error`, and optional metadata.
Remote tool failure is returned as data rather than confused with a queue/transport failure.

## Why keep this narrow

The point is reproducibility and controlled setup, not giving contestants unrestricted egress.
A run can archive every external request/response and distinguish:

1. the memory engine's behavior,
2. the LLM reader/extractor's behavior, and
3. external setup or retrieval supplied by the orchestration layer.

The existing `chatgpt_sidecar` remains a specialized LLM transport because third-party products
can already target its OpenAI- and Anthropic-compatible localhost proxy. The generic RPC layer
uses the same batching/file-queue idea for non-LLM tool calls.
