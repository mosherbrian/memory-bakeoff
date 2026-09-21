# P2 revision 2 — close the lifecycle gaps exposed by P2

**Status:** DRAFT; independent admission required before execution.
**Question:** P2-specification (same question as P2-specify).
**Revision:** 2; successor to exhausted `P2-specify`, not a reset or a
retroactive change to its terminal disposition.
**Authorized allocation:** Tern, 2026-09-21, under `campaign4/CHARTER.md`.
**Type:** judgment. **Author/director:** Tern. **Reader/verifier:** corvid.
**Worker:** kiln. **Controller/duty owner:** cairn.

## Task and decision

Complete the transition specification so an implementation need not invent
the exhaustion and blocked-verification behavior. Decide whether the four
P2 specification documents can now be frozen for a separately authorized
implementation package. Preserve the compact contract and accepted design.

The evidence is operational: P2 used its initial attempt and sole repair,
received a narrow post-repair PASS, then failed director acceptance with no
allocation left. Its own candidate table did not explicitly handle that
situation. Verification may also block and need to resume CHECKING without
rerunning the worker. Distinguish P2's actual history from that simulated
resume case; do not claim a historical event that was not recorded.

## Pinned inputs (paths relative to /home/bmosher/memory-bake-off)

- Commit `03b0ba2` (resolve full id in registration):
  `campaign4/packages/P2-specify/{contract,transitions,ownership,walkthrough}.md`,
  `acceptance-withheld.md`, `verification.md`, `repair-receipt.md`,
  `campaign4/p2-dispatch-20260921.md`, and `campaign4/p2-attempt-history/`.
  Original bytes, verdicts and exhausted disposition are immutable inputs.
- `campaign4/ACCEPTED-ARCHITECTURE.md` at
  `a4c143be903c26dea5cb82efcca015d0a671052d`, SHA256
  `cf390ce0d79bf404c166c59ca0b2548a57e6f239b5e380d88aec569ad11c2b5c`.
- `campaign4/packages/P2-specify/director-decisions.md` and P1 acceptance at
  `dd15764258317c125adc2cd193a44c57ad5dd6b4` remain binding.
- Charter including Brian's standing boundary instruction, and this contract,
  pinned by full commit and hash at registration. Cairn records an input
  manifest before dispatch; no moving-HEAD input is sufficient.

## Outputs and completion check

Write successor `contract.md`, `transitions.md`, `ownership.md`,
`walkthrough.md` here, plus a concise `changes.md` mapping changes to defects.
Copy unchanged documents verbatim. Change only what closes these gaps and
keeps cross-references and the walkthrough consistent. No controller code.

Corvid independently checks the complete resulting table, not only a diff:

1. A failed verification or director acceptance with no eligible attempt
   allocation left has an explicit owned, recorded terminal exhaustion path.
   A valid negative finding still completes; it does not become exhaustion.
2. BLOCKED records its originating phase, attempt identity and remaining
   allocation. A resolved verification block returns to CHECKING without a
   worker launch or new worker attempt. Expired verification cannot silently
   receive a fresh deadline: termination/exhaustion or an explicit recorded
   allocation is required. Other eligible phase resumptions stay defined.
3. Deadline, invalid measurement, integrity mismatch, eligible repair and
   repair-exhaustion events have unambiguous destinations and precedence;
   every nonterminal has exits and terminals have no execution transitions.
   Each execution/repair dispatch still records its start before launch.
4. Walk the actual P2 exhaustion through the table; separately walk a blocked
   verification resuming within its original allocation, a verification whose
   deadline expired, and a successful repair versus exhausted repair. Retain
   successful, valid-negative and amendment cases. Label historical,
   simulated and projected steps honestly; choose concrete terminal paths,
   not a list of possible endings. No step may require an invented transition.
5. Budget/history continuity, independent review, compactness, shared-host
   trust limits and both decided ownership questions remain intact. The
   successor does not rewrite EXHAUSTED as SUPERSEDED or COMPLETE for P2 r1.

Completion requires corvid's hash-bound PASS and Tern's explicit acceptance.
Document headings alone do not freeze outputs. One bounded rejection explains
any admission defect; only Tern repairs the contract, never its certifier.

## Explicit incremental allocation and cumulative history

This is a new allocation by Tern, not an automatic retry:

- Admission: one 15-minute corvid pass; if Tern repairs an admission defect,
  one 10-minute repair-confirmation pass. No unbounded admission loop.
- Worker: one initial attempt, at most 30 minutes, plus at most one eligible
  repair, 15 minutes. Verifier: at most 20 minutes per pass, including repair.
- Prior P2 r1 consumed one initial attempt and one repair, with two verifier
  passes. Its worker ceilings were 60+30 minutes; verification 30+30 minutes.
  With this grant, cumulative ceilings are 135 worker minutes and 100 verifier
  minutes across r1+r2; r2 does not turn r1's spent repair into unused budget.
  Actual elapsed/spend is recorded separately from ceilings. Preserve source
  timestamps, late delivery, failed attempts and unknown cost as unknown.
- Kiln/corvid spend inherits the charter. No new external services or purchases.
  Today's machinery boundary and both charter hard stops apply.

Cairn records actor, inputs, phase start and absolute deadline before each
dispatch; arm a one-shot reliable `wake` event. No polling. Acknowledged socket
delivery and artifact evidence distinguish an actual handoff from a written
intention. Redelivery uses the same attempt and original deadline.

On timeout cairn stops overdue work, records BLOCKED with owner/evidence and
wakes Tern; timeout does not automatically allocate a repair. A verified
eligible defect may use the one already allocated r2 repair. After it is spent
no further attempt is automatic. Tern decides the terminal disposition and
opens a warranted successor or records why none is warranted, without waiting
for a routine Brian prompt.

## Permissions

Read repository inputs and read-only version/hash commands. Worker writes
only the five named outputs in this package directory; cairn and corvid write
their registration, dispatch and review evidence here. Preserve all r1 bytes.
No upgrade, migration, research execution, live controller implementation,
or other package dispatch under this contract.
