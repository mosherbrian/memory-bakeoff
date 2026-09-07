# What I do every generation

> Every `- [ ]` below carries a tag in `«»`: either the file that ENFORCES it, or
> `«judgment»` for the ones no script can check. `tests/test_per_generation_checklist.py`
> refuses any item with neither. That is the point: a rule nobody enforces decays
> into a rule nobody follows, and this list already lost the rival review once
> that way.

Each item exists because skipping it cost us something real. This file is the
routine itself, not a description of one: it lives in the repo so it cannot
quietly decay the way a checklist that exists only in chat does.

## 0. The rivals check the team lead

**This is first because it was missing.** The first version of this checklist,
written 2026-09-06, listed 32 items across seven phases and did not mention the
GLM reviewers once - the exact mechanism Brian introduced after the overnight
idle-loop failure, whose whole purpose is to check *me*. A routine that
institutionalises every lesson except the one aimed at its own author has
reproduced the failure it was written to prevent. Brian caught the omission.

- [ ] `~/rivals/review-generation <repo>` before ringing the doorbell, GLM 5.3  «scripts/doorbell»
      and 5.3-flash blind to each other, reading the repository themselves
      rather than a summary I chose to write
- [ ] The reviewers read my **decisions**, not only my artifacts - the failure  «judgment»
      they were introduced to catch was a judgement call, not a bad diff
- [ ] Honour the decision token: `FIX FIRST` means repair and re-review before  «scripts/doorbell»
      the handoff goes anywhere; `ESCALATE` means Sol sees it
- [ ] `scripts/decide --review <slug>` for any judgement call I made alone  «scripts/decide»
- [ ] Degraded tier (one reviewer) escalates regardless of its verdict - a  «~/rivals/review-generation»
      reviewer that cannot disagree with anyone has agreed with nobody

## 1. Receive

- [ ] Archive the previous generation's review transcripts, first commit  «reviews/»
      (the doorbell demands a review newer than HEAD, so a round's transcripts
      can never be committed in the ring that cites them - it must happen here)

- [ ] `scripts/consume-instruction <gen>` - verify against the recorded PIN,  «scripts/consume-instruction»
      never the bare tip; the freeze releases only on a verified match
- [ ] Read the instruction end to end before touching anything  «judgment»
- [ ] Restate the scope boundary out loud, especially any NO READER RUN  «judgment»

## 2. Build

- [ ] Read the code a change touches before writing it  «judgment»
- [ ] Fix root causes in the shared function, not guards at every caller  «judgment»
- [ ] Never `sed` an import alias across files without running what I edited -  «judgment»
      one alias artefact reached four files and none was found by reading
- [ ] Nothing hardcoded that the thing itself is bound into: read the pointer,  «tests/test_gen119_run_apparatus.py»
      read the contract, read the canonical path. Two circularities so far

## 3. Verify

- [ ] Run the focused tests, then the full suite, **before** committing, not  «.githooks/pre-commit»
      chained after - twice I committed with a red suite
- [ ] Positive AND negative controls; a check that cannot fail proves nothing  «judgment»
- [ ] Mutation witnesses exercise the real write/verify path, not helper returns  «judgment»
- [ ] Separate known unrelated failures from new regressions, by name and count  «tests/test_known_failures_baseline.py»
- [ ] Confirm which code path actually executed; reading it is not evidence  «judgment»
- [ ] "It runs" is not "it works"  «judgment»

## 4. Seal

- [ ] Append-only: new attempt, never edit a sealed one  «src/memory_bakeoff/evidence.py»
- [ ] Preserve and verify every prior attempt byte-for-byte  «tests/test_gen120_evidence_closure.py»
- [ ] New contract hash; never reuse or relabel an old one  «scripts/run_gen118_freeze.py»
- [ ] Every behaviour-bearing surface bound by digest - a contract that does not  «scripts/run_reader_v6.py»
      bind the thing that will run is not a freeze
- [ ] Update `CANONICAL_ATTEMPT.md` with the exact supersession reason  «judgment»
- [ ] Confirm zero reader calls when the generation forbids them  «scripts/run_reader_v6.py»

## 5. Report

- [ ] Plain-English recap first: what changed, what was tested, what happened,  «scripts/doorbell»
      what it means, what comes next. Brian's #1 standing requirement
- [ ] Exact committed HEAD, attempt path, contract hash, test counts  «judgment»
- [ ] State nulls as no-evidence, not as findings  «judgment»
- [ ] Retract anything I published that later proved unsupported, in the same  «judgment»
      place I published it
- [ ] Never relay a subagent's reconstruction as a finding, or its jargon as mine  «judgment»

## 6. Hand off

- [ ] `scripts/doorbell` - the recap gate refuses jargon and short summaries  «scripts/doorbell»
- [ ] Pin `origin/main`, record it in `PENDING.json`, arm the watcher  «scripts/doorbell»
- [ ] Escalate on the ladder when the answer is late. **Do not idle-poll all  «scripts/await-instruction»
      night.** Coaxing Sol through the web UI is authorised and always was

## What I never do without authorisation

Run the reader. Regrade a sealed attempt. Revive a retracted claim. Rewrite
history.