# DESIGN-CORNERS-1 — what the portfolio would miss

**Author:** Stratum (worker-glm), R&D pulse item 3 ("design corners: what
would the portfolio miss?"), 2026-09-12 17:5x PDT (clock-corrected). $0, design only — nothing
was run, nothing was patched. The charter is at a frozen G0 hash; patches
post-G0 have been directive-driven, so this file **proposes**, it does not
edit `PORTFOLIO-CHARTER-draft.md`. Each corner: the miss, the existing guard
and why it doesn't cover it, the cheapest pre-registrable fix, and whether
Brian is needed.

**Plain English first:** we have checked the portfolio's logic against its own
record and found six places where the campaign as chartered could produce a
true number that answers the wrong question. None requires new money; two
are one-line pre-registrations that expire in value the moment P2 data
exists.

## Corner 1 — BAR A has no budget parity (patch-shaped; pre-register before P2)

**Miss:** the long-context null receives the *entire* history; candidate
systems deliver *retrieved* context. A system can "beat the null" simply by
delivering more tokens than the null's budget — E-1 dressed up as E-3.
**Guard today:** "Mean ctx chars" is a reported column, and overhead is
"reported, not scored" — reporting is not a gate.
**Fix:** one pre-registered sentence — a BAR A pass requires delivered-context
budget ≤ the null's on the same slice, or the null/system token ratio prints
beside every BAR A number. **Brian: no** (Verity rules on it, per the
patch pattern).

## Corner 2 — capture-side cost is never scored (patch-shaped; same window)

**Miss:** the portfolio scores retrieval quality, the stale-use penalty, and
— for agentmemory — write-side *damage* (false-supersession dimension). It
never scores write-side *cost*: ingest tokens, ingest calls, wall time. For
the agentic extractors (a_mem, langmem, memobase — family E-6), write time is
where the real bill lives.
**Guard today:** the invocation-rate dimension counts calls; it does not
price them. Overhead columns cover run-time serving, not ingestion.
**Fix:** a capture-burden column (ingest tokens / calls / wall), programmatic
from run logs, pre-registered before P2 — same evidencing class as
invocation-rate. **Brian: no.**

## Corner 3 — serve-path ecological validity (declare, don't score)

**Miss:** the benchmark scripts the serve — the harness always calls
`retrieve` and hands results to the model. Our own record says delivery is
where systems actually die (F1 0/8 spontaneous vs F2 8/8 nudged; native
admission inert; R2 exists because of this). The portfolio cannot see a
system that scores well and never gets invoked in production; invocation-rate
cannot catch it because the harness invocation is unconditional.
**Guard today:** the charter's method limit already concedes the benchmark
cannot say "which system improves Brian's actual mornings."
**Fix:** no in-benchmark scoring. Two cheap additions: (a) the P4 report
carries the limit verbatim next to the verdict; (b) a descriptive
"integration surface" column (tool-call / auto-inject / library — the map's
axis B) so the verdict and the serve path are never read apart. **Brian: no.**

## Corner 4 — incremental arrival (reporting rule for write-time systems)

**Miss:** corpus ingest is bulk-before-query. Write-time mechanisms —
agentmemory's supersession (92.9% false-retirement is a *writes-meet-writes*
phenomenon), MemBukkit's budgeting, hindsight's state transitions — are
validated by the stress slice only at ingest, not under arrivals interleaved
with queries.
**Guard today:** the charter's secondary arm (the harness's longitudinal /
conflict tasks) exists but nothing requires it per system.
**Fix:** pre-register that a write-time system's row-5 numbers without the
longitudinal arm are labeled "ingest-only" in every table. **Brian: no.**

## Corner 5 — corpus contamination (interpretive limit; no cheap check exists)

**Miss:** MemConflict is public and third-party; vendor systems may have
ingested overlapping web data before we ever run them. Q1.2 closed
*cross-run* leakage; *world* leakage is untested and, at our budget,
untestable.
**Fix:** a P4 caveat line, plus the one observable smell we can name without
new machinery: a system scoring far above its in-harness peers specifically
on named-entity recall is flagged for reading, not ranked. **Brian: no.**

## Corner 6 — metric-comparability discipline in our own table (P3 spec line)

**Miss, demonstrated today:** L-LME-01 vs L-LME-02 — two upstream
"LongMemEval-S" headlines, retrieval recall vs judged accuracy, not
comparable; one vendor explicitly disclaims the QA reading. A results table
that mixes metric classes recreates upstream's confusion with our name on it.
**Guard today:** the charter's "no bespoke metric path" rule binds systems,
not the report's *citations*.
**Fix:** adopt Corvid's disclosure checklist (split + metric + reader + judge
+ encoder + backend + top-k + context size, or the row is marked incomplete)
into the P3 results-table spec, for our rows and any upstream number we cite.
**Brian: no.**

## Disposition

All six are cheaper to pre-register now than to explain after data exists —
the charter's own logic applied to itself. Corners 1–2 are the two that
change a bar's arithmetic and belong in a Patch 4 fold before P2; 4 and 6
are table rules; 3 and 5 are declared limits. Nothing here needs Brian's
calendar; all of it needs Verity's rule-check and GiLMore's nod. Filed for
routing, not for silent self-adoption.

— Stratum. Rebuilt from the record, 2026-09-12. The corners are the map's
job: the charter tests the systems; this file is the map testing the charter.

---

## Corner 7 (added 18:3x pulse — imported from the live arm, not invented)

**Population honesty for any burden metric.** Cairn's S5 preview
(BOARD, 2026-09-13 ~01:10 label) shows the failure shape directly: 6 pairs,
median token Δ% +57.0, and one pair at **+3038%** — which is a 932-second
memory turn paired against an 8-second no-memory turn. The tick cadence, not
the memory system, manufactured the outlier; Cairn named it a diet artifact
pre-close rather than letting window-close inherit it.

**Why the portfolio inherits this corner:** Corner 2 proposes a
capture-burden column (ingest tokens/calls/wall) and the charter reports
overhead columns beside every result. Both compare *quantities over
populations the systems do not define equally* — vendors dedupe, chunk,
extract, and split records differently, exactly as the poller's cadence
splits turns differently. An unstratified burden column can measure the
harness's touching pattern and call it the system's cost.

**Fix (one pre-registration line, same shape as Corner 1):** burden and
overhead comparisons are stratified by the population definition — per equal
record counts ingested (not per corpus run), per matched turn classes (not
raw turns), with any pair whose sides differ by more than an order of
magnitude in duration or volume flagged and read before it is averaged.
Same-class second lesson from the same tick: agent-deck's "fresh" reason
fires on nearly every poller tick *by construction*, so raw fire count is
not S4 signal — instrument-construction artifacts will always be available
to dress up as system behavior; the checklist question is "what did the
harness contribute?"

**Brian: no. Verity rules the pairing/stratification line with the rest.**

*Source receipts: BOARD [CNR 2026-09-13 ~01:10] (S5 preview, diet artifact
named); team/RETRO-S1-Cairn.md (START: naming the diet in every S5
preview). The live arm keeps paying the portfolio's tuition.*

---

## Corner 8 (added ~19:52 pulse — two live receipts, same day)

**Every programmatic scorer needs three states: PASS / FAIL / INCONCLUSIVE —
and a power check before it gates anything.** Assay's instrument register
(`team/ASSAY-POWERCHECK-REGISTER.md`) demonstrates both halves on
campaign-1's own tools:

- **S6's scan rule cannot say "scan unavailable":** an empty/errored MCP scan
  marks every healthy ACTIVE row a violation — a degraded instrument
  manufactures findings instead of reporting INCONCLUSIVE.
- **B7's count-parity self-test shares a predicate with the thing it checks:**
  a classification miss is invisible to it — PASS while substance leaks.

**Why the portfolio inherits this:** the charter's P3 scoring is
programmatic-first (sha-pinned verifiers feeding the bars). A verifier that
cannot compute a metric for some system's output format — and outputs 0, or
skips the row — is the quiet cousin of the "quietly substituted instrument"
the charter already forbids: the substitution happens per-row, invisibly,
inside the scorer.

**Fix (pre-register with Corners 1/2 at P2 entry):** each scorer declares its
three states up front; a row that cannot be computed is INCONCLUSIVE and is
reported as its own outcome row (never imputed, never zero); and each scorer
gets a register entry in Assay's pattern — finding, severity, fix,
adopt-or-defer — before P3 gates on it. **Brian: no.**

**Update (2026-09-13 00:4x):** the S6 guard is now **built and validated**
(`ASSAY-S6-EMPTY-SCAN-GUARD.md`: empty scan → `INCONCLUSIVE — STOP AND
RE-SCAN`; status/source violations still fire without the scan) — the
register's find → fix → positive-control loop works end to end, which is
exactly the treatment Corner 8 asks the portfolio's scorers to adopt before
P3.

**Update 2 (00:5x):** the guard passed **second-seat check** (Alice:
reproducible, clean apply, hashes match) with one boundary finding for the
P3 spec — INCONCLUSIVE must be **machine-readable** (a parseable status
field, not prose), or the portfolio's aggregators will face the same
unreadable-state problem the guard just fixed.

**Update 3 (01:0x):** boundary closed — rev 2 makes the verdict
machine-readable and passed Alice's rev-2 re-check with no new finding
(`ALICE-S6-GUARD-REV2-SECONDCHECK.md`). The full loop, one day: finding →
fix → positive control → second seat → boundary fix → re-verified. That is
the lifecycle Corner 8 asks every portfolio scorer to complete before P3.

**Update 4 (01:2x):** register #1's fix also landed — the B7 leak scan is
now **wired into the builder itself** (`s4-b7-leak-gate.diff`: emitted
packets scanned with the validated canary rules, not just a standalone
checker), closing both close-critical register rows (#1, #4) with built,
validated fixes. Portfolio translation: a scorer's self-test and an
independent leak/value scanner are different instruments; P3 needs both.

**Update 5 (01:2x):** the class recurred anyway — Alice's second-seat check
of Corvid's brand-new AGENTS-drift guard (built *after* Corner 8 was filed)
found the same two gaps in the same failure class: out-of-scope drift and
**silent PASS when its prerequisites are missing**. One day of evidence,
four instruments. This is why Corner 8 asks for the three-state declaration
as a **pre-registration at P2 entry** rather than a lesson learned at P3:
naming the failure class does not stop new instruments from growing it.

**Update 6 (04:5x):** canary-design nuance, from Alice's second-seat check of
the S4 leak gate: keyword canaries (`draft_id`, `key=record-`) flag
**mentions, not leaked values** — a triage found 17 mentions. A gate built
on keyword canaries must state which sensitivity it claims (mention-level
assurance, not value-level proof), or its FAIL verdicts will be over-read.
Portfolio translation: P3's leak/value scanners declare canary semantics
beside their three states.

**Update 6a (05:0x, RECONCILED 05:0x):** Assay's classification split the 8
flags into **3 probable real exposures** (value-shaped `draft-<hex>` tokens)
and 5 canary-word hits; Alice's second-driver reproduces it exactly
(`n_findings=8`, 3/5 split) — dispute resolved, no numbers travel unreconciled.
And the reconciled census went further: over **all 134 frozen packets**, the
`draft_id` keyword canary catches only **3 of 24 value-carrying unredacted
non-user entries** (53 value occurrences in 21 further entries never flag).
Final form of the design point: **a canary's recall is a measurable quantity —
measure it, don't assume it.** Keyword canaries are a subsample of the leak
class; P3's scanners ship with their measured recall beside their three
states.

**Update 6b (05:1x):** the measurement became a fix — Assay's validated
value-shape patch (`ASSAY-S4-VALUE-CANARY-FIX.md`: match `draft-<hex>`,
drop the word-only canary, redact value-carrying user entries) restores
recall to the full known class and *improves* precision (5 mention-only
false positives removed). Ready-to-adopt, NOT applied — owner Kiln/fsync.
The lifecycle now reads: measure recall → fix the canary → adopt at the
owner's gate → re-measure. P3 scanners inherit all four steps.

**Update 6c (05:2x):** the adoption is now a **ruled close-gate** — GiLMore
decides before close; until adopted, **no packet goes to a rater**
(scoreboard 05:2x). The lifecycle's final step has teeth: an unmeasured
canary doesn't just weaken assurance, it blocks the pipeline at the gate.
That is the strongest possible version of Corner 8's ask, and it arrived by
ruling rather than by design — the portfolio should copy the rule, not wait
for its own incident.

**Update 6e (05:5x):** the two-sided failure, demonstrated — on a value-only
secret the current builder **leaks it AND reports clean**; on a mere mention
it **false-alarms** (Assay's power check, 4/4, both sessions × both
builders). One word-only canary simultaneously under-reports the danger
class and over-reports the safe class. That is the empirical case for
Corner 8's full declaration set in a single table row.

**Update 6g (10:0x):** the gap is live, not hypothetical — the applied gate
over the **current window's 334 packets** catches 8 entries while the
value-shape detector catches 24 (58 values, 21 unique entries, 12 files),
and one session has no word canary hit at all (`ASSAY-S4-LIVE-LEAK-CENSUS.md`,
Alice second-check filed). The apply decision remains Awaiting GiLMore; the
measured-recall line in a scanner's declarations is what makes this gap
visible instead of silent.

**Update 6d (05:2x):** the patch passed **second seat** (Alice: hashes match,
census reproduces 24 findings / 58 values, false positives gone) with one
more boundary for the P3 spec — the value regex is **case-sensitive**, so
uppercase hex would evade; normalize case before matching. The boundary list
a scanner ships with now reads: three states, machine-readable status,
declared canary semantics, measured recall, case normalization.

**Update 7 (05:3x):** the corner now has an inverse view — Corvid's checker
coverage map (`CORVID-CHECKER-COVERAGE-MAP.md`) lists defect class → guard
(12 per-class guards) plus a **Layer A of guard-level hygiene** (structured
missing-prerequisite, exit-contract meta-guard, unreadable-input handling —
all second-seat verified), and names the still-unguarded classes so the next
slice is chosen from a list. That Layer A *is* Corner 8, implemented at the
guard level before the portfolio needed it; P3 inherits the map, the
hygiene rules, and the backlog discipline.

**Update 8 (06:1x):** the list is already producing — Assay's U2 prototype
(`ASSAY-U2-REQUIRED-METRICS-PROTOTYPE.md`) closes the coverage map's first
named Layer C gap: **selective metric omission** (a cited summary passes
every check while a required harm/context metric is simply never present).
Schema-index design with waiver files, validated, adoption owner Corvid.
Portfolio translation: a P3 table row missing its harm or context column is
INCONCLUSIVE, not absent — same three-state rule, now guard-backed.

**Update 9 (06:2x):** U2 is now **guard 14, adopted** — prototype → second
seat → adoption inside a few hours, with the map's Layer C list shrinking by
its first entry. The full demonstrated lifecycle for an evidence guard is
now: named in the coverage map → prototyped → second-checked → adopted →
guard 14 in the suite. The portfolio's P3 table inherits guard 14's rule
(a missing harm/context column is INCONCLUSIVE) and the map's Layer C
inherits a checked-off row.

**Update 10 (09:4x):** Layer C gap **U4 closed** — the identifier-lifecycle
guard (now guard 17) catches documents citing superseded or withdrawn
identifiers as if current (a cold reader could act on `L-HS-02` after it
split). Only U3 remains open in the coverage map. The portfolio's evidence
index inherits the same protection: a slot row whose ledger rows have split
or moved will flag instead of silently serving stale keys. **Boundary found
at second seat** (Alice): a `split`-cue false negative — the guard's second
seat keeps finding each guard's edge, which is the system working.
**Closed at rev 4** (01:1x next day-cycle): weak `split` subjects dropped,
Assay's second-seat power check PASS with no finding.

**Update 11 (09:4x):** Layer A's "closed suite-wide" was ahead of reality —
Assay's exit-contract audit found **six guards without exit-contract
controls** and one non-hermetic control (patch validated, pending at
Corvid). The lesson repeats at every layer: a coverage claim is itself a
claim, and it verifies the same way everything else does. **Closed and
second-seated (10:2x):** the 16/16 meta-guard patch is applied and passed
Alice's independent check — Layer A's closure is now a verified state, not
a claim.

**Update 12 (10:1x):** guard 17's rev 3 folded Alice's split-cue residual
and passed her re-check, with one honest residual left open: a guard whose
declared index can include itself is **self-satisfiable** — the meta-question
recurses one level down. The suite's answer so far (second seats + the
meta-guard) handles it; the portfolio's P3 should assume the recursion never
fully closes and keep the second seat mandatory.

**Update 12a (10:2x):** the recursion demonstrated concretely — the
meta-guard's covered set was **hardcoded**, so a new 17th guard would be
silently uncovered (Assay proved it with a synthetic sibling). Completeness
patch validated, pending at Corvid. Update 12's warning was not
hypothetical; the portfolio's P3 gate card should derive its guard list
from the filesystem, never from a constant.

**Update 12b (10:3x):** the completeness patch passed its second seat
(Alice: reproduces, catches the synthetic 17th; one summary-parse nit) —
ready for Corvid's apply. The filesystem-derived guard list is now
validated, not just proposed.

**Update 12c (10:4x):** Corvid applied **his own implementation** (not
Assay's reviewed diff), and the second seat ran on the applied bytes anyway:
**PASS, and the applied version is stronger than the patch it superseded**
(Alice). The discipline that matters is visible here — the second seat
verifies what shipped, not what was proposed.

**Update 12d (11:5x):** rev 5 answers the recursion — the lifecycle guard
now **fails when it reads zero files** and when a list entry names a
nonexistent file (both proven by negative tests). A guard can no longer
silently self-satisfy; the second seat remains mandatory for what the guard
claims, but the empty-scan silence is closed.

**Update 13 (10:5x):** the P2 evidence gate card now carries all **17
guards** — entry gate includes 15/16/17, the publication gate gains the
identifier citation-hygiene step, and a stop rule fires on the meta-guard's
`INCOMPLETE`. Meanwhile the builder's parse-iso fix (register #6) correctly
waits for a ruling: it touches a frozen window instrument, and frozen means
the gate asks first.

**Update 14 (20:2x):** the leakage delta is **signed on the applied bytes**
(Alice: 18/18 cases match the pinned semantics, fails closed on the named
bad shapes, all three blockers closed in code). The P3 citation-rule
package is now complete end to end: contract → census → second drivers →
applied bytes → signature.

**Update 14b (20:3x):** G-B is now **adopted into guard 14** (boolean
`leakage_required:true` trigger, legacy floor on absent/false; hashes
`3ae6cf05…` → `09814e25…`). And the poller-defect explanation for the burst
delivery my lane received is confirmed in source: `fleet-poller.sh`'s
QUEUE-row match was exact and case-sensitive, so open-row pulses never
fired. Both facts now cite code, not reports.

**Update 14 (10:5x):** the parse-iso fix passed its second seat (PASS on
target and every claimed case; one low-severity silent edge named) — the
frozen-instrument ruling now has everything it needs. And the **sprint-2
outline** (GiLMore, draft for Brian) makes the P2-entry turn imminent: this
file's riding-set checklist is the natural cargo for that turn.

**Update 15 (11:0x):** parse-iso **v2 supersedes v1** (v1: do not apply) —
colon-form parity added, 8/8 power check. The ruling packet is final. The
sprint-2 outline is now in front of Brian with three asks (approve outline;
transcript-mining word; R2 day-0 time) — and Ledger already flags its two
stale parts, which is the gate working before the gate was asked.

**Update 16 (11:1x):** Muse batch 6 aimed the divergence input at the right
residual — the suite's four **hand-maintained declared lists** (lifecycle
skip/log, meta-guard covered set, cross-copy list, superseded-id index).
3 ACCEPTs, all one class: a declared-list guard must FAIL when it scanned
zero entries, and every skip:/log: entry must carry its reason and date.
The filesystem-derivation fix (12a) removed the biggest constant; these
close the rest of the hand-maintenance surface.

**Postscript (06:2x):** guard 14 immediately needed its own Layer A pass —
Alice's second check found a canonical-schema crash in the adopted guard and
Assay validated the fix (owner Corvid, not applied). The hygiene rules apply
to the guards themselves; adoption is the middle of the lifecycle, not the
end.

---

## Corner 7b (added ~20:0x pulse — same family as Corner 7, distinct failure)

**Deterministic-but-arbitrary choices inside a scorer are disclosures, not
defaults.** Today produced three instances of the same class across three
seats: Assay's S5 pairing is greedy-nearest-first, which is deterministic but
**not minimum-total** (counterexample: 300s greedy vs 180s optimal, same pair
count — `ASSAY-POWERCHECK-S5-PAIRING.md`); Alice's memobase overall is
**question-weighted**, worth ~5.8 points over the category average; Alice's
agentmemory fixture ships **top-10 truncated**, making R@20/MRR
self-attested. None is a defect. All three change numbers, and none would be
visible from the number alone.

**Why the portfolio inherits this:** its scorers will contain the same
arbitrary-but-deterministic choices (aggregation weighting, truncation
points, tie-breaking, per-query vs per-run averaging), and a reader who
recomputes with the other choice will cry defect — or worse, not notice.

**Fix:** the S5-INTERPRETIVE-NOTES pattern, applied at function level —
every such choice is pinned in a file **before data exists**, named in the
report beside the metric, and inherited by anyone recomputing. The charter's
pre-registration discipline already covers metrics and bars; this extends it
to the choices inside the arithmetic. **Brian: no.**

---

## Corner 9 (added 2026-09-13 00:3x pulse — Alice's charter harness audit, three additions)

**Source:** `team/ALICE-CHARTER-HARNESS-AUDIT.md` applied the day's
vendor-harness guardrails to our own P2 plan: **7/10 met outright** — the
charter's spec is already judge-free, sha-pinned, null-inclusive, and
raw-emitting. Three additions close the rest, all pre-registrable at P2
entry alongside Corners 1/2/8:

- **A — pin the eval-workload model ID per system** (`system →
  model_id@version`, or `deterministic`): for any agentic extractor, the
  answer model *is* part of the measured system (the Mem0 66.88-vs-91.56
  version split is the receipt).
- **B — state the retrieval-depth budget explicitly** (`retrieval-depth = N
  candidates, scored at k=3/5`, raw N-row list shipped): the exact omission
  that made agentmemory's R@20/MRR unre-derivable.
- **C — an explicit INVALID/abstained run label** (preflight failures become
  their own outcome row, never zero — Corner 8's three-state rule at the run
  level), plus a hashed judge-prompt pin *if* the LLM judge is ever
  authorized (the MemOS same-model-pair 11.4-point gap is the reason).

**Disposition:** proposed, not applied — the charter is at a frozen G0 hash
and this seat does not self-adopt. Filed as the third member of the
P2-entry riding set (Corners 1/2 envelope+burden, 8 scorer states, 9
harness completions), for Verity's rule-check and GiLMore's nod. Credit and
custody: Alice audited; Stratum maintains.

**The meta-finding is Alice's and worth keeping:** our harness spec is
already stronger than every vendor harness examined today. The portfolio
isn't just measuring the field — it is running the field's missing
controls.

---

## The P2-entry riding set — consolidated checklist (2026-09-13 ~05:47)

What GiLMore/Verity rule on at P2 entry, in one place. Each is a one-line
pre-registration; none needs Brian; all were proposed, none self-applied.

| # | Pre-registration line | Corner |
|---|---|---|
| 1 | BAR A pass requires delivered-context budget ≤ the null's (or the ratio prints beside every BAR A number) | Corner 1 |
| 2 | Capture-burden column: ingest tokens/calls/wall, per equal record counts | Corner 2 |
| 3 | Write-time systems' numbers without the longitudinal arm are labeled "ingest-only" | Corner 4 |
| 4 | P3 results table adopts the disclosure checklist (split/metric/reader/judge/encoder/backend/top-k/context) | Corner 6 |
| 5 | Burden/overhead comparisons stratified; >10× duration-ratio pairs flagged and read, not averaged | Corner 7 |
| 6 | Deterministic-but-arbitrary scorer choices pinned in a file before data exists | Corner 7b |
| 7 | Scorer declarations: three states (PASS/FAIL/INCONCLUSIVE) + machine-readable status + canary semantics + measured recall + case normalization; self-test ≠ leak scanner | Corner 8 (+6b–6d) |
| 8 | Harness completions: eval-model ID per system; retrieval-depth budget with raw N-row lists; INVALID/abstained run label; judge-prompt hash if a judge is ever authorized | Corner 9 |

Riding-set rule (from the S5-INTERPRETIVE-NOTES pattern): these land in one
patch at P2 entry or they do not land at all — a partial adoption is a
quietly substituted instrument set.

---

## P2-entry run spot-check against the riding set (2026-09-13 ~05:5x, on `P2-ENTRY-RUN.md`)

The entry run happened this morning (baselines only: 3,351 questions, $0,
~6 min). Spot-checking it against this file's checklist, since external
candidates enter through the same runner:

**Already satisfied:** Corner 9-A (eval-workload model: `zero LLM,
deterministic` — stated); Corner 8's INCONCLUSIVE class (162 unmeasured
questions kept separate, never imputed); Corner 7b (append-mode chronology
pinned and contract-tested); Corner 1 is trivially satisfied until external
systems arrive (single protocol, single scorer, same pins).

**One gap to close before external candidates enter:** Corner 9-B — the
retrieval-depth budget is described as "bounded relaxation" but **N is not
stated**, and the raw N-row lists are not promised. This is the exact
omission that made agentmemory's R@20/MRR unre-derivable. One line
(`retrieval-depth = N candidates; raw N-row lists shipped per question`)
closes it while the runner is still warm.

Filed read-only; the run is Kiln's artifact and row 28 (second-driver) is
the verification path. — Stratum.
