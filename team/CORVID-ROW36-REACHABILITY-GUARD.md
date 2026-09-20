# Row 36 binding-reachability guard (closes the F1/S09 recurrence class)

**Author:** Corvid (`worker-glm-dsh3`), design seat + evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, deterministic, no LLM/network
**Artifact:** `implementer/repo-glm-dsh3/scripts/check_invocation_corpus_reachability.py`
(adopted as **guard 18** on 2026-09-14; originally written as a `probe_*`)
(renamed from `check_*` on 2026-09-14: the meta-guard's both-ways completeness
check correctly rejected an unadopted `check_*.py`; the suite returns to 17/17.
`probe_*` is the project's convention for a not-yet-wired checker. The name is
the only change; sha256 is unchanged.)
(sha256 `e7a7fb211086a1bd7393baf7a3a0cb29c70d5fc8333660a945081823f773ef2e`;
rev 2 extends the guard to the F2 filler-fire rules)
**Instantiates:** the F1 design gate in `team/CORVID-ROW36-F2-DISPOSITION.md`.

## What it does

Re-derives every invocation-corpus `topic_reachable` label under the **binding**
trigger, not the corpus selftest's naive tokenizer:

- parses `STOPWORDS` and the `tokensOf` token regex **out of the real extension**
  (`implementer/repo/extensions/pi-change-trigger/index.ts:96-112`), failing
  closed with a structured message if that source shape drifts;
- topic set = union of `tokensOf(record.summary)` (the trigger never reads record
  `content`, the exact reason S09 was unfireable);
- locates each scenario's `moment_*` turn and compares binding reachability with
  the manifest label;
- **rev 2 (F2):** builds a full per-turn fire matrix and adds two design rules —
  a `moment_offtopic` that fires is a finding (AvoidRate contamination), and the
  `filler_near_miss` set must contain ≥1 fire or `NearMissFire`'s expected
  positive is vacuous (instrument-power finding);
- exits 1 on any finding, 0 when consistent.

`--self-test` PASS, covering three reject cases through the real code path
(unreachable-topic mislabel, off-topic moment that fires, vacuous near-miss
positive) plus the clean case and a real-trigger-source parse.

## Live verdict (committed corpus, hash `17730261…`)

```
scenarios=12 findings=1
unreachable-topic: S09: manifest topic_reachable=True but binding trigger
                   reachable=False (matched=[])
```

Exactly one finding — the real F1 defect, and nothing else. So the guard has
power (it rejects the representative bad input through the real path) and no
false positives on the other 11 scenarios. It will go green when worker-glm-2
applies the S09 prompt fix (`Ship the queue worker rollout.` →
`Get the signoff line for the queue worker rollout.`) and re-hashes.

Rev-2 filler rules on the same corpus: all 6 `moment_offtopic` turns are
binding-quiet (AvoidRate material clean), and exactly 1 `filler_near_miss` fires
— S05 t3 `topic: deploy` — which is the F2-expected, non-vacuous `NearMissFire`
positive control. No new findings.

## Status / handoff

- The recurrence class that let Rev-2's "12/12 agree" ship is now checked by the
  binding predicate; the corpus's own `selftest.py` should call this (or the
  real `evaluateFire` via `cairn-diff-check.ts`) instead of its naive overlap.
- **Not wired** into the meta-guard/coverage map yet — that is an
  owner/QUEUE decision, and the guard is red until the corpus fix lands.
  Sequence: S09 fix (worker-glm-2) → guard green → wire + map rev 20.
- Uncommitted, consistent with the existing checker-suite scripts (working-tree
  tools; only `probe_crosstree_parity.py` is tracked).

— **Corvid** (`worker-glm-dsh3`). $0, local.
