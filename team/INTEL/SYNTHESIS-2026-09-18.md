# SYNTHESIS-2026-09-18 — corvid-dsh's read of AGENT_MEMORY_INTEL_2026-09-18.md

Feed: `AGENT_MEMORY_INTEL_2026-09-18.md` (12,423 chars on disk; header says
12,152 fetched 14:15:02Z, generated 07:00 PDT). Header:
`priority_change: no`, `agent_action_recommended: yes`. Queue row D-13,
instance claimed 2026-09-18 09:15 PDT; verifier kiln-flash. Produced before
reading kiln's verify of yesterday's synthesis? N/A — yesterday's D-13 cycle
closed VERIFIED PASS 17:45; this is today's fresh read of today's feed, not a
re-run (re-measurement rule: what differs is the report date).

Method, per the row's standing terms: every experiment handle below was
checked against `BACKLOG-NEXT.md` (ranks as of the 2026-09-17 16:0x
revision) and `team/S6-ROADMAP/next-experiment.json` (frozen,
proposed-not-built) before any new proposal was written down. None of the
four handles is already in the backlog; the frozen outcome experiment is not
displaced by anything in this feed.

## PRIORITY CHANGES

Report says NONE. Verdict: agree. Nothing today touches the frozen
next-experiment (the G4 outcome comparison, gated on Brian's campaign-2 /
post-09-20 budget decision), and nothing interrupts the sprint: S8-7 — the
delivered-context door, backlog rank 11 from yesterday's feed — is admitted
and awaiting its build. The feed's own bottom line ("no change to current
research priorities") matches the board.

## SYSTEMS TO INVESTIGATE

Report says no new system met the evidence threshold; the "soul" memory-layer
architecture from a removed long-horizon simulation discussion is retained
only as an architectural lead. Verdict: agree, no card. The feed itself
refuses to promote it and we should too — the source post is gone and the
behavioral claims are contested. Substantively, the interesting part (write/
compression/supersession policy for a never-compressed core layer) is our
G1/G2 ground already: S7-3 measured pi-lcm native supersession under stress
(0/32 false supersessions, 12/12 missed updates — the layer never superseded
anything, so "does-not-help" was the verdict), and the roadmap's Phase-G
probe-not-build discipline governs any state-layer work. Held as a research
lead against G1/G2, not a candidate.

## BENCHMARKS TO INVESTIGATE

Report says nothing newly verified; the 09-17 backfill carry-forwards
(KnowledgeDrift v2, adebench, ForgetEval) remain active leads with no new
evidence. Verdict: matches our state exactly — KnowledgeDrift v2 is S7-4
(done, VERIFIED PASS, caveat and families_not_run recorded), adebench is the
rank-11 card (`team/EXTERNAL-ADEBENCH-20260917.md`) whose instrument is
S8-7's gate, already verified this morning (S8-7G VERIFIED PASS 08:26), and
ForgetEval was declined yesterday with the capability-block reason recorded
on the D-13 row. No new benchmark work is warranted today.

## EXPERIMENTS TO CONSIDER

Four handles; each cross-checked against the backlog and the frozen
next-experiment before disposition.

1. **EVAL-CANARY** (immutable hand-verified evaluator canaries run before
   every sweep; abort on canary failure). Verdict: PARTLY OURS ALREADY — the
   gap is real but narrow. The guard set (`team/tools/check_*.py`) with
   per-guard `--selftest` plus `check_checker_exit_contracts.py` (real
   clean/dirty CLI pairs on minimal fixtures) is exactly an immutable
   canary suite for the evaluator's guards, and its own selftest proves it
   rejects prose-only, crashy, finding-less and cry-wolf checkers. Two
   recorded gaps keep the feed's point partially alive: (a) the driver's
   covered set is the sibling guards only — the sprint gates (`S*-*/check.py`)
   are exercised ad hoc by the verifying seat, a coverage gap on record since
   `CORVID-S7-1G-VERIFY.md` and repeated in every S8 gate receipt; (b) no
   wired pre-sweep step requires the canaries to pass BEFORE an expensive
   run — they run when someone remembers. Disposition: instrument repair,
   worth a backlog line at the next re-rank (small, $0, advances measurement
   honesty; does not displace the outcome experiment). No external artifact
   to card — this is our own instrument.
2. **GOLD-ID-DRIFT** (gold sets pointing at stale store keys after
   re-indexing; emit a distinct integrity error, not a system failure).
   Verdict: ALREADY PRACTICED BY DESIGN — no new work. Corpus identity in
   this repo is pinned to content/manifest hashes and provenance is a
   release gate by AGENTS.md non-negotiable; the standing guards
   (`check_frozen_id_provenance.py`, `check_map_hashes.py`,
   `check_invalidated_pointers.py`, `check_results_value_pointers.py`) do
   the resolve-against-current-corpus job, and the invocation corpus was
   re-frozen by hash at S4-10 when its fillers changed. The feed's preferred
   practice — source-stable semantic identity over store-internal row IDs —
   is what our pinning already is. The practitioner anecdote behind this
   handle (a recall number jumping after a gold-key fix) is mechanism-level
   instructive; its numbers are not imported here (no-score-import rule).
   Decline: no card, no row.
3. **RANK-AWARE-RETRIEVAL** (MRR/nDCG as diagnostics where adapters expose
   ranked retrieval). Verdict: NEW — the one genuine gap today, small and
   diagnostic-only. Our capability reports carry Hit@k / all-relevant@k /
   prohibited@k / set-F1; S8-7 (in flight) measures delivered-context
   presence and irrelevant delivered bytes. Ordering — how early the first
   useful evidence lands — is measured nowhere. The feed scopes this
   correctly as a diagnostic that must not replace capability tests.
   Disposition: backlog line at next re-rank ($0, local, existing adapters),
   complementary to both the door and the outcome experiment; declines a
   card today because there is no external system or benchmark to card —
   it is a metric policy for instruments we already run.
4. **CORE-MEMORY-MUTABILITY** (immutable vs append-only vs self-editable
   core layer under contradiction, poisoning, supersession). Verdict: HELD
   AS A LEAD, not a candidate. Source is the removed simulation thread the
   feed itself declines to promote; readiness is low; and the deciding
   property (whether a core layer's write policy changes stale-state
   outcomes) sits behind questions G1/G2 already own, with S7-3 as the
   measured precedent that a trivial policy layer did not help pi-lcm. If
   Brian wants it staged, the honest form is a Phase-G probe proposal
   against the S7-3 machinery — a planner/GiLMore call, not a synthesis
   promotion. No card (weak source; feed's own threshold says no).

## RESEARCH LEADS

The report's four leads disposition: canaries → see EVAL-CANARY (adopt as
instrument repair, wire pre-sweep, extend driver coverage to sprint gates);
gold-reference audit → already standing as guards + hash pinning (no action);
separating retrieval presence from rank from delivered context → converges
with yesterday's adebench lead and is exactly the S8-7 build now pending
kiln — rank is the only one of the three planes we do not yet measure, per
RANK-AWARE-RETRIEVAL above; core-identity probe → held per
CORE-MEMORY-MUTABILITY. The feed's "three planes sitting on evaluator
integrity" model is convergent validation of a structure we arrived at
independently: store/control-plane correctness (S7-3), retrieval quality
(S6-2/S7-1), delivered-context quality (S8-7), evaluator integrity (the
guard set — with its two recorded gaps, see EVAL-CANARY). Adopting the
wording costs nothing and sharpens the roadmap's measurement-honesty line.

No card was warranted today: the feed's strict window found no new system or
benchmark (its own sections say so), and the four experiment handles are
dispositioned above against our own instruments — two already practiced, one
new diagnostic worth a backlog line, one held as a weak lead. Cards exist for
external artifacts; none qualified.

— corvid-dsh, 2026-09-18 09:1x PDT. $0, local reads only.
