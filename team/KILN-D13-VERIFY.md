# kiln-flash second-seat verify — D-13 intel synthesis (2026-09-17 backfill)

**Verifier:** kiln-flash (sole doer seat) · **Date:** 2026-09-17 · **Cost:** $0, local reads only
**Subject:** `team/INTEL/SYNTHESIS-2026-09-17.md` + the two Corvid cards, against
row D-13's terms (synthesize the backfill report; disposition all five handoff
sections; check the four experiment handles against `BACKLOG-NEXT.md` and
`team/S6-ROADMAP/next-experiment.json`; re-verify the checker's `Path.home()`
fix).
**Independence:** the report is Brian's external pipeline's output (intake
header: "NOT written by the fleet"); the synthesis and both cards are Corvid's;
the two parallel cards are Brian's. I authored none of them. Blind holds.

## Declared check + the owed checker re-verify

- `check_intel_synthesis.py --max-age-h 0` → rc 0 ("every intel report in
  team/INTEL/ is answered (1 report(s))").
- **`Path.home()` fix (D-9/D-10 class) re-verified:** the checker now resolves
  the team dir as the absolute `Path("/home/bmosher/memory-bake-off/team")`
  (line 34) with the sandbox failure reason and precedent in a comment. The fix
  is real and was in place before first producer use, as disclosed.
- `--selftest` → rc 0: honest no-card answer accepted; an unread report, a
  cited-but-missing card, a skipped section and a missing verdict each rejected
  **by name**. The checker tests the duty, not just file existence.

## Section accounting (the D-12 duty)

All five handoff sections are dispositioned with explicit verdicts:
PRIORITY CHANGES 2/2 (KD v2 already actioned via card+S7-4; delivered-context
actioned now); SYSTEMS 1/1 (Engram Alpha — "one system" is correct: ADE Brain
appears only in the report body, and the handoff block names only Engram);
BENCHMARKS 3/3 (KD v2 existing, adebench card, ForgetEval no-card **with a
stated reason**: control-plane operations our engines do not expose);
EXPERIMENTS 4/4; RESEARCH LEADS 4/4. The synthesis's headline claim — we were
already inside the report's top finding — checks out against the S7-4 record.

## Handle cross-checks (re-done, not inherited)

| Handle | Corvid's disposition | My re-check | Result |
|---|---|---|---|
| KD-MUTATION-SUBSET | partially exercised by S7-4 today; mutation side capability-blocked, trigger recorded | `S7-KD-WORLDS/verdict.json` exists; owner-bias caveat verbatim ("The benchmark's author has a system in its own ranking, and it wins.") travelling with the numbers | ✓ |
| DELIVERED-CONTEXT-DOOR | new → backlog rank 11 + adebench card | `BACKLOG-NEXT.md` rank 11 = S7-DOOR, card pointer, re-measurement "none exists" stated, runnable check declared | ✓ |
| BENCHMARK-OWNER-BIAS CHECK | already institutionalized | caveat-in-verdict.json (above) + no-score-import gate discipline on the board | ✓ |
| HONEST-CAPABILITY-N/A | implemented today (families_not_run) | `S7-KD-WORLDS/declaration.json` present; verdict.json framing confirms | ✓ |
| (all four) | none displaces the outcome experiment | `next-experiment.json` = `proposed-not-built` G4 outcome experiment, untouched by all four | ✓ |

## Cards (D-6 format)

Both cards carry every required element — what it is, goal mapping (Engram:
G2/G1 entrant; adebench: G3/G4 antecedent), "What it lets us stop building",
"What NOT to trust", bounded no-run next step, candidate-discovery status, no
number imported. ADE Brain — the report body's second system — is dispositioned
inside the adebench card's what-NOT-to-trust section (its published winner ran
on the author's own golden set), so nothing from the body sections is
unaccounted for.

## Brian's parallel cards (row-flagged for this pass)

`EXTERNAL-HEIMDALL-20260917.md` and `EXTERNAL-AGENT-MEMORY-ATLAS-20260917.md`
exist, are authored by Brian from the report's cited sources, and contradict
nothing in the synthesis: Heimdall is one more entrant-inspection candidate
beside Engram (not a displacement of the outcome experiment), and the Atlas is
a benchmark index relevant to the Phase-B harvest, not a score import. Their
synthesis implications are **deferred to tomorrow's D-12 cycle** per this row's
own clause, with this note as the receipt of that decision — the 16:09
synthesis could not have folded 16:07 cards, and the backlog already carries
the load-bearing one (rank 11).

## Non-blocking notes

1. The synthesis prose never names ADE Brain explicitly (it is covered
   transitively via the adebench card). Future syntheses should name
   body-section systems in one line even when dispositioned transitively.
2. Tomorrow's D-12 should fold the Heimdall/Atlas cards' implications (or
   restate no-card reasons) so the backfill closes with nothing implicit.

## Verdict

**PASS.** The synthesis discharges D-13's terms: every section answered, every
handle genuinely cross-checked, both cards D-6-complete, the checker fix real
and re-verified, nothing imported, the outcome experiment untouched.

— **kiln-flash**, 2026-09-17. $0, one turn, local reads only. Writes confined
to `team/`.
