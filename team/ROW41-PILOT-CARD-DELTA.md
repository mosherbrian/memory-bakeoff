# Row-41 pilot-card delta resolved: 15 is pre-quote-masking, 10 is current

**Author:** muse-drafter (Spark), from the row-41 export task · **Date:** 2026-09-14 · **Cost:** $0, local
**Serves:** the blocker raised in `team/outcome-pilot-bundle-20260914/README.md`
and QUEUE row 41 ("15 events per the pilot card" not reproducible).

## Finding

The pilot card's **15** correction events are the counts **before
`mask_quotes()` was in the detector path**; the committed pipeline yields **10**.
The 5-event delta is exactly the quoted third-party speech that quote-masking
removes — the precision lever `TRANSCRIPT-MINING-PILOT.md` itself names.

Re-derivation (same corpus, same glob, same commit; only `mine.mask_quotes`
toggled; outputs to a throwaway dir, corpus untouched):

| variant | wrong | negation | actually | env_fact_correction | repeated (groups) | total |
|---|---|---|---|---|---|---|
| committed (`mask_quotes` active) | 1 | 3 | 1 | 3 | 2 | **10** |
| `mask_quotes` disabled (identity) | 1 | 3 | **2** | **7** | 2 | **15** |
| `TRANSCRIPT-MINING-PILOT.md` card | 1 | 3 | 2 | 7 | 2 | **15** |

The card row matches the **unmasked** variant exactly (all five classes). So the
card is not a fabrication and not a different corpus; it is a **pre-`mask_quotes`
snapshot**. The committed pipeline (which the export step runs against) is 10.

Receipt: `mine.scan(projects, '-var-home-bmosher-memory-bake-off*', <tmp>)` at the
current commit, run twice with `mine.mask_quotes` as committed vs monkeypatched to
`lambda s: s`. Both runs: files_scanned 16, user_text_turns 224,
repeated_instruction_groups 2. Only the correction-class counts move.

Minor secondary delta, same cause: the card says **223** operator turns; the
committed pipeline says **224** (one turn's classification changed across the
detector evolution, not a count error).

## Consequence

- The **correct current artifact is the 10-event bundle** already emitted to
  `team/outcome-pilot-bundle-20260914/` (gate PASS). No missing events need to be
  produced; the "missing 5" are the quoted spans intentionally filtered out.
- The card is stale, not wrong-for-its-time. It should be **annotated** (not
  rewritten): "15 = pre-quote-masking; committed pipeline = 10." That is the
  pipeline owner's call; row 41's blocker is **resolved by explanation**, and the
  export step is correct as shipped.
- Gate rule 7 reconciles against the pipeline's own `stats.json` (10), which is
  right: reconciling against the stale card would have failed a correct bundle.

$0, local, read-only over the corpus; no raw transcript content emitted or quoted. —
muse-drafter (Spark)
