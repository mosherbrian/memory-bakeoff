# Second-seat — scope/leakage gate addendum (Corvid): G-A and G-B stand, G-C is half-closed elsewhere

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-14 02:1x UTC · **Cost:** $0, static code/artifact reads, one turn.
**Trigger:** `CORVID-SCOPE-LEAKAGE-GATE-ADDENDUM.md` §6.2 — "is any Gap A/B/C
already closed elsewhere in the record?" No tree modified.

## Answer

**G-A and G-B stand as stated. G-C's configuration half is already closed
elsewhere — on a different axis — so only selective repair is genuinely new.**

### G-A — no principal/role/trust axis: **STANDS**

`MemoryRecord` and `QueryCase` carry `scope: str = "repo:demo"` and nothing else
(`src/memory_bakeoff/models.py:23/41`). A grep across `src/memory_bakeoff/` for
`principal|trust_label|multi-principal|tenant|role_id|access control|authoriz`
finds only HTTP `Authorization` headers and a `requires_reader_authorization`
category string — no principal identity, no role, no shared pool. Gen76/78 closed
single-principal scope; G-A is greenfield.

### G-B — leakage not a required report field: **STANDS**

`scripts/check_required_metrics.py` (`3ae6cf05…`) `DEFAULT_SCHEMA` requires
exactly `["hit@5", "prohibited@5", "mean_context_chars"]` (line 41). A grep of
**all 18** `scripts/check_*.py` for `leakage|wrong_scope` returns **nothing**, so
no guard enforces the wrong-scope or leakage fields that `frozen_reader.py`
(`4f4649d7…`) already computes. A summary can drop them and pass — the U2
selective-omission class, one field over. Confirmed.

### G-C — **half-closed**: configuration isolation is measured elsewhere

The addendum's first clause is true *as scoped* ("untested under the **Gen77**
bindings"; Gen78 says so), but "configuration_collapse untested" is misleading
read as a whole. The record already has the configuration axis:

- **Gen79** bound a second, independent configuration primitive per engine;
- **Gen80** measured it (`research/PI_CONFIGURATION_ISOLATION_GEN80.md`;
  `results/configuration_isolation_gen80/*.json`): on `LQ03`, perseus/mem0/
  hindsight go **3/3 collapse → 0/3, 3/3 clean**, while **agentmemory stays 3/3
  collapse** — a real capability difference on that axis;
- **Gen81** localised it (search-time ignoring); **Gen82** closed
  `NO_USABLE_SECOND_SURFACE` (`round2_reconciliation.py:153`);
- `tests/test_configuration_isolation_gen80.py` exercises it, and
  `current_truth_audit.py` (`LQ02` purity row) already refuses to charge
  `configuration_collapse` inside a current-truth row, because it is a
  **separate layer**.

So Gap C narrows to: **selective repair after poisoning is not modeled at all**
(no `selective_repair` in `src/`; the only "repair" strings are unrelated
corpus/evidence-ruler text). The configuration half needs no new build — it needs
a pointer to Gen80 in the addendum.

## Citations verified

`scope_audit.py` `0faa1cc2…`, `frozen_reader.py` `4f4649d7…`, `longitudinal.py`
`65e57518…`, guard 14 `3ae6cf05…` all match the addendum; Gen78's
"6/6 collapse → 0/6" is confirmed in `PI_SCOPE_ISOLATION_GEN78.md` (mem0 /
hindsight / agentmemory), with `configuration_collapse` explicitly left
untested there.

## Recommendation

1. **Gap C wording:** replace "configuration_collapse untested under the Gen77
   bindings" with "configuration isolation is measured on its own axis
   (Gen79–82: 3/3→0/3 for perseus/mem0/hindsight, agentmemory 3/3 — a capability
   difference); **selective repair after poisoning is the new, unmodeled
   class**." This keeps the falsifiable core and removes a re-check of closed
   work.
2. §6.1 (waiver path before making `leakage@k` required) is the right order; G-B
   is real and worth the guard extension.
3. §3's design is otherwise sound; the principal/role extension correctly stays
   P3/P4.

## Scope and limits

- Static reads only (source, guards, results JSON, research note); no run, no
  score import. I did not re-run the Gen80 ablation.
