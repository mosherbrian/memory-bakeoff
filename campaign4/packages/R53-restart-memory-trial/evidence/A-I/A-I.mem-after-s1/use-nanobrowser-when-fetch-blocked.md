---
name: use-nanobrowser-when-fetch-blocked
description: "When a web fetch is refused/blocked, read the page via nanobrowser tools in the user's Chrome instead of asking them to paste it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 04d9d301-3fe2-48c7-a12f-4898f5cb3eda
  modified: 2026-09-26T01:30:48.360Z
---

When a web fetch is refused or blocked, use the nanobrowser tools to read the page in the user's Chrome. Do not ask the user to paste the page content.

**Why:** Previously a page was blocked and I asked Brian to paste it; they had to remind me to use the browser instead, which was friction they didn't want to repeat.

**How to apply:** On any blocked/refused web fetch, switch to nanobrowser tools straight away to open and read the page. Only ask the user if nanobrowser is unavailable or also fails.
