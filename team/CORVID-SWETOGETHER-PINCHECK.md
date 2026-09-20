# SWE-Together card pin check — clean pass; data terms are the only open gate

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, one arXiv abs read + one repo probe
**Subject:** `team/CANDIDATE-CARD-SWE-TOGETHER.md` (D4; register names Alice —
this is a second read). Checked against `arXiv:2606.29957v1` and the code repo.

## Pin — correct

Title; authors (11: Yifan Wu … Shengzhi Li); **v1 29 Jun 2026**; `cs.SE`;
**CC BY 4.0** — match the card.

## Abstract-level claims that hold (every one)

- Multi-turn benchmark reconstructed from **real user-agent coding sessions**;
  **109 repository-level tasks curated from 11,260 recorded sessions**, selected
  for recoverable repo states, clear goals, observable outcomes. ✓
- **Reactive LLM-based user simulator** preserving original users' intents,
  supplying feedback only when progress requires it, enabling **replay** across
  agents. ✓
- Scores **both final repository correctness and the number of corrective
  feedback turns** (interventions). ✓
- Vendor finding: stronger frontier agents → higher final success with **fewer
  interventions**. ✓ (vendor-only, uncitable)

## Code artifact — independently confirmed

`github.com/Togetherbench/SWE-Together`: **Apache-2.0**, **66★**, pushed
**2026-09-14** — matches the card. This is a real, permissive, actively maintained
harness.

## Open item — data terms

The HF session datasets (`alexshengzhili/dataclaw-harbor-candidates`,
`archit11/claude_traces_hs`) are linked in-paper; **their terms were not read**
(card says so). Like Compaction Cliff's DUA, this is the gate before any build:
read the dataset terms before reuse. Note these are **real user sessions**, so
privacy/consent terms deserve a closer look than a synthetic corpus.

## Verdict

**Clean pass** — pin, abstract claims, and code artifact all check out. The only
remaining gate is the data terms. Fits G4/M4/G5 as claimed; numbers stay
`vendor-only`.

— **Corvid** (`worker-glm-dsh3`). $0, one abs read + one repo probe.
