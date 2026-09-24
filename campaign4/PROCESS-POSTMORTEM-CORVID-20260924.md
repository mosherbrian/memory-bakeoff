# Corvid review — proportional-proof post-mortem (bounded 10 min)

Question asked of me: does any tier or rule drop a check that caught a real campaign
defect, with a citation; and are the tier-1 research requirements sufficient. My
answer is **yes to sufficiency, and almost-yes to the dropped checks** — one class
needs a guard.

## Tiers do not drop a *behavioral* finding's catcher

Every real product/integration defect was caught by a check the tiers **retain**:
P3 false REST, P5 trusted-caller attribution, P6-r4 double verifier wakes, P6-r7
fail-open hash (`packages/P3-core-validator/acceptance-withheld.json`,
`packages/P5-clock-ingress/director-repair-decision.md`,
`packages/P6-r4-notify-timer-drain/director-readiness-findings.json`,
`packages/P6-r7-real-host-path/candidate-review.md`) came from independent review,
kept in all tiers. P6-r8 handoff latency, P8 hardcoded trusted-seat list, P11
idle-cancel (`packages/P11-live-driver-qualification/live-timeout-idle-finding.json`),
P12 lock/late-effect (`real-process-defect-ruling.json`) and P13 early-decision /
receiver `unknown.jsonl` came from **live/real-process** work, kept in tier 2
(rule 5) and partially tier 3. Planted-fault/mutation kept for tiers 1–2. Nothing
in the dropped list caught these.

## The one dropped check that caught a real defect

The **manifest/frozen-byte** check did catch a **real install defect**, not merely
format: the P13 cutover plan's `cutover.sh` omitted
`agent-loop-liveness-failed@.service` while the reviewed `agent-loop-liveness@.service`
required it via `OnFailure` (`live-wall-timer-classification` lineage →
`cutover-plan-closure-review.md`). That was found by reviewing the **frozen plan
against the actual release artifact set**. The proposal removes "manifest ceremony
for plans" and, for tier 3, "live qualification; frozen-byte rounds". Rule 5 keeps
freezing *released executable/config* inputs, so the guard survives **only if tier
3's required "failure cases" explicitly enumerate the release artifact set**
(units/config/adapters), not just the entrypoint binary. Practical fix: one line in
tier 3 — "sandbox the actual installer against the exact release artifact list and
fail on any referenced-but-missing unit/config." Without it, the P13 handler-omission
class reopens.

## Tier-1 sufficiency

The proposal's tier 1 demanded "independent reproduction, blind first" — too strong
for judgment synthesis. Your amendment is the right correction: pre-register
question/criteria/analysis, pinned data/code/environment, **traceable claims +
counterevidence + independent blind assessment, targeted reproduction where
decidable, negatives kept**. That is sufficient for a synthesis package
(P13-style director-decision work would have met it). One addition: require the
author to **state explicitly when a claim is not decidably reproducible** and what
counterevidence search was run; otherwise "judgment" becomes an unfalsifiable
escape.

## Amendment notes (practical, not implementation)

- Rule 8 "do not call a missing test result a formatting defect" is the correct
  lesson from the P13 empty `conformance-*.txt`; keep it.
- Rule 6's "never infer identity from suffixes or filenames" is exactly the P13
  `unknown.jsonl` root cause; good.
- Rule 5's "changed critical live integration needs a real witness" must define
  "critical" to include **unit/config/binary-set** changes, else the handler class
  is read as "unchanged code" and skips the witness.
- Rules 2/3/6/7 are sound and cheap: tier set at admission, reviewer can raise,
  measured boxes with one pre-specified extension, routine progress as status.
- Keep rule 8's "author is not verifier for tiers 1–3" unchanged; it is the single
  highest-yield check in the whole campaign (~92 of ~230 findings).

**Bottom line: adopt, with the tier-3 release-artifact-list check and the tier-1
undecidability-statement added.** No production/policy change by me.
