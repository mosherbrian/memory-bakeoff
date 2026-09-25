# Writing for Brian's page

Brian's words (2026-09-24): "Tern's writing style is a little, um, formal. Can we get it more user centric?"

Brian reads the Sprint page on his phone. Keep the precise wording in the existing fields for the record and for
agents. Add a short plain field next to it, written for Brian. The page shows the plain field when it exists.

| File | Precise field (keep) | Add, for Brian |
|---|---|---|
| RESEARCH-PRIORITIES.json item | `why`, `next_step` | `for_brian_why`, `for_brian_next` |
| RESEARCH-PRIORITY-HISTORY.jsonl event | `reason` | `for_brian` |
| research package acceptance.json / terminal-disposition.json | finding, reason | `for_brian` |
| team/INTEL/triage/<report>.json | `reason` | `for_brian` |

## Rules

1. Talk to Brian: "you", "your work", "we". Say what it means for him first.
2. One or two short sentences, at most about 25 words.
3. Everyday words. No package IDs, seat names, hashes or file names.
   Avoid: tier, rubric, fixture, provenance, supersession, disposition, admission, frozen, bounded, proxy, gate.
4. Say uncertainty plainly: "not checked yet", "we don't know yet", "only in lab tests".
5. Numbers only when they help ("0 of 40"), with what they count.
6. Past = what happened; next = who does what next.

## Before and after

| Formal (keep in the record) | For Brian |
|---|---|
| Select a genuine work task, observable completion rubric and boundary before another experiment design. | Next: pick one real task you do often and decide how we will tell if memory made it go better. |
| A work-task comparison is only useful if its checks are sound; local gate failures establish that risk, and the new reports add unverified leads. | A test is only as good as its scoring. Our own checks have failed before, and outside reports say popular tests disagree with themselves. |
| No established real-work/compaction benefit in this frozen record; local proxy gains do not establish external transfer or task benefit. | Nothing measured so far shows memory helping your real work. The gains we saw were in lab tests only. |
| This design is not ready; not proof that no suitable experiment or memory aid exists. | The test could not be built from our old data: it checks recall, not real work. That does not mean memory can't help. |
| Reported identical-answer judge variation and supersession/dedup hazards are relevant to existing instrument and mutation questions. | Outside report: the same answer got different grades on repeat runs. Useful for question 2; not checked yet. |
| Initial explicit ranking of an existing question; no earlier ranked order is asserted. | First ranking of this question. |
