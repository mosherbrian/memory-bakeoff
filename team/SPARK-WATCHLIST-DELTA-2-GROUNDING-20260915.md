# Watchlist delta #2 — provenance/license pass on the top three (spark, 2026-09-15)

Trigger 4 (new frontier candidates) from `SPARK-WATCHLIST-DELTA-2-20260915.md`.
Abstract/body + API reads only; **no score import**, $0.

## MemTX — Transactional Belief Commit (`arXiv:2607.23929`)

| field | value |
|---|---|
| Authors / date | Xiaoyang Li et al. (Univ. of Southern Queensland); v1 2026-07-27, **v2 2026-07-28**, cs.AI, "Preprint" |
| Paper license | **CC BY 4.0** |
| Code | `github.com/lxy1134/MEMTX_` — **NO LICENSE** (all-rights-reserved), 3★, pushed 2026-07-27 |
| Fit | persistent **shared** memory as a commit/rollback problem — "one agent's write becomes another agent's premise"; closest net-new to our supersession-as-transaction theory + multi-agent shared state |

**Status:** design reference; **code blocked** (ARR). Multi-agent angle is genuinely
new to our map (our supersession work is single-principal). Highest-theory-fit of
the delta, lowest-artifact-readiness.

## HANDBOOK.md — long-context agentic instruction following (`arXiv:2607.25398`)

| field | value |
|---|---|
| Authors / date | Liudas Panavas et al. (Surge AI); v1 2026-07-28, **v3 2026-08-03**, cs.AI/cs.CL; **COLM 2026 WAB** |
| Paper license | **CC BY 4.0** |
| Artifact | benchmark + environments + evaluation harness at `github.com/surge-ai/handbook` — **Apache-2.0**, 54★, actively maintained (pushed 2026-09-15) |
| Fit | standing policy over ~17 steps / 30 tool calls; documented failures: an in-environment request **overrides the standing policy**, a required check is **performed then ignored**, rule details **lost over the horizon**; **deterministic two-sided grader** |

**Status:** **reuse-green and the best card candidate of delta #2.** It is the
closest net-new analogue to our stale-instruction / premise-awareness concern,
with a grader we could inspect — feeds the stale-path probe design directly
(`SPARK-STALE-PATH-PROBE-DESIGN-20260914.md`), specifically the "required check
performed then ignored" failure class.

## TraceCompiler — mine agent traces into mostly-deterministic workflows (`arXiv:2608.02680`)

| field | value |
|---|---|
| Authors / date | Salma El Yadouni (EPFL), Guanyi Li (Binome Technologies); v1 **2026-08-03**, cs.SE |
| Paper license | **CC BY 4.0** |
| Artifact | **none located** — the HTML links only third-party `appworld` and a HF dataset; no TraceCompiler repo |
| Fit | skill-guided process mining with typed bindings and **auditable evidence tuples per dependency edge** (fitness/precision/generalization quartet) — our process-mining blind spot + provenance |

**Status:** design reference only (no artifact). Its evidence-tuple-per-edge shape
is the reusable part.

## Still un-passed from delta #2 (owner/next pass)

State-Aware Runtime (Cambridge Open Engage, non-arXiv), AgentProcessBench
(`2603.14465`), AgentLongBench (`2601.20730`), NetAgentBench (`2604.09678`).
None carded; each needs the same pass.

**Added (same-day dedupe):** `AgentTrails` `2607.18816` abs read — title
confirmed, v1 2026-07-21 (VLDB 2026 DASHSys workshop), **paper CC BY 4.0**;
artifact unverified. So it is a paper-level candidate only, like the others.

> Dedup note: a second same-seat pulse filed a near-duplicate grounding note;
> it was removed and its one delta (the AgentTrails license) folded here.

## Remaining delta-#2 items — provenance/license pass (second pulse)

| item | pin | paper | artifact | verdict |
|---|---|---|---|---|
| **AgentProcessBench** | `2603.14465` v2 2026-06-01, cs.AI (RUCBM) | arXiv non-exclusive | code `RUCBM/AgentProcessBench` **NO LICENSE** (33★); HF `LulaCola/AgentProcessBench` **MIT** | data reuse-green, code ARR; step-level process-quality PRM benchmark, sibling of CodeTracer's failure-onset |
| **AgentTrails** | `2607.18816` 2026-07-21, cs.DB (NYU) | **CC BY 4.0** | **none found** (4-page DASHSys 2026) | design ref only (multi-trace provenance/quotient graphs) |
| **AgentLongBench** | `2601.20730` v3 2026-01-30, cs.CL | arXiv non-exclusive | **none found** | design ref only (long-context-null corroboration: failures not explained by context length alone) |
| **NetAgentBench** | `2604.09678` v1 2026-04-03, cs.NI | **CC BY 4.0** | **none found** | design ref only (coherence-per-turn; destructive commands erode prior state) |
| **State-Aware Runtime** | Cambridge Open Engage working paper, 2026-07-11 v2 | non-arXiv | none located | design ref only (transaction-governance layer); lower confidence |

**Delta net:** all eight items now have a provenance/license line. **HANDBOOK.md**
is the only both-lane reuse-green entry (paper CC BY 4.0, harness Apache-2.0);
AgentProcessBench is data-MIT/code-ARR; the rest are design references. No score
import.

$0, web/API reads only, no Muse batching. — muse-drafter (Spark)

## Reconciliation: AgentProcessBench data lane (2026-09-15, vs the parallel pass)

The parallel pulse `SPARK-DELTA2-PROVENANCE-LICENSE-20260915.md` calls the
AgentProcessBench **data-MIT** line unsupported ("data ships inside the repo, no
separate dataset terms → ARR"). Evidence here says the two lanes are **different
artifacts** and both readings are half-right:

| artifact | evidence | verdict |
|---|---|---|
| code repo `RUCBM/AgentProcessBench` | root has no LICENSE; GitHub license API 404 | **ARR** (agree) |
| in-repo `data/AgentProcessBench/` | covered by the repo's missing license | **ARR** (if used) |
| HF dataset [`LulaCola/AgentProcessBench`](https://huggingface.co/datasets/LulaCola/AgentProcessBench) | `huggingface.co/api/datasets/...` → `cardData.license = "mit"`, tag `license:mit`, 354 downloads, files `bfcl/ gaia_dev/ hotpotqa/ tau2/ test.jsonl`; **linked from the paper's own table** | **MIT** |

So: **code ARR, but the paper ships a separate MIT HF dataset.** An adapter using
the HF release is MIT; one using the repo's in-repo data is ARR. The earlier
"data-MIT" line was right about the HF dataset and imprecise about *which*
artifact; the parallel note was right about the repo and missed the HF link.
Card owner to pin the lane explicitly before any download.

$0, API + HTML reads. — muse-drafter (Spark)
