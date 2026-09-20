# Kiln R&D pulse — second-driver re-derivation: Claude-Mem window ablation (2026-09-13)

The last of the big inherited findings without a second-driver receipt
(after agentmemory 92.9% and the Gen38 anchors): the Claude-Mem window
ablation, a reset-plan evidence anchor ("configuration-scoped finding").
Read-only, $0.

## Claim under test (RESULTS.md row: "default 90-day window Hit@5 0.208;
window disabled 0.583")

Recounted from the cited artifacts
(`results/claude_mem_compare_core`, `results/claude_mem_compare_stress450`,
run.json per provider):

| Variant | core slice | stress450 slice |
|---|---|---|
| `claude_mem_chroma_lsa` (default 90-day recency window) | **0.2083** | **0.2083** |
| `claude_mem_chroma_lsa_no_recency` (window disabled) | **0.9583** | **0.5833** |

- The 0.208 reproduces exactly on BOTH slices.
- The 0.583 reproduces exactly on the stress450 slice.
- The 90-day default is explicit in the adapter
  (`claude_mem_core.py`: `RECENCY_WINDOW_DAYS = 90`, clock injected for
  reproducibility) and the findings doc carries the mechanism
  (only 9 of 50 core memories fall inside the window).

## One imprecision found (understatement, not error)

The RESULTS.md row's single contrast pair ("0.208 → 0.583") quotes the
stress450 disabled-window value; on the CORE slice the disabled window
scores **0.958** — the ablation effect is ~4.6× on core, larger than the
row implies. The findings doc (`research/CLAUDE_MEM_FINDINGS.md` line 45)
carries both values correctly. Suggested (owner's call, historical row):
either quote both disabled values or point the row at the findings table.

Verdict: **verifies**, direction and mechanism; one compression noted.

— Kiln, R&D pulse 2026-09-13, ~15 min, $0.

## Addendum (same day): the fts5_core 0.0 anomaly, closed

`claude_mem_fts5_core` scored 0.0 on both slices (noticed during the
window recount). Mechanically confirmed, not new: the findings doc
(line 53–55) explains the adapter wraps the entire natural-language query
as ONE quoted FTS5 phrase — no benchmark document contains it verbatim;
my probe adds the delivered-level fact that all 26 detail rows returned
zero items. Accurate measurement of a brittle product path; the
RESULTS.md row correctly quotes only the semantic path.
