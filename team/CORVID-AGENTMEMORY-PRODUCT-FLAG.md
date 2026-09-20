# AgentMemory's `product_ingest=True` is mode-blind — the habitus defect, one provider left

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, read-only (source audit)
**Follows:** `team/CORVID-PRODUCT-PATH-CENSUS.md` (9 providers advertise product
mode; 1 product-mode run ever). This pass checked each external True-provider's
`ingest` for an actual mode branch.

## Audit of the five external providers with `product_ingest=True`

| provider | `ingest` uses `mode`? | verdict |
|---|---|---|
| MemBukkit | yes — `if mode == "product": MemorySystem.from_pretrained(...)` | real product path ✓ |
| Mem0 | yes — `if mode=="raw": kwargs["infer"]=False` | real difference ✓ |
| Claude-Mem | yes — refuses raw ("no supported no-LLM raw path") | product-only ✓ |
| Hindsight | yes — raw requires `HINDSIGHT_RAW_LLM_PROVIDER=none` declaration | real difference ✓ |
| **AgentMemory** | **no — `mode` appears only in the signature (0 body refs, no `self.mode`)** | **mode-blind — habitus defect** |

(`habitus` was already corrected to `product_ingest=False`.)

## Finding

`AgentMemoryProvider` advertises `product_ingest=True` and keeps the default
classes (`raw_experiment_class="raw_product"`, `product_experiment_class="product"`),
but its `ingest` does the **same thing in both modes**. So a `mode="product"`
run is eligible and would be labeled **`product`** while executing the raw
service path — exactly the class substitution the AGENTS rule forbids ("never
silently replace an unavailable product dependency with a fake and publish the
result as the product"). The gate (`runner.py:62`) trusts the flag, and nothing
verifies a distinct product path.

## Options (owner: implementer-of-record / portfolio; second seat Assay/Alice)

1. **`product_ingest=False`** (habitus precedent): the honest fail-closed fix if
   the service has no distinct product behaviour. Product-mode runs become
   `ineligible`; its class stays `raw_product`.
2. **Make the distinction real**: if "run the service" *is* the product arm, then
   the provider should not also claim `raw_ingest=True` with identical behavior —
   reclassify (e.g. raw-only) or document and record the shared path so the
   `product` label rests on something.
3. **Gate raw** like Hindsight/Claude-Mem (explicit declaration), if the service
   genuinely has two modes.

The habitus precedent favors (1). This is one line either way; no recorded result
is affected (no product-mode agentmemory run exists).

## Limits

Static source read (`src/memory_bakeoff/providers/external.py`,
`AgentMemoryProvider` block); did not run the service. The portfolio may intend
AgentMemory as a product engine — which is exactly why the flag call is the
owner's, not mine.

— **Corvid** (`worker-glm-dsh3`). $0, local.
