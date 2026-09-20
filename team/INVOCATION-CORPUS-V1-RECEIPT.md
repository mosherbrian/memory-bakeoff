# Row 36 receipt — invocation-benchmark scenario corpus v1 (smoke tier)

**Seat:** worker-glm-2 (implementer) · **Date:** 2026-09-14 · **QUEUE:** row 36 · **Verifier:** Corvid (design fidelity)
**Spec:** `team/DESIGN-INVOCATION-BENCHMARK.md` (§2 corpus, smoke tier §2.5) · **Cost:** $0, no runs, no LLM

## Artifacts (`team/invocation-corpus-v1/`)

- `corpus.jsonl` — 12 scenarios (S01–S12), each 1 moment + 2 fillers, moment never adjacent to a moment (trivially: exactly one moment per scenario, turns 1/3 fillers).
- `manifest.json` — per-moment `record_set`, `correct_action_set`, `wrong_action_set`, `topic_reachable` (withheld from systems).
- `hashes.json` — frozen hashes.

| | |
|---|---|
| Corpus sha256 | `d708da49…b81bd6` |
| Manifest sha256 | `48c380f2…2bbb233` |
| Seed | `20260914` (deterministic; regeneration reproduces byte-identical files) |
| Tier | smoke: 12 load-bearing moments (2/family × 6 families), 24 fillers |
| Split | open 9 / heldout 3 (25%; S04, S08, S12 from distinct template positions) |
| Moment strata | `moment_topic` 6 / `moment_offtopic` 6 |
| Filler strata | plain / near-miss / stale-only / anachronism rotated across scenarios |

## Family grounding (pattern-level only, no transcript content)

Family names + weights from the pilot aggregate card per design §2.2 (`env_fact`, `convention`, `negation`, `actually`, `repeated_instruction`, `wrong`; `i_said` excluded). DIGEST-V2's probe-corpus informed only generic situation *patterns* (a record pins a port; a record forbids a legacy script) — every string in the corpus is invented. No excerpt, quote, or paraphrase of transcript text anywhere.

## Leak gate (§2.4, fail-closed) — PASS, 0 violations

Check: no `correct_action_set` string appears verbatim in its own moment prompt; no correct/wrong string (len>4) appears in any filler turn. First run caught 1 violation (S05 filler naming the sanctioned script); filler reworded, regenerated, gate re-run clean. Manifest hash is the frozen reference for the pre-run gate.

## Rev 2 (2026-09-14, spark pulse) — topic-reachability mechanically verified

A token-overlap check (prompt vs record summary+content, stopwords removed)
disagreed with the asserted `moment_topic`/`moment_offtopic` split on 7/12
scenarios — the prompts shared vocabulary with records I had labeled
offtopic, and S09 (topic) shared nothing. Per design §2.4 the split must be
a pure pre-registered string test, so 7 moment prompts were reworded (no
record, action-set, or filler changes) and the corpus regenerated:

- new corpus sha256 `17730261…27a7ee7` (manifest unchanged `48c380f2…`)
- topic-reachability check: **12/12 agree** with the manifest split
- leak gate re-run: **0 violations**

(`team/INVOCATION-CORPUS-V1-REDERIVE.md` verified the Rev 1 corpus hash;
this Rev 2 hash supersedes it. Determinism re-verified implicitly — same
seed, same script, new prompt strings.)

## Out of scope (not authorized here)

No runs, no adapters, no OFF-control pass (that establishes `L` per B2 at run time), no tier decision beyond smoke. Next steps for GiLMore/Stratum: tier call (standard needs 60 moments), harness-trigger pin (`pi-change-trigger` db31ea3e), OFF-first scoring per §6.
