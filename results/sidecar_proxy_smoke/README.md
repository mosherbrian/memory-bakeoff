# Sidecar compatibility-proxy live smoke test

Executed inside the ChatGPT coding container on 2026-08-30 (America/Los_Angeles).

Two localhost HTTP clients were launched concurrently against one sidecar proxy:

- `POST /v1/chat/completions` with `Return exactly OPENAI_BRIDGE_OK`
- `POST /v1/messages` with `Return exactly ANTHROPIC_BRIDGE_OK`

Both requests blocked in the file queue. The current ChatGPT tool loop read the two
pending requests and wrote their responses. The original clients resumed and received:

- OpenAI-shaped response containing `OPENAI_BRIDGE_OK`
- Anthropic Messages-shaped response containing `ANTHROPIC_BRIDGE_OK`

This validates transport plumbing only. It does **not** prove that a specific third-party
SDK (for example the Claude Agent SDK) uses only the subset of Anthropic Messages
semantics implemented by the bridge. Product integrations must still receive their own
end-to-end smoke test before benchmark scores are accepted.
