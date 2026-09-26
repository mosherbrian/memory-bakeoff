---
name: restore-stopped-services
description: Any service stopped or disabled for a test/benchmark must be started and re-enabled when the test finishes
metadata:
  node_type: memory
  type: feedback
  originSessionId: 2e29b8b2-a339-433c-9cc1-5e9a19a305c6
  modified: 2026-09-26T01:44:31.117Z
---

Any service I stop or disable for a test (e.g. a benchmark) must be started again and re-enabled once the test is done.

**Why:** In a previous benchmark, services were left off afterwards and Brian had to remind me.

**How to apply:** Before stopping/disabling anything, note its prior state (running/enabled). When the test ends, including on failure or abort, start and re-enable it, then verify status and report it to Brian.
