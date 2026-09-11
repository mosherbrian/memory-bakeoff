# VERIFIER — P1-1 (tessellate-export worker concurrency)

**ARM-BLIND.** Apply identically to every slot of this case, both
repetitions. This file contains no arm, adapter, or mechanism references;
it scores observable outputs only.

**Inputs (harness-supplied):** (1) the contents of `config/worker.json` as
left by the run; (2) the full text of the agent's final assistant message;
(3) the session transcript. Absence of the config file scores every file
check FAIL.

## Hidden requirement (lives only here + in seeded history)

The seeded 2026-09-02 session fixed the worker concurrency cap at **3**
(license server hard-drops >3 concurrent exports; a dropped license
corrupts the batch). The workspace is silent on worker concurrency —
no current file states or implies it. A run that does not recover the
seeded decision cannot satisfy R2 except by luck.

There is no superseded instruction in this case; nothing in the run may
be penalized for mentioning history.

## Checks

- **R1 (REQUIRED)** — `config/worker.json` exists and parses as JSON.
- **R2 (REQUIRED)** — its `concurrency` value equals `3` (number `3` or
  string `"3"`).
- **R3 (REQUIRED)** — the final answer states the concurrency cap as 3.
- Extra keys are allowed and ignored. Only `concurrency` is scored.

## FAIL triggers (any one ⇒ case FAIL)

- `concurrency` is 4, 8, 16, absent, or any value other than 3.
- The config does not parse.

## Case verdict

PASS iff R1–R3 all PASS and no FAIL trigger fires. Binary; no partial
credit.

## Mention-vs-selection note (planner VERIFIER RULE)

No obsolete instruction exists in this case, so no mention/selection
distinction arises. The mechanical `verifier.py` still implements the
shared sentence-level rule (selection cues + stale markers, rejection
cues permit) with an empty marker set, and its validation fixtures cover
the core value checks both ways.
