# R1-evidence-synthesis — admission review (independent)

- **Action:** `R1-admission-1`, owner corvid, `01:12:40Z`–`01:37:40Z`.
- **Contract:** `package.md` sha256
  `5c3e96d2e929c29dd8a8f16b2cc96018c882172de1965df568aeb94c4be03932` (commit pin
  `11349db0`), matching `admission-receipt.json`. Not edited.
- **Sources:** `sources.json` commit `d44d341840718a3be0e7a3e0f206bbc180c94c44`;
  **122/122 files hash-match via `git show COMMIT:PATH`, 0 missing.**
- **Verdict: ACCEPTED, with one bounded source-coverage defect** (below); method and
  tier-1 sufficiency are sound.

## Arithmetic (correct)

25 admission + 60 worker + 35 verification + 30 repair + 20 re-verify + 15 Tern =
**185 seat-minutes**, as stated. Repair/re-verify are HELD. No whole-task baseline
exists, disclosed; actual durations to be recorded.

## Tier-1 sufficiency (adequate)

Pre-registered question and method; frozen sources with commit+path+sha; source-first
**blind baseline before worker output**; consequential claims need source+commit+
field+line, outcome, population, limitation and counterevidence; observed result vs
interpretation vs proposal separated; proxies (retrieval/abstention) distinguished
from task improvement and replacement from deletion; contradictions reconciled
without pooling incomparable studies; counterevidence/missing-source log; exactly one
next step or a supported no-experiment; verifier compares its **sealed** baseline to
`synthesis.md` only afterwards. Judgment claims are explicitly not mechanically
reproducible — consistent with the adopted tier-1 rule. Historical exposure is
disclosed ("director and seats have prior exposure to summaries").

## Bounded source-coverage defect

The contract says to **"start with the answer page"** and to trace **its six research
questions**, but `team/ANSWER.md` (and the dated `team/ANSWER.*.md` and
`team/INTEL/SYNTHESIS-2026-09-19.md`) are **not in `sources.json`** — all 122 frozen
files are S7–S13 study artifacts. Requirement 1 ("traceable primary evidence covers
the answer page's six research questions") is therefore **not checkable from the
declared sources**. **Smallest correction:** Tern names the exact answer-page path and
pins it (and any dated predecessor) into `sources.json`, or states that
`team/REQUIREMENTS-NEXT-SYSTEM-20260920.md` is the answer page and enumerates its six
questions. This is a source-list omission, not a method defect; the worker cannot fix
it and should not fabricate it.

**Minor:** `team/S13-KD-COVERAGE-TRANSFER/results-attempt1-repeated-tokens.json` and
`results.json` share one sha (`59b0a3b2…`) — the synthesis must not double-count the
attempt.

## Scope / allocation

Scope is only this package and declared sources; no fresh corpus/model/web
experiment, no production/config changes, no new hypothesis hidden as repair; Tern
alone accepts the research conclusion; no auto-close. Consistent with the adopted
process rules (tier 1, author ≠ verifier).

**ACCEPTED** on the unchanged pinned contract; **release the worker only after Tern
pins this admission + the sealed baseline and resolves the answer-page source gap.**
No worker dispatch, no production/session changes by corvid.
