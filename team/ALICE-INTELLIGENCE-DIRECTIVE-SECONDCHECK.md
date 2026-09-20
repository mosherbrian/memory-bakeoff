# Second-check — Intelligence Directive assessment: benchmark coverage + three headline numbers verified

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 21:4x UTC · **Cost:** $0, reads + public sources, one turn.
**Trigger:** `CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §5 second-check block
— "(a) are any named benchmarks already covered by our ledger/coverage map, and
(b) are the numeric claims (StreamMemBench 27.5→40.6; MemSecBench 310/48;
AMA-Agent 57.22) worth a verification pass?" No tree modified.

## (a) Coverage — the benchmarks are new; two partial touches only

Searched `CLAIMS-LEDGER.md`, `ECOSYSTEM-MAP.md`, `CORVID-CHECKER-COVERAGE-MAP.md`,
`RESEARCH-4-ENGINES-SURVEY.md` for each named benchmark:

| benchmark | in our docs? |
|---|---|
| MemOps, StreamMemBench, MemSecBench, GateMem, STALE, Supersede, Mem2ActBench, AMA-Bench/AMA-Agent, LongMemEval-V2, Agent Memory Leaderboard, SWE-Gym, BEAM | **none** |
| HaluMem | only as a **column in MemOS's vendor table** (`L-S16-02`: "HaluMem 80.91") — the benchmark is not surveyed |
| EvoMemBench | one line in `ECOSYSTEM-MAP.md` E-1/§ (intake note); no ledger row or survey entry |

So Corvid's §2 "benchmarks we have not surveyed" holds, with the caveat that
**HaluMem and EvoMemBench already touch our record** and should be credited as
partials when the candidate cards are written (no score import). The lowercase
`stale`/`supersede` hits are our own vocabulary, not the benchmarks.

## (b) Verification — all three numbers CONFIRMED from primary sources

| claim | source | verdict |
|---|---|---|
| StreamMemBench: paired ablation on **160 trajectories**, committing the interaction raises FUR **27.5% → 40.6%**, the remaining **13.1 points** are the commit gain | [arXiv 2606.14571](https://arxiv.org/abs/2606.14571) **PDF** ("We run a paired ablation on 160 trajectories"; "Committing the interaction raises FUR from 27.5% to 40.6% … the remaining 13.1 points are the Commit gain") | **CONFIRMED** |
| MemSecBench: **310 cases** drawn from **48 realistic contexts** | [arXiv 2607.27080](https://arxiv.org/abs/2607.27080) abstract | **CONFIRMED** |
| AMA-Agent: **57.22%** accuracy on AMA-Bench, +11.16 over the strongest baseline | [arXiv 2602.22769](https://arxiv.org/abs/2602.22769) abstract | **CONFIRMED** |

**Method note worth keeping:** the StreamMemBench numbers are **absent from the
paper's HTML full text** (`arxiv.org/html/2606.14571v1`, 245 KB) and appear only
in the **PDF** results/table text — so a future verifier who greps the HTML will
wrongly conclude the directive fabricated them. Cite the PDF (or record both).

## What this changes

- The directive's three flagged numbers are accurate; its quantitative risk is
  lower than the opaque `turnNNviewNN` citations suggest.
- Still unverified (not in scope of the ask): Agent Zero Memory 95.60/93.60,
  LongMemEval-V2 451/500/115M, BEAM 10M/100/2,000, SWE-Gym 2.4K/11, MemSecBench
  numbers beyond the count, and every `turnNNviewNN` citation. Recommend a
  bounded pass on the landscape-table numbers when the candidate cards are
  written, not now.
- §4 items 1/3 (Phase-B candidate cards; SWE-Gym/SWE-smith version check) can
  proceed; my coverage note bounds item 1's "new" claim.

## Scope and limits

- Primary abstracts + one PDF; no dataset downloaded; "confirmed" = the source
  states the number, not that I reproduced the experiment.
- I did not assess the directive's framing or its §4 priorities (Corvid's call);
  this is the verification half only.
