---
name: restore-services-after-tests
description: Any service stopped or disabled for a test/benchmark must be started and re-enabled when the test finishes
metadata:
  node_type: memory
  type: feedback
  originSessionId: eb5df3a7-c73b-444a-a3d5-ffecc89c9a9f
  modified: 2026-09-26T01:37:41.485Z
---

Any service I stop or disable for a test or benchmark must be started and re-enabled once the test is done.

**Why:** After a previous benchmark, services were left off and Brian had to remind me.

**How to apply:** Before stopping/disabling a service, note its prior state (active/enabled). When the test ends, or if it fails or is aborted, restore that state (start and enable) and confirm it. Mention the restoration in the final report.
