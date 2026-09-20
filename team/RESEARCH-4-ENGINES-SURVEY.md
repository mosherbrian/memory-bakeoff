# R&D survey — the four unmeasured local engines

**Author:** Corvid (worker-glm-dsh3), R&D staff
**Task:** GiLMore dispatch 2026-09-12; feeds `team/PORTFOLIO-CHARTER-draft.md` Row 5 ("do the four unmeasured local engines change the picture?") and the P1 license receipt.
**Date:** 2026-09-12
**Status:** research only. No experiment, pipeline, benchmark, or engine run. Four bounded read-only helper subagents plus direct source/license inspection. One metered turn.

---

## Plain English (for Brian)

The portfolio campaign is about to measure a dozen memory systems on the same conflict benchmark. Four of them — Habitus, agentmemory, Hindsight, MemBukkit — have never been measured on that benchmark, and the charter's license column for three of them read "unknown."

This note resolves the cheap unknowns before anyone spends: **all four are permissively licensed** (Habitus, agentmemory, MemBukkit: Apache-2.0; Hindsight: MIT), so none is a legal blocker. It also records what each one *claims*, what our existing receipts *actually show*, and where the two differ. Two entries are load-bearing before the campaign runs: agentmemory must be included because it already falsely deleted 92.9% of stress memories in our own tests, and Hindsight's headline rests on a product path we have never run.

No decision is required from you. This is the research half of "the fleet originates, Brian gates": the findings and the four cheap follow-up probes are handed to P1 and the campaign design. If the campaign never runs, this note still stands as the license and claim inventory.

---

## Summary

| Engine | Pin (verified) | License (verified at pin) | Entry surface | Class today | Existing receipt | Known-bad / unverified |
|---|---|---|---|---|---|---|
| **Habitus** | `munch2u-a11y/Habitus-AI` @ `f93b770e` (2026-08-28) | **Apache-2.0** (© 2026 HUMAN Project / Fractal Memory Contributors) | in-process import; `HabitusProvider` `external.py:146` | `controlled_core` (settled — see addendum) | core Hit@5 0.875; stress 0.792, prohibited@5 0.025 | "dense" lane is a deterministic hash, not embeddings; retrieval learning untested; no product run |
| **agentmemory** | `rohitg00/agentmemory` @ `e04ba888` (0.9.29) | **Apache-2.0** (© 2026 Rohit Ghumare) | REST daemon `:3111` + vendored controlled core | controlled_core + raw_product | core 0.958; **418/450 false supersessions (92.9%)** | lifecycle is known-bad; high product Hit is purchased by deleting valid records |
| **Hindsight** | `vectorize-io/hindsight` @ `ebad4782` (v0.9.2) | **MIT** (© 2025 Vectorize AI, Inc.) | REST/Python client; needs API + Postgres/pgvector | raw_product (no LLM) | core Hit@5 1.000 (no-LLM); Gen31 stale_persistence 12/60, 0 entities | **no faithful product run**; SOTA claim unverified; extraction/consolidation untested |
| **MemBukkit** | `memseekai/membukkit` @ `f28a2e58` (0.1.0) | **Apache-2.0** | in-process import; `MemBukkitProvider` `external.py:312` | controlled_core + intended | bucket routing parity with dense scan (0.5833/0.5417 both) | **scan fraction ~32.9% RETRACTED**; product 92.6% and token claim unrun; intended models load but no score |

**Bottom line for the charter:** the license ❓ marks can be closed (receipt below). None of the four has a license blocker at P1.

---

## License receipt (for Stratum's P1 checklist)

Every SPDX value below was read from the **LICENSE file at the frozen commit**, not just the repo page. The vendored subtrees ship **no** LICENSE file, so the P1 receipt must pin these blobs (or their SHA via `/contents?ref=<commit>`):

| Engine | Commit pinned | LICENSE URL | SPDX | Copyright line |
|---|---|---|---|---|
| Habitus | `f93b770e4b3c1875151dc13eb90421598c3efa5f` | `raw.githubusercontent.com/munch2u-a11y/Habitus-AI/<commit>/LICENSE` | Apache-2.0 | 2026 HUMAN Project / Fractal Memory Contributors |
| agentmemory | `e04ba88819c365c9acf9d6661ea802143e728bd6` | `raw.githubusercontent.com/rohitg00/agentmemory/<commit>/LICENSE` | Apache-2.0 | 2026 Rohit Ghumare |
| Hindsight | `ebad478240d3171bb88201ececda5e8d9883d22d` | `raw.githubusercontent.com/vectorize-io/hindsight/<commit>/LICENSE` | MIT | 2025 Vectorize AI, Inc. |
| MemBukkit | `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807` | `raw.githubusercontent.com/memseekai/membukkit/<commit>/LICENSE` | Apache-2.0 | (Apache appendix boilerplate; no explicit copyright line) |

Method limit: `web_search` is unconfigured on this endpoint, but `web_fetch` works; these four were fetched directly. The vendored trees do not carry the license, so a re-verifier should fetch the same pinned URLs, not inspect `vendor/`.

---

## Per-engine detail

### Habitus-AI
- **Adapter surface.** `HabitusProvider` (`src/memory_bakeoff/providers/external.py:146-183`), registered `providers/__init__.py:9,20`. `ingest` → `HabitusAI.remember()`; `retrieve` → `.recall(query, include_current_input=False)`. In-process import only (`_ensure_vendor_path` adds `vendor/habitus/src`); no service, no CLI, no model weights. Default `DeterministicHashEmbedder(1024)` (`vendor/habitus/src/habitus_ai/embeddings.py:37-44`); no env knobs; `supports_feedback=False`.
- **Claimed.** Zero-external-runtime-dependency pure Python; dual-cipher Y-axis traversal; conserved edge weights; locked top-3 "dense" rail; receipt-gated durable learning; 1024-D "concept vectors." `DEVELOPMENT.md` at the same commit claims LLM-free benchmarks (100% pattern reconstruction, <0.8 ms/turn, 100% LOOK/DO routing).
- **Verifiable.** Raw only. Core (26 cases, k=5) Hit@5 0.875, all-relevant 0.750, prohibited@5 0.097 (`results/habitus_core/`); 450-distractor stress Hit@5 0.792, MRR 0.701, prohibited@5 0.025 (`results/habitus_stress/`); k=3/5/8/10 identical (plateau at 3). **Pointer correction (2026-09-12, revised):** the earlier attribution of "`README.md:134-139`: 22 non-as-of positives Hit@5 0.955" to **Habitus's** README is wrong — the pinned vendor `README.md` (sha `8449b7e7…`) contains no `Hit@5`/`0.955`, and the pinned `DEVELOPMENT.md` (sha `5a86a199…`) reports only LLM-free diagnostic trials. The number is **our own result**, not an upstream claim: `implementer/repo/README.md:136` and `STATUS_AND_FINDINGS.md:138` record Habitus **21/22 = 0.955** on the positive non-as-of core cases (the two as-of queries excluded; the remaining miss is the NDJSON-debugging procedure). Cite it as ours, at that path — do not cite it as a vendor or benchmark claim. (This corrects my 19:41 over-correction; ECOSYSTEM-MAP addendum 2i and fsync ESC:FIND agree.) **Backing receipt (re-derived 2026-09-13):** `results/habitus_core/detail.csv` — **21 hits of 22** positive non-as-of cases (excludes the 2 `temporal_asof` and 2 `negative` cases), i.e. 21/22 = 0.9545.
- **Gap.** (1) The "dense" lane is a deterministic lexical hash, so "dense + BM25" is two lexical signals — verified in the vendored code, and the README does not say so. (2) The learning claim is untouched by our run: stock `record_outcome` credits output-decision paths, not retrieval (`research/HABITUS_RETRIEVAL_CREDIT.md`). (3) `product_ingest=True` but `ingest` ignores `mode` — there is no product path. (4) Class label was inconsistent (`raw_product` adapter default vs `controlled_core` in `ROUND1_FINAL_READOUT.md:13`, `RESULTS.md:74`); **SETTLED 2026-09-12** (R&D thread continuation): `controlled_core` — the vendored `DeterministicHashEmbedder` docstring calls itself a test/demo stand-in, so the representation is a replaced component and the adapter default is the defect. See the addendum at the end of this file. (5) Frozen `run.json` predates the provenance schema. **Artifact half closed 2026-09-12** (addendum point 4): all 24,169 retrieved IDs across 102 frozen dirs are canonical `M###`, 0 empty/unmapped; only the resolution *method* is unrecorded.
- **Bounded probe.** Re-run core + stress with the current runner into a new directory and read `run.json` `provenance.methods` / `publishability` / `experiment_class`. Any `fuzzy_subtext`/`unmapped` makes the headline rows exploratory-only.

### agentmemory
- **Adapter surface.** Two distinct paths. Real product: REST daemon, `AgentMemoryProvider` (`external.py:441`), `POST /agentmemory/remember` + `/agentmemory/smart-search`, `GET /agentmemory/health`; `AGENTMEMORY_URL` (default `http://127.0.0.1:3111`), `AGENTMEMORY_SECRET`, `AGENTMEMORY_PROJECT`, `AGENTMEMORY_AGENT_ID`; pinned iii-engine 0.11.2. Vendored controlled arm (no daemon): `AgentMemoryCoreProvider` (`agentmemory_core_lsa`) and `AgentMemoryRememberCoreProvider` (`agentmemory_remember_lsa`) via stdio JSON-RPC to `vendor/agentmemory/core_worker.mjs`, shared 32-D LSA, graph/reranker off. Only `SearchIndex`, `VectorIndex`, stemmer, synonyms are byte-identical upstream; RRF and the >0.7 Jaccard write-time supersession are transcribed.
- **Claimed.** LongMemEval-S R@5 95.2%, R@10 98.6%, MRR 88.2%; BM25+vector+graph RRF; four-tier consolidation, decay, auto-forget.
- **Verifiable.** Controlled core (supersession off) core Hit@5 0.958, stress 0.583. With supersession on, stress Hit@5 0.792 but **418/450 false supersessions, 82 live, 0 legitimate** (`research/AGENTMEMORY_FINDINGS.md`; `results/agentmemory_raw_product_gen13_stress-r1/lifecycle.json`). Gen35 ablation flips ON 1/rep → OFF 0, with history erasure 2→0 and correction failure 1→0 (`results/agentmemory_gen35_retirement_ablation/`). Surface probe: no usable second surface.
- **Gap.** The headline R@5 is unverified on our corpora; the raw-product core/stress Hit@5 1.000 is purchased by deleting valid near-neighbors (92.9%). No upstream claim maps to our lifecycle receipts — the product's own docs never report supersession accuracy. **This engine must be included in the portfolio precisely because it is known-bad.**
- **Bounded probe.** Re-run the 450-distractor stress on the real daemon (`EMBEDDING_PROVIDER=local`) with `AGENTMEMORY_EXPERIMENT_DISABLE_AUTO_SUPERSESSION` ON vs OFF, two reps, reporting Hit@5 and live retention both arms.

### Hindsight
- **Adapter surface.** `HindsightProvider` (`external.py:601`), registered `providers/__init__.py:30`; `ingest` → `hindsight_client.Hindsight(base_url).retain(...)`, `retrieve` → `.recall(..., max_tokens=4096, query_timestamp=as_of)`, `probe` → `GET /health`. Transport REST/Python client; `HINDSIGHT_URL` default `:8888` (launchers `:8891`). Requires the Hindsight API plus PostgreSQL/pgvector: pg0-embedded 0.15.1 proven (PostgreSQL 18.1 / pgvector 0.8.5), or Homebrew PostgreSQL 17.11 + pgvector 0.8.6. Raw mode is `HINDSIGHT_API_LLM_PROVIDER=none`; product mode needs a real LLM (OpenAI-compatible base URLs supported). Embedder `intfloat/multilingual-e5-small` ONNX (384-D); reranker `rrf` or CPU cross-encoder. `supports_as_of=True`.
- **Claimed.** "Most accurate agent memory system ever tested"; SOTA LongMemEval (independently reproduced); retain LLM-extracts facts/entities/temporal structure; recall fuses semantic + BM25 + graph + temporal via RRF + cross-encoder into a token budget; background consolidation; strict bank isolation.
- **Verifiable.** All `raw_product`, no LLM. Gen6 core Hit@5 1.000 / all-relevant 1.000 / MRR 0.931 / prohibited 0.142; learned-reranker stress 0.833 versus RRF-only stress 0.208. Gen4 invalidated (stale listener, ONNX path); Gen5 pg0 blocked on `ENOBUFS` before ingestion; external-Postgres runs succeeded. Gen31: 20 cases ×3 identical, **stale_persistence 12/60**, zero entities extracted.
- **Gap.** **No faithful networked product run exists.** No receipt exercises LLM extraction, occurred-start/end, consolidation, product graph/temporal arms, reflect/mental models, or lifecycle — all excluded by the no-LLM gate. No reader evaluation. The SOTA claim is unverified here.
- **Bounded probe.** `hindsight-all==0.9.2` product mode with one real LLM over 50 core records / 26 queries, top-k 5, preserving native IDs/context; score retrieval plus the existing reader.

### MemBukkit
- **Adapter surface.** In-process import (`vendor/membukkit/src` or `MEMBUKKIT_UPSTREAM_PATH`), `MemorySystem` + in-memory backend, no service. `MemBukkitControlledCoreProvider` (`membukkit_core_lsa`, `external.py:187`) and `MemBukkitProvider` (`membukkit`, `external.py:312`), registered `providers/__init__.py:21-22`; test doubles in `providers/membukkit_test_doubles.py`; MemConflict path `providers/membukkit_memconflict.py` + `memconflict_engines_gen42.py`. Knobs: `MEMBUKKIT_SELECT` (`none` controlled default, `hybrid` intended), `MEMBUKKIT_SCAN_BUDGET=0.3`, `MEMBUKKIT_UPSTREAM_PATH`, model dirs. Intended models `MemseekAI/membukkit-biencoder-v1` / `membukkit-reranker-v2`; fallbacks `all-mpnet-base-v2` / `ms-marco-MiniLM-L-6-v2`. Raw = `ingest_facts`; product = `from_pretrained(...).ingest(sessions=)`.
- **Claimed.** LongMemEval-S 92.6% under the official gpt-4o judge; ~3.2k reader tokens versus ~100k full-context; budgeted bucket routing; excluding receipt-named buckets collapses accuracy 80.0% → 1.3%; HotpotQA document retrieval 87.4% vs qmd 86.1%.
- **Verifiable.** Controlled shared-LSA bucket routing **matches** full dense scan: `membukkit` and `dense_lsa` both Hit@5 / all-relevant 0.5833 / 0.5417 in `results/current_full_stress4505/` (and `current_stress4505`). Scan fraction **RETRACTED**: `~32.9%` appears nowhere; the only artifacts (Gen40 intended-model) are 31.3% on a different run (`research/MEMBUKKIT_SCAN_FRACTION_AUDIT.md`). Gen40 intended models load without fallback but score nothing (synthetic only). Gen41 intended stress Hit@5 0.9167 vs fallback 0.8750, but MRR 0.4486 vs 0.5535. Gen42 MemConflict Hit@3 0.3237. **(Artifact-verified 2026-09-12, Corvid R&D pulse:** Gen41 intended stress `0.9167`/MRR `0.4486` in `results/membukkit_intended_gen41_product_default_stress-r1/`, fallback `0.8750`/`0.5535` in `results/membukkit_fallback_gen8_stress-r1/`, and Gen42 Hit@3 `0.3237` in `results/membukkit_memconflict_gen42_calibration/calibration-report.json`.)**
- **Gap.** The product 92.6% and the token-saving claim are unverified — no LLM/reader run; the product path exists but is unrun. The routing saving is unquantified (retracted figure; only a 60-fact synthetic measured 0.30–0.33). **Receipt caveat:** `RESULTS.md` links `results/membukkit_stress_lsa` (0.458/0.375) for the routing claim, which does *not* show the advertised parity; the parity lives only in the `current_full_stress4505` runs. P1 should cite the right artifact.
- **Bounded probe.** Run `MemBukkitProvider` product mode over the frozen Round1 core + stress under a pinned reader/judge, recording native `scan_fraction` per query.

---

## Cross-cutting findings

1. **All four are license-clear.** Three Apache-2.0, one MIT. The charter's `❓` on Habitus, agentmemory, Hindsight, and MemBukkit closes; P1's job is the pinned-blob receipt, not a legal decision.
2. **Every headline number is unverified on the benchmark that matters.** Each of the four advertises a LongMemEval-class result (agentmemory LongMemEval-S 95.2%, MemBukkit LongMemEval-S 92.6%, Hindsight "most accurate ever," Habitus LLM-free benchmarks). None of those runs is in our tree under matched conditions. Only Habitus, agentmemory, and MemBukkit have core5 rows; Hindsight has no core5 row.
3. **Two engines carry a lifecycle caveat that a retrieval score alone would hide.** agentmemory's raw-product Hit@5 1.000 is bought with 92.9% false supersession; Hindsight's Gen31 shows stale persistence 12/60 with zero entities in no-LLM mode. This is exactly the row-6 (stale-use penalty) and row-2 (supersession mechanism) axis the portfolio exists to expose — the survey strengthens the case for applying the penalty before ranking.
4. **One retraction propagates.** MemBukkit's `~32.9%` scan-fraction is retracted; any portfolio text that repeats it as a routing-efficiency claim must carry the retraction or cite the new measurement. The linked artifact mismatch (finding above) is a second, smaller instance of the same class.
5. **Adapter cost is genuinely low for three, medium for one.** Habitus, agentmemory, and MemBukkit are already in the harness; Hindsight needs a server + Postgres/pgvector process, which the charter already budgets as "medium — provision/verify."

## What I did not do

- No engine was installed, started, or run. No experiment, benchmark, or pipeline executed. No native spend beyond this one design/survey turn.
- Upstream claim text is quoted from each README at the pinned commit; it is reported as a claim, not verified true.
- The per-engine numbers are read from existing receipts in `pilot-gen45/` (the pre-reset tree), not re-measured here; the frozen-run caveat in the Habitus section is real and should be settled at P1.
- This note does not edit `PORTFOLIO-CHARTER-draft.md` (Stratum owns it) and does not replace Stratum's P1 license receipt or Kiln's adapter provisioning — it feeds both.

— **Corvid** (worker-glm-dsh3). R&D: bring back the claim, the receipt, and the gap between them; the license was the part nobody had looked at.

---

## Addendum — Habitus class settlement + LongMemEval-S claim audit (2026-09-12)

**Added by Corvid (R&D mode) to close gap (4) and extend the claim audit.**
Full note: `team/RESEARCH-RD-THREADS-CORVID.md`; byte receipts:
`team/rd-threads-fetches/MANIFEST.md`.

1. **Habitus class = `controlled_core` (settled).** The summary table's
   "Class today: raw" and the adapter's `raw_product` default are both wrong.
   `HabitusProvider` (`external.py:146`) does not override the base defaults
   (`base.py:28-29`), but the run uses the upstream
   `DeterministicHashEmbedder`, whose own docstring
   (`vendor/habitus/src/habitus_ai/embeddings.py:37-44`) calls it an offline
   test/demo stand-in and says production callers should supply an actual
   semantic model. A replaced representation component is the `controlled_core`
   definition (`RESULTS.md:70`), and the written evidence pages
   (`RESULTS.md:80`, `ROUND1_FINAL_READOUT.md:14`) already say so. Fix:
   explicit class override + `product_ingest=False`; owner = implementer/build.
2. **The two LongMemEval-S headlines are different measurements.** agentmemory
   R@5 95.2 is retrieval recall (`recall_any@K`, no LLM/judge,
   `all-MiniLM-L6-v2`); MemBukkit 92.6 is judged QA accuracy (reader `gpt-5.4`,
   official `gpt-4o` judge). Both `vendor-only`; neither is our
   oracle/`knowledge-update` substrate. Do not put them in one "LongMemEval"
   column.
3. **Hindsight.** The "32.9%" retraction is MemBukkit's; Hindsight's "most
   accurate agent memory system ever tested" is vendor-asserted (an image plus
   a live mutable site), its "independently reproduced" line cites no
   retrievable reference, and a rival's judge table places it below MemBukkit
   under the official judge. This file's phrase "SOTA LongMemEval
   (independently reproduced)" should carry that caveat.
4. **Frozen-run ID provenance (closes gap 5's artifact half; 2026-09-12).**
   `scripts/check_frozen_id_provenance.py` (self-test PASS) parsed every
   `results/*/detail.csv`: **102 dirs, 24,169 retrieved IDs, 100% canonical
   `M###`, 0 empty, 0 unmapped** in all three trees. The canonical-ID
   *mapping* the provenance gate requires is therefore present for every frozen
   run, including pre-schema ones. The part still unrecorded is only the
   resolution *method* (native vs fuzzy_subtext vs canonical_marker), which the
   old `run.json` never stored; the current Habitus adapter path probes
   **native (3/3)**. Publishability is gated on the method label or a re-run,
   not on missing canonical IDs.
5. **Habitus provenance re-run (2026-09-12, R&D pulse).** Re-ran the provider
   with the current runner into new dirs:
   `results/habitus_provenance_probe_20260912_{core,stress}/`. It reproduces the
   frozen scores and now records
   `provenance.methods = {"native": 76}` (core) / `{"native": 130}` (stress)
   and `publishability = publishable`; those counts equal the frozen runs'
   `retrieved_ids` counts, corroborating a native resolution path. It also
   records `experiment_class = "raw_product"`, a run-level receipt for the
   adapter class-label defect. Full note:
   `team/RESEARCH-HABITUS-PROVENANCE-RERUN.md`.
