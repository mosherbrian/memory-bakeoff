# R2H-FREEZE — freeze receipts, R2 explicit-prompt habit arm (v2)

**STATUS: FROZEN — 2026-09-12, on Brian's FINAL GO** (verbatim: *"The deploy
to my work will need instructions and/or a script, please. Go for it."*,
relayed by GiLMore). Per proposal v2 §"On final GO", the three freeze items
were executed in order, before day 1. This file is the record; the seed
value and full schedule are committed below so anyone can verify post hoc
that the schedule was never edited.

## Freeze items, in order

**1. Design of record — proposal v2:**
`sha256 9390f7ad5a0b241e4d86d5c0df1dc6e44a3e255871fd9bc68d88402de940933f`
(`team/PROPOSAL-R2-explicit-prompt-habit.md`; v1 archived beside it).
Design-only caveat now partially lifted by the FINAL GO: day-0 deploy and
the 10-day unmonitored run are authorized; adjudication still awaits the
returned bundle.

**2. Adjudication rule — R2H-ADJUDICATION.md:**
`sha256 979c636c052733d3cff48f52cdba43f93b93437bab77f478753949be499a6fb4`
(rater: Verity, blind, on the arm-stripped slice; labels APPLIED /
NOT-APPLIED / UNDECIDABLE + HARM; falsifiers inside; rule-only file).

**3. Day-schedule seed:**
`sha256(SEED.txt) 7c9f7d5e23589e29b9a0e88bda738ecd51c52ea0e427e7b81b4a4960bb20c3a7`
Seed value (committed, see derivation below):
`9e2aac78cbc3243967a557cd10fddf7a2382046516e90e9e6ce196f0c38371e7`

## Derived schedule (deterministic from the seed)

Derivation (predeclared): days 1–10 sorted by `sha256("<seed>:day<i>:perm")`;
first five in the permutation are ON, last five OFF. Balanced 5/5 by
construction; re-derivable from SEED.txt by anyone.

| Counted day | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Arm | ON | ON | OFF | ON | ON | OFF | ON | OFF | OFF | OFF |

Counted days are consumed by `flip` invocations, not calendar dates (miss a
day, flip when you remember). Stated imbalance: 4 of the first 5 days are ON
— kept as drawn; re-rolling after looking would be exactly the tampering the
seed-hash freeze exists to prevent. Pairing and denominators carry the load,
per proposal v2 change 2.

## Deploy package (Brian's copy)

All in `deploy/r2-habit-20260912/` (mirrored to `team/`):

| File | sha256 |
|---|---|
| `r2h_deploy.py` | `74e7ae86b79343280715af4af77f0a407651ac06e9f2c890aa42ebacfdaa0c54` |
| `RUNBOOK.md` | `34bf02469f603109b4feb5754e52789596af195d242213ec505388b9986ea017` |
| `SCHEDULE.txt` | `3a2cf55860f3e3e2683ec15a0f52e10c0599cdb044d98149128aedbbae5753d0` |
| `SEED.txt` | `7c9f7d5e23589e29b9a0e88bda738ecd51c52ea0e427e7b81b4a4960bb20c3a7` |

Script tested 2026-09-12 against a sandbox agent dir (check, install-check,
smoke via stub pi, 10-flip sequence == schedule, bundle close, arm-strip
verified: raw nudge line present, stripped zero). One bug found and fixed in
testing (`flip` referencing an undefined argparse attribute); the hash above
is the fixed, tested file. No network paths in the script; no fleet contact.

## Honest note on blinding (supersedes v2's commit-reveal phrasing, by correction)

V2 §Runbook day −1 said the seed value would be "held by GiLMore, revealed
after labels freeze." That is unworkable and this freeze corrects it: Brian
must know the arms to flip them, so the schedule ships in his package.
Blinding of the rater is enforced by **arm-stripping plus rater procedure**
(R2H-ADJUDICATION §"The material Verity sees"), not by schedule secrecy.
The commit half of commit-reveal still stands: the seed hash was frozen
here before day 1, so the schedule provably predates the data.

## What happens next

Day-0 runbook to Brian (this directory's RUNBOOK.md + script) → smoke
receipt returned → fleet verifies before day 1 counts → 10 counted days →
bundle returns at his discretion → Verity labels the stripped slice → labels
frozen → GiLMore joins the arm map, computes H1–H5 with denominators →
results to Brian with citations. Method limits per proposal v2 §"Method
limits" travel unchanged.

— Freeze executed by Stratum (worker-glm), 2026-09-12, one turn per
GiLMore's dispatch. Every hash above is checkable; nothing here requires
trusting anyone's memory.
