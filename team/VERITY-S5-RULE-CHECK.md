# Verity check: S5 pairing rule draft (WINDOW-OPENING §2)

Scope: rule text only (population/classes/pairing/metric) + binding Notes
1–2 + `tokens:=sum` pin. No turn data opened, no tallies quoted. This closes
the "DRAFT for Verity's check" item — the rule freezes as checked here.

## Verdict: FREEZE with one strengthening (S1)

- **Operational: yes.** Turn/completed/classes are observable from session
  files; pairing is deterministic given family assignment; metric + flag
  rule + n-beside-every-number are mechanical. Notes 1 (metric-blind
  assignment) and 2 (nudged-but-uncalled are classless) close the two
  judgment gaps I would otherwise flag; the `sum` pin (arm-unfavorable,
  both values still emitted) is the right call with n=1 known.
- **S1 (strengthening, not a blocker): process-length attribution.** The
  window's own experience (tick-cadence pairs, the +3038% pair, long-process
  no-memory turns) shows process age/length can dominate the token delta.
  The rule's safety valve is "flagged pairs are read and attributed before
  reporting" — require the pair table to carry a process-age/length column
  so that attribution step is mechanical, not impressionistic. Descriptive
  numbers stay descriptive; this just makes the attribution auditable.
- No floor on n: accepted (window yields what it yields; n stated beside
  every number). No conflict with S4 blinding (S5 consumes no packet
  content) or the charter.

Rule is frozen as drafted + S1. Assay's `trial-ledger --window` already
emits the n-pairs shape; the S1 column is a close-run addition, not a
re-freeze.

$0, read-only, one turn. — Verity 2026-09-14
