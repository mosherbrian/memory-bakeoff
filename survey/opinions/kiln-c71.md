# kiln (Practitioner) — c71: bounded injection exists; relevance doesn't follow

**kiln · 2026-09-26 · see systems/claude-mem-delivery.md. Quoting ROLES practical fit.**

claude-mem's delivery is real implemented machinery: multi-event hooks including post-compaction refresh, 10k-char budget ladder with overBudget flag, recency+filter selection defaulting semantic off, visible failure states with queued retention. That removes the oversized-native-index failure for sessions it covers — the one operation asked. It does not select by importance, guarantee obedience, or cover Pi/local. Adopt the budget-ladder + refresh-on-compact pattern as design; the product itself stays a candidate with unmeasured benefit. **Medium confidence** (source-read mechanics; installed behavior on Brian's box unmeasured).
