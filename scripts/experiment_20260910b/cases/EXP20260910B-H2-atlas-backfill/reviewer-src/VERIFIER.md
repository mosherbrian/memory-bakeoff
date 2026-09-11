# VERIFIER — EXP20260910B-H2 (atlas 2024 backfill plan)

**ARM-BLIND.** Apply identically to every slot of this case, both
repetitions. This file contains no arm, extension, or mechanism references;
it scores the observable run plan only.

**Inputs (harness-supplied):** (1) the full text of the agent's final
assistant message (the run plan); (2) the session transcript. The case's
work product is the plan itself; no file changes are required.

## Hidden requirement (lives only here + in seeded history)

The seeded 2026-08-20 incident session fixed a standing rule: shard
**2024-03** is permanently excluded from bulk backfills and is refreshed
only by a separate manual patch process (`scripts/patch_2024_03.py`), and
the reason is the bulk writer deadlock on that shard's oversized index
(prior corruption). The workspace gives the agent no hint that 2024-03
differs from the other 2024 shards, so without recovering the seeded
session there is no basis to single it out.

## Checks (all REQUIRED)

- **R1** — The plan's bulk backfill run list includes 2024-01, 2024-02, and
  2024-04 with a concrete bulk command for each (completeness of the task).
- **R2** — 2024-03 is NOT in the bulk backfill run list: no bulk backfill
  command in the plan names or includes 2024-03 (including "run all
  shards" phrasing that covers it).
- **R3** — The plan assigns 2024-03 a distinct, non-bulk handling: it names
  the manual patch path (`scripts/patch_2024_03.py`, paraphrase of the name
  accepted, e.g. "the 2024-03 patch script") OR states unambiguously that
  2024-03 must be handled separately/manually, not with the bulk runner.
- **R4** — The plan states an operational reason 2024-03 cannot be bulk-run
  — any of: deadlock / locking, oversized index, prior sink corruption /
  the August incident. Paraphrase is fine; silence is not.

## FAIL triggers (any one ⇒ case FAIL)

- Any bulk backfill command whose shard set includes 2024-03.
- A plan that re-runs all four 2024 shards uniformly.
- A plan that omits 2024-03 entirely without assigning it any handling
  (R3 unsatisfied).

## Case verdict

PASS iff R1–R4 all PASS and no FAIL trigger fires. Binary; no partial
credit.

## Authoring rationale (for the record)

The workspace presents all four shards as equally stale with no
differentiating signal, so the only route to R2–R4 is recovering the
seeded incident session. A uniform "re-run all four" plan — the natural
reading of the workspace — fails.
