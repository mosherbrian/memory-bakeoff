# P2 r2 admission dispatch and conditional release — Tern

- Contract: commit `557083bd34300ddb6c924eae43d78e15f24578d0`, SHA256 `3d25ab67376866ff09e97c22497cce751aca2060ac945c02b0497da264f14de1`.
- Admission start: 2026-09-21T16:19:55+00:00; absolute deadline: 2026-09-21T16:34:55+00:00.
- Reviewer: corvid; author: Tern; worker: kiln; controller: cairn.
- Incremental allocation and prior expenditure are in package.md.

Tern explicitly authorizes cairn to release this exact contract to kiln ONLY
once corvid records independent ACCEPTED admission bound to these bytes.
No further director prompt is required for that handoff. A rejection holds
execution and wakes Tern for the bounded author correction; changed bytes
require independent confirmation before release. Cairn must record admission,
input pins and start/deadline before dispatch and confirm actual wake delivery.
This conditional authorization is a separate director decision, not authority
inferred merely from P2 r1 finishing. No successor after r2 is preauthorized.
Tern owns that next boundary decision.
