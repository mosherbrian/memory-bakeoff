# SPRINT-1 DEMO — what this sprint produced, assembled for Brian

**Assembled by:** Stratum (the team's file/cold-read seat, worker-glm lane) —
QUEUE row 18, on GiLMore's (the conductor's) dispatch.
**Date:** 2026-09-12. **Cost of this document:** $0. It is read-only assembly:
nothing was run, spent, or measured to produce it; every claim cites a file
listed in §Sources. If a number here disagrees with its source file, the
source file wins — receipts claim; state is.

---

## Plain English first

**What this is.** One document covering the four things this sprint produced:

1. A security review of the tools you use to supervise agents from a browser
   or phone (agent-deck and its web UI). Headline: five serious findings,
   each with a small proposed fix. Nothing has been changed yet.
2. Build progress on the portfolio campaign you approved ("Go, Zep parked"):
   every license question is closed, four adapters are test-receipted, and
   still $0 of the ≤$5 envelope is spent. No benchmark runs yet.
3. The state of the live trial window: it is OPEN, two supersession cycles
   have closed with **zero** confirms asked of you, counting is live on the
   trigger criteria, and nothing is waiting on you except the R2 smoke run.
4. Research notes from Corvid (the R&D staff seat): four memory engines
   cleared for use, one retracted number verified to stay retracted, one
   cheap idea batch (3 of 9 ideas survived review), and one integrity probe
   that passed cleanly. No decisions needed from you on any of it.

**What we're asking of you — three things, none urgent:**

| # | Ask | If you do nothing |
|---|-----|-------------------|
| 1 | Decide whether the five serious agent-deck findings get fixed by the builder lane (each is a ~10-line edit; the fix list is already written). | The findings stay known-but-unfixed on file. The tools keep working as they do today. |
| 2 | Run the R2 day-0 smoke on your work machine when convenient. | The R2 arm stays dark (no counting). Everything else continues. |
| 3 | Nothing on the portfolio yet. Your only decision there is the close report (gate P4). | The campaign keeps building inside its envelope. Touching $5 stops it automatically and reports to you. |

**No clock is expiring.** If you read only this block, you are current.

---

## 1. Agent-deck review

**Source:** `team/REVIEW-agentdeck-design.md` (Cairn, the local-pi worker
seat). agent-deck is the session-manager app for the agent fleet; its web UI
(conductor-chat) is what shows approval buttons when an agent asks for a
permission. The review is line-level on the UI's source (~/conductor-chat),
read-only; agent-deck itself was reviewed at behavior level only (its binary
is stripped; an upstream source checkout exists at ~/src/agent-deck but is
not yet the source of truth).

Severity labels, translated: **S1** = can grant more than the button says, or
can be abused by a token-holder, or can lose work. **S2** = wrong behavior or
availability coupling. **S3** = robustness/performance/hygiene.

The five S1 findings, in plain terms:

1. **A one-time "accept" can grant a permanent permission.** If a dialog's
   buttons are labeled unusually (e.g. `['Always allow', 'No']`), the
   fallback types the first option — the persistent grant. Fix: refuse
   instead of guessing (~10 lines).
2. **"Approve for session" can silently degrade to one-time.** The button
   promises a session grant; odd labeling delivers a one-turn grant. Safe
   direction (under-grant), but the UI would lie about it.
3. **The deny matcher treats "no" as a substring.** An option named "Note…"
   counts as a refusal. Fix: word-boundary matching (1 line).
4. **Unbounded request bodies and threads.** A token-holder can crash the
   server or fill the disk; a double-tapped send delivers the prompt twice.
5. **A shell timeout kills bash but not its children.** A backgrounded build
   or `sleep 3600 &` keeps running with the server's credentials.

There is also a 12-item ordered fix list (file:line, effort estimates) and —
recorded because a review that only lists sins is half a review — a
"genuinely good" list: path containment done before the check, passwords
never written to logs, and comments that record the measured bug each change
fixed. The review changed nothing; every fix is a proposal.

**Decision needed from you:** whether the builder lane applies the fix list.
Items 1–4 are the ones that touch permissions and resource limits.

---

## 2. Portfolio build status

**Sources:** `team/PORTFOLIO-CHARTER-draft.md`,
`implementer/repo/docs/PORTFOLIO-P1-ADAPTER-RECEIPTS.md`,
`team/CLAIMS-LEDGER.md` §P1, `team/ECOSYSTEM-MAP.md`.

The portfolio campaign measures about a dozen memory systems — ours and
open-source — on one frozen conflict benchmark, to answer the decision
memo's three open questions: does any system beat just putting the history
in the context window (row 4), do the four never-measured engines change the
picture (row 5), and what does each system do with a stale record it returns
(row 6). You approved the charter and the ≤$5 envelope at G0; Zep is parked.

Phase P1 (build; no runs) status:

| Item | Status |
|---|---|
| Licenses | **Closed.** All four unmeasured engines license-clear at pinned commits (Corvid, row 11); the five remaining systems verified by pinned-blob receipts, byte-identical to the builder's frozen fetches (Alice, row 15). No copyleft blocker. |
| Adapters test-receipted | agentmemory (13 tests PASS), the long-context null (7-contract suite PASS; 15 combined), Perseus and the baselines (prior receipts). |
| Adapters still pending | pi-lcm store-reader wrap (Kiln, not started); the five upstream harnesses (blocked only on materializing the 182 MB pinned dataset — disk, free). |
| Charter | Three patches since draft, all pre-registered: Verity's (the independent reviewer's) criteria pass; agentmemory moved in-portfolio with its known fault — it falsely deleted 92.9% of stress memories — carried as a scored dimension, because a system that is known-bad is exactly what a benchmark should measure; baselines locked, an invocation-rate dimension added, and the recommendation bar hardened so a bare Hit@3 win is not adoption evidence. |
| Envelope draw | **≈$0.** P1 is build-only. Touching $5 = automatic stop + report (standing switch). |
| Synthesis frame | `team/ECOSYSTEM-MAP.md` skeleton (taxonomy + slot ids) + Corvid's claims ledger filling it. Rows 16–17 (fire-log readiness, claim classification) still open in the QUEUE. |

**Decision needed from you: none until P4** (the close report — your second
and last planned decision in this campaign).

---

## 3. Trial window state (campaign-1)

**Sources:** `team/WINDOW-OPENING.md`, `team/SCOREBOARD-20260912.md`,
canonical doc `team/CAMPAIGN-1.md`. The window is the measured evaluation
period — only agent work inside it counts toward the success criteria. The
criteria are labeled S1–S6 (pre-registered before the window opened; note
the label collision with the review's severity S1 — different S1).

**Window OPEN since ~11:05 PDT.** All six pre-window checklist items are
receipted, and provenance is sealed: the memory extension is byte-identical
to its frozen lineage, the Perseus binary hash matches the pinned study
provenance. The T0 tier (agent-confirmed low-stakes memory writes — no human
tap needed) is live and proven end-to-end: config flip receipted, first
agent-confirmed write accepted and delivered, zero unsanctioned changes in
the vault.

Criteria state:

| Criterion | State |
|---|---|
| S1 supersession closes on real work | **CLOSED — 2 complete cycles, 0 confirms asked of you.** |
| S2 stale-action events (target 0) | Pending; blind scoring pack built (fsync), not yet adopted; a non-Cairn rater is needed. GiLMore + Verity decide before close. |
| S3 burden under tiering (≤1 human confirm/day) | Measuring; sample so far: 11 confirmed writes, 8 by agents (receipt: `team/ROW9-BLIND-HARNESS.md`). |
| S4 trigger fire/application rate | **Counting live since ~14:21** — change-aware trigger applied, smoke PASS, independent verification 14/14 (Assay), first real fire receipted with matching prompt hash. False-fire count pending Verity's blind rulings; Corvid pinned as second rater at close. |
| S5 overhead (within +25%) | Harness built (Assay); pairing rule frozen; `tokens := sum` pinned; final paired-run analysis happens at window close. |
| S6 capture-at-rest integrity (0 unsanctioned demotions) | **0 violations** across every scan to date. |

One honest wrinkle from the record: the window-open file's gate checklist
briefly showed a stale "awaiting Verity" line after GiLMore had already
declared the window open; GiLMore's reconciliation note is on file. The
board, not the checklist, was right.

**Decision needed from you: the R2 smoke receipt only** (ask #2 above). The
window itself runs without you.

---

## 4. R&D notes for Brian

**Sources:** `team/RESEARCH-4-ENGINES-SURVEY.md`,
`team/RESEARCH-PROVENANCE-AUDIT.md`, `team/MUSE-IDEATION-01.md`,
`team/RESEARCH-Q1.2-ISOLATION-RESULT.md` (all Corvid, R&D staff).

1. **Four-engine survey (QUEUE row 11).** Habitus, agentmemory, Hindsight,
   MemBukkit — the four never measured on the conflict benchmark — are all
   permissively licensed (Apache-2.0 / MIT), verified at frozen commits, so
   none blocks the campaign. The sharper finding: every one of their
   headline numbers (95.2%, 92.6%, "most accurate ever") is unverified on
   our benchmark — those runs are the portfolio's job to produce. And two
   carry faults a retrieval score would hide: agentmemory's perfect score
   was bought by deleting valid memories (92.9% false supersession);
   Hindsight has never had a faithful product run.
2. **Provenance audit (row 12).** The retracted MemBukkit scan-fraction
   figure (32.9%) stays retracted in all nine documents that mention it —
   healthy. But three rows of RESULTS.md link artifacts that do not contain
   the numbers cited, and one links a formally invalidated run. Correct
   artifacts exist and are named; each fix is one line. Also corrected on
   the record: 32.9% is MemBukkit's figure, not Hindsight's. Those three
   fixes currently have **no named owner** — they gate clean citations
   before P2.
3. **Muse ideation batch 1 (row 13, ~$0.0011).** Muse (a cheap external
   model used as an idea generator, public questions only) proposed 9 items;
   Corvid accepted 3 (each now a named, bounded probe), marked 5 as already
   covered by existing work, rejected 1. Accepts are proposed checks, not
   findings — "Muse proposes, Corvid disposes."
4. **Cross-run leakage probe Q1.2 (row 14, $0, no LLM).** Each of the seven
   in-process engines was run twice on the same benchmark to see whether run
   2 inflates because run 1 warmed a cache. It does not: results are
   byte-identical across runs for every engine and every metric, and the
   reset observably empties each store. A deliberately leaky fake engine was
   flagged immediately (+0.96), so the clean result means something.
   Limit stated inside the result: this cannot catch leaks in engines that
   run as separate services (Hindsight, the agentmemory daemon, MemBukkit's
   product path) — those stay flagged until that arm runs.

**Decision needed from you: none.** The only loose thread is an owner for
the three one-line pointer fixes (§4.2).

---

## Sources

- `team/QUEUE.md` row 18 (this task) — and rows 1–19, the sprint's worklog
- `team/BRIAN-FACING-STYLE.md` (this document's format rules)
- `team/REVIEW-agentdeck-design.md`
- `team/PORTFOLIO-CHARTER-draft.md`; `implementer/repo/docs/PORTFOLIO-P1-ADAPTER-RECEIPTS.md`;
  `team/CLAIMS-LEDGER.md` §P1; `team/ECOSYSTEM-MAP.md`
- `team/WINDOW-OPENING.md`; `team/SCOREBOARD-20260912.md`; `team/CAMPAIGN-1.md` (canonical; not re-read)
- `team/RESEARCH-4-ENGINES-SURVEY.md`; `team/RESEARCH-PROVENANCE-AUDIT.md`;
  `team/MUSE-IDEATION-01.md`; `team/RESEARCH-Q1.2-ISOLATION-RESULT.md`

## Method limits, inside the deliverable

- Assembly only, one turn, $0: no runs, no re-measurement, no re-reading of
  primary data. I verified claims against their receipts at the document
  level, not by re-running anything.
- State as of 2026-09-12 ~16:28 PDT. QUEUE rows 16, 17 (open) and 19
  (Ledger's burndown) were in flight at assembly; their outcomes are not in
  this document.
- One record discrepancy flagged, not resolved: the row that assigned this
  task says **Sprint-1**; the scoreboard's section header says "Sprint-2
  status." I kept the row's name (it owns the artifact) and hand the
  numbering question to row 19's burndown, which has to count something.
- Costs quoted are those on file (portfolio ≈$0 draw; Muse call ≈$0.0011;
  Q1.2 $0). Per-lane totals live in the lane-counter design, not yet wired
  to a live counter (QUEUE row 3 delivered the design; the schema is empty).
- Correction (2026-09-12 ~18:2x, after QUEUE row 22's second-seat check
  found it): §3's S3 sample figures are receipted in
  `team/ROW9-BLIND-HARNESS.md`, which the S3 row now cites. Everything else
  in the checker's 14/14 path check passed as written.

— Stratum. Rebuilt from the record, 2026-09-12. The ghost seat's first
sprint row; the receipts, as always, were already there.
