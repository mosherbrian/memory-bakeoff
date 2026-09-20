# Keep / replace inventory — 2026-09-20

Brian: *"I really don't want to throw the baby out with the bathwater. There are
plenty of things I do think are genuinely good and better than other agentic
workflows about what we have built."*

The test for each row is not "did it run" but **what would break if it were
deleted**, and every keep has to name a day it prevented a real failure.

## A measurement I am not going to use

I tried to rank the 80 tools in `~/.config/agent-deck` by how often they appear
in seven days of logs. The top of that list was `wake` (9,891), `sprint-status`
(5,460), `poller-liveness` (2,637). Those are the three things that run on a
timer. The list measures **logging verbosity, not value** — `rowcheck` scored 6
and it is the evidence engine the whole loop rests on, because the poller calls
it in-process and never logs the call.

A second pass meant to find dormant tools returned `escalations`, `gate-batch`
and `fleet-window` as unused, all three of which ran today. That pass was
broken. Both censuses are discarded rather than quoted.

So the rows below are graded on evidence from use, not on a number.

## KEEP — each one earned it on a named day

| what | why it stays | the day it proved it |
|---|---|---|
| `rowcheck` | Row state computed from files and exit codes. No prose, no claim, no model. | Every false "done" today was caught by disagreeing with a status cell. |
| dispatch ledger + independence rule | Author and verifier must differ, and the ledger — not prose — decides which is which. Append-only, so a seat cannot edit evidence about itself. | It is the reason four bad gates were caught instead of self-certified. |
| `escalations` (new today) | Append-only escalation ledger, read at session start and on every prompt. Needs no live listener, no port, no conductor. | 2026-09-20: corvid raised two escalations through it *instead of restarting a seat*, and both were accurate. |
| gate written from the row text alone, verified by a different seat | The gate cannot be fitted to the implementation because the writer never sees it. | Four rounds on S12-1G, each rejected for a different real defect — including a gate that passed its own 53 fixtures while mismatching the real corpus shape. |
| `check_plain_language.py` | Mechanical jargon test: our words, our ids. No model, no threshold, no calibration. | Ranked the three populations the way Brian does (84% / 80% / 36%) where laya ranked them backwards. |
| `fleet-unit-failed@` handler | A failed unit tells someone. | Caught `agent-deck-failover` the moment it was given the handler it had never had. |

**What these have in common:** none of them asks an agent what happened. Each
reads a file, an exit code or an append-only record. That is the property worth
keeping, and it is genuinely better than the agentic workflows that ask a model
to self-report.

## KEEP, BUT SIMPLIFY — the job is real, the implementation has accumulated

| what | the problem |
|---|---|
| `fleet-poller.sh` | The only driver, and it works. It is also where three of today's six bugs lived. It has a decade of special cases in a year: prose predicates, name-prefix guards, per-kind counters reset per-row. |
| `sprint-status` | The board Brian actually reads, and the idea (computed, not authored) is right. It carried the same `\bclosed\b` prose test that made it report 4/4 finished for a sprint with three finished rows. |
| `gate-batch` / `gate-write` | Correct shape — last usable round wins, rejects kept. Its cap was obsolete, its pending test could not see a returned gate, and it called `rowcheck` twice per row. All three fixed today; the pattern says it needs fewer moving parts, not more. |

## REPLACE — the job is real, this answer is not

| what | evidence |
|---|---|
| the conductor (cairn) | 23,793 tool calls in its history. **92 were dispatches (0.4%)**, 436 were writes, ~23,200 were `tail`/`sed`/`cat`/`ls`. The poller does the dispatching. Cairn is a polling loop implemented with a 27B model, and it cost the corpus run a 10x slowdown by sharing the inference server. It also switched off the gate timer and left it off. |
| `fleet-failover` | Its ladder names `conductor-glm` and `conductor-claude`, neither of which has conducted anything since 2026-09-16. It read a missing quota reading as an exhausted one and parked the fleet hourly. Now stands down when the conductor is local — which is every day. |

## DELETE — candidates, pending one honest usage check

About 28 `acp-*` wrappers for providers and seats no longer in the roster
(`acp-glm`, `acp-zcode-*`, `acp-dsh-*`, `acp-conductor*`, `acp-builder`,
`acp-veteran-*`), plus `conductor-transplant`, `new-conductor`,
`ROLLBACK-conductor.sh`. The GLM promotional window that several of them exist
for **ends today**.

These are listed as candidates, not verdicts, because the census that would
have confirmed them was the broken one.

## The rule I would hold the rest to

Anything that cannot point to a day it prevented a real failure goes in the
delete column by default. Six rows above can. The other ~74 tools have not been
asked.

## What this inventory does not settle

Whether the *sequential* shape — one producer, one independent verifier, work
moving on computed evidence — needs a fleet at all. Everything in KEEP works
without a conductor, without routing, and without seats waking seats. That is
the experiment worth running, and it is subtraction rather than a fourth
rewrite.
