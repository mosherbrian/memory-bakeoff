# R20 remedy estimate (read-only; no code edited)

Estimate by Claude, 2026-09-25 about 19:55Z, for the six blockers in candidate-review.md. The base is the rejected candidate d0264366, whose sound parts are kept: prospective Pkg.Stamp, block-before-transition, one director notice, decide-before-mutation, terminal rules and the size bound.

## Smallest complete design
1. **Question binding.** `dispatch --question-id Q` is stored in Pkg.QuestionID (required when the stamp is on). Worker, verifier and director stamps must have `moved.question_id == Pkg.QuestionID`. The loop becomes the authority, not an external receipt file.
2. **Owner authorization.** `next.owner` must be a config seat, the director, the duty seat, or a name in a new config list `stamp_owners` (for example "claude", "brian"). Anything else: E_STAMP_OWNER.
3. **Attributable drop acknowledgement**, inside the declared same-UID trust boundary. This reuses P13's capability mechanism (ack.go / Cap: 256-bit, 0600 file, digest stored, rotated). A dropped item in a stamp moves the package to `blocked` with E_DROP_UNACKED. The loop issues a capability for that item to the named owner, delivered on that owner's own channel (wake to the seat, or the notify-claude ledger for claude). The owner runs `agent-loop drop-ack --qid Q --item N --cap-file F`. The loop records the ack in its own state and advances on the next tick. The worker never sees the capability, so a file it writes cannot count as an acknowledgement. An unacked drop past its deadline escalates on the existing director, duty, external ladder. Worker-written `ack:true` files are no longer accepted at all.
   - **Cheaper alternative (saves about 20 min):** no per-owner capabilities. Every dropped item blocks until the DIRECTOR disposes of it with `agent-loop drop-dispose` (director authority, like decide). Attribution is then "director accepted ownership on the owner's behalf". That is weaker, but honest and simple.
4. **Director stamp persistence.** The validated director stamp is copied byte-exact into claims_dir as `decide-<qid>.stamp.json` (loop-owned). Its sha256 and parsed next or terminal go into Pkg.DecisionStamp. The core event is unchanged (core stays frozen).
5. **Exact-action measurement.** Each stamp's `next` gains a required `action_id`. The loop records every commitment (question, action_id, owner, deadline, source execution) in a loop-owned commitments log. Start evidence is `dispatch --fulfills ACTION_ID` (recorded at dispatch), or a drop-ack or decide that names the action. A small addition to measure_v2 joins them exactly on action_id, owner, question and deadline: started on time, late, pending, or no start evidence (unknown). There is no question-only join.
6. **Path confinement.** One helper refuses absolute paths and `..` for every stamp, receipt and decide path.
- **Rollback qualification.** On rollback, `status` lists stamped packages still open. The procedure holds them, and the director disposes each explicitly before the old binary resumes. There is no silent contract change.

## Exact tests (unit rig plus CLI)
- **Negatives:** undeclared or mismatched question_id; unknown next.owner; worker-authored ack file for another owner (must stay blocked); drop-ack with a wrong, stale or rotated capability; drop-ack for another package or item; path escape for stamp, decide and receipt.
- **Positives:** acked drop advances once; replayed ack is a no-op; director stamp persisted, and its hash matches after restart; commitment with a `--fulfills` start reported on-time or late; pending commitment at the window end is censored; commitment with no start is reported unknown.
- **CLI:** the built binary against a temp config: dispatch, claim with stamp, drop-ack, decide --stamp, status. This covers the exact command surface, not just Loop methods.
- **Planted faults:** keep the 14, and add about 8 more (owner allowlist, question match, capability digest, cross-item ack, persistence, action_id join, path helper, rollback hold).

## Minutes
| Phase | Full design | Director-dispose alternative |
|---|---|---|
| Author (code, tests, CLI tests, faults, docs) | 90 | 70 |
| Independent review | 25 | 20 |
| Held repair + recheck (not automatic) | 20 + 15 | 15 + 10 |
| New allocation needed | **150** | **115** |
The held witness (15), activation (10) and follow-up measurement (15) already in R20 are unchanged and not repurposed. The R20 ceiling would go from 200 to about 350 (full) or 315 (alternative).

Recommendation: the full design. Item 3 is the part that makes "someone owns the dropped item" true rather than asserted, which is the point of the stamp. The alternative is acceptable if minutes matter more than per-owner attribution.
