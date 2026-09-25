# TEAM RECOMMENDATION — external corpora acquisition (our judgement, not the report's)

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Co-sign:** Alice (`worker-glm-dsh`, verification/provenance) — **conditional,
given 2026-09-13 18:25 UTC** (A1–A3 in §7 required before filing)
**Date:** 2026-09-13 · **Cost:** $0, synthesis + already-fetched public sources
**Governance framing (Brian via GiLMore):** the ChatGPT Deep Research report
(`team/RESEARCH-EXTERNAL-CORPORA-20260913.md`) is **candidate-discovery input
only**. Its rankings, verdicts and acquisition order are one outside opinion to
weigh, **not a plan to adopt**. This document evaluates the sources against
**our** frozen evaluation goals and states the team's own recommendation. Until
Alice signs, this is a **draft**, not the team's filed position.
**Evidence base:** `team/CORVID-EXTERNAL-CORPORA-VERIFY-TRIAGE.md` (this
session's primary-source verification) + `team/ASSAY-EXTERNAL-CORPORA-SPOTCHECK.md`.

## 1. Our frozen goals (the only axes this recommendation scores)

| # | Goal | Where it is frozen | What a source must contain to ground it |
|---|---|---|---|
| **G1** | **Conflict handling** — what happens to the OLD truth when two records disagree | `ECOSYSTEM-MAP.md` E-7 / cross-cutting axis C; Gen38 `dynamic_conflict` anchor (`research/MEMCONFLICT_GEN38_FULL_RELEASE.md`); charter row 2 | genuinely conflicting records over the same subject, with the correct resolution externally observable |
| **G2** | **Supersession** — newer instruction/state replaces older; stale must not win | AGENTS rule ("false merge/supersession must not be rewarded as better retrieval"); agentmemory 418/450 false-supersession finding; invocation `stale_use` + `anachronism_violation` | an explicit "old value → new value" transition in a real workflow, plus a later turn where acting on the old value is observably wrong |
| **G3** | **Invocation** — the system notices, proactively, before the action | `team/DESIGN-INVOCATION-BENCHMARK.md` primary `FBMR_topic` (+ `CBMR`/`stale_use`/`anachronism`) | ordered turns with decision moments, a covering record, and an action deadline the harness can observe |
| **G4** | **Material outcome** — did the work actually go better with memory | `team/SPEC-OUTCOME-PROTOCOL.md` M1–M4 (time, errors, redundant re-discovery, operator corrections) | matched tasks with a DONE condition and programmatic failure/correction signals |
| **G5** | **Longitudinal continuity** — cross-session/compaction continuity, durable vs transient | `ECOSYSTEM-MAP.md` E-8; our own pi-lcm line; R2 pilot (`RESET_STATUS.md`); agentmemory/report "do-not-remember" targets | the same project/human across sessions, with a durable decision that must persist and transient state that must decay |

**Scoring rule we add (the report does not):** a source may be cited **only for
a goal it can ground**. Synthetic autonomous trajectories cannot ground human
conflict handling, requirement change, or preference persistence; a prompt dump
cannot ground invocation or outcome. No source gets credit for "coverage" it
cannot evidence. **Labels carry provenance too (A2):** a goal grounded only by an
LLM-annotated field must be re-derived from the raw text before it anchors a
score, and the label's provenance is reported beside it.

## 2. Source × goal evaluation (our matrix)

Legend: **Y** = can ground the goal with the stated evidence; **p** = partial /
needs curation; **–** = cannot ground; **?** = unverified.

| Source (verified counts) | G1 conflict | G2 supersession | G3 invocation | G4 outcome | G5 continuity | Class | Notes / what it is FOR |
|---|---|---|---|---|---|---|---|
| **Internal transcript miner** (Brian's own sessions; correction events) | **Y** — operator corrections, "actually"/negation | **Y** — "I said…" reversals, repeated instruction, env-fact corrections | **Y** — the only source wired to the invocation benchmark's correction events | **Y** — matched tasks already under `SPEC-OUTCOME-PROTOCOL.md` | **Y** — one long project, durable decisions vs transient state | real human | **Tier 0.** Highest goal coverage and the only source with *our* ground truth; already in Sprint-2 goal 2, gated on Brian's pilot read. |
| **SWE-chat** (5,851 sessions / 2,692,480 conversations / 14,459 commits / 205 repos; ODC-BY; file access `gated: "auto"`) | **Y** — `prompt_pushback` = correction / rejection / failure_report / pacing_complaint / **takeover** / **requirement_change** (card schema) | **Y** — `queue_op_subtype` delivered-vs-discarded, `is_continuation`, interruptions | **p** — decision moments exist but records must be reconstructed from file history | **Y** — commit diffs, code-survival, human-vs-agent attribution; `session_success` (LLM-annotated) | **Y** — `is_continuation`, file-history snapshots, 205 real projects | human transcripts + human commit attribution; **pushback/intent/persona/success labels are LLM-annotated, re-derivable from raw text** | **Tier 1 — the one external acquisition to make.** The only public source spanning all five goals; ground the LLM labels from raw text (A2). |
| **Wisp** (MIT, n<1K, Claude Code JSONL) | – | p — a config decision vs obsolete process state | – | – | p — multi-hour sessions, one workstation | real human, tiny | **Tier 2 control.** Format/authenticity control (same JSONL as Brian's own); **not** a benchmark source. |
| **Nebius SWE-rebench** (67,074 / avg 64.3 turns; CC-BY) | – | **Y** — stale early hypotheses must not persist; 64-turn state dependencies | – | **p** — resolved/unresolved + tests, but autonomous | – | synthetic agent | **Tier 2 negative control.** Use to prove the *harm* side (a system that keeps every observation is hurt); never for human conflict/supersession claims. |
| **MindForge** (1,001; mean 181.6 turns / 177K tokens; synthetic; license/release **?**) | – | **Y** — evidence accumulation + hypothesis revision over hundreds of turns | – | p — buildable submission | – | synthetic agent | **Tier 3 stress.** Long-horizon hypothesis-revision torture test; only after release/license confirmed. |
| **MEnvData-SWE-Trajectory** (3,872 / 10 languages; Apache-2.0) | – | p — state dependencies | – | p — task instances | – | synthetic agent | **Tier 3 stress.** Polyglot state-dependency control; sample only. |
| **Open-SWE-Traces** (card 207,489; report's 511,668 **wrong**; CC-BY) | – | p | – | p | – | synthetic agent | **Tier 4 — do not acquire separately.** Family-overlaps Nebius (`SWE-rebench-V2`); the report's count is not the card's. |
| **DevGPT** (17,913 prompts; no tool traces) | p — human dialogues | p | **–** — no tool traces, cannot ground invocation | **–** | – | real human, prompts only | **Tier 4.** Weak on every goal we score; not worth an acquisition slot. |
| **Programming by Chat** (11,579 sessions; raw chats excluded) | **?** | **?** | – | – | **?** | real human, privacy-blocked | **Tier 4 / legal gate.** Do not auto-recollect; legal/privacy review first. |
| SWE-Hero / SWE-smith 66k / SERA (scale) | – | p | – | p | – | synthetic agent | **Tier 4.** Add no new goal coverage; acquire only after the human anchor + dedupe design. |

## 3. Where we diverge from the report (explicitly)

1. **Volume is not a goal.** The report's acquisition order drifts toward the
   large synthetic corpora; our goals are lifecycle *behaviours*, and a million
   autonomous rollouts add no new ground truth for G1/G2/G5. We demote them to
   controls.
2. **The human anchor is the whole point, not a first step.** The report says
   this in prose but plans "scale corpora last" only after five autonomous
   datasets. We invert that: acquire **SWE-chat** (the one real-human
   multi-goal source) or nothing external as an anchor.
3. **We require goal-specific ground truth** (the scoring rule in §1). The
   report's "EXCELLENT" ranks conflate scale with relevance to our eval.
4. **We add the harm controls as first-class.** Supersession must be measured
   with `stale_use` / `anachronism` and "do-not-remember" targets; sources that
   cannot provide a stale/obsolete record cannot test G2.
5. **We keep our own corpus first.** The internal transcript miner covers all
   five goals with our ground truth and is under-weighted in the report because
   it is not public.
6. **We treat the report's numbers as claims to verify** — done, with a
   self-correction: its Open-SWE-Traces count is wrong (v1.0 card **207,489**,
   not 511,668), and its SWE-chat **annotation vocabulary was right** — my
   first-pass paper-only check missed the card's `prompt_pushback` schema
   (`takeover`, `requirement_change`), and Alice's co-sign review (A1) caught
   the error.

## 4. Our recommendation (sequence + rationale)

- **Tier 0 — proceed (internal, no external acquisition):** the transcript
  miner's correction-event corpus, per Sprint-2 goal 2, gated on Brian's pilot
  read. Feeds G1–G5 and both new benchmarks.
- **Tier 1 — the decision to ask Brian for:** **SWE-chat file access** — ODC-BY,
  `gated: "auto"` (accept the terms with an **authenticated account**, not a
  manual grant), repseudonymize, pin a snapshot (living dataset). This is the
  only external acquisition that advances all five goals; ground its
  LLM-annotated labels from raw text (A2). If access is refused, the external
  anchor is **not** replaced by scale corpora; the team runs on Tier 0 +
  controls and says so.
- **Tier 2 — acquire now, $0/free, as controls only:** **Nebius SWE-rebench**
  (stale-hypothesis harm control) and **Wisp** (format/authenticity control).
  Both public; neither may be cited for human G1/G2/G5.
- **Tier 3 — design-only until licensed:** **MindForge** (long-horizon
  hypothesis-revision stress) and a sample of **MEnvData-SWE-Trajectory**
  (polyglot state). Confirm MindForge release/license first; these produce
  stress items, not scores.
- **Tier 4 — do not acquire now:** Open-SWE-Traces (overlap + wrong count;
  v1.0 card **207,489**, with v1.1/v1.2 and a 151k post-filter count also
  published — pin the version if ever used), DevGPT (no tool traces),
  Programming by Chat (legal), SWE-Hero/SWE-smith/SERA (no new coverage).
  Revisit only if a goal gap appears that a family representative cannot fill.
- **Dedupe rule:** acquire at most **one representative per dataset family**
  (keyed on repo+issue/commit), plus the one human anchor. Never sum counts.
- **Corpus-item rule:** keep the raw event stream; derive annotations
  separately; **carry label provenance** (human vs LLM-annotated) on every
  derived annotation; preserve supersession → superseded-by links and
  `valid_from/to`; never precompute memory as facts only (the report's own good
  design point — accepted).

## 5. What we will NOT do (Phase-B discipline)

No score import; no leaderboard/ranking of systems from these corpora; no
winner declarations; no synthetic corpus cited for human lifecycle claims; no
scale acquisition before the human anchor and a dedupe key; no recollection of
privacy-blocked corpora without a legal review.

## 6. Open decisions / blockers

1. **Brian:** SWE-chat file access — `gated: "auto"`, so the ask is **"confirm
   the team HF account can accept the gate and download"** plus the snapshot
   pin (the gating decision); if yes, the repseudonymization plan is ours.
2. **Brian:** transcript-miner pilot read (Tier 0 gate).
3. **Owner (Corvid/Alice):** confirm MindForge official release + license.
4. **Legal/privacy:** Programming by Chat before any use.
5. **Co-sign:** Alice has co-signed (A1–A4 folded; see §7) — this is now the
   team's filed position.

## 7. Co-sign block

- **Corvid:** recommend as above — goal-first, human anchor first, controls
  explicit, no score import. `2026-09-13 18:20 UTC`.
- **Alice:** **conditional co-sign** `2026-09-13 18:25 UTC` (A1–A3 required, A4
  minor); detail in `team/ALICE-EXTERNAL-CORPORA-COSIGN.md`.

## Rev 2 (2026-09-13) — Alice's A1–A4 folded; co-sign **unconditional**

- **A1 (factual, corrected):** the card documents `prompt_pushback` =
  correction / rejection / failure_report / pacing_complaint / **takeover** /
  **requirement_change** / non_pushback, so the report's SWE-chat vocabulary was
  right; the "overstated" clause is removed from this note and from
  `CORVID-EXTERNAL-CORPORA-VERIFY-TRIAGE.md` (my paper-only check missed the
  card schema).
- **A2 (grounding):** SWE-chat's G1/G2 grounding is now stated as human
  transcripts + human commit attribution with **LLM-annotated** pushback/queue
  labels (re-derivable from raw text); the scoring rule and corpus-item rule
  carry the label-provenance requirement.
- **A3 (gating refined):** `gated: "auto"` on both `SALT-NLP/SWE-chat` and the
  `cfahlgren1` mirror; data endpoint 401. Tier 1's blocker stands; the Brian ask
  is reframed as "authenticated account accepts the gate + snapshot pin".
- **A4 (version pin):** Open-SWE-Traces correction carries **v1.0 = 207,489**
  (v1.1/v1.2 and the 151k post-filter count noted).

— **Corvid** (`worker-glm-dsh3`). Alice co-sign folded; **filed as the team's
position**. $0.

## What about this document should NOT be trusted (mandatory section per QUEUE D-6)

- **No number in the source report is importable.** Every benchmark figure the
  ChatGPT report cites is vendor-only provenance (CLAIMS-LEDGER §PROVENANCE:
  the Mem0 paper v1 Table 2 alone originates four systems' numbers); importing
  any of them would break the no-score-import rule this document is built on.
- **The count corrections travel with the tiers.** Open-SWE-Traces is
  do-not-acquire partly because its card count (v1.0 = 207,489) contradicts
  the report's 511,668 — a same-class discrepancy may exist for any count we
  have not card-verified. Cite card-verified numbers only.
- **SWE-chat's tier-1 status is gated, not granted.** Its file access 401s
  until an authenticated account accepts `gated: "auto"` plus a snapshot pin;
  until then Tier 1 is an aspiration, not an acquisition.
- **The goal→source matrix is our judgement, not a measurement.** The tier
  ordering encodes which frozen goals we could ground TODAY; it has no
  experimental evidence behind it and should be re-derived if the goal set or
  the instrument changes.

[Section added 2026-09-17 by kiln-flash under QUEUE D-6: the card contract's
mandatory do-not-trust section was missing from this file; no claim above was
changed, the trust boundaries were made explicit.]
