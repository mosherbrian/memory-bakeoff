# Sprint 4: repair trust, then measure

## THE GOAL

**Measure at least two memory systems on a corrected instrument, and run the
outcome comparison that was built in September and never executed.**

That is the one thing this sprint is for. Steps 1-3 below exist only because the
instruments are currently broken - a measurement window that closed seven hours
early, and a firing test whose control scores identically to the system - so
nothing measured today would mean anything. They are the route to the goal, not
the goal.

Judge the sprint on whether step 4 ran. If steps 1-3 consume the whole sprint,
that is a failure to report, not a sprint delivered. Brian set this condition on
2026-09-16 after noting that a sprint should have a goal, and that the ordering
made this one read as cleanup.


Until Saturday’s reset, the accepted plan repairs the evidence and completion
checks, then runs free local measurements. Both existing headlines remain
unpublishable. The firing test cannot distinguish useful
memory behaviour from a trivial control; its headline describes the test
machinery, not a memory system.

Kiln, the sole doer, owns the ordered work below; Corvid, the reviewer, checks
each deliverable. Where Corvid authored the underlying work, Kiln supplies the
independent check. Every completion needs an existing deliverable, a passing
declared check and a named independent verifier. Sign-offs identify the exact
file version; edits invalidate them. Passing isolated tests without connection
to the running system means “tested, not integrated,” not “done.”

1. **Repair existing claims, then automate completion checks.** Kiln checks the
   outstanding research note and corrects the missing-file claim without
   manufacturing historical evidence. Then Kiln builds the automatic checker,
   using the existing pass/fail rules. Corvid verifies its self-test; Kiln uses
   it to check Corvid’s audit of missing reviewer names.
2. **Correct the measurement period.** Kiln stores exact start/stop times once,
   generates readable dates from them and freezes the input list. Corvid
   independently reproduces the dates and numbers. A date mismatch or early
   close must fail. Relabelling the old run is allowed, but leaves the intended
   period’s result unpublishable until rerun correctly.
3. **Repair the firing test.** Kiln replaces repetitive misleading examples,
   freezes the revised test set and reruns the fixed stand-in worker. Corvid
   checks that ordinary examples no longer share the misleading wording and
   that all test self-checks pass.
4. **Measure actual systems and outcomes.** After those repairs, Kiln measures
   when at least two free local systems supply memory before a mistake; Corvid
   checks recorded system/test versions and separately reported controls.
   Kiln also calibrates correction counting against 286 saved events, then
   compares matched tasks over the corrected period for completion cost/time,
   errors, repeated discovery and human corrections. Corvid reproduces the
   results. Calibration alone can run earlier; it does not depend on dates.
5. **Enforce safeguards, then clean up.** Kiln blocks duplicate task claims and
   differences between agreed scoring rules and review checklists. Corvid
   verifies rejection of bad inputs through the running system. These follow
   measurement unless the Product Owner revisits that trade-off. Last come
   missing evidence links, stale instructions and identity checks: Kiln or
   Corvid does them; the other checks the resulting files and corrections.

Cairn, the conductor, immediately fixes automatic task alerts to read current
state and address exact seats, then connects them to passing completion checks.
Corvid verifies the alert log: at least nine in ten alerts over the trailing
14 days must lead to claimed work; declines count against it. Failing routes
pause. Furloughed seats receive no alerts.

Spend $0, run locally, allow one request at a time and stop resumably at 18:00
local. No new benchmarks, imported scores or product-specific work.
Checks compare machine fields with accompanying human text. Stop and report
when work finishes or any limit is hit; no automatic continuation.

## DECISION

Keep the accepted scope, or stop after repairing the test and defer measurement
until after Saturday? I recommend keeping it: corrected instruments can produce
useful evidence during the remaining free work windows. The downside is one
doer tackling five additions, with safeguards behind measurements. Doing nothing
preserves this order and its hard stops; it authorizes no spending or publication.

After reset, Brian separately decides publication, cheaper memory retrieval or
conditions for another campaign, using corrected numbers. Any paid comparison
needs explicit approval, with one maximum. Previously tested but unconnected
work must be finished or dropped before new post-reset measurement.
