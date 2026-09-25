# R35 feasibility — executed work where a remembered fact decides completion

**Question.** R32/R34 showed the office-access fact changes *plans* (routing) in 2 of 4 pairs. Does a conversation-born fact change *finished local work* measured by an objective end state?

**Sources inspected.** RULE-CANDIDATES-FROM-TRANSCRIPTS.md (9 rules), R17 packet (python, loopback, office access), R19 (PY1 clear T win as prose), R24/R29 (persistence: no differential once the fix was on a menu), R32/R34 (office routing, plan-only). No new transcript search.

**Candidates (candidates.json).**
- **K1 patch delivery (recommended).** Rule #5: pi-lcm changes go to Brian as format-patch files, not a push. The task is real work: fix a bug, add a test, deliver. Both channels (a local bare `origin`, an `outbox/`) exist in the arm; the common task names neither as correct. End state: the outbox patch applies to a pristine clone and passes a hidden test, and origin is unchanged. A /tmp probe with no model confirmed the oracle separates correct patch delivery, a push, and an unfixed change.
- **K2 python vs python3.** Executable (grader runs the given command with a silent `python3` stub, as on Windows), but R19 already showed the effect on the same token; low new information.
- **K3 re-enable services after a test.** Blocked: kiln has a real shell and real `systemctl --user`; a stub-only arm does not deny the real service. Smallest next step: Tern decides whether a denied-systemctl sandbox is in scope (owner tern, about 30 min design).

**Why K1 meets the bar.** Natural useful output (a working patch); objective end state (apply + hidden test + origin ref); the memory is relevant and treatment-only; the common task gives what a normal request gives ("deliver it") and shows both channels, so it is not a trap. The oracle is not circular: the hidden test comes from the bug statement, not from any arm output.

**Limits.** The outbox folder may raise the control ceiling; that is honest, since Brian's real setup offers both. The real rule also covers continuous patch numbering and chat upload; neither is graded. One model, prior exposure.

**Recommendation.** Run K1 as one pair (about 50 seat-minutes), then decide on replication.
