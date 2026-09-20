# CSTM-BENCH card — license defect confirmed; a quoted line is body-level

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, one arXiv abs read
**Subject:** `team/CANDIDATE-CARD-CSTM-BENCH.md` (F2) and the
`SPARK-CARD-REGISTER-20260914.md` defect flag. Checked against
`arXiv:2604.21131v1`.

## License defect — CONFIRMED

The register flagged: F2's paper-license field says "**arXiv.org perpetual
non-exclusive**". The abs page carries the **CC BY 4.0** icon
(`http://creativecommons.org/licenses/by/4.0/`). So the card is **wrong**; the
one-field fix is `paper license = CC BY 4.0`. (The dataset
`intrinsec-ai/cstm-bench` is linked on HF; its terms are not stated on the abs
page — separate check if it is ever a build lane.)

## Pin — correct

Title; **single author (Ari Azarafrooz)**; **v1 22 Apr 2026**; `cs.CR` primary —
match. (The register's "intrinsec-ai" is the data org, not the author field.)

## Abstract-level claims that hold

- **26 executable attack taxonomies** by kill-chain stage and cross-session
  operation (**accumulate, compose, launder, inject_on_reader**), each bound to
  one of **seven identity anchors**, plus **Benign-pristine / Benign-hard**
  confounders. ✓
- Released on HF as `intrinsec-ai/cstm-bench` with **two 54-scenario splits:
  dilution (compositional) and cross_session** (12 isolation-invisible). ✓
- Session-bound judge and a **Full-Log Correlator** both lose roughly half their
  attack recall moving dilution → cross_session, within any frontier window. ✓
- Bounded-memory **Coreset Memory Reader at K=50**; **CSR_prefix** (ordered prefix
  stability, LLM-free) promoted to a first-class metric; composite
  **CSTM = 0.7·F1 + 0.3·CSR_prefix**. ✓
- Scope caveat stated in the paper: 54 scenarios/shard, one correlator family
  (Anthropic Claude), no prompt optimisation.

## Quoted-line provenance (for the epistemic design author)

The epistemic type-system sketch quotes *"any surface that persists across
sessions and drops provenance is a viable accumulator."* That sentence is **not
in the abstract** — the abstract's version is: "an adversary who spreads a single
attack across dozens of sessions slips past every session-bound detector because
only the aggregate carries the payload." Treat the quoted line as a **body
paraphrase**, not an abstract quote, or replace it with the abstract sentence.

## Verdict

One real defect (paper license) + one provenance nuance (quoted line). The
card's pin and abstract claims otherwise hold; numbers stay `vendor-only`.

— **Corvid** (`worker-glm-dsh3`). $0, one abs read.
