# Product-mode eligibility vs product-mode evidence

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, read-only (source + `results/` scan)
**Trigger:** the experiment-class census showed `product` never appears in any
run artifact. Checked whether the product arm is *reachable* or merely
*unevidenced*.

## Static: who accepts product mode (`product_ingest=True`)

`runner.run_provider` (`src/memory_bakeoff/runner.py:62`) and
`reader_eval` (`reader_eval.py:142`) gate product mode on the capability alone:
`if mode=="product" and not product_ingest: ineligible`.

| provider | `product_ingest` | product-mode class (`product_experiment_class`) | `ingest` honours `mode`? |
|---|---|---|---|
| bm25, dense, tfidf, hybrid | **True** | `baseline` (override) | **no** — ignores `mode` |
| agentmemory, hindsight, mem0, membukkit, claude_mem | True | `product` (default/base or explicit) | provider-specific (notes describe LLM product paths) |
| habitus | **False** (after the class/product fix) | `controlled_core` | no — fixed to fail closed |
| agentmemory_core, mem0_core, claude_mem_core, perseus_vault, toy_adaptive | False | `controlled_core`/— | raw-only |

## Evidence: product-mode runs actually recorded

Across **218 result dirs / 106 `run.json` lists / 206 records**, there is
**exactly one product-mode record** — `results/habitus_product_ineligible_probe_20260912/`,
and it is `ineligible` (no product path). Every other product-capable provider has
**zero** product-mode receipts. So the `product` class is emitted by 5+
providers but has **no standing run evidence**.

## Findings

1. **The product arm is unexercised.** `product`-class results cannot exist today
   because no provider with product mode has ever produced a product-mode run
   (the sole one was refused as ineligible). Any future `product` row would be the
   first, and has no baseline for comparison.
2. **Four baselines advertise `product_ingest=True` while `ingest` ignores
   `mode`** — the exact shape of the habitus defect. Their class override to
   `baseline` prevents a *product label*, so the harm is bounded to a semantically
   misleading capability flag, not a mislabeled result. Still, the flag is what
   the gate trusts.
3. **The gate trusts the flag, not a path.** `runner.py:62` will run `mode="product"`
   for any provider whose flag is True; nothing verifies that a product
   ingestion path exists. The habitus fix corrected one instance; the mechanism
   remains flag-only.

## Follow-up audit (2026-09-14): only one external True-provider is mode-blind

Checked each external provider's `ingest` for a real `mode` branch:
MemBukkit (`MemorySystem.from_pretrained` on product), Mem0 (`infer=False` on
raw), Claude-Mem (refuses raw), and Hindsight (raw needs an explicit declaration)
all use `mode`. **AgentMemory does not** — `mode` appears only in the signature
(0 body refs), so product mode is behaviorally raw while labeled `product` and
keeping the default `product` class. That is the habitus defect, one provider
left; detail + options in `team/CORVID-AGENTMEMORY-PRODUCT-FLAG.md`.

## Recommendation

1. Set `product_ingest=False` on the four baselines (one line each, mirroring the
   habitus fix) — they have no product path and their `mode` is ignored.
2. For the 5 external providers that keep `product_ingest=True`: either run one
   product-mode receipt per provider (so the `product` class is evidence-backed),
   or mark them ineligible until then. Do not publish a first `product` row with
   no path receipt.
3. Optional hardening: have `run_provider` refuse product mode when the provider's
   `ingest` silently ignores `mode` (a capability/path consistency check), so the
   defect cannot recur as a flag-only claim.

## Limits

Static source read + a scan of existing result artifacts; does **not** judge
whether any external provider's product path works (that needs a live run), and
does not change any code.

— **Corvid** (`worker-glm-dsh3`). $0, local.
