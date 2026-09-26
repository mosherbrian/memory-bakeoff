# Local GPU test dependency — effective immediately

Tern ·26 September2026 · Sponsor rule, not a supplied facility or test result.

**No fleet test run on llama-swap port8080’s `gpu` group until Claude ships GPU booking.** Build order: reflector tonight, then booking. Claude owns the booking implementation and workload transitions. Tern must not hand-pause Cairn, move ClawdBot, stop night jobs or improvise a reservation as a substitute.

| Delivery activity | Dependency |
|---|---|
| Letta comparison using a local GPU model | Brian’s trial go-ahead **and** a valid booking covering foreground/background calls |
| Letta local backend with an authorized remote model | Local backend does not itself imply GPU use; ordinary trial approval/cost limits still apply |
| OptionB Pi pilot using that GPU group | Booking before any pilot model request, including setup smoke tests |
| Laya fine-tuning or GPU evaluation/teacher-label test | Relevant execution/data authorization and booking; current candidate preparation is not training approval |
| CPU-only extraction, duplicate grouping, split checks, source review | Continue now without reserving GPU |

The mechanism is to pause Cairn, move ClawdBot to NPU, keep night jobs off, expire itself and mark the run **clean or disturbed**. Its actual interface is not yet supplied; do not invent commands or assume a lock file accomplishes these transitions.

Before a GPU run, retain the booking identifier, owner, target resource, start/expiry and workload-isolation status supplied by the shipped mechanism. The test’s bounded execution must fit the booking; expiry/failed isolation stops further GPU test requests. Do not auto-renew or route around the resource rule. The booking owner handles restoration/release through the mechanism.

At completion, retain the clean/disturbed disposition with the result. A disturbed run is not clean comparative evidence: show it separately, retain all outputs/costs, and do not silently drop it or automatically rerun it. A rerun must still fit the original approved budget or receive the necessary go-ahead. This is part of the existing trial contract, not another review committee.

**Fleet metrics:** a documented booking pause is a named resource wait, not avoidable idle. Keep raw inactive lane-time visible and classify the pause using the booking interval; do not retroactively invent bookings for historical inactivity. No claims about reduced interference until the mechanism and a run exist.

**Current state:** no booking available to this survey; no local-GPU fleet test launched. GPU-dependent execution waits; independent delivery preparation continues. [Queue](QUEUE.md).
