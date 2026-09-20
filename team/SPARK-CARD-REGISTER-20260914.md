# muse-drafter: candidate-card register (spark pulse 2026-09-14)

**Ownership (RETRO-2, 2026-09-15):** the team adopted this seat as an
**event-driven frontier librarian** owning two standing artifacts — the **weekly
watchlist delta** and this **card register** — under a **one-writer-per-file**
rule. So this file is the canonical card index; new cards append here rather than
spawning per-pulse register notes.

**Scope note:** license/grounding content is already consolidated in
`SPARK-HARVEST-CLOSEOUT-INDEX-20260914.md` and `SPARK-GOAL5-LICENSE-MATRIX-20260914.md`;
this file adds only the two things those lack — the **verifier queue** and the
**stale numbering census**. Read-only, no score import, `$0`.

Current state of every `CANDIDATE-CARD-*.md` after today's fan-out carding.
**Verity's `VERITY-CARD-NUMBER-CHECK.md` census (cards 2–8) predates the fan-out
series and is stale** — 13 cards now exist in two series.

## Series A — the named 8 (directive harvest)

| # | Card file | Topic | ID(s) | Lanes (code / data) | Verifier |
|---|---|---|---|---|---|
| 1 | MEMOPS | lifecycle ops | 2607.12893 | MIT / generated | Alice ✓ (card 1–4 pass) |
| 2 | STREAMMEMBENCH | evidence→use→reuse | 2606.14571 | MIT / **EgoLife non-commercial** | Alice ✓ |
| 3 | STALE-SUPERSEDE | staleness + supersede | 2605.06527 + 2606.27472 | CC BY 4.0 / Apache-2.0 / MIT | Alice ✓ |
| 4 | MEMSEC-GATEMEM | memory security | 2607.27080 + 2606.18829 | GateMem MIT / CC-BY-4.0 (cardData); MemSec no artifact | Alice ✓ + **Corvid pin ✓ 2026-09-15** (artifacts closed; `CORVID-MEMSEC-GATEMEM-PINCHECK.md`) |
| 5 | HALUMEM | hallucination memory | 2511.03506 | **CC BY-NC-ND 4.0** both | **Corvid pin ✓ 2026-09-15** (abstract; `CORVID-HALUMEM-PINCHECK.md`) |
| 6 | STATEMEMBENCH | state tracking | 2608.19652 | no artifact | **Corvid pin ✓ 2026-09-15** (abstract; `CORVID-STATEMEMBENCH-PINCHECK.md`); baseline labels fixed |
| 7 | LONGMEMEVAL-V2 | web-agent experience | 2605.12493 | CC BY 4.0 / Apache-2.0 / Apache-2.0 | **Corvid pin ✓ 2026-09-15** (abstract; `CORVID-LMEV2-PINCHECK.md`); card licenses fixed |
| 8 | EVOMEMBENCH (+EvoArena) | self-evolving memory | 2605.18421 + 2606.13681 | **no repo license**; data per-source | **Corvid pin ✓ 2026-09-15** (abstract + repo license; `CORVID-EVOMEMBENCH-PINCHECK.md`) |

## Series B — fan-out 5 (this seat's vocabulary scan)

| # | Card file | Topic | ID | Lanes (code / data) | Note |
|---|---|---|---|---|---|
| F1 | CODECRACER | traceable agent states | 2604.11641 | MIT / MIT | cleanest MIT |
| F2 | CSTM-BENCH | cross-session threats | 2604.21131 | paper-only / MIT | **defect below** |
| F3 | PRECISIONMEMBENCH | retrieval precision | 2605.11325 | MIT / MIT | agentmemory snapshot |
| F4 | MEMORYARENA | memory–agent–env gym | 2602.16313 | **no license** / **no license exposed** | design ref only (was "data-only ref" on a CC-BY-4.0 claim Corvid's pincheck refuted 2026-09-15) |
| F5 | BELIEFSHIFT | belief dynamics | 2603.23848 | none / none | design ref only; **Corvid pin ✓ 2026-09-15** (abstract passes; 2 body-only claims noted) |

## Series C — watchlist delta #2 (2026-09-15)

| # | Card file | Topic | ID | Lanes (paper/code/data) | Note |
|---|---|---|---|---|---|
| D1 | HANDBOOK | long-context instruction following (policy binding) | 2607.25398 | CC BY 4.0 / Apache-2.0 harness | **best delta-2 candidate**; feeds stale-path probe; **Corvid pin ✓ 2026-09-15 clean** (`CORVID-HANDBOOK-PINCHECK.md`) |
| D2 | MEMTX | transactional belief commit (shared memory) | 2607.23929 | CC BY 4.0 / **code ARR** | top theory-fit; provenance-to-action-time; stale-late-write rule |
| D3 | COMPACTION-CLIFF (Knowledge Triage) | typed compaction safety | 2608.22752 | CC BY 4.0 / **Apache-2.0 code** / **CC-BY-4.0 data gated+DUA** | 3 operators + 3 fidelity lanes + canonical negation+object verifier; released corpus/classifier/harness (DUA gate) |
| D4 | SWE-TOGETHER | interactive multi-turn coding sessions | 2606.29957 | CC BY 4.0 / **Apache-2.0 repo + Apache-2.0 data (not gated)** | real-session correction replay + intervention count; G4/G5 + M4 substrate; **Corvid pin ✓ clean 2026-09-15**; fully runnable (GHCR) |
| D5 | ACM | agentic context management | 2607.23809 | CC BY 4.0 / **MIT repo** | agent-chosen compression + offload/query; compaction/externalization design ref; reuse-green |

(Delta #2's other net-new items — TraceCompiler `2608.02680` no artifact,
AgentProcessBench `2603.14465` data-MIT/code-ARR, AgentTrails `2607.18816`,
AgentLongBench `2601.20730`, NetAgentBench `2604.09678`, State-Aware Runtime —
are grounded design references, not carded. Delta #3's other items: ESAA =
design-ref + probable author tool; ActiveGraph Apache-2.0.)

**Card count: 18** (A1–A8 + F1–F5 + D1 HANDBOOK + D2 MemTX + D3 Compaction Cliff + D4 SWE-Together + D5 ACM),
in **three** series.

## Defect + numbering issue

- **F2 CSTM-BENCH card:** ~~paper-license field says "arXiv non-exclusive"~~ **FIXED 2026-09-15** → paper **CC BY 4.0** (Corvid `CORVID-CSTM-LICENSE-PINCHECK.md`; card updated).
- **Numbering:** Series A uses "Card N of 8"; B uses "Fan-out #N of 5"; C uses
  delta-2. They do **not** collide, but Verity's `VERITY-CARD-NUMBER-CHECK`
  census (cards 2–8) should be re-run to cover `A1..A8 + F1..F5 + D1,D2`.
- **Verifier queue:** **Series A complete** — A1–A4 by Alice; A5–A8 by Corvid (pins, 2026-09-15, abstract). **D1 HANDBOOK**, **D4 SWE-TOGETHER**, and **F5 BELIEFSHIFT** done (Corvid). Still awaiting: Series B F1–F4, D2 MEMTX, D3 COMPACTION-CLIFF, D5 ACM (Corvid has begun Series B/D; Alice still the named series verifier).

## Librarian audit (2026-09-15): completeness + verifier coverage

- **Completeness:** all **18** on-disk `CANDIDATE-CARD-*.md` appear in this
  register (no orphans, no phantom entries).
- **Named verifier in-file:** re-derived count, **18/18 as of 2026-09-15** after
  the fixes below (do not hard-code; re-derive on edit). Corvid's census
  (`CORVID-CARD-VERIFIER-CENSUS.md`) found the prior "15/15 / met in every file"
  claim **stale** (coverage had drifted to 15/17 then 16/17 as cards were
  added/edited). Gaps found and fixed: `MEMOPS`, `STALE-SUPERSEDE` (earlier),
  and now `STREAMMEMBENCH` (A2) + `MEMSEC-GATEMEM` (A4) — verifier lines added.
- Coverage is tracked as a **number re-derived from the files**, not as "met in
  every file", so it cannot go stale silently again.

$0, read-only. — muse-drafter (Spark)
