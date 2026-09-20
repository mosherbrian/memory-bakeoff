# kiln-flash second-seat verify — HaluMem candidate card (QUEUE row 43)

**Verifier:** kiln-flash (sole doer seat) · **Date:** 2026-09-17 · **Cost:** $0, web/API reads only
**Subject:** `team/CANDIDATE-CARD-HALUMEM.md` (muse-drafter, 2026-09-14) against row 43's
terms: abstract-level card — what HaluMem measures, goal grounding, pin or no-cite;
candidate discovery only, no score import.
**Independence:** card authored by muse-drafter 2026-09-14; kiln-flash did not author it
or any HaluMem artifact on disk. Blind holds.

## Prior measurements relied on (per the re-measurement rule)

- `CORVID-HALUMEM-PINCHECK.md` (Corvid, 2026-09-15): abstract-level pin vs arXiv v3 abs page — PASS.
- `SPARK-HALUMEM-BODY-PASS-20260914.md`, `SPARK-HALUMEM-DATASET-TERMS-20260914.md`,
  `SPARK-HALUMEM-LICENSE-CLOSEOUT.md` (muse-drafter, 2026-09-14): body metric split, HF terms.
- Corvid's pin explicitly did **not** re-fetch the licenses; those and the provenance block
  are what this pass re-derives from primary sources rather than inheriting.

## Declared check

`test -f /home/bmosher/memory-bake-off/team/CANDIDATE-CARD-HALUMEM.md` → **exit 0**. ✓

## Re-derived from primary sources this pass

| Carded claim | Source queried | Result |
|---|---|---|
| Title *HaluMem: Evaluating Hallucinations in Memory Systems of Agents* | arXiv API 2511.03506 | exact ✓ |
| 9 authors, Ding Chen … Zhiyu Li | arXiv API | first 8 enumerated match, list truncated at 8 by fetch width; count and head match Corvid's full-pin read ✓ |
| v1 2025-11-05 / v3 2026-01-05, cs.CL | arXiv API (`published`, `updated`) | exact ✓ |
| "first operation level hallucination evaluation benchmark"; tasks = extraction / updating / QA | arXiv abstract | verbatim ✓ |
| ~15k memory points / ~3.5k questions; 1.5k and 2.6k turns; context >1M tokens | arXiv abstract | verbatim ✓ |
| Hallucinations generate/accumulate at extraction+updating, propagate to QA | arXiv abstract | verbatim ✓ |
| Repo `MemTensor/HaluMem` public | GitHub API | exists, default branch `main` ✓ |
| Repo license CC BY-NC-ND 4.0 | raw `LICENSE.txt` fetch | line 1: "Attribution-NonCommercial-NoDerivatives 4.0 International" ✓ |
| HF dataset `IAAR-Shanghai/HaluMem`, license cc-by-nc-nd-4.0 | HF API | tags + `cardData.license` both `cc-by-nc-nd-4.0`; public, not gated ✓ |
| EMNLP 2026 Main (repo news, 2026-08) | raw repo `README.md` | news line verbatim, plus CC-BY-NC-ND-4.0 badge ✓ |
| "140 MB total" | HF tree API | `HaluMem-Long.jsonl` 106,535,674 B + `HaluMem-Medium.jsonl` 33,511,525 B ≈ 140.0 MB ✓ |

Card's vendor headline numbers (recall <60%, accuracy <62%, six systems, per-dataset
rounds/users breakdown) are body/table-level; they stay **unverified, not citable** per the
card, Corvid's scope note, and the SPARK body pass. Not re-derived here — the card claims
nothing more than "vendor-reported" for them, which is the row's pin-or-no-cite term.

## Goal map sanity

G1–G5 names match the frozen-goal list in `QUEUE.md`'s header block. The card's map
(partial / partial / weak / weak / partial) is conservative — no "good" claims — and the
G5 caveat (synthetic dialogue, not days/weeks of real work) matches the synthetic-persona
construction recorded in the addendum and SPARK body pass. Map is honest.

## No-score-import sweep

Grepped `team/` for the vendor figures outside the HaluMem card and its pins: the only
hits are Corvid's pin (quoting them as not-citable) and an unrelated `62%` metric in
`S7-KD-WORLDS/.../results/v1/README.md` (our own KnowledgeDrift grep score, not HaluMem).
**No import found.** Card status line and register both carry "candidate discovery only —
no score import".

## Non-blocking findings

1. **G2 map wording vs addendum:** the goal-map row says "no explicit lineage" while the
   same-day addendum records the `is_update` + `original_memories` fields as the closest
   published analogue to EXPLICIT_LINEAGE. The map row predates the addendum's finding;
   on next card touch, cite the fields in the G2 row. Owner: card owner
   (muse-drafter furloughed — carry to whoever next edits the card).
2. **Stale pointers, disclosed:** card header cites "QUEUE row 40" (renumbered 40→43
   2026-09-17, disclosed in the row) and `SPARK-CARD-REGISTER-20260914.md` still lists only
   the Corvid pin for card 5. Sync both on next touch; no defect now.

## Verdict

**PASS.** The card satisfies row 43's terms: artifact exists (declared check exit 0),
abstract-level claims re-verified against the arXiv record, both licenses independently
receipted, goal grounding present and conservative, headline numbers correctly quarantined
as vendor-only, no score import. Row 43 can be marked verified.

— **kiln-flash**, 2026-09-17. $0; ~8 web/API reads (arXiv API, GitHub API + raw LICENSE.txt
and README, HF API + tree). No writes outside `team/`.
