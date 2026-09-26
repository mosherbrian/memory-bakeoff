---
name: feedback-blocked-fetch-use-nanobrowser
description: "When a web fetch is refused/blocked, read the page via nanobrowser tools in the user's Chrome instead of asking them to paste it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 37e152a4-ada9-4828-a17c-40f3d2d289c9
  modified: 2026-09-26T01:57:57.516Z
---

When a web fetch is refused or blocked, use the nanobrowser tools to read the page in Brian's Chrome rather than asking him to paste the content.

**Why:** Previously a page was blocked and I asked Brian to paste it; he had to remind me, which was friction he wanted to avoid.

**How to apply:** On any fetch failure/refusal, go straight to nanobrowser to open and read the page. Only ask Brian if nanobrowser tools are unavailable or also fail.
