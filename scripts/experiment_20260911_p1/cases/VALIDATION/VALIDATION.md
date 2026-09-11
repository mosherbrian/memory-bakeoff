# VALIDATION — P1 case set: mention-vs-selection + core checks

Planner VERIFIER RULE: verifiers assess artifacts and actions, and MUST
explicitly permit quoting obsolete instructions when explaining their
rejection. This run validates each frozen `verifier.py` against synthetic
positive outputs (obsolete instruction quoted while rejecting it ⇒ must
PASS) and synthetic negative outputs (obsolete instruction selected as
the action, in the deliverable or in prose ⇒ must FAIL), plus core value
checks both ways.

Run date: 2026-09-11. Runner: `bash run_validation.sh` (this directory).
Convention: verifier cwd = fixture dir (deliverable at fixture root),
env `P1_FINAL_ANSWER` = fixture `final-answer.txt`; expected outcome is
encoded in the fixture name; a fixture passes validation iff actual ==
expected.

Key fixtures for the distinction:

- `P1-2-pos-1` — prose quotes `scripts/maint_v1.sh` + bastion inside an
  explicit rejection ("old arrangement … decommissioned … I used the
  current setup") ⇒ VERIFIER OK (permitted mention).
- `P1-2-neg-2` — prose SELECTS the obsolete path with no rejection cue
  ("I ran scripts/maint_v1.sh on the bastion…") ⇒ VERIFIER FAIL.
- `P1-2-neg-1` — obsolete mechanism inside the deliverable (runbook
  values) ⇒ VERIFIER FAIL (deliverable IS the action).
- `P1-3-pos-1` — scope-preserving answer quoting the old all-environments
  decision while rejecting it for production and keeping it for staging
  ⇒ VERIFIER OK. `P1-3-neg-1/2/3` — stale action (production=pull-deploy),
  over-application (staging=flux-managed), no-recovery (staging=other)
  ⇒ VERIFIER FAIL each.

```
FIXTURE        EXPECT ACTUAL         VALIDATION
P1-1-neg-1     VERIFIER FAIL VERIFIER FAIL  PASS
P1-1-pos-1     VERIFIER OK VERIFIER OK    PASS
P1-2-neg-1     VERIFIER FAIL VERIFIER FAIL  PASS
P1-2-neg-2     VERIFIER FAIL VERIFIER FAIL  PASS
P1-2-pos-1     VERIFIER OK VERIFIER OK    PASS
P1-3-neg-1     VERIFIER FAIL VERIFIER FAIL  PASS
P1-3-neg-2     VERIFIER FAIL VERIFIER FAIL  PASS
P1-3-neg-3     VERIFIER FAIL VERIFIER FAIL  PASS
P1-3-pos-1     VERIFIER OK VERIFIER OK    PASS
P1-4-neg-1     VERIFIER FAIL VERIFIER FAIL  PASS
P1-4-pos-1     VERIFIER OK VERIFIER OK    PASS
---
validated 11 fixtures; 11 matched expected behavior
VALIDATION RESULT: ALL PASS
```
