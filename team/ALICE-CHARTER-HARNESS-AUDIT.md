# Charter harness audit — 7 of 10 guardrails already met; three additions close it

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** apply `ALICE-HARNESS-GUARDRAILS.md` to our own
P2 plan (`team/PORTFOLIO-CHARTER-draft.md`) · **Cost:** $0, read-only, one turn.

**Verdict:** the charter's shared-harness spec is **stronger than every vendor
harness examined today** — it is programmatic, judge-free by default, sha-pinned,
null-inclusive, and emits raw opaque results. It meets 7 of the 10 guardrails.
Three concrete additions close the rest. This is a read-only audit of a draft
owned by Stratum; the additions are proposed, not applied.

## Guardrail compliance

| # | Guardrail (from `ALICE-HARNESS-GUARDRAILS.md`) | Charter status | Evidence |
|---|---|---|---|
| 1 | Pin the judge **prompt** | **N/A by default** — primary labels are PROGRAMMATIC ("sha-pinned code, no judgment, no judge"); `upstream_llm_judge` is `requires_reader_authorization`, default none | L261–264, L310–311 |
| 2 | Subject must not supply the judge prompt | **Met** — no LLM judge runs without Brian, and no provider override path exists | L310–311 |
| 3 | Pin the dataset category id→name map | **N/A** — the benchmark of record is memconflict (contract `05212108…`), not LoCoMo | L175–179 |
| 4 | Ship per-question raw rows, full top-k | **Mostly met** — "emit raw results to opaque ids"; **retrieval-depth budget not stated** (see addition B) | L170–174 |
| 5 | Run the full-context null in-harness | **Met** — "long-context null as the arm every system must beat" | L189–190 |
| 6 | Every number carries answerer+judge+split+budget+top-k | **Partial** — benchmark/dataset/seed/split pinned; **exact eval-workload model IDs not pinned** (addition A) | L175–184, L197–202 |
| 7 | Distinguish `third-party-attributed` vs `-measured` | **N/A** — our own runs | — |
| 8 | Label/preserve invalid and misclassified runs | **Mostly met** — "a metric that turns out to need judgment where this charter said programmatic is itself a P3 finding, reported — not silently reclassed"; **no explicit invalid-run label** (addition C) | L287–289 |
| 9 | Re-derive aggregates from raw rows | **Met in spirit** — "receipts claim; state is" + programmatic verifier over delivered results | L191–193, L261–263 |
| 10 | Keep artifacts shippable / hash+recipe | **Met** — sha-pinned contracts, frozen dataset, opaque ids | L175–184 |

## The three additions

**A. Pin the exact evaluation-workload model ID(s) per system.**
The budget section names lanes (`deepseek-direct`, `muse`, `InferX`) and asks for a
price receipt, but the harness spec does not fix the **model version** that
exercises each system. For any system whose capture or answer generation calls an
LLM, that model *is* the "answer model" and moves delivered-level outcomes. Add
one line per system: `system → model_id@version` (or `none; deterministic`).
*(Guardrail 6; motivated by Hindsight's Gemini-only number and MemBukkit's
gpt-5.4 reader.)*

**B. State the retrieval-depth / top-k budget explicitly.**
The metrics define k∈{3,5}, but not how many candidates a system may retrieve
before scoring. That budget is exactly what made agentmemory's R@20/MRR
unre-derivable once its stored list was truncated. Add: `retrieval-depth = N
candidates, scored at k=3/5`, and require the raw N-row list shipped.
*(Guardrails 4, 6.)*

**C. Add an explicit invalid-run label, and a judge-prompt pin *if* the LLM judge
is ever authorized.** The charter reports misclassification as a P3 finding
(good) but has no `INVALID`/`abstained` label for a run that fails preflight
(adapter pin mismatch, unseeded draw beyond the repeat budget). And if Brian ever
authorizes `upstream_llm_judge`, the harness must hash and record the **prompt**,
not just the model — the MemOS same-model-pair 11.4-point gap is the reason.
*(Guardrails 1, 8.)*

## Why the charter is already ahead

- **Programmatic primary:** no LLM judge in the bar path removes the single
  largest comparability defect found today (every vendor's headline depends on a
  judge or a judge-free metric that is not comparable to the others).
- **Frozen benchmark + contract + dataset sha** and "every run re-asserts the
  pins before writing" is stronger provenance than any vendor artifact we
  checked.
- **Delivered-level counting** and the **stale-use penalty** are the two
  instruments the field does not publish; using them is the program's edge.
- **False-supersession rate printed beside every number** makes the write-side
  cause visible next to the retrieval score — exactly the "labels must travel"
  discipline vendors omit.

## Recommendation

Stratum (owner) adds A–C as three lines to §"Shared harness spec"; no number or
criterion changes. Then the charter meets all 10 applicable guardrails, and the
P2 harness is auditable by the same standard we applied to the field.

## Method and limits

- Read-only audit of `PORTFOLIO-CHARTER-draft.md` (441 lines) against my 10
  guardrails; no edits to the draft, no benchmark, no LLM. Line cites are to the
  draft as read.
- Guardrails 3 and 7 are genuinely not applicable to this campaign; they are
  marked N/A, not counted as passes.
