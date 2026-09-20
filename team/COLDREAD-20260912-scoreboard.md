# COLD-READ — SCOREBOARD-20260912.md plain-English block (17:45 refresh)

**Reader:** Stratum, per adopted rule 5 ("nothing reaches you until a named
seat with no stake reads it cold") — first pass under the rule. The block is
Ledger's file; I changed nothing. **Scope:** the two Brian-facing surfaces of
the refresh — the "Plain English for Brian" block and the burndown's
reader-facing claims. **Method:** read against `team/BRIAN-FACING-STYLE.md`
(4 rules) + serveability (can Brian act from the block alone?). One read, $0.

## Verdict: PASS — serveable now; three findings, none blocking

The block does the load-bearing things right: roles stated with jobs
attached ("Corvid finds and probes evidence; Alice independently checks it;
Stratum reads every document for you"), rules stated as numbered plain
sentences, an honest self-flag ("rows 20 and 21 are marked done but no
second seat has checked them yet"), a "Changed since ~17:40" freshness line,
and the one genuinely open question (S4 second-rater pin) names its actor
(GiLMore) and its stakes instead of burying them. Burndown arithmetic
spot-checked at 16:08, 16:30, and 16:45 — internally consistent, standing
row 8 correctly counted apart.

## Findings (for Ledger; owner fixes, reader never edits)

1. **The three asks are referenced, not stated.** "Your three asks from the
   demo are unchanged" sends Brian to another file to learn what he is
   being asked. The whole point of the plain block is acting from it alone.
   Fix: one line each — (1) builder-lane decision on the five agent-deck
   fixes, (2) R2 day-0 smoke on the work machine, (3) nothing on the
   portfolio until P4 — or accept that the block is a summary, not a
   surface, and say which file is the surface.
2. **Count drift: "Two results already:" introduces three bullets** (Alice
   row 20, Corvid row 21, builder's own thread). Small, but a Brian who
   counts bullets stops trusting counts. Same class as fsync's "15 vs 13".
3. **Three terms cross the block untranslated:** "S4 second rater" (S4 is a
   criterion label; one clause — "the trigger-relevance success criterion" —
   would carry it), "frozen rule" (pre-registered rule, fixed before the
   window opened), "live arm" (the trial lane that is actually running).
   Style rule 3 says translate or don't use it; the block was written
   before the rule-5 pass existed, which is the pass working as designed.

Non-finding, recorded because it looks like one: "Cairn is still running
live-arm work" — the job is arguably attached ("live-arm work"), so rule 2
is satisfied; noted as a pass, not a defect.

— Stratum, cold read, 2026-09-12 17:5x PDT (clock-corrected; first draft said ~17:58 from inference). Findings are the countable
output; next pass gets to check whether the count goes down.

---

## Pass 2 — the 17:55 refresh (same day, 17:5x PDT, clock read)

**Verdict: PASS — 0 findings.** All three pass-1 findings are applied:
(1) the three asks are restated inline, each with its if-no column, matching
the demo's structure; (2) "Two results already" is now "Eight results so
far" with exactly eight bullets — counted; (3) "live arm," "frozen
instrument," and "S4" each carry a defining clause on first use. The honesty
lines survived the edit (rows 20/21 second-seat caveat retained; "Changed
since" section now cites this gate's own pass-1 result). Burndown and queue
counts re-spot-checked — consistent.

**Trend: 3 → 0 in one refresh cycle.** One datapoint, but it is the one the
sunset rule needs: the gate's findings are a number that can go down. Next
pass runs whenever the block next substantively changes.

— Stratum, pass 2. Reader changed nothing; owner's fixes verified against
the four style rules.

---

## Pass 3 — the 19:10 refresh (17:5x → 19:1x same day)

**Verdict: PASS — 2 findings, neither blocking.** Structure is now the best
yet: "New since 18:55, most important first" with the price ruling leading,
per-item if-no/who phrasing retained, and every spot-checked number traced
clean — including the agentmemory item, whose receipt
(`team/ALICE-REDERIVE-AGENTMEMORY-LONGMEMEVAL.md`: R@5/R@10 reproduce
exactly; R@20/MRR self-attested because shipped lists truncate at 10) the
block compresses fairly ("data truncation, not overstatement" is the point
and survives the compression).

1. **Internal contradiction on the price state.** The New section correctly
   says prices are set (Patch 4, off-peak, peak receipt owed) — but the
   Earlier section's builder item still reads "You or GiLMore must choose
   the price source" with no superseded marker, and the anchor-map item
   closes with "The missing piece is prices for the $5 line." Same surface,
   two states of the same fact. Fix: tag superseded items inline
   ("(superseded — prices set above)") and update the anchor-map line to
   "prices set; remaining: the P2-entry re-print."
2. **Pattern, proposed not demanded:** items in the "Earlier" list carry no
   per-item state. A one-word state tag per item (current / superseded /
   resolved) would let the block grow all day without regrowing
   contradictions — the same generated-status instinct as Ledger's own
   scoreboard_facts proposal, applied at sentence level.

Pass trend: 3 → 0 → 2. The 2 are the growth pains of a block that now
updates itself hourly; both are one-line fixes.

— Stratum, pass 3.

---

## Pass 4 — the ~19:3x refresh (19:15 → 19:35 same day)

**Verdict: PASS — 1 minor finding.** Both pass-3 items are adopted and
visible: a "How to read" header with **[superseded]**/**[resolved]** state
tags (credited to this gate), the price item tagged
"[superseded ~18:5x — prices set by Brian's ruling, Patch 4]", and the S5
item "[resolved 19:27 — freeze tool shipped]". New claims spot-checked:
the LoCoMo category-id collision is receipted (Alice's file, Part 4 — same
question ids, different category labels across vendors, so per-category
cross-vendor tables are unsafe), Kiln's pi-lcm port and the spend-counter
cross-check are covered, and the Corvid/fsync commit discrepancy is
resolved on the record (wrong hash searched; 33da73c is real).

1. **One dropped qualifier:** "Mem0's own table rows add up to 90.23" is the
   **question-weighted** aggregation; unweighted they give 86.80. A reader
   who recomputes unweighted will get the other number and conclude the
   block is wrong. One word fixes it ("question-weighted"), same class as
   Assay's 418/450-vs-1.0 denominator note: the aggregation is part of the
   number.

**Trend: 3 → 0 → 2 → 1.** The gate is converging on a block that updates
hourly without regrowing contradictions; the residual findings are
single-word qualifiers, not structural. Queued for my next map fold:
Alice's category-id collision as a new collision class alongside
"LongMemEval" and "LoCoMo" (addendum 2b).

— Stratum, pass 4.

---

## Gate pass 5 — SPRINT-2-OUTLINE.md (GiLMore draft for Brian; 05:5x→filed 06:0x, clock-read)

**Verdict: PASS — serveable, four small findings for the author.**

1. **Goal 1 omits the retrieval-depth line** just as external systems are
   about to enter the runner. One line (retrieval-depth = N; raw N-row lists
   shipped) closes the exact trap that made agentmemory's R@20
   unre-derivable.
2. **Goal 4 states rev-2 "frozen and verified" but omits the remaining
   step:** the package is not yet re-sent to Brian's work machine. The ask
   list should carry it (or fold it into the day-0 ask).
3. **Goal 2's gating wording is ambiguous after this morning:** the miner's
   full-corpus scale-up already ran under Brian's approval; what remains
   gated on his pilot read should be named precisely (the invocation/
   outcome benchmark corpus build, presumably), or Brian will sign a gate
   that has already opened.
4. **Minor:** the ablation ladder's terms (+retrieval / +state / +OM
   projection) are untranslated for Brian; one clause each.

Positive: user-story form, honest "what we are NOT doing" section, window
deadline stated twice, repo-push receipt included. The two stale parts
Ledger flagged are covered by findings 2 and 3.

— Stratum, gate pass 5. Author edits; reader never edits.
