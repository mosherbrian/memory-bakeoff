# P3 prospective allocation extension 1 — Tern, 2026-09-21

**Decision: continue the nonterminal P3 revision with one explicitly allocated
narrow repair. No terminal state or boundary disposition is committed here.**
This is a director allocation decision within today's machinery authority,
not an automatic retry, reset or request for Brian.

## Evidence and reason

Corvid's post-repair FAIL (`verification.md` SHA256
`1e0abdfca6a512b07f4078a7bc7fc99cc0798d19f02b2b22d7eb56896206c19b`)
confirms the first four defects fixed and identifies one introduced regression:
completed worker-flight identity/deadline survives publication into CHECKING.
Tern read the verdict and source and verified the affected source hashes.
V2 and its verdict are preserved byte-for-byte at
`campaign4/p3-attempt-history/postrepair-v2/` with a full preservation manifest.

Another narrow allocation is warranted: the failure is localized and has an
independent concrete reproducer, and fixing it advances the already admitted
deadline/identity behavior. No contract acceptance criterion changes.

## Additional ceilings, prospectively granted

- Worker kiln: **one additional repair, at most 15 minutes** from its newly
  recorded dispatch start. This is total worker attempt 3 (repair 2).
- Independent verifier corvid: **one additional pass, at most 15 minutes**
  from its recorded verification start; cairn dispatches promptly on completion.
- P3 historical cumulative grants become **105 worker minutes** (60+30+15)
  and **75 verifier minutes** (30+30+15). Actual time/cost remains separate;
  unknown cost remains unknown. Prior attempts and repair are spent, unchanged.
- No further retry or extension is automatic. Expiry stops the overdue
  activity, records BLOCKED and wakes Tern. Another defect returns to Tern
  for a separate boundary/allocation decision; the fleet does not self-extend.

## Bounded repair and required evidence

End or rotate worker `flight` on publication. Record the verifier's own action
identity, owner, acknowledgement and absolute deadline for CHECKING. Merely
dropping the deadline to make validation pass is insufficient: every active
verification remains bounded. A waiting handoff must be explicitly owned and
bounded, not an ACTIVE claim with null identity/deadline. Preserve phase and
attempt identity through BLOCKED/resume and ledger replay.

Touch only the admitted P3 output paths needed for this correction and its
tests/fixtures/documentation. No unrelated redesign or live effects.

Regression evidence must show on v2 that worker deadline 17:10, publication
17:05, verifier deadline 17:25, validation 17:15 incorrectly alarms, and on
the repair that CHECKING uses the verifier action and is ACTIVE. At verifier
expiry it must fault or block correctly. Reopen the store and reproduce both
outcomes; stale worker deadlines after publication must not stop verification.
Also cover blocked verification resuming the same action/allocation and
publication without a dispatched verifier (bounded handoff, not unbounded
silence). Corvid independently checks these and the existing D1–D4, REST,
omission, atomic publication and no-duplicate-dispatch regressions.

Cairn records this grant and pins its commit before dispatch. Record start and
absolute deadline, arm one-shot wake, then confirm actual socket delivery.
Bind final source tree and verdict; preserve this v2 archive before any write.
No additional admission is needed for an allocation extension that leaves the
independently admitted completion requirements unchanged. Independent execution
verification and Tern's final acceptance are still mandatory.
