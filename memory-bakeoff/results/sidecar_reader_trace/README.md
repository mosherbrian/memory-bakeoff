# ChatGPT sidecar reader trace

This directory archives the exact OpenAI-shaped request/response envelopes used for the real reader-impact evaluation.

- Model label: `GPT-5.6 Sol via ChatGPT sidecar`
- Providers: `bm25`, `tfidf_cosine`, `dense_lsa`, `hybrid_rrf`
- Cases per provider: 14
- Total requests/responses: 56 / 56
- The `replay` LLM backend validates each request fingerprint before returning an archived response.
- A full four-provider replay reproduces the canonical reader scores exactly.

The trace records model inputs and outputs; token usage is left empty because the ChatGPT surface does not expose exact API usage for these calls.
