---
name: feedback-blocked-fetch-use-nanobrowser
description: "When a web fetch is refused/blocked, read the page with nanobrowser tools in the user's Chrome instead of asking them to paste it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: fd579e5f-a73b-4bf9-9845-b37bbee1cd4f
  modified: 2026-09-26T02:04:44.184Z
---

When a web fetch is refused or blocked, use the nanobrowser tools to read the page in Brian's Chrome rather than asking him to paste the content.

**Why:** Previously a page was blocked and I asked Brian to paste it; he had to remind me, which was friction he wants to avoid.

**How to apply:** On any refused/blocked WebFetch, immediately fall back to the nanobrowser tools to open and read the page. Only ask Brian for help if nanobrowser is unavailable or also fails.
