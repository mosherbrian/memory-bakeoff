# Verity design review: A1 vault-serve watchdog (2e247bb)

Scope: design/mechanism review of `team/SERVE-WATCHDOG-AMENDMENT.md` (Kiln,
2026-09-13). Provenance already second-driven by Assay (hashes match, 47/47;
`team/ASSAY-A1-PROVENANCE-SECONDDRIVER.md`) — not re-derived here. No
packet/fire-log content read; no S4/S5 figures quoted.

## Verdict: PASS as amendment, with one superseded diagnosis

1. **Mechanism is sound defense-in-depth.** Timeout→suspect→respawn-before-next-op
   preserves recall (respawn replaces the child; tools stay registered) and never
   blind-retries the timed-out mutation. The one-failed-draft-per-incident cost is
   stated openly (§Open items 3). Happy-path claim holds: no timeout → no respawn →
   identical queries/prompts/instruments; S6 semantics unchanged (same MCP scan on a
   fresh serve).
2. **The diagnosis is superseded, the fix is not invalidated.** The amendment
   attributes the hang to serve-internal deadlock (futex-idle threads, live
   transport). Cairn's later root-cause analysis + Assay's A2 v3 (landed fbd3149,
   10/10 power) show the actual trigger was the extension client's chunk-boundary
   bug (>64KiB replies dropped → 30s timeout), with the "deadlocked" serve actually
   healthy-idle. The watchdog therefore mitigates the symptom class (any 30s timeout
   self-heals on next op) without fixing the trigger — which A2 does. Both layers
   are worth keeping; neither alone was sufficient.
3. **Residuals (low, for the record, not blockers):** (a) respawn storms — repeated
   timeouts respawn per-op with no backoff/cap stated; acceptable in-window (every
   timeout already costs a failed draft) but worth a cap post-window; (b) the
   A1 receipt belongs in WINDOW-OPENING.md (Assay's doc-only diff `18ce32b2` covers
   it; still uncommitted per Kiln's report — GiLMore/Brian call).

No frozen-instrument objection. A1 stands; A2 v3 is the trigger fix.

$0, read-only, one turn. — Verity 2026-09-14
