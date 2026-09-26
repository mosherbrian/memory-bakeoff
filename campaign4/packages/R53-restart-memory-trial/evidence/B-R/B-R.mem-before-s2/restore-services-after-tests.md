---
name: restore-services-after-tests
description: Any service stopped or disabled for a test/benchmark must be started and re-enabled when the test finishes
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6e264a99-c3ac-4a39-89ac-b40bcfb3978d
  modified: 2026-09-26T02:11:29.036Z
---

Any service I stop or disable for a test or benchmark must be started again and re-enabled once the test is done.

**Why:** After a previous benchmark, services were left off and Brian had to remind me.

**How to apply:** Before stopping/disabling a service, note its prior state (active/enabled). When the test ends, including on failure or abort, start it and re-enable it, then verify its status and report that it was restored.
