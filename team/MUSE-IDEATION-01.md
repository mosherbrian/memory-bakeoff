# Muse ideation batch 1 — proposals and dispositions

**Author:** Corvid (worker-glm-dsh3), R&D staff
**Authorization:** Brian via GiLMore, 2026-09-12. Muse (`acp-dsh-muse`, Meta Muse Spark 1.3 **Contributor** via OpenRouter) is Corvid's ideation contributor for **non-sensitive content only** — synthetic prompts and public research questions, never personal/work code. **Muse proposes, Corvid disposes.**
**Status:** one batched call, one turn, read-only apart from the Muse call. Receipts in `implementer/repo-glm-dsh3/scripts/experiment_20260912_muse_ideation/`.

---

## Plain English (for Brian)

Muse is now a cheap idea-generator for my R&D work: I give it public research questions, it returns candidate hypotheses, edge cases, and system ideas, and I decide which are real. This first batch asked three generic memory-evaluation questions. Muse returned nine items; **three were genuinely new and worth a bounded check, five were already covered by existing receipts, and one assumed a design the lane counter does not have.** Nothing Muse said is treated as evidence — each accepted item now needs its own measured receipt. The whole call cost about a tenth of a cent.

## Guardrails (recorded, not implicit)

- **Content:** the exact prompt is in `PROMPT.txt`, written before the call and containing only public methodology questions with all project-specific detail removed.
- **Never sent to Muse:** personal data, work code, internal paths, unpublished results, or team strategy. If a question cannot be phrased as a public research question, it does not go.
- **Role:** an ACCEPT is not a finding; it becomes one only when a bounded run produces a receipt. This is the same "receipts claim; state is" rule applied to ideation.
- **Cost:** ≤$1 per metered R&D task; the lane refuses to start if `meters.py --check` fails closed.

## What actually ran

| Field | Value |
|---|---|
| Tag / prompt | `batch1` / `scripts/experiment_20260912_muse_ideation/PROMPT.txt` (3 public questions) |
| Model on the wire | `meta/muse-spark-1.3-contributor` (no tier substitution) |
| Latency | 10.46 s (≈3 s pre-first-word, as expected) |
| Usage | input 9,346 · output 797 · cache read 113 · total 10,256 |
| Response id | `gen-1789252763-8zrGzpNckAJnYVpSf4gH`, stopReason `stop` |
| Estimated cost | ≈ $0.0011 at $0.10/M in · $0.002/M cache-read · $0.20/M out |
| Meter | `$0.7017` before and after (below the meter's 4-decimal resolution) |
| Block signals | none (no age gate, credential, routing, or training-rule block) |
| Receipts | `receipts/batch1-{stream,history,state,pty,summary,dsh-session}.jsonl/json` |

## Muse's proposals (verbatim) and dispositions

### Q1 — auditing a published memory-engine claim against runnable evidence

| # | Muse item | Verdict | Reason / next step |
|---|---|---|---|
| Q1.1 | [H] Undisclosed retrieval-time filtering or reranking can inflate reported accuracy relative to the runnable open-source configuration | **DUPLICATE** | Already a standing rule: pin embedder/reranker and treat config as part of the evaluated system (`providers/configuration_bound.py`; survey's Hindsight config-bound reranker). Nothing new to build. |
| Q1.2 | [E] Cached embeddings or precomputed answers from the evaluation set can leak into the measured run when storage is not reset between trials | **ACCEPT** | Distinct from the known stale-*process* invalidation (`HINDSIGHT_GEN4_INVALIDATION.md`). Extend the isolation preflight to assert (a) a fresh store is empty, (b) no cross-run cache artifact exists, (c) two identical runs do not inflate. Bounded and cheap. |
| Q1.3 | [I] Version drift between the benchmarked commit and the published code can hide performance-relevant differences | **DUPLICATE** | Covered by blob-pinned vendoring (`UPSTREAM.md` hashes) and the frozen-lineage check (QUEUE row 2). |

### Q2 — per-lane spend counter on a shared prepaid account

| # | Muse item | Verdict | Reason / next step |
|---|---|---|---|
| Q2.1 | [H] Concurrent sessions may race when incrementing the shared counter, so atomic updates are needed to avoid lost spend | **REJECT** | The designed counter never increments shared state: it reads provider-side balances (`meters.py`) and harness-written per-session `tokenUsage`. There is no lost-update race. The claim path is already serialized by QUEUE first-writer-wins. |
| Q2.2 | [E] Retried or failed provider calls may be billed despite returning no usable result, so the counter must reconcile attempts with confirmed charges | **DUPLICATE** | This is the design's named "unattributed residual" (`team/LANE-COUNTER-DESIGN.md` §4–5); balance-delta truth already captures failed-call spend. Worth an explicit call-out in that section, not a new mechanism. |
| Q2.3 | [I] Late-arriving usage records can push a lane over budget after new spend was approved, so the counter should reserve estimated cost upfront | **ACCEPT** | Genuinely new and directly evidenced by this run: the meter read `$0.7017` both before and after a call that cost ~$0.0011, i.e. the spend had not landed at read time. Add a **reservation/hold** to the claim arithmetic (`lane-meter --check` subtracts the row's worst-case estimate). Verification: bracket a known call and poll `meters.py` to measure update lag, then re-test the claim gate. |

### Q3 — retrieval benchmarks rewarding wrong-over-time behavior

| # | Muse item | Verdict | Reason / next step |
|---|---|---|---|
| Q3.1 | [H] Returning superseded facts as correct can earn retrieval credit while violating expected temporal validity | **DUPLICATE** | This is DECISION_MEMO row 1 (every engine co-returns the superseded record) plus row 6 (stale-use penalty). |
| Q3.2 | [E] Conflicting records with no recency or precedence resolution can all be scored as hits when only the latest version should count | **DUPLICATE** | DECISION_MEMO row 2 (supersession mechanisms, 48/48 vs 0/48 vs 12/48); the as-of/current-state evaluation already encodes "only latest counts." |
| Q3.3 | [I] Repeated stale passages across many queries can accumulate score without demonstrating updating or forgetting | **ACCEPT** | Extends the longitudinal work: Gen31 tracks `stale_persistence` (12/60) but does not frequency-weight repeated stale exposure or report time-to-correction. Verification: extend `stale_use_penalty.py` over the longitudinal set, reporting repeat count and turns-to-correction. Bounded. |

**Tally:** 3 ACCEPT · 5 DUPLICATE · 1 REJECT. Muse's yield here is divergence, not truth: the value is Q1.2, Q2.3, and Q3.3, each of which has a named, bounded check.

## Cadence going forward

- One batched Muse call per R&D item, prompt recorded before the call, all content public/synthetic.
- Every item dispositioned ACCEPT / REJECT / DUPLICATE with a reason; only ACCEPTs become proposed backlog rows, and only after a run do they become findings.
- Muse is a divergence input, not a co-author: no Muse text enters a team document without a receipt behind it.
- The three ACCEPTs above are the proposed next probes; Q2.3 folds into the lane-counter design I already own, and Q1.2/Q3.3 are cheap instrument extensions.

— **Corvid** (worker-glm-dsh3). Muse gave me nine candidates; the useful part was knowing which three were not already in our own record.
