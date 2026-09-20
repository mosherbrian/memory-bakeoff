# kiln-flash verify receipt — D-13 intel synthesis, re-verification on cairn's direct chase

**Verifier:** kiln-flash (sole doer seat; D-13's named verifier) · **Date:** 2026-09-17 17:45 PDT · **Cost:** $0, one turn, local reads only
**Subject:** `team/INTEL/SYNTHESIS-2026-09-17.md` (corvid-dsh 16:09) against
`team/INTEL/AGENT_MEMORY_INTEL_2026-09-17.md` (the 2026-09-11→17 backfill), row D-13's terms.
**Independence:** I authored none of the feed (Brian's external pipeline),
the synthesis, or the two cards (corvid). Blind holds.
**Why two receipts:** verification first happened at 16:55 and was receipted as
`team/KILN-D13-VERIFY.md`; cairn's chase and the poller key on the dash-corrected
`KILN-D-13-VERIFY.md`, which did not exist — so this seat re-ran the whole
verification fresh rather than renaming the old file. The 16:55 receipt stands
as the original; this one is today's independent re-run. Same verdict.

## What was re-run and re-derived fresh this turn (17:41–17:45 PDT)

- Declared check `python3 team/tools/check_intel_synthesis.py --max-age-h 0` → **rc 0**
  ("every intel report in team/INTEL/ is answered (1 report(s))").
- `--selftest` → **rc 0**: honest no-card answer accepted; unread report,
  cited-but-missing card, skipped section, missing verdict each rejected by name.
- The owed `Path.home()` fix re-read at source: `TEAM = Path("/home/bmosher/memory-bake-off/team")`
  (check_intel_synthesis.py line 34), absolute on purpose, D-9/D-10 precedent named
  in the comment. The disclosure in the synthesis matches the code.
- **Re-derivation against the feed, not inherited from either prior pass:**
  all five handoff sections present in the report and each dispositioned in the
  synthesis with an explicit verdict (PRIORITY CHANGES 2/2 — KD v2 already
  actioned, delivered-context actioned at rank 11; SYSTEMS 1/1 — Engram Alpha
  carded; BENCHMARKS 3/3 — adebench carded, ForgetEval no-card with a stated
  capability reason; EXPERIMENTS 4/4; RESEARCH LEADS 4/4).
- Faithfulness spot-checks against the report body: the KD v2 ladder
  decomposition (whole-file 71% raw / score 390 at ~404k tokens vs TF-IDF 43%
  raw / score 580), the adebench caveat (author's own golden set, pre-distilled
  facts — method is the contribution, not the winner), Engram's architecture
  list (replaces/conflicts-with edges, tombstones, confidence-aware recall,
  append-only audit), and ForgetEval's shape (1,000+385 cases, supersede/
  release/purge) — all quoted accurately; nothing invented, nothing imported.
- Handle cross-checks re-executed: `BACKLOG-NEXT.md` rank 11 = S7-DOOR with the
  adebench card pointer, "none exists" re-measurement statement, and a runnable
  declared check (corroborated independently by this seat's own S8-5 turn —
  S8-7 was admitted today from exactly that rank at Brian's instruction);
  `next-experiment.json` = the G4 outcome experiment, `proposed-not-built`,
  blocked on Brian's campaign-2 call, displaced by none of the four handles;
  `S7-KD-WORLDS/verdict.json` carries the owner-bias caveat, `declaration.json`
  present (HONEST-CAPABILITY-N/A implemented).
- Cards re-checked on disk: `EXTERNAL-ENGRAM-ALPHA-20260917.md`,
  `EXTERNAL-ADEBENCH-20260917.md` (corvid's, D-6-complete), plus Brian's two
  parallel finds `EXTERNAL-HEIMDALL-20260917.md`,
  `EXTERNAL-AGENT-MEMORY-ATLAS-20260917.md` — no contradiction with the
  synthesis; their implications stay deferred to tomorrow's D-12 per the row's
  own clause (the 16:09 synthesis could not fold 16:07 cards; rank 11 already
  carries the load-bearing one).

## Verdict

**PASS (re-confirmed).** The synthesis discharges D-13: every section answered,
every handle genuinely cross-checked, cards D-6-complete, checker fix real,
nothing imported, the outcome experiment untouched.

Non-blocking, carried for tomorrow's D-12: fold the Heimdall/Atlas implications
(or state no-card reasons), and name body-section systems like ADE Brain in one
line even when dispositioned transitively via a card.

— **kiln-flash**, 2026-09-17 17:45 PDT. $0, one turn. Writes confined to `team/`
(this receipt + the D-13 row stamp).

---

# 2026-09-18 instance — VERIFIED PASS (kiln-flash, 09:34 PDT, clock read at write)

Artifact: `team/INTEL/SYNTHESIS-2026-09-18.md` (corvid-dsh 09:19), feed
`AGENT_MEMORY_INTEL_2026-09-18.md` (07:15, 12,423 chars). Independence holds:
synthesis is corvid's, this verification is kiln's, neither authored the other's
text. Re-measurement note: this is today's fresh read, not a re-run of
yesterday's instance; what differs is the report date and content.

## Checks run fresh this turn

- Declared check `python3 team/tools/check_intel_synthesis.py --max-age-h 0`
  rc 0 ("every intel report in team/INTEL/ is answered (2 report(s))") and
  `--selftest` rc 0 (honest no-card accepted; unread report, cited-but-missing
  card, skipped section, missing verdict each rejected by name).
- Synthesis re-derived against the feed by kiln: header flags
  (priority_change: no, agent_action_recommended: yes), all five handoff
  sections dispositioned with explicit verdicts, the three NONE/no-new findings
  represented faithfully, the removed-source "soul" lead held at the feed's own
  threshold, carry-forwards (KD v2 / adebench / ForgetEval) matched to our
  state (S7-4 verified; rank-11 card + S8-7G verified 08:26; capability-block
  recorded 09-17).
- All four handles re-cross-checked by kiln against `BACKLOG-NEXT.md`
  (grep: zero hits for all four handle names — none is already a backlog
  candidate) and `team/S6-ROADMAP/next-experiment.json` (status
  proposed-not-built, G4 outcome question; nothing in today's feed displaces
  it). Corvid's claim on this duty: exact.
- GOLD-ID-DRIFT "already practiced by design": all four named standing guards
  exist (`check_frozen_id_provenance.py`, `check_map_hashes.py`,
  `check_invalidated_pointers.py`, `check_results_value_pointers.py`); the
  S4-10 invocation-corpus re-freeze by hash is in the record (cell + corvid's
  S4-10 VERIFIED PASS). Claim accurate.
- EVAL-CANARY "partly ours": SUBSTANCE CONFIRMED —
  `check_checker_exit_contracts.py` `_COVERED_NAMES` covers 21 sibling
  evidence-integrity guards and NO sprint-gate `check.py` files, and its
  `uncovered()` scan is scoped to `team/tools/` so it structurally cannot see
  gates living in row artifact dirs. The gap is real.
- S7-3 precedent quoted in the synthesis (0/32 false supersessions, 0/12
  missed updates) matches the verified receipt. Accurate.

## Two corrections (dispositions unaffected; fold in at next use)

1. RANK-AWARE-RETRIEVAL is NOT "measured nowhere". The shared instrument
   computes it: `src/memory_bakeoff/metrics.py` carries per-case
   `reciprocal_rank` and aggregates `mrr`; MRR was actually reported in
   `team/RESEARCH-Q1.2-ISOLATION-RESULT.md` (five recorded metrics incl. MRR)
   and `team/COLDREAD-20260912-scoreboard.md` (R@20/MRR). The honest gap is
   narrower: nDCG exists nowhere, and the S6/S7 sprint capability reports
   chose set-F1/capability families without surfacing MRR. The disposition
   (diagnostic-only backlog line at next re-rank, no card) still stands, but
   its rationale must read "surface and extend existing metrics", not
   "measure ordering for the first time" — otherwise the backlog line would
   re-derive an existing metric (re-measurement-rule violation in the making).
2. The EVAL-CANARY coverage gap is real (confirmed above) but its cited
   provenance is wrong: `team/CORVID-S7-1G-VERIFY.md` contains no coverage-gap
   statement (checked this turn; its subject is the S7-1 gate's selftest
   quality). The gap's first valid record is effectively this synthesis plus
   kiln's confirmation here. Cite that, or re-point to wherever corvid
   actually saw it.

## Non-blocking staleness noted

The synthesis (written 09:19) says S8-7 is "admitted and awaiting its build";
S8-7 was built and closed 09:12 (gate rc 0, artifact `team/S8-DOOR/`, done
cell + board post 09:15). Fleet-state aside only; no feed disposition rests on
it. Corvid will encounter the built artifact as S8-7's verifier in any case.

## Result

Row D-13, 2026-09-18 STANDING instance: VERIFIED PASS — declared check rc 0,
sections and handles dispositioned per the row's terms, cross-checks exact,
no card decision sound; two rationale corrections recorded above for the
next re-rank and any backlog line spawned from this synthesis.

---

# 2026-09-19 instance — VERIFIED PASS (kiln-flash, 12:58 PDT, clock read at write)

Artifact: `team/INTEL/SYNTHESIS-2026-09-19.md` (corvid-dsh 08:46, claimed
08:40 under cairn's morning dispatch), feed
`AGENT_MEMORY_INTEL_2026-09-19.md` (07:15, 8,455 chars on disk / 8,185
fetched — both figures in the synthesis match the bytes). Independence
holds: synthesis is corvid's, this verification is kiln's. Routed by cairn
direct because the chain-verdict did not fire on the 09-17 claim stamp
leading the cell (same class as the 09-18 instance's stale replay).

## Checks run fresh this turn

- Declared check `python3 team/tools/check_intel_synthesis.py --max-age-h 0`
  rc 0 ("every intel report in team/INTEL/ is answered (3 report(s))") and
  `--selftest` rc 0 (honest no-card accepted; unread report,
  cited-but-missing card, skipped section, missing verdict each rejected by
  name).
- Synthesis re-derived against the feed by kiln: header flags quoted exactly
  (priority_change: no, agent_action_recommended: no, NO_ACTION_REQUIRED
  explicit — a declared-quiet day); all five handoff sections say NONE and
  all five are dispositioned with explicit verdicts; the feed's strict-window
  refusals (CogniCore Sep-14 material not reclassified; MemAware/canary/
  auditability held as watchlist calibration; removed-source rule) are
  represented faithfully, including the Executive Signal's two surviving
  directions mapped to work actually in flight (mutation/control-plane →
  S11-3, gate verified and build released today; delivered-context →
  S8-DOOR + S9-RANK-DIAG, both VERIFIED PASS 09-18).
- All five handles re-cross-checked by kiln (re-ran the greps, did not
  inherit corvid's): CogniCore, MemAware, IMPLICIT-RELEVANCE,
  RUNTIME-CANARY, HISTORICAL-RECONSTRUCTION — **zero hits in
  `BACKLOG-NEXT.md` and `team/S6-ROADMAP/next-experiment.json`**
  (verified). `next-experiment.json` re-read: proposed-not-built, the G4
  outcome question, undisplaced by anything in today's feed; the feed's own
  bottom line ("no change to current research priorities") matches the board.
- Spot-checks against the record: `S9-EVAL-CANARY` exists with
  `guards.json` = 28 guards and `covered_gates.json` = 17 entries (the
  "driver now covers 17 sprint gates" line is exact); `S10-BM25-ABSTAIN2`
  artifacts on disk (second abstention mechanism refuted); BACKLOG rank 18
  carries the results-tree-canon line with the "8 of the 21" wording the
  synthesis quotes; S11-1 and S11-2 BUILD rows both lead
  `verified: corvid-dsh 2026-09-18 17:59 — VERIFIED PASS`, so the bottom
  line's "S11-1 and S11-2 verified" is accurate (the gates 09-18 17:07/17:03,
  the builds 17:59); the S11-3 corpus's declared distractor shape is the
  agentmemory 92.9% shape (this seat wrote that declaration this morning).

## Two corrections (dispositions unaffected; record for next use)

1. The synthesis's recorded grep claim "zero hits for CogniCore, MemAware,
   implicit, reconstruction, and time-travel across the backlog, the queue,
   and the frozen next-experiment" is FALSE for the queue as a raw grep:
   `QUEUE.md` line 560 — this D-13 row's own standing text — contains
   CogniCore ×2 and MemAware ×2 (it quotes the feed it exists to process).
   The zero-hit claim is TRUE for the backlog and next-experiment (re-verified
   this turn), and the material conclusion holds: neither name is a backlog
   candidate, no row was admitted under either, no card was warranted. The
   line should have scoped the queue grep to admitted-row task cells, or
   dropped the queue from the list.
2. "the LSA arms … are the only arms that gain on oblique phrasing, 3/10"
   overstates the S10-KD-CROSS by-phrasing cells: the two LSA arms
   (dense_lsa, claude_mem_chroma_lsa) do hold the TOP oblique score (0.3 each,
   lexical 0.4, crossed 0.0 everywhere — those parts exact), but they are not
   the only arms with nonzero oblique retrieval: bm25 0.1 and hybrid_rrf 0.2.
   Precise form: "the only arms above 2/10 on oblique". The disposition
   resting on the cell (implicit relevance PARTLY INSTRUMENTED; a dedicated
   corpus would extend, not start) is unaffected.

## Result

Row D-13, 2026-09-19 STANDING instance: VERIFIED PASS — declared check rc 0,
all five sections dispositioned on a feed that itself says NO_ACTION_REQUIRED,
no-card decision sound (nothing qualifies under the feed's own threshold and
our evidence standards), frozen G4 outcome experiment undisplaced; two
numeric/scoping imprecisions recorded above, neither load-bearing.

— kiln-flash, 2026-09-19 12:58 PDT. $0, one turn, local reads only. Writes
confined to team/ (this receipt + the D-13 row stamp).
