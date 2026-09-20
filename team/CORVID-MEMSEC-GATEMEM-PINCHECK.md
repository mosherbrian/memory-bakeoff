# MemSecBench + GateMem card pin check — both pins pass; GateMem artifacts verified

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, two abs reads + two host probes
**Subject:** `team/CANDIDATE-CARD-MEMSEC-GATEMEM.md` (A4) — its provenance table
says artifacts are "abstract only this pass; repo/license to verify", and the
card is one of two still lacking an in-file verifier line
(`CORVID-CARD-VERIFIER-CENSUS.md`). Checked against both abs pages.

## Pins — correct

| | MemSecBench | GateMem |
|---|---|---|
| title / authors | ✓ (Xuanze Chen … Qi Xuan, 6) | ✓ (Zhe Ren … Shuicheng Yan, 10) |
| id / date / subject | `2607.27080`, v1 **29 Jul 2026**, cs.CR | `2606.18829`, v1 **17 Jun 2026**, cs.LG |

## Abstract-level claims that hold (exact)

**MemSecBench:** 310 cases from 48 contexts; controlled **Write–Execute–Forget**
protocol; **24-configuration matrix** (2 harnesses × 4 memory × 3 LLM backends);
adjudication over **seven lifecycle checkpoints**; malicious memory persists in
**84.2%**, full chain succeeds **50.3%**, **59.6%** complete Execute, **56.1%**
selective repair; largest spread **16.1 pp** end-to-end and **41.3 pp** on
repair. ✓ (all `vendor-only`, uncitable)

**GateMem:** multi-principal shared memory across **medical / office / education /
household**; jointly evaluates utility, **access control across authorization
boundaries**, and **active forgetting**; long multi-party episodes, **hidden
checkpoints**, **leak-target annotations**; "no method simultaneously achieves"
all three; long-context best governance at high token cost. ✓

## Artifacts — the card's open "to verify" item, now closed

- Code `github.com/rzhub/GateMem`: **MIT, 142★** (GitHub API). ✓
- Data HF `Ray368/GateMem`: **`cc-by-4.0`** in `cardData` (the top-level
  `license` field reads `null`, so the license lives in the dataset card — a
  metadata nuance worth knowing for license checks; unlike MemoryArena, where
  neither field carries a license).
- MemSecBench: card says abstract-only / no artifact; the register row agrees
  ("MemSec no artifact").

## Effect

The card's provenance row can change from "repo/license to verify" to
**"GateMem MIT code / CC-BY-4.0 data (cardData); MemSecBench no artifact"**, and
the owner can add `Verifier: Corvid (abstract pin ✓ 2026-09-15, this file)` —
leaving only **STREAMMEMBENCH** without a verifier line. Numbers stay
`vendor-only`.

## Fold status (2026-09-15, re-checked)

The sibling license fixes from `CORVID-LICENSE-D-VS-H.md` have landed and credit
this seat: CSTM paper → CC BY 4.0; MemoryArena data → "no license exposed";
LME-V2 code → Apache-2.0. **This card's provenance row is the one still unfilled**
— it reads "abstract only this pass; repo/license to verify" and the tail still
says "both licenses remain to verify". Ready-to-paste replacement for the
Artifacts cell:

> GateMem code `rzhub/GateMem` — **MIT** (GitHub API, 142★); GateMem data
> `Ray368/GateMem` — **CC-BY-4.0 in `cardData`** (top-level field null);
> MemSecBench — no artifact found. Corvid pin 2026-09-15.

— **Corvid** (`worker-glm-dsh3`). $0, two abs reads + two host probes.
