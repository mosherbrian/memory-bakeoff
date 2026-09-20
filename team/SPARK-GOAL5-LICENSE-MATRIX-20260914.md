# muse-drafter: goal-5 license matrix (spark pulse 2026-09-14)

One-table consolidation of the license facts scattered across ~10 seat notes, so
card owners and Alice do not have to re-read them. **Read-level 2026-09-14, web
reads only; not legal advice.** `$0`. Candidate/benchmark discovery only — no
score import.

## Named 8 (cards)

| Card | Paper | Code | Data | Reuse verdict |
|---|---|---|---|---|
| 1 MemOps | arXiv (per Corvid card) | `MemTensor/MemOps` **MIT** | generated in-repo; no separate corpus → repo terms | **green** (MIT) |
| 2 StreamMemBench | CC BY 4.0 (Alice) | `landian60/StreamMemBench` **MIT** | **EgoLife: S-Lab License 1.0 — non-commercial** (upstream); HF tag says `mit` and is **wrong** | **code green / data non-commercial**; don't trust the HF tag |
| 3 STALE + Supersede | CC BY 4.0 (both) | `Vrin-cloud/supersede` **Apache-2.0** | Supersede pulls LongMemEval knowledge-update **MIT**; train episodes generated | **green** |
| 4 MemSecBench + GateMem | MemSecBench arXiv-nonexclusive; GateMem (2606.18829) | MemSecBench **no artifact**; GateMem `rzhub/GateMem` **MIT** | GateMem HF `Ray368/GateMem` **CC-BY-4.0** | **GateMem green (attribution)**; MemSecBench design-only |
| 5 HaluMem | — | repo **CC BY-NC-ND 4.0** | HF `IAAR-Shanghai/HaluMem` **cc-by-nc-nd-4.0** | **non-commercial, no adapted-set republication** (ND) |
| 6 StateMemBench | arXiv-nonexclusive | **no artifact** (release watch open) | none | **design-only** |
| 7 EvoMemBench | arXiv-nonexclusive | `DSAIL-Memory/EvoMemBench` **no LICENSE** | per-source mirrors (MemoryAgentBench, BFCL v4, CL-Bench, xbench, WebWalkerQA, ALFWorld) — **each own terms** | **all-rights-reserved code**; data per-source |
| 8 LongMemEval-V2 | **CC BY 4.0** | `xiaowu0162/LongMemEval-V2` **Apache-2.0** | HF `xiaowu0162/longmemeval-v2` **Apache-2.0** | **green** |

(EvoArena `2606.13681`, card-8 addendum: no artifact, arXiv-nonexclusive.)

## Fan-out candidates (5)

| Candidate | Paper | Code | Data | Verdict |
|---|---|---|---|---|
| BeliefShift `2603.23848` | arXiv-nonexclusive | none | none | **no artifact** |
| MemoryArena `2602.16313` | arXiv-nonexclusive | `ZexueHe/MemoryArena` **no LICENSE** | HF `ZexueHe/memoryarena` **no license exposed** (was CC-BY-4.0; refuted by Corvid pin + my API re-check 2026-09-15) | **both lanes all-rights pending author statement** |
| CSTM-Bench `2604.21131` | CC BY 4.0 | paper-only | HF `intrinsec-ai/cstm-bench` **MIT** | **green (data)** |
| CodeTracer `2604.11641` | arXiv-nonexclusive | `NJU-LINK/CodeTracer` **MIT** | HF `NJU-LINK/CodeTraceBench` **MIT** | **green (both)** |
| PrecisionMemBench `2605.11325` | **CC BY 4.0** (v3) | `tenurehq/tenure` | `tenurehq/precisionmembench` **MIT** | **green** |

## Load-bearing caveats

- **StreamMemBench data is the one non-commercial surprise**, and its HF tag is
  self-contradicting — trust upstream. Corpus is 512 GB and self-described "data
  cleaning, stay tuned".
- **HaluMem ND** bars *sharing adapted material*: read/measure fine, re-cut
  republication not.
- **Two all-rights code repos** (EvoMemBench, MemoryArena) — do not vendor/adapt;
  MemoryArena's *data* is CC-BY 4.0 so the lane split is inverse of the norm.
- EvoMemBench repo read is **read-level, not clone-verified**; re-check before
  any reuse.
- Several numbers here are single-read; **Alice** is the second seat.

## Paper-license verification — authoritative method + one card conflict

**Method note (load-bearing):** use the **abs-page license href**
(`arxiv.org/licenses/...`) **for the exact version cited** — the HTML-header
"License:" banner reflects the displayed version too, and **licenses can change
between versions** (confirmed: CodeTracer `2604.11641` v1 = `by/4.0`, v3 =
`nonexclusive`). An earlier note in this file called the banner "unreliable"; the
accurate statement is that both signals are version-scoped, so **bind the license
to the pin**. Verified via `https://arxiv.org/abs/<id>` this pass:

| ID | paper license |
|---|---|
| MemOps `2607.12893` | nonexclusive |
| StreamMemBench `2606.14571` | CC BY 4.0 |
| STALE `2605.06527` | CC BY 4.0 |
| Supersede `2606.27472` | CC BY 4.0 |
| MemSecBench `2607.27080` | nonexclusive |
| GateMem `2606.18829` | nonexclusive |
| HaluMem `2511.03506` | nonexclusive |
| StateMemBench `2608.19652` | nonexclusive |
| EvoMemBench `2605.18421` | nonexclusive |
| **LongMemEval-V2 `2605.12493`** | **CC BY 4.0** |
| CSTM-Bench `2604.21131` | **CC BY 4.0** |
| CodeTracer `2604.11641` | nonexclusive |
| MemoryArena `2602.16313` | nonexclusive |
| BeliefShift `2603.23848` | nonexclusive |
| PrecisionMemBench `2605.11325` | CC BY 4.0 |

**Finding:** `CANDIDATE-CARD-CSTM-BENCH.md` line 17 states the paper license is
"arXiv.org perpetual **non-exclusive**"; the abs page resolves to
`licenses/by/4.0/`, i.e. **CC BY 4.0**. Flag for **Alice** (verifier) / card
owner — one-field fix. All other card paper-license fields agree.

## Card provenance audit (ID / date / subjects)

Cross-checked every card's ID, v1 date, and subject class against its abs page
(`arxiv.org/abs/<id>`), including the two new fan-out cards:

- **All 10 cards match** their abs pages on ID, submission date, and subjects —
  e.g. CodeTracer `2604.11641` v1 **2026-04-13**, revised v3 **2026-04-15**,
  cs.SE/cs.AI (card exact); CSTM-Bench `2604.21131` v1 **2026-04-22**, cs.CR
  (card exact); MemOps 14 Jul 2026; StreamMemBench v1 12 Jun 2026; STALE 7 May /
  Supersede 25 Jun; MemSecBench 29 Jul / GateMem 17 Jun; StateMemBench 20 Aug;
  EvoMemBench 18 May; LME-V2 12 May.
- **Only defect is the CSTM paper-license field above.** No date or ID
  misattribution found.

Read-only, `$0`. — muse-drafter (Spark)

## License-version audit (v1 vs latest) — one anomaly

Compared the abs-page license href at `v1` vs the latest version for all 15
goal-5 papers cited in this file:

- **Only `2604.11641` (CodeTracer) differs** — v1 = `by/4.0` (CC BY 4.0), v3 =
  `nonexclusive`.
- **All other 15 are version-stable.** In particular `2604.21131` (CSTM) is
  `by/4.0` at both v1 and latest — so the CSTM card's "non-exclusive" field is
  **simply wrong**, not version drift.

**Rule implication:** version-dependent licensing is **rare but real**, so the
citation rule needs only a narrow clause — *the pin binds the license; re-check
the license for the pinned version* — not a sweeping change. Routed with the
confound proposal to Verity/Corvid.

**Fleet-wide extension (2026-09-15):** repeated the v1-vs-latest license-href
comparison over **all 51 distinct arXiv IDs cited across top-level `team/*.md`**.
**Only `2604.11641` differs**; the other 50 are version-stable. So the defect
class is a single known case fleet-wide, and the narrow pin-binds-license clause
is the right-size fix.

`$0`, read-only (51×2 abs reads). — muse-drafter (Spark)
