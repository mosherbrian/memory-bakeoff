# muse-drafter: Compaction Cliff code pass — what the released verifier actually does (spark, 2026-09-15)

Code-grounding step 1 from `CANDIDATE-CARD-COMPACTION-CLIFF.md`, done from the
**Apache-2.0** repo `searchsim-org/cikm26-knowledge-triage` (raw files; no clone,
no install, no run). Corrects one prose-vs-code phrasing in the card. $0.

## Inventory

| file | role |
|---|---|
| `knowledge_triage/classifier.py` | `KnowledgeType` = constraint / procedural / belief / preference / episodic; `classify_instruction`, `classify_lines` |
| `knowledge_triage/preservation.py` | per-type preservation checks (the "verifier") |
| `knowledge_triage/operators.py` | `type_compact`, `type_decompose`, `type_retrieve` + baselines (`hierarchical_summarize`, `temporal_window`, `aggressive_prune`) and metrics (`constraint_locality_violations`, `constraint_recall_at_k`) |
| `knowledge_triage/{kb,safety_margin,cascade_singleton,classifier_cascade,learned_classifier,clients,secrets,spend}.py` | KB, safety margin, cascade/learned classifier, model clients |

## What the verifier does (the reusable part)

The paper prose says a "canonical form (negation + object phrase)". The **code**
implements preservation per type, and for constraints it is **key-token
substring survival**, not a canonical phrase:

- `constraint_key_tokens(text)` → ≤ **5** lowercased distinctive tokens: at most
  one **negation keyword** (`never|must not|do not|shall not|cannot|forbidden|
  critical|mandatory|required|important`) plus tokens that contain `._/-`, are
  capitalized, or are ≥6 chars.
- `constraint_preserved(orig, out)` = **all** key tokens appear as substrings in
  the output (`d_C = 0`). Empty key set → trivially preserved.
- `procedure_preserved` = primary command + first argument survive (regex over
  `run|execute|install|build|test|deploy|npm|yarn|pip|cargo|go`), else any of the
  first 3 long tokens.
- `belief_preserved` / `preference_preserved` / `episodic_preserved` =
  `content_recall >= 0.5 / 0.4 / 0.3` (fraction of distinctive content words).
- `PRESERVED_FN` maps each `KnowledgeType` to its check.

There is **no LLM on the verify path** — the guarantee is a deterministic
substring/recall test.

## Reuse notes for us

- **Directly adaptable:** `constraint_key_tokens` + `constraint_preserved` are a
  compact, LLM-free **prohibited/presence** check — the same shape as our
  stale-path and required/prohibited reporting. Portable into a probe (design).
- **Honest limitation:** substring token survival is crude — it can pass on an
  incidental occurrence of a token (false positive) and fail on a legitimate
  synonym/rephrase (false negative). The paper's "by construction" guarantee is
  therefore only as strong as this crude check **plus** classifier recall. Any
  adaptation should treat it as a *floor*, not a proof, and pair it with the
  marker-free discipline already in the stale-path probe.
- **Thresholds are free parameters** (0.5/0.4/0.3 recall, ≤5 key tokens) — pin
  them before use, do not inherit silently.

## Card correction

`CANDIDATE-CARD-COMPACTION-CLIFF.md` described the verifier as "canonical
negation + object". That is the paper's prose; the **shipped implementation** is
key-token substring survival + per-type recall thresholds. The card's
Verification/Next fields should say "code pass done; verifier = key-token
presence (see this note)".

$0, raw-file reads only, no run, no data download. — muse-drafter (Spark)
