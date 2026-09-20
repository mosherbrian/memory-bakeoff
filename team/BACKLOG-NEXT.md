# BACKLOG-NEXT — the next sprint's candidates, ranked

Maintained by corvid-dsh under QUEUE row D-8 (verifier: kiln-flash). First
written 2026-09-17; revised 2026-09-18 at 10:42, 12:4x, 16:1x, and **13:5x
PDT 2026-09-19 (this revision, on the conductor's commission: sprint 11
closed with every candidate finished or non-discriminating — prune what the
board finished, re-check every blocker, add what the research needs)**. The
ranking standard is no longer this seat's judgement of worth: it is the
planner's own open questions in `team/ANSWER.md` (the planner's 13:44 PDT
post-sprint-11 update, re-read in full this revision). A candidate
earns a rank by moving one of those questions' named next discriminating
steps. A candidate becomes a QUEUE row via the self-organization rule (row
written, second seat named verifier, cost cap stated), not by being on this
list.

Placed on the map, as the ceremony requires: this backlog serves Brian's
mission (MISSION-20260912.md), the program mission (team/MISSION.md), and the
recovered PHASE2_ROADMAP.md; every candidate names the frozen goal G1-G5
(frozen in team/EXTERNAL-CORPORA-RECOMMENDATION.md §1) or roadmap item it
advances, or says plainly that it advances neither and why it is still worth a
slot. Ranked by: value to the mission, then readiness, then cost — a strict
total order. **Startable means a seat could begin it today with what is on
this machine**; candidates blocked on Brian, on hardware, or on a date are in
their own section below and are deliberately NOT ranked.

**Rank numbers are non-contiguous by design; every number 1-15 is now
burned.** Admitted QUEUE cells cite their source rank permanently and the
duplicate detector reads those citations. Live census at this revision (grep
over team/QUEUE.md): every rank 1-15 appears in at least one admitted cell —
13, 14 and 15 are cited by the S11-1/S11-2/S11-3 admissions of 09-18/09-19
and joined the burned set at this revision. Ranks 16-20 below have never been
admitted and are uncited (verified by census before the renumbering below);
the old ranks 16/17/18 were RENUMBERED to 18/19/20 in this revision — no cell
cites any of the three numbers, so the renumbering cannot trip the detector,
and the change log records it.

Sweep sources for this revision (read 2026-09-19 13:4x-13:5x PDT):
team/ANSWER.md 2026-09-19 version — all six questions re-read after the
planner folded today's three verdict files; its Q4 next step ("Compare native
pi-lcm with the existing thin layer on the unchanged broader corpus,
pre-registering false-supersession reduction and missed-update limits") and
Q2 next step ("Pre-register a different relevance decision, with held-out
cases and both rejection and retrieval-loss criteria") are quoted into ranks
16 and 17, and its DECISION-READY line ("Reopen the state-layer comparison:
an observed native failure now justifies testing protection") is the
conductor's "missing strongest comparison", now ranked; the three S11 board
cells and this seat's verification receipts (S11-1/S11-2 VERIFIED PASS 17:59
09-18, S11-3 VERIFIED PASS 09:15 today — receipt
team/CORVID-S11-3-VERIFY.md, incl. the 46-trial replay on the real pinned
store); team/RD-THREADS.md head (the three corvid threads — all three still
open, unchanged); team/S6-ROADMAP/next-experiment.json (unchanged,
proposed-not-built, Brian-gated); EXTERNAL-CORPORA-RECOMMENDATION.md Rev 2
(Alice's A1-A4 co-sign UNCONDITIONAL — re-read for the SWE-chat re-check);
a live df this revision (111 GB free at 85% — the SWE-chat disk half has cleared);
an HF-credential sweep (env, ~/.cache/huggingface, token paths: none — the
SWE-chat access half now names the precise remaining blocker);
team/OPS-PI-LCM-TWO-ROLES-20260918.md (the two-hats rule carries to rank 16);
~/.config/agent-deck/go-budget's recorded caveat (unchanged); and the
conductor's dispatch text quoting the planner's own reason.

## The startable candidates

| Rank | Candidate | Artifact | Check | Advances | Prior measurement |
|---|---|---|---|---|---|
| 16 | State-layer protection against the observed native failure — the answer page's Q4 named next step, and the planner's DECISION-READY line makes it the reopened comparison: "an observed native failure now justifies testing protection". On the UNCHANGED frozen broader corpus (`team/S10-PI-LCM-HIST/trials.jsonl`, sha `52289107…367b1d`, generator re-executed byte-identically at verification), run the EXISTING tested thin layer (`team/S7-STATELAYER/thin_layer.py`: key = (scope, fact_type), decide = key equality — both fields present per write in the frozen trials) beside the native arm, under a declaration written before any receipt that pre-registers BOTH limits the answer names: the false-supersession reduction required to count as protection AND the missed-update allowance required to count as safe (the S7-3 rule's m=0.5 / k=0.1 are the prior's values; the builder declares them fresh or redeclares them explicitly, before the run, and reports the sensitivity grid as data). Both sides counted the same way, controls at both ends, old-beside-new in verdict.json: native on the controlled corpus 0/32 with 12/12 updates (S7-STATELAYER), native on the broader corpus 22/33 with 0/13 missed (S10-PI-LCM-HIST), layer on the broader corpus = this row's result. Either number decides: protection that holds reopens the state-layer question with evidence; protection that fails (the layer's key-equality rule never marks a cross-key distractor, but the trials' distractor writes carry the ORIGINAL's declared key — the honest prediction is the builder's to pre-register, not this list's) closes the trivial-layer class on this failure shape. REPORTING RULE (two hats, per team/OPS-PI-LCM-TWO-ROLES-20260918.md): pi-lcm the bake-off MEMORY contestant — it does not touch pi-lcm's separate role as Brian's stack compaction layer, which no retrieval or supersession number measures. Depends on none — $0, local, no LLM; reuses the frozen corpus and the S7-3 layer and harness. | /home/bmosher/memory-bake-off/team/S11-LAYER-HIST | python3 /home/bmosher/memory-bake-off/team/S11-LAYER-HIST/check.py --selftest | G2 supersession; R-PF / Decision Gate F — the reopened state-layer comparison, DECISION-READY per the answer page | team/S10-PI-LCM-HIST/verdict.json (native 22/33 false supersession, 0/13 missed — VERIFIED PASS 09:15 today, replay-proven) and team/S7-STATELAYER/verdict.json (layer on the controlled corpus 0/32, 12/12; rule m 0.5, k 0.1) — this candidate measures the tested layer on the corpus where the native fails and must report old-vs-new |
| 17 | BM25 abstention, third declared relevance decision with held-out cases — the answer page's Q2 named next step after two refutations: the stopword filter rejected 0/5 and cost a retrieval; the declared margin rule rejected 2/5 and cost a retrieval; none of its three tested thresholds achieved rejection without loss. Pre-register a relevance decision from a DIFFERENT family than both refuted mechanisms — not a token filter (no token is removed), not a score-margin rule (no score distribution is read); the declared candidate shape is a corpus-coverage rule (abstain when the query's content tokens lack declared document-frequency support in the case corpus), exact rule and threshold grid fixed in declaration.json BEFORE any run, grid reported as data, never picked post-run. Add the held-out half the answer demands: a second case set generated by a pinned mechanical generator, frozen before the rule is declared, unread at declaration time (the declaration is written against the original ten cases only), and reported SEPARATELY — declaration set beside holdout set — so a survival or a refutation is not a ten-case artifact. BOTH sides measured on both sets: irrelevant queries rejected AND useful retrievals lost. Depends on none — $0, local, no LLM; the S7-1 harness (declare-then-run, sha-bound rows) is reused. | /home/bmosher/memory-bake-off/team/S11-ABSTAIN3 | python3 /home/bmosher/memory-bake-off/team/S11-ABSTAIN3/check.py --selftest | G3 invocation (abstention is the invocation-quality half every instrument shows at zero); roadmap R-PE measurement honesty | team/S7-BM25-PREFILTER/verdict.json (0/5 rejected, retrievals 5/5 → 4/5), team/S10-BM25-ABSTAIN2/verdict.json (margin: 2/5 rejected, 1 useful lost; grid 0.5 → 0/0, 1.0 → 2/1, 1.5 → 5/2), team/S6-SELECTIVITY/results.jsonl (bm25 0/5 abstain, 5/5 retrieve) — this candidate pre-registers a third family and must report both sides on the declaration set AND the holdout set |
| 18 | Provenance chase on the three open corvid threads in team/RD-THREADS.md: Habitus class-label inconsistency on frozen runs (re-checked this revision: the dsh3 worktree fix is verified, canonical implementer/repo still carries the defect pending the implementer-of-record applying `fix-habitus-adapter.diff`), LongMemEval-S upstream claim audit (three benchmark variants circulate), Hindsight retracted-figure live pointer defect (94.6 confirmed vendor-benchmark, not in the ACL paper). One receipt per thread naming what the defect does or does not touch in the protected findings, plus a guard update where a checker applies (check_longmemeval_qualifiers.py exists for one). $0, local reads. DEFERRAL HISTORY, said aloud: kept out of sprint 9 for capacity, declined at the sprint-10 close as non-discriminating, deferred again at the sprint-12 opening in the planner's own words ("protect reporting and infrastructure rather than discriminate") — the deferral is now explicit and repeated; it protects findings already claimed from silent drift, which is why it stays ranked at all. | /home/bmosher/memory-bake-off/team/S10-PROVENANCE-CHASE | test -f /home/bmosher/memory-bake-off/team/S10-PROVENANCE-CHASE/receipt.md | advances neither a frozen goal directly — it protects findings already claimed from silent drift; R-PB no-score-import discipline is what the audit serves | team/RD-THREADS.md head names all three as open defects and no chase receipt exists for any — stated per the re-measurement rule |
| 19 | Run-spread honesty: adopt the standing rule the ATLAS card names — every headline number produced from a single run is marked as single-run wherever the portfolio states it, and the portfolio's summary pages (RESULTS.md, STATUS_AND_FINDINGS.md, and the team/ read-first documents carrying headline numbers, protected findings included) are swept so existing single-run headlines carry the mark retroactively. Bounded sweep, declared page list in the row; $0, local, own docs only. Planner declined this once (sprint-10 close) and deferred it again at the sprint-12 opening as reporting rather than discriminating; it stays ranked because a one-run number read as a distribution is a reporting-integrity defect that will otherwise be discovered during the campaign. | /home/bmosher/memory-bake-off/team/S10-SINGLE-RUN-MARKS | python3 /home/bmosher/memory-bake-off/team/S10-SINGLE-RUN-MARKS/check.py | advances neither a frozen goal nor a roadmap item directly — measurement-honesty hygiene beside R-PH | the ATLAS card names the rule and it is not adopted anywhere: no marking convention exists in the portfolio's summary pages — stated per the re-measurement rule |
| 20 | Results-tree canon: this machine holds the results evidence TWICE (`~/pilot-gen45/results` 318M/236 entries, `~/memory-bake-off/implementer/repo/results` 147M/237) and the guards see NEITHER — they resolve `results/<dir>` against `team/`, where it does not exist, so 8 of the 21 live guard failures are one missing pointer. Independent re-verification (diff -rq rerun, sha256 spot-checks) found ZERO content differences between the trees; pilot-gen45 is fuller only in raw per-run capture (49 files), the repo tree alone carries `p2_entry_20260913`. RULING (receipt team/CORVID-RESULTS-TREE-CANON-20260918.md): `implementer/repo/results` is canonical (repo lineage, referenced by the roadmap symlink, sole home of p2_entry_20260913); reconcile ADD-ONLY — rsync --ignore-existing the 49 raw-capture files into it — prove the union (two-tree diff empty) and the archive untouched (before/after hash manifest), never move or delete from pilot-gen45, then wire `team/results` → `../implementer/repo/results` (relative symlink) and re-run the S10-3 declared check expecting the 8 missing-prerequisite failures to clear. Depends on none — $0, local, no LLM; disk needs ~171 MB of the 111 GB now free. | /home/bmosher/memory-bake-off/team/S11-RESULTS-CANON | python3 /home/bmosher/memory-bake-off/team/S11-RESULTS-CANON/check.py | advances neither a frozen goal nor a roadmap item directly — it re-attaches the evidence base the guard set already requires; the provenance release gate ("source provenance is a release gate") is what it serves, and it unblocks 8 of the 21 canary failures | team/OPS-RESULTS-TREE-20260918.md (cairn's evidence) independently re-verified by this seat — receipt team/CORVID-RESULTS-TREE-CANON-20260918.md records the ruling and the numbers; no artifact exists yet — stated per the re-measurement rule |

## Local outcome pilot — scope resolved; not selected

**CORRECTED 2026-09-19 by Tern on Brian's explicit answers:** the blanket
"campaign-2 window/scope call" blocker is false for the local first rung.
The four questions in `SPEC-OUTCOME-PROTOCOL.md` §10 are answered in
`OUTCOME-FIRST-RUNG-SCOPE-20260919.md`: fleet/cairn, Design A memory on/off,
two unscored plumbing pairs then eight scored pairs (20 task executions),
local-only with no private transcripts and $0 incremental API spend. Tern
owns numeric per-run token/time limits and the scoped preregistration;
one to two days of instrumentation is an estimate. This is authorized scope,
not a completed design or run. The random-60 index review comes first;
the pilot is NOT selected into a sprint and no runs start from this correction.

The serving model and treatment must be declared, and the preregistered
evidence-use check from `CANDIDATE-CARD-ALTK-EVOLVE.md` remains required.
Every outcome is model-conditional. Arm isolation, outcome instrumentation,
and stopping rules remain fleet-owned preparation, not unanswered Brian decisions.

## Blocked or deferred — named, not ranked (see dated corrections within entries)

- **Private-transcript outcome scale-up — explicitly deferred, not authorized.**
  Brian answered "NOT YET" on 2026-09-19; see
  `OUTCOME-FIRST-RUNG-SCOPE-20260919.md`. This restriction applies to the
  private-data scale-up, not the local pilot above. A later private-work
  campaign still needs its own data authorization and applicable budget/window.
  Do not present this explicit deferral as an unanswered immediate request,
  or use it to block the non-private first rung.
- **SWE-chat acquisition** — blocker RE-CHECKED this revision with live
  measurements, and it has materially moved: a live df at 13:5x reads
  **111 GB free at 85%** — the disk half has CLEARED (the 39.3 GB full-set
  projection now fits with headroom; it was 17 GB free at 98% yesterday
  afternoon). The A1-A3 co-sign conditions are DISCHARGED: Alice's Rev-2
  co-sign is unconditional (EXTERNAL-CORPORA-RECOMMENDATION.md, Rev 2,
  2026-09-13). REMAINING BLOCKER, named precisely: the dataset is
  `gated: "auto"` on HuggingFace and this machine holds no HF account or
  token (env, `~/.cache/huggingface`, and token paths checked this revision)
  — one authenticated access request must be made before any byte can move.
  CORRECTED AND UNBLOCKED 2026-09-19 14:4x. Two things in the paragraph above
  are false, and the second explains the first. There IS a token at
  `~/.cache/huggingface/token`; `whoami` returns `brianmosher`; and
  `corpora/swe-chat` already holds 3.3 GB - all six metadata parquets plus 615
  of 5,850 transcripts - which is data that only downloads WITH a credential.
  The check that reported "no token in ~/.cache/huggingface" was reading a
  DIFFERENT HOME: the zcode lanes run under redirected homes in
  `~/.local/share/agent-deck/zcode-homes/`, none of which carries the token. A
  true reading of the wrong home, reported as a fact about this machine - the
  same trap as T-008. Any seat checking for host credentials must say which
  HOME it looked in, or the answer means nothing.
  The real blocker was that the transfer DIED SILENTLY: two passes ended
  mid-progress-bar with a leaked-semaphore warning and no error, leaving 168
  then 615 files while the row read as in progress.
  Brian authorised the fleet to use his token for this dataset, 2026-09-19,
  verbatim: "Of course I authorize it, how else would it get done?" Resumed
  with `corpora/fetch-swe-chat.py`, which loops until the count on disk matches
  the count in the repo and stops only when a pass adds nothing. Projected
  10.6 GB of transcripts against 111 GB free. NOT blocked; in flight.
- **Standing R&D watch** — date-blocked by the one-request-in-flight contract
  until 2026-09-20. Today is the 19th; still holds. Note also reached: today
  is the Saturday Go reset per AGENTS.md — no returning-seat activity
  observed as of 13:5x; the watch's own block is the contract date, not the
  reset.
- **Keep-warm TTL re-run** — the OpenCode Go reset is due today (Saturday per
  AGENTS.md); the trigger remains one full steady-pattern day on Muse, which
  has not occurred. Blocker updated from "cannot occur before the reset" to
  "reset due/arriving; trigger still unmet". The pre-committed trigger
  stands.
- **Decision-held (GiLMore/Brian), re-checked this revision:** the R-PC
  Gate-C batch choice (map.md: no batch chosen — unchanged); the R-PF Gate F
  adopt/compose/build decision — UPDATED for this revision: the answer
  page's 09-19 DECISION-READY line reopens the state-layer comparison ("an
  observed native failure now justifies testing protection, but does not
  establish that protection works or justify a composite build; keep the
  Phase G build restriction") — the reopened comparison is rank 16 above,
  and the adopt/compose/build decision itself stays GiLMore/Brian-held and
  must now absorb the 22/33 broader-corpus number; the next-experiment build
  (proposed-not-built; Brian's scope call — unchanged).

Pruned this revision (2026-09-19 13:5x): **ranks 13, 14 and 15 — done and
verified as sprint 11's three rows.** BM25 abstention v2 → S11-1
(`team/S10-BM25-ABSTAIN2`, VERIFIED PASS 17:59 09-18, receipt
`team/CORVID-S11-1-VERIFY.md` — honest refutation: no declared threshold
separates the families, rejections always bundled with losses); KD
cross-system replay → S11-2 (`team/S10-KD-CROSS`, VERIFIED PASS 17:59 09-18,
receipt `team/CORVID-S11-2-VERIFY.md` — five systems on the frozen sample,
abstention 0/40 flat, the bm25 control reproduced the prior item-for-item);
pi-lcm native broader histories → S11-3 (`team/S10-PI-LCM-HIST`, VERIFIED
PASS 09:15 today, receipt `team/CORVID-S11-3-VERIFY.md` — native-failure
22/33 with 0/13 missed, verified down to a 46-trial replay through the real
pinned store). All three rank numbers are now cited by their admitted cells
and join the burned set. The earlier prunes stand; artifacts and receipts are
the record.

Also considered and NOT added, with reasons: **the Q3 union composition
(either-may-retrieve)** — unchanged from the 16:1x revision: on the frozen
sel corpus it is arithmetically identical to bm25 (pi-lcm's gate opens on
1/5 retrieve cases where bm25 is already correct and abstains on all 5
abstain cases where bm25 fires), and the answer page keeps it
corpus-gated ("only with a corpus where additional coverage and acceptable
abstention are plausibly achievable" — a planner corpus decision, named in
Decision-held's orbit). **The Q5 declinable implementation** — the answer's
next step needs "a declared implementation capable of declining queries" on
the frozen KD sample; all five admitted implementations scored 0/40
abstention and none exposes a decline path, so the candidate has no on-disk
subject: choosing (or admitting) one is an implementation decision in the
planner's orbit, named here rather than ranked. **MUSE ideation batch 7**
is startable but ranks below every candidate above on value (six batches
filed, dispositions closed). **CORE-MEMORY-MUTABILITY** stays a weak lead —
and the Q4 reopen makes the distinction sharp: what rank 16 tests is the
page's OWN named step (the existing thin layer on the existing corpus); a
NEW protection design remains a Phase-G planner proposal, not a backlog
rank. GOLD-ID-DRIFT is already practiced by design (guards + hash pinning).
A Heimdall code-read is R&D-watch work, date-blocked to the 20th. Verifying
the ATLAS's own neutrality waits until an atlas number is load-bearing in a
protected finding. S3-7 (checker-suite durable home) is already a board row.
The lane-meter aggregate-cap defect keeps its 16:1x disposition (consumers
furloughed; becomes a then-startable ops row if the Go reset makes it
load-bearing; owner cairn/ops). No candidate above was invented to fill
time: rank 16 is the answer page's own Q4 next step and DECISION-READY line,
rank 17 is its Q2 next step, and ranks 18-20 are the standing protectors the
planner has now twice declined explicitly.

## How to consume this file

Pick one candidate, write its QUEUE row (type-tagged, user-story line Brian
can read, cost cap, verifier named — never the author), claim it, and strike
nothing here: the file is a standing backlog, rows are the work. Re-rank when
evidence changes, per roadmap durability rule 5. Blocked candidates stay in
their own section with the blocker named and re-checked at every revision —
they rejoin the ranking the day their blocker clears, above startable equals
only if their value puts them there. Rank numbers may be non-contiguous; the
planner selects from the numbers that exist.

## Change log

- 2026-09-17 ~10:09 PDT — first written: same ten candidates, same ranks,
  prose-shaped (per-rank headings and bullets). Corvid's 10:22 CNR called it
  "gate-shaped" against D-8G's stated requirements; that was true of the
  content and false of the form.
- 2026-09-17 ~12:3x PDT — rebuilt into the table above, substance unchanged,
  after the D-8G gate (written blind by plumb-fable) rejected the prose form
  on first contact: `[PROSE-ONLY] no candidate table`, rc 1. The gate was
  right per its contract; this section records the rejection rather than
  silently replacing the file it punished.
- 2026-09-17 16:0x PDT — rank 11 added (corvid-dsh, D-13): delivered-context
  door metric from the day's intel report; card
  `team/EXTERNAL-ADEBENCH-20260917.md`. No existing rank changed.
- 2026-09-18 10:42 PDT — rewritten on the conductor's instruction (sprint
  cannot open from a finished list). PRUNED seven done candidates (ranks
  2, 3, 4, 5, 7, 10, 11 — the conductor's message said six while enumerating
  seven; the board's state governs). RE-CHECKED every survivor's blocker:
  the old rank-1 budget blocker is instrumented (~/.config/agent-deck/go-budget,
  today 06:57) leaving only Brian's campaign call; rank 6's disk blocker
  re-measured and still holds (14 GB free, 99%); ranks 8 and 9 remain
  date-blocked. ADDED five startable candidates from the fleet's own research:
  stale-path probe build (S8-5 design inputs), door rung 2 (S8-7's declared
  next rung), rank diagnostics (today's RANK-AWARE-RETRIEVAL + the S8-7
  sel-005 finding), evaluator-integrity canaries (today's EVAL-CANARY + the
  recorded driver gap), provenance chase (RD-THREADS open corvid items).
  Blocked candidates moved out of the ranking into a named section. D-8 gate
  re-run clean on the revision.
- 2026-09-18 10:5x PDT — two corrections from kiln's 09:36 D-13
  verification folded in (they were addressed to exactly these lines and
  the 10:42 rewrite missed them): rank 3 re-phrased from measure-first to
  surface-and-extend with the real priors named (metrics.py RR/MRR;
  RESEARCH-Q1.2-ISOLATION-RESULT and COLDREAD-20260912-scoreboard —
  "ordering is measured nowhere" was false); rank 4's canary-gap provenance
  re-pointed to team/INTEL/SYNTHESIS-2026-09-18.md as first valid record
  (CORVID-S7-1G-VERIFY.md contains no such statement). No rank changed.
  D-8 gate re-run clean after the edit.
- 2026-09-18 11:1x PDT — OUTCOME of that revision: the loop re-planned from
  it at 11:04:57 (sprint-next log) after the stale 09:55 SELECT:none
  proposal left the way. Astra selected ranks 1, 2, 3, 4 and deferred rank 5
  for capacity; the blocked four were skipped citing this file's blocked
  section. Rank 1 was admitted as S9-1/S9-1G. Ranks 2, 3 and 4 were REFUSED
  by the tool's duplicate detector on a false positive: its rank-citation
  test (sprint-next, already_admitted) keys on the bare string 'BACKLOG-NEXT
  rank N', and the S8-1..S8-4 cells permanently cite ranks 2-5 from the OLD
  eleven-candidate list, so any revision that reuses those numbers reads as
  re-admission (journal 11:04:57: rank 2 refused as row S8-2, rank 3 as
  S8-1, rank 4 as S8-3; the path test correctly cleared all three). These
  three candidates remain live in this list, unspent. The path test needed
  no change; the rank test needs candidate identity, not rank number
  (builder's; diagnosed on the board 11:1x). SPRINT-9-OUTLINE.md carries
  Goals 2-4 whose rows do not exist — do not work them without rows.
- 2026-09-18 12:4x PDT — restock commission (sprint-next recorded BACKLOG
  OWED ~12:27). PRUNED rank 1 (done and verified). RE-CHECKED every blocker.
  RENUMBERED survivors to 6, 8, 9, 13 dodging burned {1-5, 7, 10, 11}.
  ADDED rank 12 (the duplicate-test repair) and rank 14 (single-run marks).
  PROOF 12:5x: D-8 gate rc 0; duplicate test on the real board all clean.
- 2026-09-18 16:1x PDT — restock commission (planner declined to pad a
  sprint). RANKING STANDARD CHANGED to the planner's ANSWER.md next steps.
  PRUNED ranks 6, 8, 9, 12 (done as S10-1..S10-4). RE-CHECKED every blocker.
  RENUMBERED old 13/14 to 16/17. ADDED ranks 13-15 (Q2, Q5, Q4's named next
  steps). Q3 union considered and not added (arithmetic). PROOF 16:1x: D-8
  gate rc 0; sprint-next candidates()/already_admitted()/lint() green.
- 2026-09-18 16:5x PDT — rank 18 ADDED (results-tree canon), disposition of
  cairn's evidence note, independently re-verified before ranking; S10-1G
  pipe repair and R2H disclosure recorded. Header census updated to 13-18.
- 2026-09-19 13:5x PDT — THIS REVISION, on the conductor's commission
  (sprint 11 closed; every candidate finished or non-discriminating; the
  planner named the missing strongest comparison). PRUNED ranks 13, 14, 15 —
  done and verified as S11-1/S11-2/S11-3 (receipts cited in the prune
  section); 13/14/15 are now cited by their admitted cells and join the
  burned set. RE-CHECKED every blocker with live measurements: SWE-chat's
  disk half CLEARED (111 GB free at 85% vs 39.3 GB projection — was 17 GB at
  98%); its A1-A3 conditions are discharged (Alice's Rev-2 co-sign
  unconditional); the remaining blocker is named precisely (one gated:auto
  HF request — no account/token on this machine, checked) and it stays in
  the blocked section, not the ranking; R&D watch holds (contract to the
  20th; Go reset due today, no returning-seat activity observed); keep-warm
  re-worded to the reset being due with the trigger unmet; Brian's campaign
  call, R-PC and the next-experiment build unchanged; the Gate F entry now
  carries the answer page's reopen line and points the adopt/compose/build
  decision at the 22/33 number; Q6's next step named in the outcome
  experiment's orbit (same gates, not ranked). RENUMBERED old 16/17/18 to
  18/19/20 (census-verified: zero cells cite any of the three numbers).
  ADDED rank 16 — the answer page's Q4 named next step and DECISION-READY
  line: the existing thin layer vs the native arm on the UNCHANGED frozen
  broader corpus, both limits pre-registered before any run, the planner's
  "missing strongest comparison"; and rank 17 — the Q2 named next step: a
  third relevance-decision family (neither token filter nor score margin)
  with the held-out case set the answer demands, frozen before declaration
  and reported separately. Q5's next step considered and not added (no
  admitted implementation can decline a query — no on-disk subject; planner
  orbit). PROOF at 13:5x (clock read 13:58:51 at write): D-8 gate re-run on this
  file rc 0 clean ("5 candidates, each gateable, placed, and ranked without
  a tie") + --selftest rc 0; sprint-next candidates()/already_admitted()/lint()
  against the live board with SN_TEAM pinned: 5 ranks parsed [16-20],
  already_admitted None on every rank (the duplicate detector can refuse
  none of them), lint clean on all five; rank-citation census grep: ranks
  1-15 each cited, 16-20 uncited. The loop's next cycle reaches the planner
  on a list whose top rank is the comparison the planner itself named as
  missing.
