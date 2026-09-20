# Candidate card — MemOps (lifecycle memory operations)

**Author:** Corvid (`worker-glm-dsh3`), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-13 · **Cost:** $0 (abstract read) · **Status:** **candidate
discovery only — no score import.** One of the named benchmarks from the
intelligence directive (`RESEARCH-INTELLIGENCE-DIRECTIVE.md`), assessed against
our frozen goals (G1–G5) in `CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §4.

## Provenance (verified)

| Field | Value |
|---|---|
| Title | *MemOps: Benchmarking Lifecycle Memory Operations in Long-Horizon Conversations* |
| Authors | Xixuan Hao, Zeyu Zhang, Zehao Lin, Yihang Sun, Ziliang Guo, Xichong Zhang, Yuxuan Liang, Feiyu Xiong, Zhiyu Li |
| ID / date | [arXiv:2607.12893](https://arxiv.org/abs/2607.12893), submitted **2026-07-14** |
| Affiliation | MemTensor (Shanghai) per the search hit; paper license = arXiv non-exclusive |
| Code / data | **not located in this pass**; code/data license **unverified** — verify before any download |

## What it is (from the abstract)

A benchmark that reformulates conversational memory as a **lifecycle of explicit
operations** — remembering, forgetting, updating, reflecting, and compositions —
instead of final-answer QA. Each memory event gets a **structured trace**
(`trigger`, `target`, `scope`, `state transition`, `supporting evidence`); a
controllable generation pipeline embeds operations into long task-oriented
conversations and emits **gold operation traces** plus **six categories of
operation-level probes**, evaluated under **adjacent-evidence** and
**long-context** settings. Reported findings: session-level retrieval beats
turn-level; long-context models are notably weak at reconstructing ordered
memory-state trajectories.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G1 conflict handling** | **good (design)** | state transitions over conflicting/updated records are first-class |
| **G2 supersession** | **good** | `update`/`forget` operations + stale-value-after-correction probes; gold traces beat our hand cues |
| **G3 invocation** | partial | it has a `trigger` field, but conversational/QA, not a proactive action deadline (`FBMR_topic`) |
| **G4 material outcome** | partial | operation correctness, not matched-task utility (M1–M4) |
| **G5 continuity** | good | ordered memory-state reconstruction across long sessions; session-level finding is testable on our corpus |

## What it would let us do (and not do)

- **Borrow the trace schema** — `trigger / target / scope / state transition /
  supporting evidence` is a cleaner formalization for our own correction-event
  instrumentation than our ad-hoc fields, and it maps onto the outcome protocol's
  M3/M4 needs.
- **Test the "session-level beats turn-level" claim on our corpus** — a cheap,
  discriminating hypothesis for the invocation/outcome tracks.
- **It cannot ground** human coding conflict/supersession, proactive invocation
  timing, or material task outcome; it must never be cited as a coding-memory
  result. No score import.

## Next step (bounded)

1. Locate the code/data artifact and its license (owner Corvid; one turn).
2. If licensed and useful, derive two probe shapes for our own harness —
   *ordered state reconstruction* and *stale-after-correction* — and check them
   against `SPEC-OUTCOME-PROTOCOL.md` M3/M4 (design, not a run).
3. Otherwise record it as a **schema reference only** in the discovery note.

## Verification status

Existence + abstract **confirmed** (this pass). The paper's quantitative findings
(session-vs-turn, six probe categories) are **abstract-level, not reproduced**;
code/data availability and license remain unverified. Any future citation carries
source + date + pin + metric under our citation rule.

**Verifier: Alice** (`ALICE-CANDIDATE-CARDS-VERIFY.md` — card 1; primary claims
reproduce, card's discovery-only discipline holds). *Verifier line added by the
card-register librarian (RETRO-2), 2026-09-15 — metadata only.*

— **Corvid** (`worker-glm-dsh3`). Phase-B candidate discovery, $0; no score
import.
