# ChatGPT sidecar LLM backend

## Why it exists

ChatGPT in this conversation cannot expose its hidden/live completion stream as a
localhost model server. It *can*, however, read and write files through the tool loop.
The sidecar exploits that distinction without pretending there is a direct model API:

1. The benchmark writes one or more OpenAI-shaped requests to a local queue.
2. The benchmark waits for response files.
3. ChatGPT reads all outstanding requests through the tool loop.
4. ChatGPT answers them, preferably as a batch, and writes atomic response files.
5. The original benchmark process sees the files and resumes.

This is intended for a **small, high-quality realistic evaluation set**, not large
statistical runs.

## LLM abstraction

The benchmark code depends on `LLMClient`, `LLMRequest`, and `LLMResponse`, not an SDK.
`LLMRequest` deliberately mirrors the useful subset of OpenAI Chat Completions:

- messages
- model
- temperature
- max tokens
- response format
- function tools / tool choice
- seed

Current backends:

- `DeterministicFakeLLM`: plumbing/replay tests
- `ChatGPTSidecarLLM`: interactive ChatGPT via file queue
- `OpenAICompatibleLLM`: OpenAI or any compatible local server (llama.cpp, vLLM, SGLang)
- `AnthropicLLM`: Anthropic Messages API

## Queue layout

```text
.memory-bakeoff-sidecar/
  requests/   req_<uuid>.json
  responses/  req_<uuid>.json
  batches/    <batch_uuid>.json
  archive/
```

Requests and responses are written by temporary-file + atomic rename. A batch writes
**all requests before it begins waiting**, allowing ChatGPT to process them together.

## Response schema

```json
{
  "protocol_version": 1,
  "request_id": "req_...",
  "content": "assistant response text",
  "model": "chatgpt-sidecar",
  "finish_reason": "stop",
  "usage": {},
  "tool_calls": []
}
```

`usage` may be empty because the ChatGPT product tool loop does not necessarily expose
exact tokenizer accounting to this bridge. The benchmark must report unknown usage as
unknown rather than fabricate numbers.

## Optional OpenAI-compatible localhost proxy

`SidecarOpenAIProxy` exposes:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`

This lets a third-party product that accepts a custom OpenAI-compatible base URL use the
same queue. The proxy itself is only a bridge: it blocks until ChatGPT answers the file
request. If a client asks for `stream=true`, the proxy waits for the complete answer and
then emits one SSE delta plus `[DONE]`; it does **not** provide true token streaming.

This may let product-mode memory engines use ChatGPT without modifying their code, but
only when the product supports an OpenAI-compatible endpoint. Engines that hard-wire an
SDK/provider still need a provider-specific adapter.

## Experimental policy

Use three LLM tiers:

1. **Fake/deterministic** for harness plumbing, unit tests, and large deterministic
   algorithmic diagnostics.
2. **ChatGPT sidecar** for a small manually supervised realistic set where stronger
   language understanding is valuable.
3. **Real API/local model** for repeated statistical runs and final end-to-end numbers.

Never mix results from these tiers into one unlabeled leaderboard. The evaluated system
is the complete memory engine + ingestion mode + LLM backend + model/configuration.
