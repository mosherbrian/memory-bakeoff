# Corvid admission pass — deadline record (cairn, controller)

- Dispatch of corvid's single independent admission pass: 2026-09-21 14:34Z (wake confirmed started).
- Bound: 30 minutes total → **deadline 2026-09-21T15:04:00Z**.
- Expected evidence: `packages/P1-inspect/admission-review.md` and `packages/P2-specify/admission-review.md` (accepted-or-bounded-rejection disposition per package).
- Deadline wake: one-shot timer, PID 702294 (`sleep 1644` → `agent-deck -p campaign4 session send cairn -message-file /tmp/corvid-deadline-msg.txt`), fires exactly once at 15:04:00Z. Not a polling loop; no campaign-3 machinery involved.
- On deadline event or corvid completion: cairn wakes tern with evidence. Cairn does not author or certify corvid's review.
- Kiln dispatch: HELD pending tern's explicit release of independently reviewed contract versions.
- 2026-09-21 ~07:4x local: operator-error stop retracted (no pending sponsor decision). Corvid resumed by operator; kiln stays HELD. Cairn remains wake-driven.
- 2026-09-21 14:40Z (reconciliation complete, evidence `resume-20260921.md`): old shell 702294 + sleep 702296 retired after identity check. Replacement one-shot `campaign4-corvid-admission-deadline.timer` due **15:04:00Z**, delivers via wake socket. `campaign4-watch.timer` armed, 45m cadence, first check 15:25:10Z, wake delivery. No budget reset; no timers duplicated by cairn.
