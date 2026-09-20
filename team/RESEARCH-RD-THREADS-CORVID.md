# R&D thread continuation — Habitus class label, LongMemEval-S claims, Hindsight retraction provenance

**Author:** Corvid (worker-glm-dsh3), R&D + evidence-integrity seat
**Task:** GiLMore R&D mode, 2026-09-12 — "continue your open threads … Muse
batching as fitted."
**Status:** read-only apart from six pinned web fetches (receipts in
`team/rd-threads-fetches/`) and the disposition of one **already-run** Muse
batch (batch2, 15:52). No engine, pipeline, or benchmark was run.
**Cost:** $0 project model spend this turn. Merge/batch2 was metered at 15:52
(≈$0.0011); no new call was made.

---

## Plain English (for Brian)

Three loose threads from my earlier R&D notes are now closed or advanced.

1. **Habitus class label — settled.** Our own vendored code says the "dense"
   embedder we ran is an offline **test/demo stand-in** ("Production callers
   should supply an actual semantic model"). That is a replaced component, so
   the row is a `controlled_core`, not a `raw_product`. The adapter's default
   label is the bug; the written evidence pages already had it right.
2. **LongMemEval-S claims — audited.** The two headline numbers are not the
   same kind of thing. agentmemory's 95.2% is **retrieval recall with no LLM
   or judge**, and the vendor explicitly says it is *not* a "LongMemEval
   score." MemBukkit's 92.6% is **end-to-end QA accuracy under the official
   gpt-4o judge**. Putting them side by side is apples-to-oranges. Both are
   vendor-only; neither is our LongMemEval-oracle reader substrate.
3. **Hindsight retraction provenance — one defect contained, one still open.**
   The "32.9% is Hindsight's" mislabel is contained: every durable document
   says MemBukkit. The real defect is the opposite asymmetry — a *retracted
   number* is flagged everywhere, but an *invalidated run* is still linked as
   evidence. `RESULTS.md` row 85 still points at the invalidated Hindsight
   Gen4 directory in all three trees, while the valid Gen6 core artifact sits
   unlinked. Separately, Hindsight's "most accurate ever tested" claim rests
   on an image plus a live mutable benchmark site; its "independently
   reproduced" line is vendor-asserted with no retrievable reference, and a
   competitor's judge table puts Hindsight below MemBukkit under the official
   judge.

Muse batch 2 (already run, never dispositioned) is dispositioned at the end;
2 of its 5 items map directly onto these threads.

---

## Thread 1 — Habitus class label: settled `controlled_core`

**The open question** (`RESEARCH-4-ENGINES-SURVEY.md` gap 4): the adapter
default resolves one way, the written evidence pages another —
`raw_product` (adapter default) vs `controlled_core`
(`ROUND1_FINAL_READOUT.md:14`, `RESULTS.md:80`).

**Code evidence (this turn):**

| Fact | Evidence |
|---|---|
| Base defaults are `raw_product` / `product` | `src/memory_bakeoff/providers/base.py:28-29` |
| `HabitusProvider` sets **no** class override | `src/memory_bakeoff/providers/external.py:146-148` (contrast `MemBukkitControlledCoreProvider` at `:188-189`, which sets both explicitly) |
| Class definitions | `RESULTS.md:70-71`: `controlled_core` = "real upstream code with a shared or replaced component so one variable is isolated"; `raw_product` = "the real product retrieval path in a documented raw/no-LLM mode" |
| The embedder actually run is a stand-in, by its own docstring | `vendor/habitus/src/habitus_ai/embeddings.py:37-44`: *"Offline lexical embedder for reproducible tests and demonstrations. Production callers should supply an actual semantic model."* |
| The pipeline silently defaults to that stand-in | `vendor/habitus/src/habitus_ai/pipeline.py:82`: `self.embedder = embedder or DeterministicHashEmbedder(1024)` |
| There is no product path | `external.py:155-168`: `ingest(..., mode="raw")` ignores `mode`; survey gap 3 |

**Decision: `controlled_core` is correct.** The run uses real vendored
upstream code with the representation component replaced by the vendor's own
offline test embedder — exactly the `controlled_core` definition. It is not
the real product retrieval path (`raw_product`) because the production
semantic model was never supplied. The adapter's default is the defect.

**Exact fix (not applied — R&D is read-only; owner = implementer/build):**

```python
class HabitusProvider(MemoryProvider):
    name = "habitus"
    raw_experiment_class = "controlled_core"
    product_experiment_class = "controlled_core"
    capabilities = ProviderCapabilities(
        raw_ingest=True, product_ingest=False, supports_as_of=False,
        supports_feedback=False,
        notes="Controlled core: vendored upstream code with the offline "
              "DeterministicHashEmbedder test stand-in; no LLM/product path.",
    )
```

Companion test: `tests/test_preflight_hardening.py:17` already asserts the
class for BM25 and Membukkit but has **no Habitus assertion**; add
`PROVIDERS["habitus"]().experiment_class("raw") == "controlled_core"` (and
`"product"`). The `product_ingest=True` flag is a second, separate defect
(no product path exists) and should flip to `False` in the same edit.

**Consequence for the survey:** its summary table cell "Class today: raw" is
wrong; corrected by addendum to this file's sibling survey (see
`RESEARCH-4-ENGINES-SURVEY.md` addendum). No experiment was invalidated — the
evidence pages already carried the correct label.

---

## Thread 2 — LongMemEval-S claim audit

**Sources (all pinned, raw-byte receipts in `team/rd-threads-fetches/`):**

- agentmemory `README.md` @ `e04ba888` (sha `49b467eb…`),
  `benchmark/COMPARISON.md` (sha `d74a5290…`), `benchmark/LONGMEMEVAL.md`
  (sha `72a5f411…`).
- MemBukkit `README.md` @ `f28a2e58` (sha `a462d9cc…`),
  `docs/guide/benchmarks.md` (sha `11c34675…`).

### What each number actually is

| System | Claim | Metric | Reader / judge | Where |
|---|---|---|---|---|
| **agentmemory** | LongMemEval-S R@5 **95.2%**, R@10 98.6%, MRR 88.2% | `recall_any@K` — **retrieval recall, no LLM, no judge** | embedder `all-MiniLM-L6-v2` (384-D); no reader | `LONGMEMEVAL.md`; `README.md:292-296` |
| **MemBukkit** | LongMemEval-S **92.6%** | **end-to-end QA accuracy** | reader `gpt-5.4`; judge **official `gpt-4o`**; encoder `text-embedding-3-large@1536` | `README.md:128`; guide `:15` |

### Findings

1. **Different metrics, same label.** agentmemory's 95.2 is retrieval recall
   on the LongMemEval-S haystack; MemBukkit's 92.6 is judged answer accuracy.
   They are not comparable, yet both are quoted as "LongMemEval-S." Anything
   that ranks them together is a category error.
2. **agentmemory disclaims the QA interpretation explicitly.**
   `LONGMEMEVAL.md`: *"We do NOT claim these as 'LongMemEval scores' — they
   are retrieval-only evaluations on the LongMemEval-S haystack"*; the
   official metric is QA accuracy with a GPT-4o judge, and official-leaderboard
   systems score 60–95% (Oracle GPT-4o ≈82.4%). `COMPARISON.md:22` repeats
   the apples-vs-oranges caveat and says only its own 95.2 is measured.
3. **MemBukkit's number is a genuine official-judge QA result, but still
   vendor-only.** The recipe pins reader, judge, encoder, and distiller
   (`guide:4,13-18`) and reports a band (±0.03). It is the strongest-form
   vendor claim in the set — and still not independently reproduced by us.
4. **Our own "LongMemEval" is a third thing.** The project's substrate is the
   **oracle** split, `knowledge-update`, used for reader-attribution
   (GEN125 instruction; `research/LONGMEMEVAL_SUBSTRATE.md`) — neither the
   agentmemory retrieval harness nor the MemBukkit judged pipeline. Three
   different LongMemEvals now circulate; every citation must say which.
5. **Competitor numbers in MemBukkit's judge table are not independent.**
   `guide:44-62` lists Hindsight 91.4, Mem0 Cloud 94.4, Mem0 OSS 91.0,
   Supermemory 85.2, Zep 71.2. Under the ledger's own rule these are
   `vendor-only` / competitor-published, not third-party verification.
6. **Useful per-type signal for us:** agentmemory's `knowledge-update` R@5 is
   98.7% (78 Q) and `multi-session` 97.7% — the closest vendor analogue to our
   knowledge-update substrate, but retrieval-only.

### What would move each row

- **agentmemory:** locally reproducible *cheaply* — retrieval-only, no LLM or
  judge, `all-MiniLM-L6-v2`, public 500-Q split and public harness. This is a
  $0 candidate for the portfolio's reader-attribution lane, not a claim that
  needs a vendor run.
- **MemBukkit:** a faithful run costs ~$9 and ~60M input tokens plus an OpenAI
  key (`guide:131-135`) — outside the ≤$5 portfolio envelope as specified, so
  it needs a scope decision; do not silently substitute a no-LLM run.
- **Cross-cutting:** any portfolio table that lists a "LongMemEval" column
  must carry split + metric + reader + judge + encoder, or it is unreadable.

---

## Thread 3 — Hindsight retraction provenance defect

### (a) The wrong-engine mislabel is contained

`~32.9%` is **MemBukkit's** bank-scan fraction, retracted in
`research/MEMBUKKIT_SCAN_FRACTION_AUDIT.md`. Every durable document I grepped
attributes it to MemBukkit; the only place it was ever called "Hindsight's"
was a GiLMore dispatch, and `RESEARCH-PROVENANCE-AUDIT.md:15` records the
correction rather than hiding it. **No doc needs a fix.**

### (b) The open defect: a retracted number travels; an invalidated run does not

This is the asymmetry the thread is actually about.

- `research/HINDSIGHT_GEN4_INVALIDATION.md` invalidates **all** Gen4 Hindsight
  directories — "excluded from leaderboards, comparative analysis, and product
  claims."
- `RESULTS.md` row 85 (present identically in `implementer/repo/RESULTS.md`,
  `implementer/repo-glm-dsh2/RESULTS.md`, and `implementer/repo-glm-dsh3/RESULTS.md`)
  still links `results/hindsight_gen4_core_r1` as evidence. That directory
  contains an `INVALIDATED.md` sidecar — the defect is detectable from the
  linked artifact itself.
- The valid core artifact `results/hindsight_gen6_external_local_core_r1`
  (Hit@5 / all-relevant 1.000 / 1.000) exists but is **not linked**; the row's
  stated 0.833/0.708 matches its Gen5 **stress** link, which is correct and
  should stay.
- Contrast: the *number* retraction (`32.9%`) is flagged in all nine active
  docs the provenance audit checked. The *run* invalidation is not flagged in
  the index that cites it. A reader of `RESULTS.md` has no way to know row 85's
  core link is void.

**Fix (one line per tree, still unapplied; owner = implementer):** delete the
`results/hindsight_gen4_core_r1` link from row 85 and replace it with
`results/hindsight_gen6_external_local_core_r1`; add a one-line caveat beside
any surviving Gen4 reference ("Gen4 invalidated — see
research/HINDSIGHT_GEN4_INVALIDATION.md"). This is the same class as the
row-81/82 MemBukkit pointer defects and belongs in the same P1 pointer-fix
row.

### (c) New: Hindsight's own "most accurate ever" claim, audited

Hindsight `README.md` @ `ebad4782` (sha `7a992a27…`):

- L42: *"Hindsight is the most accurate agent memory system ever tested …
  state-of-the-art performance on the LongMemEval benchmark."*
- L44–46: the actual figures are an **image** (`hindsight-benchmarks.png`)
  plus a **live, mutable** site (`benchmarks.hindsight.vectorize.io`) — there
  is no pinned text table to audit.
- L48: *"independently reproduced by research collaborators at the Virginia
  Tech Sanghani Center … and The Washington Post."* This is a **vendor
  assertion of independence**; the fetch contains no report, DOI, or link to
  the collaborators' result. It is not a third-party reference we hold.
- MemBukkit's competitor guide (`guide:58`) lists **Hindsight 91.4 with the
  judge swapped to GPT-OSS-120B** — i.e. *not* the official gpt-4o judge —
  and `guide:64-65` says that restricted to systems the official judge scored,
  **MemBukkit 92.6 is the highest published result**. So under the official
  judge, a rival's table places Hindsight below MemBukkit.

**Class: `vendor-only`.** The "independently reproduced" line is a
self-asserted third-party note, not a reference receipt; the competitor's
91.4 is also vendor-only. This does not contradict our own receipts (we have
no faithful product run), but it directly qualifies the survey's phrase
"SOTA LongMemEval (independently reproduced)" — which should read
"vendor-claimed SOTA; independence self-asserted; rival table places it below
MemBukkit under the official judge."

---

## Muse batch 2 — disposition (already run 15:52; receipts in the Muse dir)

**Prompt** (`PROMPT2.txt`, public methodology only): "…which specific kinds of
claims are most often unverifiable or misleading, and which should be chased
first?" · model `meta/muse-spark-1.3-contributor` · 11.3 s · meter
`$0.7328` before and after (spend not landed at read time). Muse proposes,
Corvid disposes.

| # | Muse item | Verdict | Reason / where it lands |
|---|---|---|---|
| 2.1 | [H] Retrieval accuracy without pinned dataset version, split, grading script, full config is unverifiable; chase first | **DUPLICATE** | This is now a live instantiation: the LongMemEval-S audit (Thread 2) shows exactly the four missing fields. Folded into the ledger checklist below. |
| 2.2 | [E] Update claims that report successful overwrites while hiding false supersession | **DUPLICATE** | agentmemory 418/450 false supersessions (92.9%); already the portfolio's known-bad lifecycle axis. |
| 2.3 | [I] Demand embedding model, reranker, DB backend, top-k, thresholds, returned context size for every score | **ACCEPT** | Added as a ledger field checklist (Thread 2): the LongMemEval-S table is only readable because MemBukkit pins reader/judge/encoder; most rows do not. Bounded, $0. |
| 2.4 | [E] Latency/scale claims on small warm caches collapse under concurrency, large histories, cold start | **ACCEPT** | New and consistent with Q1.2/leakage; add to the ledger's "reported-with" caveats (MemBukkit HotpotQA 47 ms is a small-candidate warm measurement; Hindsight latency unrun). |
| 2.5 | [H] "Unlimited memory" conflates large prompt windows with persistent cross-session recall | **DUPLICATE** | The long-context null arm in the charter; nothing new. |

**Tally:** 2 ACCEPT · 3 DUPLICATE · 0 REJECT. ACCEPTs become proposed bounded
checks, not findings, until a run produces a receipt. Note: batch2 was executed
at 15:52 but never written up — this section closes that gap; batch 1 remains
in `MUSE-IDEATION-01.md`.

---

## Method and limits

- Read-only plus six pinned `raw.githubusercontent.com` fetches (byte receipts
  + sha256 in `team/rd-threads-fetches/MANIFEST.md`). No engine installed,
  started, or run; no benchmark reproduced.
- The Habitus settlement is from the vendored source at the surveyed commit;
  the proposed patch was **not** applied and its companion test was not run.
- The 32.9%-mislabel containment check is a `grep` over `team/` and the
  `repo-glm-dsh3` tree, not a full-history search.
- MemBukkit's judge table and Hindsight's "independently reproduced" line are
  vendor assertions; both stay `vendor-only`. No number in this note is
  `verified-by-us`.
- The pointer fixes in Thread 3(b) are recommended, not applied; the canonical
  edit belongs to the implementer lane, and three trees must move together to
  avoid mirror drift.

— **Corvid** (worker-glm-dsh3). Three threads continued: one label settled from
our own code, one comparison shown to be two different measurements, and one
retraction shown to travel everywhere except into the run it invalidates.
