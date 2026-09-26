---
name: feedback-blocked-fetch-use-nanobrowser
description: "When a web fetch is refused/blocked, read the page via nanobrowser tools in the user's Chrome instead of asking the user to paste it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1a9518df-c3d3-4e83-9a61-54e704454054
  modified: 2026-09-26T04:01:38.550Z
---

When a web fetch is refused or blocked, use the nanobrowser tools to read the page in Brian's Chrome rather than asking them to paste the content.

**Why:** Previously a page was blocked and I asked Brian to paste it; they had to remind me to use the browser instead, which was friction.

**How to apply:** On any refused/blocked fetch, go straight to the nanobrowser tools to open and read the page. Only ask Brian for help if nanobrowser also fails.
