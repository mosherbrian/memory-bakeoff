# Candidate card — SWE-Together (interactive multi-turn coding sessions with correction replay)

**Author:** muse-drafter (proposal-drafter seat), watchlist delta #3 follow-up (Sprint-2 goal 5)
**Date:** 2026-09-15 · **Cost:** $0 (abstract/body/API web reads only)
**Status:** **candidate discovery only — no score import.** One of two new
reuse-green delta-#3 candidates (`SPARK-WATCHLIST-DELTA-3-20260915.md`). Owner
unassigned; verifier: Alice.

## Provenance

| Field | Value |
|---|---|
| Title | *SWE-Together: Evaluating Coding Agents in Interactive User Sessions* |
| Authors | Yifan Wu, Zhuokai Zhao, Songlin Li, Ho Hin Lee, Jiacheng Zhu, Shirley Wu, Tianhe Yu, Serena Li, Lizhu Zhang, Xiangjun Fan, Shengzhi Li |
| ID / date | [arXiv:2606.29957](https://arxiv.org/abs/2606.29957) v1 **2026-06-29**, cs.SE |
| Paper license | **CC BY 4.0** |
| Code | official [`Togetherbench/SWE-Together`](https://github.com/Togetherbench/SWE-Together) — **Apache-2.0**, 66★, actively pushed (2026-09-14) |
| Data | official HF [`yifannnwu/SWE-Together`](https://huggingface.co/datasets/yifannnwu/SWE-Together) — **Apache-2.0**, not gated (109 task specs: instruction, repo, base commit, scoring targets, reference patch, user intents; `docker_image` → GHCR prebuilt env). NB: the `archit11/claude_traces_hs` and `alexshengzhili/dataclaw-harbor-candidates` links are **cited prior corpora, not this benchmark's data** |
| Numbers | vendor-reported only — **NOT verified, do not cite** |

## What it is

A **multi-turn** coding-agent benchmark reconstructed from **real user-agent
sessions**: 109 repository-level tasks curated from **11,260 recorded sessions**
(selected for recoverable repo states, clear user goals, observable outcomes).
A **reactive LLM-based user simulator** preserves the original users' intents and
supplies feedback when progress requires it, so interactions can be **replayed**
across agents. It scores **both final repository correctness and the number of
corrective feedback turns** (interventions) needed.

Vendor finding: stronger frontier agents achieve higher final success with
**fewer interventions**.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G4 material outcome** | **good** | final repo correctness is a harness-owned DONE-like signal |
| **M4 correction events** | **good** | "corrective feedback turns" is the closest published analogue of our correction-count metric, from real recorded sessions |
| **G5 continuity** | **good** | multi-turn interactive sessions, not single-shot tasks |
| **provenance / replay** | **good** | recovered repository states + replayable interaction is our record→origin + replay shape |
| G1/G2 conflict/supersession | partial | corrections imply revision, no explicit lineage |
| G3 invocation | weak | no proactive deadline |

## What it offers us

- **A real-recorded correction-event substrate** — 11,260 sessions is directly the
  kind of corpus our transcript miner assumes, with a published task-curation rule
  (recoverable state / clear goal / observable outcome) we could borrow.
- **The intervention-count metric** — "corrective feedback turns" is a natural
  companion to our M4, and it is measured end-to-end under a controlled simulator.
- **Replay machinery** for interaction, relevant to our M4 replay use-case
  (`SPEC-OUTCOME-PROTOCOL §5.3`).

## What it cannot ground

A memory/supersession or retrieval result; it is an agent-collaboration benchmark.
Its user simulator is an **LLM reconstruction**, not the real user — grading under
the simulator is not a live-session measurement. Numbers stay uncited.

## Artifact status: fully released and runnable

- code `Togetherbench/SWE-Together` **Apache-2.0** (66★, active; `tasks/`,
  `canonical_full109.json`, `eval`, Dockerfiles + verifiers + user-sim prompts);
- data HF `yifannnwu/SWE-Together` **Apache-2.0**, not gated, 109 rows;
- GHCR prebuilt task environments → tasks are **actually runnable**.
This is the strongest released artifact in Series C (only Compaction Cliff's DUA
is comparable). The "data terms/consent" gate that an earlier second-read flagged
rested on the cited prior corpora, not the official dataset.

## Released schema — grounded (2026-09-15, HF datasets-server first-row)

The official dataset's row is a **SWE-bench-style task + a multi-turn intent
layer**, and the pieces we care about are shipped, not just described:

- `instruction`, `repo`, `repo_url`, `base_commit`, `language`, `difficulty`,
  `category`, `tags`, `scoring_tier`;
- **`oracle_intents` + `num_user_intents`** — the fixed user-intent list that
  drives the reactive simulator (the M4/user-correction substrate);
- harness-owned correctness: `fail_to_pass` / `pass_to_pass`, `test_cmd`,
  `log_parser` (JUnit), `source_files`;
- runnable: `docker_image` (GHCR `togetherbench/...`), `cpus`, `memory`,
  `agent_timeout_sec`, `allow_internet`;
- `reference_patch`, `patch_files_changed/additions/deletions`, and
  **`patch_is_agent_author`** (the sample row is `True`).

**Provenance caution:** the sample's reference patch is **agent-authored**
(`patch_is_agent_author: True`), and the interaction ground truth is
`oracle_intents`. Any use must distinguish this ground truth from a human fix —
directly our provenance-gate concern.

## Next step (bounded)

1. ~~Body pass: task-curation rule + intervention accounting~~ **DONE** (schema
   grounded above). Compare `oracle_intents`/`user correction` to our M4 counting.
2. Check whether any scoring lane reads the agent-authored reference patch as
   ground truth (provenance flag).
3. Otherwise record as a G4/G5 + correction-event design reference.

## Verification status

Pin, authors, date, venue class, and the **Apache-2.0** official repo confirmed
via API. **Data corrected/verified:** official HF `yifannnwu/SWE-Together` is
**Apache-2.0, not gated**; the two earlier HF links are cited prior corpora.
Numbers are **unverified vendor claims**. No score import. Second seat **done**:
`CORVID-SWETOGETHER-PINCHECK.md` (clean pass) — but its "data terms are the only
open gate" rests on the cited-priors misread; the official dataset is Apache-2.0.

— **muse-drafter** (Spark). Candidate discovery, $0; no score import.
