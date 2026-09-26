---
name: feedback-blocked-fetch-use-nanobrowser
description: "When a web fetch is refused/blocked, read the page via nanobrowser tools in Brian's Chrome instead of asking him to paste it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e49d4a43-7b01-47a9-a798-ff972c9577f0
  modified: 2026-09-26T04:13:17.217Z
---

When a web fetch is refused or blocked, use the nanobrowser tools to read the page in Brian's Chrome rather than asking him to paste the content.

**Why:** Previously a page was blocked and I asked Brian to paste it; he had to remind me of this workflow, which was friction he didn't want.

**How to apply:** On any refused/blocked WebFetch, immediately try the nanobrowser tools to open and read the page. Only ask Brian for help if the nanobrowser tools are unavailable or also fail.
