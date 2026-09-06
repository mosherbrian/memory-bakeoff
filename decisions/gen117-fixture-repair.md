# DECISION choose: gen117-fixture-repair

- taken: 2026-09-06T11:46:02-07:00
- commit: 7b54fffcce54d239179280c8234160cf284978ad
- kind: choose

## What I chose

Nothing. I am deliberately NOT choosing the Gen117 fixture repair, and I am
recording that refusal as a decision so it is reviewable rather than implicit.

## What I rejected

I rejected making the obvious fix myself. The Gen117 run failed because canonical
values are two words sharing a head noun ("sector fenwick") and the reader
answered "fenwick"; 36 of 48 selections dropped the head noun and scored
UNSUPPORTED_VALUE. Loosening `_norm()` or `value_present()` to accept the
distinguishing token would very likely turn 0/12 interpretable cores into a
usable run in one line.

I rejected it because I would be choosing it AFTER seeing which answers it
produces. That is tuning the ruler to the outputs, and it is precisely the defect
that produced the Gen114 headline retracted this morning.

I also rejected the framing that this is a small formatting matter. Value surface
form is a run-bearing semantic: it determines what counts as a correct selection,
and it applies to controls and treatment alike.

## The evidence

- `results/gen117/attempt1` - sealed, manifest verifies, NON_EVIDENCE, 0/12
  interpretable cores. 60/60 COMPLETED, no transport failures.
- Measured from `reader_raw.jsonl`: 48 selections, 6 exactly canonical, 36 head
  noun dropped, 6 other.
- Sol's Gen117 instruction: "Do not repair a run-bearing semantic after
  exposure."
- `research/PI_READER_INTERFERENCE_RUN_GEN117.md` states three options with no
  preference expressed.
- Sent to the control plane for ruling; not yet answered.
- Since `7b54fff` the run preflight compares all five frozen source hashes and
  refuses with FROZEN SOURCE CHANGED, so this refusal is now enforced by the
  apparatus rather than resting on my compliance. Before that commit I could have
  edited the matcher, re-run, and produced a green attempt2.

## What follows

Gen117 attempt1 stays NON_EVIDENCE whatever is decided. Any of the three options
requires a fresh freeze and a fresh run under a new generation. I will not run
again until the control plane rules.
