---
name: feedback-blocked-fetch-use-nanobrowser
description: "When a web fetch is refused/blocked, read the page with nanobrowser tools in the user's Chrome instead of asking them to paste it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ae8616bd-71c8-4524-bc39-65d40c0d44a1
  modified: 2026-09-26T06:21:40.424Z
---

When a web fetch is refused or blocked, use the nanobrowser tools to read the page in Brian's Chrome rather than asking them to paste the content.

**Why:** Previously a page was blocked and I asked Brian to paste it; they had to remind me, which was avoidable friction.

**How to apply:** On any refused/blocked web fetch, switch to the nanobrowser tools to open and read the page directly. Only ask the user if nanobrowser is also unavailable or fails.
