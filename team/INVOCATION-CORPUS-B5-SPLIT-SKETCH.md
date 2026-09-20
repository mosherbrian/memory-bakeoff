# B5 paraphrase-split build sketch (corpus tier-up prerequisite)

**Seat:** worker-glm-2 (corpus owner) · **Date:** 2026-09-14 · **Cost:** $0, no runs
**Parent:** `team/DESIGN-INVOCATION-BENCHMARK.md` B5 (tell-removed paraphrased
split + necessity/sufficiency counterfactual); this sketches the build, it
does not build it.

## Why the current corpus can't serve as its own B5

The smoke corpus passed the mechanical topic test — but several moments are
winnable on lexical fingerprint alone (exact distinctive tokens shared
between prompt and record): S05 (`deploy-legacy.sh`), S01 (`staging`, `8443`
adjacent), S07 (`retry`). A system doing substring match would score
`FBMR_topic` without anything resembling noticing. The held-out split (S04,
S08, S12) rotates *templates*, not *lexical cues*, so it does not catch this.

## Proposed build (deterministic, $0, pre-run)

1. **Paraphrase map (frozen, committed):** for each of the 12 moments, one
   tell-removed paraphrase of prompt AND record summary/content that shares
   **zero content tokens** (same tokenizer + stopword set as the self-test's
   topic check) while preserving the situation. Example:
   - S05 prompt "Deploy tonight's build with the legacy script." → "Ship this
     evening's artifact with the deprecated procedure." Record summary "legacy
     deploy forbidden" → "old release path banned"; content keeps the exact
     script id `deploy-legacy.sh` (the *injection payload* must stay exact per
     F3 — only the human-readable cue words are scrubbed).
2. **Mechanical acceptance:** the self-test's overlap predicate must read
   `moment_offtopic`-equivalent (zero shared tokens) for all 12 paraphrased
   pairs, while the record *ids* and action sets are byte-identical to the
   open split. A system scoring high on open but collapsing on paraphrase is
   reported as **cue-overfit**, not as proactive invocation.
3. **Necessity/sufficiency counterfactual (puppet-level, harness-run):**
   (a) wrong-without-memory: OFF puppet takes `wrong_action` on all 12
   paraphrased moments (establishes load-bearing, B2-style frozen `L`);
   (b) correct-with-only-cover: puppet with *only* the covering record
   injected takes `correct_action`. If (b) fails, the moment is broken (the
   record doesn't actually govern the choice) and is excluded per §4.5, not
   scored.
4. **Size:** paraphrase the smoke 12 first (validates the procedure); standard
   tier (60 moments) gets paraphrased at build time, same map format.

## Open for Corvid/Assay

- Is zero-shared-token too strict (does it also strip legitimate topic
  signal a real proactive layer should use)? If so, define the allowed
  residual (e.g. generic verbs) explicitly.
- Should the paraphrase map itself be held out from any prompt/tuning pass?
  Recommend yes — it is adversarial material.
