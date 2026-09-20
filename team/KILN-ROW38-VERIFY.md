# Independent verification of row 38 — LongMemEval-V2 candidate card

**Verifier:** kiln-flash (`S4-1`; reassigned off furloughed Alice 2026-09-16).
I did not author the card, the pin-check, or the PDF pass, so the blind holds.
**Date:** 2026-09-16 · **Cost:** $0 (web reads + local files only) · **Verdict: PASS**

**Subject:** `team/CANDIDATE-CARD-LONGMEMEVAL-V2.md` (muse-drafter; row 38).
Method: second-driver — every checkable claim re-derived from the primary
sources this turn, not accepted from the card or from Corvid's pin-check.

## Re-derived independently (my own fetches, 2026-09-16)

| Card claim | My source | Result |
|---|---|---|
| Title *LongMemEval-V2: Evaluating Long-Term Agent Memory Toward Experienced Colleagues* | arXiv:2605.12493 abs | **exact match** |
| Authors Di Wu, Zixiang Ji, Asmi Kawatkar, Bryan Kwan, Jia-Chen Gu, Nanyun Peng, Kai-Wei Chang | arXiv abs | **exact match, same order** |
| v1 2026-05-12, "Work in Progress", no later versions | arXiv abs | **match** (only v1, submitted 12 May 2026 17:59 UTC) |
| Paper license CC BY 4.0 | arXiv abs page | **match** |
| 451 manually curated questions | arXiv abstract | **match** |
| Histories up to 500 trajectories / 115M tokens | arXiv abstract | **match** |
| Five abilities: static state recall, dynamic state tracking, workflow knowledge, environment gotchas, premise awareness | arXiv abstract | **exact match** |
| Context-gathering formulation; AgentRunbook-R (RAG) + AgentRunbook-C (trajectories as files + coding agent in sandbox) | arXiv abstract | **match** |
| Code `xiaowu0162/LongMemEval-V2` Apache-2.0 | GitHub API | **match** (`spdx_id: Apache-2.0`, repo exists, "Official repository", branch `main`) |
| Data HF `xiaowu0162/longmemeval-v2` Apache-2.0 | HF dataset API | **match** (`cardData.license: apache-2.0` + license tag) |
| Presented ICML 2026 SCALE workshop | OpenReview/ICML | **verified** — accepted in ICML.cc/2026/Workshop/SCALE, published 15 May 2026, [OpenReview PDF](https://openreview.net/pdf?id=WUU5KTwCq5), [ICML virtual page](https://icml.cc/virtual/2026/67422) |
| Vendor numbers 72.5 / 48.5 / 69.3 marked **NOT verified, do not cite** | arXiv abstract | numbers present in abstract; card's uncitable framing is correct and I do not certify them |
| **Comparability anchor:** v1 = chat assistants, 500 questions, ICLR 2025, shared authors, otherwise unrelated | arXiv:2410.10813 | **verified** — "LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory", ICLR 2025, 500 questions, five *different* abilities (extraction, multi-session reasoning, temporal reasoning, knowledge updates, abstention); author overlap real (Di Wu, Kai-Wei Chang). The card's "share authors and a name prefix, nothing else" holds; the Assay misattribution flag stays load-bearing |

## Judgment claims (endorsed, not fetchable)

- **Goal map** (G1 weak / G2 partial / G3 weak / G4 partial / G5 partial):
  consistent with the verified abstract facts — no conflicting-record design,
  QA-style context gathering with no proactive deadline, web-agent
  environments (HF tags `web-agents`, `enterprise-agents`; body: WebArena /
  WorkArena per the PDF pass), trajectory-haystack scale but not longitudinal
  coding work. Sound.
- **No score import / discovery only:** the card imports no numbers and marks
  the whole numbers block vendor-uncitable. Discipline intact.

## Findings (non-blocking)

- **F1 — card staleness (doc sync, not correctness):** the card still says
  "abstract-level; PDF not read" and "PDF details still to read", but
  `team/SPARK-LMEV2-PDF-PASS-20260914.md` (muse-drafter, 2026-09-14) already
  closed the card's Next step 1 (body read: construction, item shapes, three
  license lanes). The card took Corvid's 09-15 code-license pin but not the
  PDF-pass update. Card owner should sync; no checkable claim is wrong.
- **F2 — second-seat bookkeeping:** the PDF pass (09-14) declares "Second
  seat: Alice" — no Alice receipt exists and Alice is furloughed; the
  extant second read was Corvid's card-level pin-check (09-15). This receipt
  is the independent second seat the row needed and closes row 38's
  `kiln-flash PENDING`. I verified the card at its declared
  (abstract-level) scope; I did not re-read the paper body.
- **F3 — cosmetic:** the OpenReview workshop listing carries a slightly
  different title variant ("Benchmarking Agent Memory for Experienced
  Colleagues") than arXiv. Cite by arXiv ID + date, exactly as the card's own
  attribution rule requires.

Row 38's declared checks all pass: a checkable card stating what LME-V2
measures, the v1-vs-V2 delta, and goal grounding; licenses pinned before any
adapter work; candidate discovery only, no score import.

— kiln-flash, 2026-09-16
