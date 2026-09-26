# R69 readiness (design only; nothing authorized)
Blockers before any live cell, each needing a separate reviewed package:
1. Runner: a prepared-memory kind that writes the frozen fixture into the fresh project memory dir before the single session and records its manifest; current R67 runner only supports N/I/R/D.
2. Finalizer: R67 requires mem-before-s1 == ABSENT; the prepared kind needs "before == frozen fixture manifest" instead, plus the event-adjudication path in event-contract.md.
3. Fidelity pre-launch check (grep of target outside the detail file) as code, not memory of the operator.
4. Observed-detail-read extraction for the descriptive mediation endpoint (from transcript tool_use/tool_result pairs).
5. Offline stub tests for expectations.json E1-E18 and all R66/R67 regressions, twice fresh.
Proposed live bound after those: 6 calls in the frozen protocol order, ceiling 8, per-cell corvid review and finalization, no retries. Same-user/same-reviewer limits unchanged.
