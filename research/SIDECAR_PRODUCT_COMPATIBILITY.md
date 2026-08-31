# ChatGPT sidecar — product-mode compatibility map

The benchmark owns one normalized `LLMRequest` contract. The localhost bridge exposes
that backend as both OpenAI Chat Completions (`/v1/chat/completions`) and a minimal
Anthropic Messages (`/v1/messages`) compatibility surface. Responses are buffered until
the interactive ChatGPT tool loop answers; there is no access to ChatGPT's live token
stream.

## Current integration map

| Product | Likely sidecar route | Status |
|---|---|---|
| Hindsight | `HINDSIGHT_API_LLM_PROVIDER=openai` + custom `HINDSIGHT_API_LLM_BASE_URL=http://127.0.0.1:8765/v1` | Strong candidate; upstream explicitly documents custom OpenAI-compatible Chat Completions endpoints. |
| Mem0 | OpenAI LLM provider + `openai_base_url` / `OPENAI_BASE_URL` | Strong candidate for ordinary OpenAI LLM calls; pin the Mem0 version because base-URL handling has changed/fixed over time. Embeddings remain a separate dependency. |
| Claude-Mem | Claude provider in gateway mode with `ANTHROPIC_BASE_URL=http://127.0.0.1:8765` | Plausible now that the bridge implements `/v1/messages`; still requires an end-to-end Claude Agent SDK smoke test before trusting it. |
| MemBukkit | Configure its supported API/local LLM path; exact arbitrary-endpoint route still needs version-specific validation | TBD. Raw `ingest_facts`/evidence search does not need the reader LLM, but product distillation does. |
| Habitus | Reference agent/model adapter is separate from raw library `remember`/`recall` | Sidecar is unnecessary for the raw engine round; product/reference-agent routing can be added later if useful. |
| agentmemory | Raw coding-agent-life path uses `/remember` + `/smart-search` without an LLM in retrieval | Sidecar not needed for the raw round. |

## Why expose both protocols?

Hindsight and many generic products can consume an OpenAI-compatible base URL directly.
Claude-Mem's documented Claude gateway path instead expects an Anthropic-compatible
endpoint. Supporting both at the transport edge avoids contaminating the benchmark with
product-specific LLM abstractions.

## Compatibility boundary

The bridge currently supports the subset needed for ordinary text/tool model calls:

- OpenAI chat messages, function tools, tool choice, buffered streaming
- Anthropic system/messages text blocks, tool schemas/tool choice, tool-use responses,
  tool-result text normalization, and buffered Anthropic SSE events

It does not claim to be a complete proxy for every vendor-specific feature (images,
prompt caching headers, extended-thinking blocks, citations, beta APIs, etc.). A product
that requires an unsupported feature must fail explicitly rather than silently changing
semantics.
