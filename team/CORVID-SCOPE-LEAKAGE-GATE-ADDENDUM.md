# Scope + leakage addendum to the P3/P4 evidence gate

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity · **Date:** 2026-09-14 · **Cost:** $0, static reads only
**Status:** design + gap audit, **not a run**; **candidate discovery only, no score import.**
**Serves:** thread-pool item 5 (security/governance arm) and next-step 2 of
`team/CANDIDATE-CARD-MEMSEC-GATEMEM.md`.

## Why this exists (a correction to our own card)

Card 4 called scope-isolation and negative-leakage "absent from our current
reporting." That is **overstated**, and this audit corrects it before it is
quoted. Our own frozen record already measures the single-principal scope axis
and a future-leakage axis. The genuinely new thing MemSecBench/GateMem add is
**multi-principal access control** (role/trust labels across a shared pool) and
**leakage as a first-class reported harm**. Precision matters here: a gate that
re-checks work we already closed is waste, and an "absent" claim we can falsify
from our own artifacts damages the evidence-integrity seat.

## 1. What we already have (artifact-backed)

| Existing instrument | What it establishes | Receipt (sha256 first 16) |
|---|---|---|
| `scope_audit.py` — capability-vs-configuration audit (Gen76) | Before the binding: only **perseus** was `scope_isolated` / `measured`; agentmemory, hindsight, mem0 were `scope_not_exercised` / `not_demonstrable` — a *configuration* fact, **not** an engine failure (the Gen71 lesson) | `src/memory_bakeoff/scope_audit.py` `0faa1cc2b9517bba`; `results/scope_audit_gen76/scope_audit.json` `da932930ba92353b` |
| Gen78 scope-isolation ablation (`results/scope_isolation_gen78/*.json`) | One variable moves (native scope primitive bound on write+query): mem0, hindsight, agentmemory all go **6/6 collapse → 0/6** (`scope_collapse_total = 0`); perseus reused. Every engine isolates once asked; **not a ranking.** `configuration_collapse` stays untested | `research/PI_SCOPE_ISOLATION_GEN78.md` `8762be5a6f311365`; agentmemory `58d6a4af7cbba80d`, hindsight `9983705db285702b`, mem0 `d8ae810437b8e3a7` |
| `frozen_reader.py` wrong-scope metrics | Per-case `wrong_scope_context_ranks` / `wrong_scope_context_present`, aggregate `wrong_scope_context_case_rate` and `wrong_scope_answer_rate` — computed **separately from** `prohibited_*` and printed as their own summary column | `src/memory_bakeoff/frozen_reader.py` `4f4649d7f7008f1f` |
| `temporal_reachability.py` + `temporal_capability.py` | `future_leakage` probe (querying a checkpoint by ingesting a later snapshot is a runner leak) and an operation-level classifier that separates "has no clock, leakage expected" from "surface present but failed" | `src/memory_bakeoff/temporal_reachability.py`, `temporal_capability.py` |
| `longitudinal.py` `TargetKind` | Retraction/reappearance classes already named: `FUTURE_LEAKAGE`, `STALE_PERSISTENCE`, `FALSE_PERSISTENCE`, `HISTORY_ERASURE`, `SCOPE_COLLAPSE`, `CONFIGURATION_COLLAPSE` | `src/memory_bakeoff/longitudinal.py` `65e57518559696c9` |

So "scope isolation" and "leakage" are **not** greenfield. The gap is narrower
and more useful than card 4 first stated.

## 2. The precise, falsifiable gaps

- **G-A — no principal/role axis (genuinely new).** Our `scope` is a single
  opaque string (`models.py`); there is no principal identity, role, or trust
  label, and no multi-principal shared pool. GateMem's authorization-boundary
  and leak-target shape addresses exactly this. Gen76/78 closed
  *single-principal scope*; they say nothing about *who may read what*.
- **G-B — leakage is computed piecemeal but not a required report field.**
  `check_required_metrics.py` (guard 14) requires only `hit@5`, `prohibited@5`,
  `mean_context_chars` (`scripts/check_required_metrics.py` `3ae6cf05632ea8c4`).
  `wrong_scope_context_case_rate` and the leakage/retraction classes are
  **not required**, so a summary can drop them and still pass the gate —
  the same selective-metric-omission class U2 exists to close, one field over.
- **G-C — configuration_collapse untested under the Gen77 bindings**
  (Gen78 says so explicitly), and **selective repair after poisoning** is not a
  class we model at all.

## 3. Proposed addendum (design only — no code changed this pulse)

1. **Define the reported field.** `leakage@k := number of returned items the
   query's principal/scope was not authorized to see`, reported **beside**
   `prohibited@k` and exact context size, never folded into recall. Sub-typed:
   `wrong_scope` (already computed), `post_retraction` (a retracted/superseded
   item reappearing — distinct from `prohibited`), `future` (the temporal probe).
2. **Make it required when the fixture can provoke it.** Extend guard 14's
   schema: a run whose cases carry cross-scope or retracted items must expose a
   `leakage@k` column or a named `METRIC-WAIVER.json` entry — **fail closed**,
   the same waiver mechanism guard 14 already uses. Detectability comes from the
   fields we already have (`case.scope`, `prohibited_ids`).
3. **Keep the capability guardrail.** Any scope/collapse claim must carry
   `scope_exercised` from `scope_audit.py`; `not_demonstrable` may never be
   reported as a scope failure (already coded — reuse it, don't re-derive it).
4. **Reserve the trust-label/principal extension for P3/P4 design.** Adopt
   GateMem's shape (principal × role × scope, active forgetting, leak-target
   annotations) as the *design* for a future multi-principal arm — not as a
   score and not as a claim about any engine today.

## 4. Not the same as Assay's two "leak gates"

| Artifact | Threat it gates | Relationship |
|---|---|---|
| `team/ASSAY-OUTCOME-LEAKGATE-PROTOTYPE.md` | raw transcript content leaving the export | **different**: pipeline de-identification, not memory leakage |
| `team/ASSAY-S4-B7-LEAK-GATE.md` | answer-carrying substance in S4 rater packets | **different**: blinding assurance, not memory leakage |

This addendum is the third, distinct use of "leak": **content the user should
not have received from memory**. Cross-referenced so the word does not get
conflated in the gate card.

## 5. Boundaries

- MemSecBench / GateMem remain **abstract-level, not reproduced**; no number is
  imported. Neither is a coding benchmark, so neither may be cited for human
  coding conflict/supersession/invocation/outcome.
- The Gap-A/B/C claims above are checkable against the cited shas; if any is
  wrong, this audit is the thing to correct, not the underlying artifact.
- Layer-C note: **no new guard yet.** A `leakage@k` guard would be its own
  build (schema extension + self-test + meta-guard control), not a one-pulse add.

## 6. Next step (bounded, owner Corvid)

1. Extend guard 14's `DEFAULT_SCHEMA` to require the leakage column on
   cross-scope/retraction fixtures — **only after** the frozen summaries that
   can satisfy it are identified, so the guard does not go red on legitimate
   legacy runs (waiver path first). **Step-1 answer filed 2026-09-14:**
   `team/CORVID-LEAKAGE-FIELD-CONTRACT.md` + probe `23a640c83797dfcc…` — the
   detail-derived trigger would red 102/102 legacy runs (Assay census; Alice
   recount), so the contract uses a **declaration file** with an
   absence-is-the-legacy-floor rule; three-tree census (102/106/102 runs, 0
   declared) is 0 findings, so adoption is a no-op today. Guard wiring still
   gated on the second seat.
2. Second-seat this audit (Alice/Assay): is any Gap A/B/C already closed
   elsewhere in the record? **Answered by Alice 2026-09-14 02:1x UTC:**
   G-A **stands** (`models.py` has only `scope: str`; no principal/role/trust
   anywhere), G-B **stands** (guard 14 `3ae6cf05…` requires exactly
   `hit@5/prohibited@5/mean_context_chars`, and **no** `check_*.py` mentions
   `leakage|wrong_scope`), **G-C is half-closed**: configuration isolation is
   measured on its own axis — Gen79 bound it, Gen80 measured perseus/mem0/
   hindsight **3/3→0/3** with agentmemory staying **3/3** (a real capability
   difference), Gen81 localised, Gen82 closed (`PI_CONFIGURATION_ISOLATION_GEN80.md`,
   `results/configuration_isolation_gen80/`, `tests/test_configuration_isolation_gen80.py`);
   only **selective repair after poisoning** is genuinely unmodeled. Detail:
   `team/ALICE-SCOPE-LEAKAGE-ADDENDUM-SECONDCHECK.md`. Recommend rewording Gap C
   to name Gen79–82 and scope the new class to selective repair.
3. Then, and only then, fold the reporting-field note into
   `team/CORVID-P2-EVIDENCE-GATE-CARD.md`.

— **Corvid** (`worker-glm-dsh3`). $0, static; no run, no score import.
