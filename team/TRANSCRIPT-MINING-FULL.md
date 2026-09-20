# TRANSCRIPT-MINING — full corpus, closed sessions (consolidated 2026-09-13)

Brian approved the scale-up with the closed-sessions rule. Executed and
iterated same-day: the pipeline gained a scheduler-template detector, a
personal-context pre-filter, a pasted-output label, and cross-file
dedupe — each driven by a measured precision finding. **All transcript-
derived content stays local** at
`~/.local/share/memory-bakeoff/transcript-mining/full-20260913/`
(correction-events.jsonl, durable-facts.jsonl, both digests, stats.json).
This note carries aggregates only. Pipeline code + synthetic-fixture
tests committed in this lane (18 self-tests). Intermediate iteration
states are in the RD-THREADS log; this consolidated version supersedes
the earlier append-style history.

## Final corpus numbers (dedupe-corrected)

| | |
|---|---|
| Files scanned (closed sessions; 60-min mtime rule) | 1,250 (6 open files excluded, incl. the live driver session) |
| Operator turns extracted | 4,353 |
| Continuation-copy duplicates removed | 255 (session continuation files COPY prior turns) |
| **Unique operator turns** | **4,098** |
| Personal-life turns excluded (never persisted) | 230 |

(The scanned+excluded total is 1,256; the dispatch's 1,242 was the count
at planning time. The mtime rule, not the count, is the binding
constraint. Project coverage: 12 of 13 dirs contributed turns; the
claude-mem-observer dir's 573 turns are pipeline records (the condense
macro), correctly excluded.)

## Deliverable 1 — correction-event corpus (labeled, one per event)

**270 per-event correction events** (env-fact-correction 169, negation
61, actually 21, wrong 9, i_said 10) **+ 26 repeated-instruction groups**
(240 events). Per-class precision (local eyeball): negation and i_said
~100%, actually ~80%, env_fact_correction ~30–50%, wrong ~20–40% — the
pasted-output class is LABELED (`pasted_output: true`), not dropped.

Integrity corrections applied during the pass (each test-locked now):
- A scheduled 17:00 clawdbot prompt (Brian's daily TurboQuant-upstream
  check) masqueraded as 44 corrections — scheduler-template detection
  reclassified it.
- Session-continuation file copies inflated counts ~34% — cross-file
  dedupe fixed it (dedupe by timestamp + normalized text, first
  occurrence kept).

## Deliverable 2 — durable-fact candidates (vault longlist)

**324 candidates** (env_fact 311, convention 13) after the
personal-context pre-filter (230 personal turns excluded, excerpts never
persisted) and tightened class definitions (convention requires
message-initial always/never or explicit decision structures; env_fact
requires environment anchors — absolute paths, ENV=, localhost/private
hosts, pinned-at). A curation digest (deduplicated → 318 unique groups,
ranked by cross-session strength) sits alongside.

**These are a LONGLIST for Brian's per-record curation** — the
precision pass found personal-adjacent noise in the unfiltered set
(house-hunting, school-board content); no vault write without Brian's
per-record selection, and any automated classification pass must stay
local for the same reason.

## Deliverable 3 — stats

`stats.json` (per-project breakdown, exclusion accounting, dedupe
accounting) plus both digests in the same local dir. Verified consistent
across stdout, stats.json, and the corpus files after a write-omission
regression was caught and fixed with a test.

## Serving notes

- Raw counts differ between runs only via the closed-sessions mtime rule
  (new sessions close and enter the corpus) and the dedupe/filter
  improvements above — never via retuning after seeing outcomes.
- The corrections side precision bands are separate from and stronger
  than the facts side; both are local-eyeball estimates on samples
  (n≈5–8 per class), not exhaustive audits.

## Next decision (Brian's)

1. Read the 324-candidate digest (local) and mark vault-worthy records —
   or delegate curation criteria.
2. Decide whether a model-assisted second pass runs (anonymized or
   local-only terms) for the correction corpus's subtle classes and the
   fact candidates' semantic filtering.

— Kiln, consolidated 2026-09-13 (day's slice total ~4h across mining
turns, $0, all local).
