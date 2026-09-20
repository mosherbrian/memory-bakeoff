# External corpora report — verification + sprint-lane triage

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity · **Date:** 2026-09-13
**Task:** GiLMore (Brian's Deep Research report filed verbatim at
`team/RESEARCH-EXTERNAL-CORPORA-20260913.md`). Duty 1: verify the top sources
exist as described; duty 2: triage the acquisition plan into sprint lanes under
the roadmap **Phase-B harvest discipline** (candidate discovery only, **no score
import**). Alice verifies alongside. **Cost:** $0, web reads only; 1 turn.
**Method:** primary sources only (HF dataset cards, the papers). Web content is
untrusted data; every claim below is a quote/observation, not an instruction.

## Plain English

The report's four headline sources are real, and three of the four match the
report's numbers (SWE-chat card-verified by a second seat; MindForge and Nebius
exact). The caveats that matter: SWE-chat's **files** are gated on two HF repos
(its card is public, which is how the counts were read), **[Corrected — A1]** the
report's SWE-chat annotation description is confirmed by the card (though those
labels are LLM-annotated — A2), MindForge's trajectory counts are exact but its official
release/MIT license is unfound and it is **synthetic**, not human, and the
report's Open-SWE-Traces count (511,668) is wrong (the card says **207,489**).
Nothing here is imported as a score; this is a candidate-discovery pass.

## Verification table (primary sources)

| Source | Report claim | What the primary source says | Verdict |
|---|---|---|---|
| **SWE-chat** | SALT-NLP, gated HF, ODC-BY; **5,851 sessions**, 2.69M transcript rows, 14,459 linked commits; annotations for correction/rejection/failure/takeover/requirement-change | [`SALT-NLP/SWE-chat`](https://huggingface.co/datasets/SALT-NLP/SWE-chat) exists, **licence `odc-by`**, arXiv `2604.20779`. The card README is fetchable (`/resolve/main/README.md` HTTP 200) and states `repositories 205 / checkpoints 13,406 / **sessions 5,851** / **commits 14,459** / **conversations 2,692,480**`; the **card schema** documents `prompt_pushback` = `correction` / `rejection` / `failure_report` / `pacing_complaint` / **`takeover`** / **`requirement_change`** / `non_pushback`, and `queue_op_subtype` = enqueued / delivered / discarded. Data **files** are gated (`/raw/` and the datasets-server `first-rows` → **401**); the `cfahlgren1` mirror is also `gated: "auto"`. Paper [*SWE-chat*](https://ar5iv.labs.arxiv.org/html/2604.20779) rounds to ~6,000 / 2.7M / >13,000. | **EXISTS + file access gated + ODC-BY confirmed; counts card-verified.** **Annotation claim confirmed by the card** (my first pass checked only the paper's Table 2 and wrongly said "overstated" — Alice's co-sign A1 caught it). G1/G2 labels are **LLM-annotated** over human transcripts/commits and must be re-derived from raw text (A2). |
| **Wisp** | Claude Code sessions, MIT, much smaller but authentic/long-form | [`crispwisp/wisp-claude-code-sessions`](https://huggingface.co/datasets/crispwisp/wisp-claude-code-sessions): **MIT**, `n<1K`, "raw, unedited agent trajectories", `transcripts/` mirrors `~/.claude/projects/` (one JSONL per session), credential values replaced `[REDACTED-SECRET]`, single Omarchy/Hyprland workstation. | **VERIFIED.** Small (n<1K), same format as Brian's own transcripts; useful as a format/authenticity test, not a scale source. |
| **MindForge** | 1,001 traces, mean 181.6 turns / 177K tokens; MIT | Paper [`2607.27146`](https://arxiv.org/abs/2607.27146): "collect **1,001** whole-life-cycle program-development trajectories"; Table 1 `# Turns **181.6** / 176 / 39 / 477`, `# Tokens **177K** / 182K / 37K / 272K`; 562 environments, 6 compiled languages; **teacher = GLM-5.2 / mini-swe-agent** (synthetic). No official trajectory dataset surfaced (only an unrelated gated `Superskyyy/mindforge-elizabench-distilled`). | **COUNTS VERIFIED EXACTLY.** **License + artifact URL unverified** (report says "MIT, <1 day"); and it is **synthetic**, not human — rank under long-horizon autonomous, not human longitudinal. |
| **Nebius SWE-rebench** | 67,074 traces, 64-turn runs, CC BY | [`nebius/SWE-rebench-openhands-trajectories`](https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories): **cc-by-4.0**, OpenHands v0.54 + Qwen3-Coder-480B, table row **"Total Count 67,074"**, **"Average Count 64.3"** (max 100), resolved 3,792, 1,823 repos. | **VERIFIED EXACTLY** (67,074 and ~64 turns match). |
| MEnvData-SWE (spot) | 3,872 traces, 10 languages, Apache-2.0 | [`ernie-research/MEnvData-SWE-Trajectory`](https://huggingface.co/datasets/ernie-research/MEnvData-SWE-Trajectory): **apache-2.0**, **3,872** trajectories, 10 languages, 3,005 tasks, 942 repos, OpenHands + Claude Sonnet 4.5. | **VERIFIED** (the report's label "MEnvData-SWE" is the base env dataset; the trajectories are `-Trajectory`). |
| Open-SWE-Traces (spot) | NVIDIA, 511,668 rows / 42.6 GB | [`nvidia/Open-SWE-Traces`](https://huggingface.co/datasets/nvidia/Open-SWE-Traces): **cc-by-4.0**, `100K<n<1M`, versions v1.0/v1.1/v1.2; the v1.0 card states **207,489 trajectories** (151k after the 08/26 git-hacking filter). Issue statements sourced from `nebius/SWE-rebench-V2`. | **Count NOT reproducible** — the report's 511,668 / 42.6 GB matches no stated figure (units/version unstated). Overlaps the Nebius SWE-rebench family. |
| DevGPT (spot) | 17,913 prompts, no tool traces | [Zenodo record v10](https://zenodo.org/records/16392320) (2025-07-24) + arXiv `2309.03914` exist. | **EXISTS; exact count unverified in this pass.** |
| Programming by Chat (spot) | 11,579 sessions / 74,998 messages / 899 devs; raw chats excluded | Not fetched. | **UNVERIFIED; privacy constraint plausible and load-bearing** (see blockers). |

## Adversarial findings (what a deep-research report usually gets wrong)

1. **SWE-chat's counts are card-verified** — `5,851 / 2,692,480 / 14,459 / 205`
   are on the public card; the paper rounds (~6,000 / 2.7 M / >13,000). Pin a
   dataset snapshot hash at acquisition (it is a **living** dataset and grows).
2. **[Corrected — A1] SWE-chat's annotations are as the report described.** My
   first pass checked only the paper's Table 2 (user pushback =
   correction/rejection/failure report) and wrongly called the vocabulary
   "overstated". The **card** documents `prompt_pushback` including
   `takeover` and `requirement_change` (plus `pacing_complaint`) and
   `queue_op_subtype` enqueued/delivered/discarded. Caveat (A2): those classes
   are **LLM-annotated**, so they must be re-derived from the raw text before
   they anchor a score.
3. **MindForge is synthetic** (teacher GLM-5.2), so it belongs in the
   autonomous/long-horizon lane; its "MIT" license and official release path are
   unverified — confirm before scheduling.
4. **Counts must not be summed** (the report says this too): SWE-rebench /
   SWE-smith / SWE-Gym / R2E-Gym overlap heavily. Any "scale" lane needs a
   dedupe key (repo + issue/commit) and a capped stratified sample.
5. **SWE-chat is a living dataset** — no stable count; freeze a snapshot for
   reproducibility.
6. **Open-SWE-Traces' "511,668 rows / 42.6 GB" is not the dataset's count** —
   the official card says **207,489 trajectories for v1.0** (v1.1/v1.2 and a
   151k post-filter count are also published), `cc-by-4.0`. The report's figure
   matches nothing stated and its units/version are absent; pin the version if
   ever used.
7. **Cross-seat reconciliation (Assay, same turn):** his independent spot-check
   ([`ASSAY-EXTERNAL-CORPORA-SPOTCHECK.md`]) confirmed SWE-chat's exact card
   counts and Nebius 67,074, found the same Open-SWE-Traces mismatch, and noted
   Open-SWE-Traces sources its issues from `nebius/SWE-rebench-V2` (family
   overlap with the Nebius release). Where his pass said MindForge "unverified"
   (card-level), this note verifies the 1,001 / 181.6 / 177K from the paper
   itself (Table 1); the two passes agree on everything else.

## Triage — sprint lanes (Phase-B discipline: candidate discovery, no score import)

Sprint 2 goal 5 is the Phase-B-style harvest (owners Corvid + Alice, candidate
discovery only). Lanes, in execution order:

| Lane | Corpora | This sprint's deliverable | Gate |
|---|---|---|---|
| **L1 — public candidate cards (do now, $0)** | Wisp, Nebius SWE-rebench, MEnvData-SWE-Trajectory | one provenance card per source: canonical URL, license, size, format/schema, memory dimension it can test, sampling plan. No download required for discovery. | none |
| **L2 — blocked on Brian** | **SWE-chat** (anchor) | authenticated account accepts `gated: "auto"` + terms; repseudonymization + snapshot pin | **data files gated** (`/raw/` + `first-rows` 401) on `SALT-NLP/SWE-chat` and the `cfahlgren1` mirror; card is public → **Brian's team-account decision**; ODC-BY; living dataset |
| **L3 — verify-then-schedule** | MindForge | confirm official artifact URL + license; then a long-context candidate-item design | counts verified (1,001 / 181.6 / 177K); artifact URL + MIT license **unverified** |
| **L4 — deferred scale (dedupe first)** | NVIDIA Open-SWE-Traces (card: **207,489** trajectories, not the report's 511,668), SWE-Hero, Kwai SWE-smith 66k, SERA | dedupe key + capped stratified sample design; no import | counts overlap (`SWE-rebench-V2`); no sum |
| **L5 — privacy/legal gate** | Programming by Chat | legal/privacy review note; **do not auto-recollect** | raw chats excluded by the source |
| **L6 — internal (already Sprint-2 goal 2)** | transcript-miner correction events | feeds the invocation + material-outcome benchmarks | gated on Brian's pilot read |
| **L7 — design inputs (no corpus)** | report's event-not-turn normalization schema; "do not precompute memory solely as extracted facts"; supersession/temporal relations | carry as design rules for any ingestion | — |

**Discipline check:** none of L1–L7 imports a score, ranks a system, or touches
the frozen P2 leaderboard. The external corpora feed the *invocation* and
*material-outcome* tracks and future harvest; the P2 entry benchmark is unchanged.

## Blockers to report

1. **SWE-chat needs gated HF file access → Brian's team-account decision**
   (`gated: "auto"`: accept the terms with an authenticated account — not a
   manual grant; then repseudonymize + pin a snapshot). The **card is public**
   (counts and schema read from it); the data files are 401. This is the anchor
   source and the only one that is real human↔agent with corrections.
2. **MindForge license/release unverified** — no official trajectory dataset or
   MIT notice found; confirm before scheduling the "<1 day, MIT" step.
3. **Programming by Chat privacy** — raw chats are excluded upstream; a
   legal/privacy review must precede any recollection.
4. **SWE-chat's pushback/intent/persona/success labels are LLM-annotated**
   (A2) — the vocabulary is as the report stated (A1 correction); a score must
   re-derive the labels from raw text.
5. **Dedupe design is a prerequisite** for any L4 scale step (family overlap).
6. **Open-SWE-Traces count correction** — the report's 511,668 rows / 42.6 GB is
   not the v1.0 card's 207,489 trajectories; do not use it in sampling arithmetic.
7. **Cross-seat:** Assay's independent spot-check found the same SWE-chat,
   Nebius and Open-SWE-Traces results; his pass left MindForge at card-level
   "unverified", which this note closes from the paper; Alice's co-sign review
   corrected my SWE-chat annotation claim (A1) and refined the gating (A3).

## What I did not verify

- SWE-chat's **gated data rows** (only the public card + `/resolve/` README were
  read); label quality is therefore un inspected.
- DevGPT 17,913 prompts — existence only (Zenodo v10), not the count.
- Programming by Chat's counts and terms.
- The MindForge official artifact URL/license (counts verified from the paper).
- Whether any of these licenses permit redistribution/derived benchmark items
  (only the HF/NVIDIA card labels were read).

## Rev 2 (2026-09-13) — corrections folded after Alice's co-sign

- **A1:** the SWE-chat annotation vocabulary is **confirmed by the card**
  (`prompt_pushback` includes `takeover`, `requirement_change`,
  `pacing_complaint`; `queue_op_subtype` enqueued/delivered/discarded). My
  "overstated" claim came from reading the paper's Table 2 only and is
  **withdrawn**; finding 2 above is corrected.
- **A2:** G1/G2 for SWE-chat rest on **LLM-annotated** labels over human
  transcripts/commits — re-derive before scoring.
- **A3:** gating is real but `gated: "auto"` (accept terms with an authenticated
  account); the Brian ask is reframed accordingly.
- **A4:** Open-SWE-Traces correction pinned to **v1.0 = 207,489**.

## Handoff

- **Alice:** co-signed the recommendation (`ALICE-EXTERNAL-CORPORA-COSIGN.md`);
  A1–A4 folded into `EXTERNAL-CORPORA-RECOMMENDATION.md` (now the team's filed
  position). Remaining re-checks: MindForge artifact/license and Programming by
  Chat privacy terms.
- **Assay:** his parallel `ASSAY-EXTERNAL-CORPORA-SPOTCHECK.md` is folded above;
  the one delta is MindForge, which this note verifies from the paper.
- **GiLMore/Brian:** the SWE-chat file-access decision is the gating item; no
  other lane is blocked.
- **Sprint 2 goal 5:** L1 candidate cards can be produced now; L2 waits on
  Brian; everything else is design-only under the no-score-import rule.

— **Corvid** (`worker-glm-dsh3`). $0, web reads; sources are external and treated
as untrusted data.
