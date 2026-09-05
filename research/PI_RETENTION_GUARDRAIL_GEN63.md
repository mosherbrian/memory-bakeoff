# Gen63: the screen now notices when a filter deletes the evidence

## Why this generation exists

Gen62 turned every unsafe bank safe by deleting 158 of 188 tests, 142 of them
sound, and the frozen screen returned PASSED. That was the screen working
exactly as written and being wrong, because every quantity it measures improves
as tests disappear. A bank with no tests accuses nobody.

So the measuring instrument was the broken component, and it gets repaired
before anything else changes. This generation runs **no model, no GPU, no
regeneration and no filter change**. It re-reads outcomes already committed and
says what the screen should have concluded.

## The rule, predeclared

`gen63-retention-guardrail-v1` adds two conditions, checked **before** the
reference-validity test so a hollowed bank is never labelled valid on its way
out:

- **Retention** — a bank must keep at least **50%** of its original distinct tests.
- **Liveness** — no bank may be emptied, whatever the ratio says.

Retention is a precondition for admissibility, not another score. Sensitivity and
specificity are then read only from banks that still exist, which is what those
numbers were always assumed to mean.

## What the corrected screen says

| generation | as recorded | under the guardrail | |
|---|---|---|---|
| Gen60 | PASSED | PASSED | unchanged |
| Gen61 | PASSED | PASSED | unchanged |
| Gen62 | PASSED | **UNEVALUABLE** | **changed** |

All eight Gen62 banks are discarded as hollowed, so no task carries an
admissible bank and coverage cannot be met. Retention per bank:

| task | retained |
|---|---|
| valve | 0.333 |
| ledger | 0.292 |
| tally | 0.250 |
| pathsafe | 0.192 |
| dispatch | 0.154 |
| culvert | 0.107 |
| manifest | 0.036 |
| thermo | 0.000 |

Not one bank reaches half. The best keeps a third; `thermo` keeps nothing.

Gen60 and Gen61 ran no deletion filter, so their retention is total and their
verdicts cannot move. They are re-scored here precisely to show that: **the
guardrail changes the one generation that hollowed its banks, and no other.**

## What this does and does not establish

It establishes that our screen was reporting success for a filter that destroyed
its own evidence, and that the defect is now closed. Gen62's real result is
UNEVALUABLE: the critic did not demonstrate precision, and the data it left
behind cannot support a claim either way.

It establishes nothing new about the critic. No new critic call was made and no
Gen62 output changed. The removal-precision figure of 0.101 stands exactly as
measured; this generation only stops that run being scored as a pass.

The 50% floor is a judgement, not a derived quantity. It is predeclared here
rather than tuned, and I would not adjust it after seeing a future result — the
whole point of Gen63 is that thresholds chosen after the fact are worthless.

## An honest note on the pattern

Three generations in a row returned PASSED while the underlying evidence got
weaker: Gen60 passed with half its banks unusable, Gen61 passed having changed
nothing, Gen62 passed having deleted 84% of its tests. A verdict that survives
all three is not measuring what we care about. This repair addresses the third
case. The first two are still worth revisiting: as recorded in Gen60, specificity
cannot fail once the validity gate has run, so it contributes nothing to any of
these verdicts.

## What comes next

With the screen repaired, Gen64 can fairly test a critic that must **name the
specific unsupported extra condition** before it may delete anything — a positive
obligation to justify each removal, which the Gen62 prompt never imposed. Under
the guardrail, that critic can no longer earn a pass by deleting everything.

## Artifacts

- `results/pi_retention_guardrail_gen63/rescore.json` - all three generations, before and after
- `src/memory_bakeoff/evidence_ruler/retention_screen.py` - the rule and its contract
- `scripts/run_gen63_rescore.py` - the re-score, reading committed outcomes only
