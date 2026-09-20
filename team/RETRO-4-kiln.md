# Sprint-4 retro — kiln-flash (2026-09-16)

**Closed:** S4-8 rowcheck + S4-11 guards, S4-9 window correction, S4-10 corpus v3 freeze, S4-12 cross-engine, S4-13 outcome M1–M4, S4-14 config-artifact re-run, S4-4 backfill, S4-5/S4-15 policy de-mute (live + base), second-seat verdicts on S4-3/S4-7, re-pointed verifications of rows 21 and S3-4 — every closing row gated by its declared check, not a word.
**Churned:** the poller — three defect classes diagnosed from wake evidence (stale snapshot, owner/verifier conflation, template cycling), escalated 12:30, rebuilt on rowcheck gating; 11 further phantoms after the rebuild showed the snapshot itself still doesn't advance, so the fix is incomplete.
**One thing wrong:** S4-12 — I verified my zeros were *honestly measured* and never asked whether the configuration was the *right one*; the strict surfaces I scored are paths the vendors don't ship, and Brian's one-row ruling (S4-14) undid the whole result. Honest-zero verification is not validity; ask "is this the system's real path" before certifying a zero.
**One thing to keep:** the computed-done gate — "done = declared artifact exists + declared check exits 0" caught the S4-4 path-less-done class, survived adversarial re-checks, and is now the fleet's wake primitive; it turned queue honesty from prose into a machine property.

— kiln-flash, $0.
