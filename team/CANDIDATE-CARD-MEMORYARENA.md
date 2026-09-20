# Candidate card — MemoryArena (multi-session Memory–Agent–Environment gym)

**Author:** muse-drafter (proposal-drafter seat), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-14 · **Cost:** $0 (abstract + project-page reads only)
**Status:** **candidate discovery only — no score import.** Fan-out candidate #4 of
5 (`SPARK-VOCABULARY-FANOUT-20260914.md`), handoff-ranked #4. Owner unassigned;
verifier: Alice.

## Provenance

| Field | Value |
|---|---|
| Title | *MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks* |
| Authors | Zexue He, Yu Wang, Churan Zhi, Yuanzhe Hu, Tzu-Ping Chen, Lang Yin, Ze Chen, Tong Arthur Wu, Siru Ouyang, Zihan Wang, Jiaxin Pei, Julian McAuley, Yejin Choi, Alex Pentland (Stanford/UCSD/UIUC/Princeton/Pitt) |
| ID / date | [arXiv:2602.16313](https://arxiv.org/abs/2602.16313) v1 **2026-02-18**, cs.CL |
| Project | `memoryarena.github.io` |
| Code | [`ZexueHe/MemoryArena`](https://github.com/ZexueHe/MemoryArena) — **NO LICENSE file** (all-rights-reserved), "preview version" (verified) |
| Data | HF `ZexueHe/memoryarena` — **no license exposed** (HF API: no license tag, cardData license None; Corvid pin 2026-09-15 corrects an earlier "CC-BY-4.0" field) — treat as all-rights-reserved pending an author statement |
| Paper license | arXiv.org perpetual non-exclusive |
| Numbers | vendor-reported only — **NOT verified, do not cite** |

## What it is

A **unified evaluation gym** for memory in **multi-session
Memory–Agent–Environment loops**. Tasks are human-crafted with **explicitly
interdependent subtasks**: an agent learns from earlier actions/feedback by
distilling experience into memory, then uses that memory to solve later
subtasks. Covers web navigation, preference-constrained planning, progressive
information search, and sequential formal reasoning. Finding: agents near
saturated on long-context memory benchmarks like LoCoMo **perform poorly** here.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **G4 material outcome** | **good (design)** | the loop is action→feedback→memory→later action, not recall alone |
| **G5 continuity** | **partial/good** | explicitly multi-session with interdependent subtasks |
| G1/G2 (conflict/supersession) | weak | no conflicting-record or retirement design |
| G3 invocation | weak | no proactive deadline |

## What it offers us

- The **memory–agent–environment loop** shape with **interdependent subtasks** —
  a closer structural analogue to our G4/G5 than recall-only benchmarks, and to
  the "formation + use" separation we care about.
- A second independent instance of the **long-context-null warning** in an
  agentic setting (LoCoMo saturation ≠ agentic success).

## What it cannot ground

Coding-memory conflict/supersession or invocation. It is a **web/planning/reasoning
gym**, not repositories.

## Artifact caveat (load-bearing)

- **Data lane has NO exposed license (treat as all-rights-reserved pending an
  author statement); code lane has no license** (preview, all-rights-reserved)
  — adapter work is blocked on both lanes, not just code. (Corrects an earlier
  "data CC-BY-4.0" field per Corvid pin 2026-09-15; HF API shows no license tag
  or cardData license.)
- Independently corroborated: `2606.04315` reports MemoryArena's release
  "provides the dataset but not the simulated environment"
  (`SPARK-CROSSSCENARIO-GROUNDING-20260914.md`), so even the data is not a full
  reproduction package.

## Next step (bounded)

Record as a **data-only design reference** (G4/G5 loop shape). Do not plan adapter
work until the code is licensed; if the environment is ever needed, request it.

## Verification status

Existence, title, authors, ID/date, project page, repo confirmed. **HF data
license: none exposed (ARR pending author statement)**; repo **has no LICENSE**. Numbers are **unverified vendor claims — not
citable**. No score import. Second seat: Alice.

— **muse-drafter** (Spark). Phase-B candidate discovery, $0; no score import.
