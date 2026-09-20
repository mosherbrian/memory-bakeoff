# Muse ideation batch 3 — static-checkable evidence-integrity defect classes

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Authorization:** GiLMore R&D pulse 2026-09-12. Public methodology only; no
project-specific detail on the wire.
**Cost:** one batched call, ~$0.001 (meter read `$1.2040` before and after —
spend not landed at read time, same late-arrival pattern as Q2.3). No block
signals. Receipts:
`implementer/repo-glm-dsh3/scripts/experiment_20260912_muse_ideation/receipts/batch3-*`;
prompt `PROMPT3.txt` (sha `bef4e06a…`); summary sha `a2fdae8e…`.

**Plain English (for Brian):** I asked Muse for *other* evidence-index mistakes
a simple static checker could catch, because the invalidated-pointer checker I
just built covers only one. It named five; I judged three new and worth
building, two already covered. The useful one to build next is dangling-link
detection — the same class as the three bad pointers already found in
`RESULTS.md`, but caught automatically.

## Prompt

> A static checker inspects a research repository's Markdown evidence index for
> one defect class: a benchmark result whose source run was later invalidated is
> still linked as live evidence. Name five OTHER evidence-integrity defect
> classes of the same static-checkable kind, and say which to chase first.

## Muse output (verbatim) and dispositions

| # | Muse item | Verdict | Reason / next step |
|---|---|---|---|
| 3.1 | [H] A live index link points to a result directory that was renamed or deleted and no longer resolves — chase first | **ACCEPT** | Cheapest and already real: the row-12 audit found three bad `RESULTS.md` pointers. Next bounded step: extend `check_invalidated_pointers.py` to resolve every `results/`/`research/` link and flag dangling targets, with a synthetic dead-link self-test. |
| 3.2 | [E] Two index entries reuse the same evidence ID for different run hashes/commits, silently forking provenance | **ACCEPT (proposed)** | New class. Detectable once `run.json` carries per-run hashes (the new provenance schema does); needs an ID→hash cross-index, so not first. |
| 3.3 | [H] The metric quoted in Markdown disagrees with the value in its referenced canonical result file | **DUPLICATE** | Already the executable-numbers guard (`tests/test_preregistration_numbers_are_real.py`; LEDGER 146). The gap is coverage of `RESULTS.md` values, not a missing class. |
| 3.4 | [E] An entry cites a dataset/model version marked superseded or withdrawn while presenting it as current | **ACCEPT (proposed)** | New and cheap once a maintained "superseded identifiers" list exists (e.g. LongMemEval V1→V2, retired model pins). Worth a small list + check. |
| 3.5 | [I] A publishable score claimed without a resolvable canonical record ID plus required provenance fields | **DUPLICATE** | Exactly `provenance_report`/publishability plus the field checklist adopted in the LongMemEval-S audit (`CLAIMS-LEDGER.md` §LongMemEval-S). |

**Tally:** 3 ACCEPT · 2 DUPLICATE · 0 REJECT.

## What I take from it

- **Chase first: 3.1 (dangling links).** It is the same defect family as the
  three bad pointers already found, and it is pure static resolution — no
  schema, no hashes, no new data. This is the next bounded extension to the
  checker I built this pulse-cycle.
- **3.2 and 3.4** are genuinely new static classes but need an index (run
  hashes / superseded-identifier list) before the check can exist.
- **3.3 and 3.5** are already adopted mechanisms; the work is coverage, not
  invention.
- Muse is divergence, not truth: every ACCEPT becomes a *proposed check*, and
  becomes a finding only after it rejects a real bad input through its own
  self-test.

— **Corvid** (`worker-glm-dsh3`). Three of five suggestions were not already in
our record; the first one is the cheapest missing guard.
