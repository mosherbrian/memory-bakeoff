# S3-6 toy-run receipt — pi-blackhole 0.5.5 isolated install + row-36 smoke (muse-drafter, 2026-09-15)

**Row:** QUEUE S3-6 (owner Corvid + muse-drafter; GiLMore addressed the approval
"Assay —" but the run plan is in this seat's `SPARK-S3-6-PROBE-20260915.md`;
filed by muse-drafter). **Cost:** $0 local (local model `night/qwen3.8-27b-code`).
**No score import.** Plan honored: isolated-prefix install, NOT the shared runtime.

## 1. Install (isolated prefix)

- Pinned tarball `pi-blackhole@0.5.5`, sha256
  `475bbb5d1cd83aa88ec30fe52b6ee307be6c41c70f6cd6e86cd5dda8e0d7dc34`.
- Installed to **`/tmp/opencode/pbh-install/node_modules/pi-blackhole`** (268 MB
  with peer packages), `--no-save`; the shared Pi runtime was **not** touched,
  nothing added to any live `settings.json`.

## 2. Load compatibility on row-36 smoke

Ran a blackhole-enabled **copy** of the smoke runner (`/tmp/opencode/row36-blackhole-toy.py`,
`packages = [pi-change-trigger, pi-blackhole]`; Cairn's committed runner unmodified):

| run | result |
|---|---|
| `--expect post` | **36/36 match**, near-miss fires **1** (S05 t3, pre-registered), `filler_plain` topic contamination **0** |
| `--expect pre` | 35/36; the single miss is S09 t2 firing `{required}` — i.e. the corpus is post-fix, as expected |

So **blackhole loads alongside the trigger extension without disturbing the
wiring**, and scaffolds its config per isolated agent dir
(`pi-blackhole/pi-blackhole-config.json`).

## 3. Live OM observation (the part the abort-smoke cannot reach)

The abort-smoke writes no session and never compacts, so I ran a short
**session-preserving** toy (isolated agent dir, `--no-tools`, local model,
`observeAfterTokens/reflectAfterTokens` lowered to 1 for the toy). It produced a
real ledger entry:

```
type=custom  customType=om.observations.recorded
  data.coversUpToId = ebe55446
  data.observations[0] = {
    id: "2fc0e5d140d5" (12-hex ✓ matches MEMORY_ID_PATTERN),
    content, timestamp, relevance: "critical", tokenCount: 24,
    sourceEntryIds: ["f08ef41c"]
  }
```

**Provenance resolution: 1/1** — `sourceEntryIds` resolves to a real session
entry id. So the code-read claims are now **empirically confirmed**: observations
carry a **relevance class** (salience, not truth class) and **resolving source
provenance**; the 12-hex id schema holds.

## 4. Not exercised (named, not silently skipped)

Setting a 1-token observe threshold forces observation but **not** the rest:
- **tombstones / dropper** (`om.observations.dropped`) — needs pool pressure;
- **reflections** (`om.reflections.recorded`) — needs reflect threshold/pool;
- **fold** (`activeObservations` vs `observationsById`) — no drops to fold;
- **compaction chain / `compile()`** — compaction needs the context preset;
  `compile()` is model-summarize anyway.
These remain **code-read only** (see `SPARK-S3-6-PROBE-20260915.md` §code half).

## 5. pi-lcm audit floor

No compaction occurred, so there is **no compacted context to audit** — the floor
is trivially satisfied and was **not** a meaningful check this run. For a real
compaction run the floor stands as: replay the same queries through pi-lcm
(`src/memory_bakeoff/providers/pi_lcm_store_reader.py`; contract 12/12, differential
6/6, both receipted) and require the compacted-context answer set to be a subset
of the uncompacted set except for declared tombstones.

## 6. Verdict

- Install, load, and the **observation/provenance/relevance** half of the ledger:
  **verified live**.
- The **lineage**-relevant half (tombstones, fold, compaction chain): still
  **code-read only**; a real compaction run is needed to exercise it.
- No score import; the toy used synthetic memory (`deploy target = cluster-north`,
  `never portable mode`) — no real corpora, no vault, no secrets.

## 7. Cleanup

`/tmp/opencode/pbh-install` (268 MB) and the throwaway sessions are in `/tmp` and
can be deleted at will; nothing landed in the repo or any live Pi runtime.

$0, local. — muse-drafter (Spark)
