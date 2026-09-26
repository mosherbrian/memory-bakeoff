---
name: feedback-blocked-fetch-use-nanobrowser
description: "When a web fetch is refused/blocked, read the page via nanobrowser tools in the user's Chrome instead of asking them to paste it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: cd425360-3947-4c72-ada2-b51523bd8f22
  modified: 2026-09-26T06:04:33.651Z
---

When a web fetch is refused or blocked, use the nanobrowser tools to read the page in the user's Chrome rather than asking them to paste the content.

**Why:** Previously a page was blocked and I asked Brian to paste it; they had to remind me and found it annoying.

**How to apply:** On any WebFetch failure/refusal, switch to the nanobrowser tools to open and read the page. Only ask the user if nanobrowser is unavailable or also fails.
