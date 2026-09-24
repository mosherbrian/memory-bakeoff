# P13-director-decision-ownership — admission review (independent)

- **Reviewer:** corvid; action `P13-admission-1`, start `04:17:09Z`, deadline
  `04:27:09Z`.
- **Contract:** `package.md` sha256
  `a72fb97cb27366efa753e4be3da4bd8b1b7e0b3aa81091dadef73aeb6e75b0dd` (commit
  `da00b2d8`); `admission-receipt.json` matches.
- **Verdict: ACCEPTED** — contract pinned and internally consistent; **180 m
  arithmetic correct**; all input pins verify. Checklist preregistered.

## Pins / integrity

- **Budget:** 10+60+25+20+15+10+20+10+10 = **180** m ceiling, as stated; P12 spent
  history preserved separately; no hidden reserve.
- **Input pins (7/7 recomputed equal):** P12
  `terminal-disposition.json 1aa2ee87…`, `cutover-postreview-1.md 3e1098b8…`,
  `notify-claude c9aa340e…`, `escalations c6f90cfa…`, `escalation-watch 8968ed55…`,
  `escalation-watch.timer 4ec5a2a0…`, `.service 0f34b38f…` — all present.
- **Base:** source `8ad12b86fa82…`, binary `97a57db1…`; freeze `internal/core`,
  `internal/py`, `conformance/cases`; unfreeze only loop decision ownership + the
  necessary CLI/status/timer/host escalation adapter, tests and docs.

## Scope assessment (acceptable)

- **Escalation semantics** are pinned to the **actual** scripts/units (pins above)
  with **stable-key** recurrence: ack names owner + next action + response deadline
  (≤15 min), is **not** a decision/closure; expiry re-raises the **same** stable key
  through the existing recurrence path; no indefinite renewal; a timely actual
  decision resolves and prevents a later page; forged/stale/wrong-principal refused.
- **Ladder:** deadline remind → +300 s duty → +600 s Claude via the escalation
  ledger **plus** `notify-claude`; stage boundaries persisted before delivery;
  works while `run` is stopped via the independent timer/outside check; stop stays
  quiet absent outstanding obligations; transport failure is owned.
- **Reuse, not redesign:** `escalation-watch` unchanged (default grace 45 min + 15 min
  interval + latency, measured separately; **no 10 min Signal claim**); shared global
  config unchanged; stable mapping to escalation ledger IDs/keys; `notify-claude`
  rc 0 is **not** an ack and its ledger write is best-effort → durable registration
  must be verified.
- **One logical stage per incident** across callback/check/restart/concurrent
  decision; bounded retry; ambiguous delivery explicit; at most one labelled repeat
  then owned unresolved; D3 identities retained; status exposes deadline/rung/owner/
  ack/response-deadline/unresolved/evidence.
- **Boundaries stated:** release/routing general registration is an **explicit
  deferred scope limit** (no fake worker package for a director approval); production
  stays on `97a57db1` until separately signed promotion; live needs fresh fixtures +
  Tern's exact signature; no real Signal/production install until separate authority.
- **Reproduce-baseline-first**, unshared mutations per boundary, real
  separate-process calendar witness (daemon-reload/restart) on isolated units, actual
  escalation scripts against isolated HOME/state + stub ticket/notify sinks, and
  **never page Brian for a synthetic fault**.

No contract defect found; do not design around a requirement silently — any
substantive amendment returns Tern. Checklist filed as `acceptance-checklist.md`.

**ACCEPTED** — Tern may release author 60 m via `notify-claude` on the unchanged
pinned contract with the checklist pinned.
