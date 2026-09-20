# Intel synthesis — 2026-09-17 (report AGENT_MEMORY_INTEL_2026-09-17.md)

Synthesizer: corvid-dsh, 2026-09-17 16:0x PDT, under QUEUE rows D-12 (standing
duty) and D-13 (today's backfill instance). Read in full: all 26 headings of
the report, `BACKLOG-NEXT.md`, `team/S6-ROADMAP/next-experiment.json`, and the
existing `team/EXTERNAL-KNOWLEDGEDRIFT-20260916.md`.

**Headline context first: we were already inside this report's top finding
before the report arrived.** KnowledgeDrift v2 is the benchmark S7-4 ran today
at 14:19 (`team/S7-KD-WORLDS/`, worlds/v2 seeds 1+2, per-family scores
re-derived, controls honest, caveat travelling). The report's "add KnowledgeDrift
v2 to the benchmark-evaluation queue" is already partially discharged, and its
"do not adopt the aggregate score blindly" caution is already structurally
enforced in our run (no score import; the owner-bias caveat quoted verbatim in
verdict.json; D-14's gate would flag any leaderboard citation).

## PRIORITY CHANGES

Two actions named; both dispositioned:

1. "Add KnowledgeDrift v2 to the benchmark-evaluation queue" — **already
   actioned**: card `team/EXTERNAL-KNOWLEDGEDRIFT-20260916.md` (2026-09-16),
   run `team/S7-KD-WORLDS/` (2026-09-17, done+verified). Remaining from the
   report's recommendation: compare its task families against our taxonomy —
   partially done (three read-side families scored; six mutation-side families
   excused with capability reasons). The report's import-fixtures-before-
   adopting-scores advice matches what we already did: we imported its frozen
   worlds, not its leaderboard.
2. "Add a delivered-context evaluation layer inspired by adebench" —
   **actioned now**: card `team/EXTERNAL-ADEBENCH-20260917.md` and backlog
   rank 11 in `BACKLOG-NEXT.md` (S7-DOOR, $0 local, design-only readiness).
   No card was warranted beyond the adebench card itself for the priority
   line; the card carries it.

## SYSTEMS TO INVESTIGATE

One system: **Engram Alpha.** Card written:
`team/EXTERNAL-ENGRAM-ALPHA-20260917.md`. It matters because it is (a) the
KnowledgeDrift v2 reference system — so the owner-bias question applies in
both directions, and (b) an entrant shape that exposes supersession edges,
conflict edges, and tombstones natively — which is exactly what S7-4's
families_not_run excuses and S7-3's Gate F number need to become a real
comparison instead of a capability absence. No run is admitted by the card;
bounded next step is inspection of the mutation model and adapter surface.

## BENCHMARKS TO INVESTIGATE

- **KnowledgeDrift v2** — existing card (above) + S7-4 run. The report's new
  information for us: the ladder's decomposition (whole-file-in-context 71%
  raw vs TF-IDF 43% but better efficiency score) independently reproduces the
  shape our own S6-2/S7-4 headline warns about — presence is not delivery.
  Nothing new to run; our second axis should be the door metric (rank 11),
  not their weights.
- **adebench** — card written: `team/EXTERNAL-ADEBENCH-20260917.md` (method
  is the contribution; the published winner ran on the author's own golden
  set with pre-distilled facts — do not trust the ranking).
- **ForgetEval** — **no card warranted**: it is lineage and reinforcement
  (control-plane placement, supersede/release/purge), its adversarial cases
  overlap the class S7-3 already measured on our stack (pi-lcm native 0/32
  false supersession), and our current engines expose no control-plane
  operations to test it with — the HONEST-CAPABILITY-N/A condition applies to
  us before it applies to anyone else. Revisit with the Engram inspection.

## EXPERIMENTS TO CONSIDER

Each of the four handles checked against `BACKLOG-NEXT.md` and
`team/S6-ROADMAP/next-experiment.json` (which holds the outcome experiment,
proposed-not-built, blocked on Brian's campaign-2 call — none of the four
displaces it, and none is it arriving back from outside):

- **KD-MUTATION-SUBSET** — partially exercised TODAY by S7-4 (read-side
  families on upstream worlds); the mutation-side subset (supersede/release/
  purge replay) is blocked by the same recorded capability absence (bm25 has
  no write path; pi-lcm's supersession was measured separately in S7-3).
  No new row: revisit when an entrant with a mutation surface exists (the
  Engram inspection is that trigger). No card beyond the two filed.
- **DELIVERED-CONTEXT-DOOR** — **new**: backlog rank 11 (S7-DOOR) + the
  adebench card. This is the one genuinely new instrument the report hands us.
- **BENCHMARK-OWNER-BIAS CHECK** — **already institutionalized**: controls
  first in every run (return-nothing/oracle), caveat travels with every S7-4
  number, no-score-import is gate-enforced, and Brian's 2026-09-16 decision
  bars ranking claims outright. Nothing to add; the report's version asks for
  "at least one independently designed system" — that is what rank 6 (SWE-chat)
  and the Engram inspection would supply if Engram advances.
- **HONEST-CAPABILITY-N/A** — **already implemented today**: S7-4's
  families_not_run declares capability absences with reasons instead of
  scoring six families as zero. Generalization (future adapters carry a
  capability declaration) is folded into the Engram card's inspection step.

## RESEARCH LEADS

Four leads, dispositioned:

1. Audit whether KD v2 covers authority/provenance/scope/disposition — our
   S7-3 already contributes one data point (pi-lcm never false-supersedes on
   different-scope distractors: scope is handled where it matters most), and
   the authority family is KD's optional ninth — unrun in S7-4 for capability
   reasons. Folded into the Engram inspection questions rather than a card.
2. Deterministic grading vs judge/critic — we already own ground truth
   deterministically (the harness grades; no model self-report scores), so
   this is alignment, not action.
3. Delivered-context as first-class metric — **yes**: that is backlog rank 11.
4. Resurrection-after-deletion — the hardest proposed case (does a deletion
   survive consolidation/re-ingestion). Blocked by the same capability gate as
   KD-MUTATION-SUBSET; recorded on the Engram card as an inspection question
   (does a tombstone survive Engram's maintenance?). No card of its own.

## Verdicts and disclosure

- Cards produced: `team/EXTERNAL-ENGRAM-ALPHA-20260917.md`,
  `team/EXTERNAL-ADEBENCH-20260917.md`. Both exist as of this writing.
- No-card verdicts: ForgetEval, BENCHMARK-OWNER-BIAS (already practice),
  HONEST-CAPABILITY-N/A (already practice), KD-MUTATION-SUBSET and
  resurrection (capability-blocked, trigger recorded).
- Disclosure: the declared checker `team/tools/check_intel_synthesis.py`
  carried the same `Path.home()` defect fixed on D-9 and D-10 — from a
  sandboxed seat it reported a false [NO-REPORTS] on this answered feed.
  Fixed before first producer use (one line, absolute `/home/bmosher/...`,
  precedent cited in a comment); selftest rc 0; kiln re-verify owed with this
  row's verification.
- Nothing in the report warrants stopping current work; the one priority
  change we did not already cover (delivered-context) is actioned at rank 11.
