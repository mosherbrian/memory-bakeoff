# COLD-SEAT RECALL DRILL — Corvid (reassigned from worker-codex)

**Time:** 2026-09-12 ~16:34 PDT · **QUEUE row 4** · **Cost:** 1 turn, $0.
Reassigned to Corvid per GiLMore (from worker-codex, WILD).

**Coordination note:** QUEUE row 4 was re-edited by Ledger to dispatch the
same drill to a recreated seat `anvil-oai` in the same 16:3x window. That is a
collision, not a contradiction I resolved: I executed the drill on the direct
GiLMore reassignment to me, left row 4 open, and flagged it for GiLMore
adjudication. Two independent baselines are stronger than one.

**Drill as defined** (`team/RETRO-1-worker-codex.md` §5): give one parked or
outside worker only `MISSION-20260912.md`, `SCOREBOARD-20260912.md`, and
`CAMPAIGN-1.md`; ask the three operational questions needed to join the work
tomorrow. **Artifact required:** 3 answers + confidence notes.

**Corpus used for the answers** — the three named documents only:

- `/home/bmosher/memory-bake-off/MISSION-20260912.md` (Brian's mission statement)
- `team/SCOREBOARD-20260912.md` (refreshed ~16:25 PDT; Ledger)
- `team/CAMPAIGN-1.md` (v4; APPROVED, window open)

All line cites below are to those three docs. **Instrument note:** the three
questions are *not* in the corpus — they live in `team/RETRO-1-worker-codex.md`
§5 and `team/QUEUE.md` row 4. I read those two to learn the task; a seat
handed only the three-doc corpus would not know what was asked. That gap is
recorded in the confidence notes as a finding, not hidden.

---

## Q1 — What is forbidden?

**Confidence: HIGH.** CAMPAIGN-1 states most of these verbatim under "Hard
guardrails" (L230–248) and "Standing instrument rules" (L195–209).

Forbidden acts / stop events:

1. **Any native `remember` call in the live arm.** It is itself a stop event
   (S6 tightening 3, L172–176). Native `remember` on an active key demotes
   the record `active→proposed` while returning `ok:true,
   action:"updated"`, and recall then abstains; **no record migrates to
   native remember** (guardrail 1, L232–235). CLI `write` remains the only
   activation path.
2. **Treating the native admission chain as usable** until a record is
   *observed* going `proposed→active` through public tools (never observed;
   attested-journal route unreached). `maintain`/`consolidate` do not promote
   proposals. Corollary: **campaign-C (upstream capture repair) stays gated**
   (guardrail 2, L236–240).
3. **Using the wrong capability nouns.** Only `memory.propose` /
   `memory.commit` / `memory.read` are real; `memory.write.*` silently denies
   while echoing a success-shaped string. Any authority work must use the
   verified vocabulary **plus** explicit `capability_constraints_json` **plus**
   explicit `mode: "enforce"` (guardrail 4, L243–247; standing rule 3,
   L203–209).
4. **Treating stream-level presence as sufficient.** Everything is measured at
   **DELIVERY level** (the delivered toolResult text); stream presence is
   necessary-but-insufficient, always (guardrail 3, L241–242; standing rule 2,
   L200–202).
5. **Treating an echoed receipt as evidence.** "Receipts claim; state is."
   Instruments assert *observed state* (vault scan, delivered toolResult),
   never a receipt alone (standing rule 1, L197–199).
6. **Agent-confirming high-stakes records.** T0 is agent-confirmed
   **LOW-STAKES only** (conventions, notes, pointers); T1 — decisions that bind
   future behavior (architecture, deployments, project conventions) — is
   operator-confirmed, with the finding-#1 plain-language format REQUIRED
   (L64–76).
7. **Quietly engineering around the burden metric.** Never raise TTL or reach
   for auto-confirm mid-window; expiries are reported and interpreted as a
   gate-friction finding (L185–189).
8. **Unbounded spend on metered lanes.** dsh lanes (Aletheia, Assay, Corvid)
   are metered with no counter → **bounded tasks only**; no new
   native-pipeline spend; Muse is calibrated, no further spend (L250–262).
9. **Exposing raters to trigger events / fire-log content mid-window.**
   S4 relevance adjudication is blind under a rule frozen before the window
   (L144–148); the scoreboard makes the live hazard explicit: row 16 was
   amended to "no raw fire-log content, sealed output only" (SCOREBOARD
   L166–172).
10. **Causal or overreaching claims.** "Tiering reduced burden by X%" is a
    causal claim the design cannot support (no control arm) — L124–126.
    The campaign is descriptive, small-n, no causal claims (L26–27).

Not forbidden / allowed: negative results are **deliverables**, preserved
verbatim with receipts (guardrail 5, L248).

---

## Q2 — What would count as campaign success?

**Confidence: HIGH on the criteria; MEDIUM on "success overall," because
success is a conjunction of six criteria and the window is mid-flight, not
closed.**

Success is the six pre-registered criteria (CAMPAIGN-1 L83–177), all
**descriptive, small-n, no causal claims** (L26–27, L83). Targets:

- **S1 — Supersession cycle closes on real work.** Target **≥1 complete
  cycle**, with "deliberate convention change" operationally defined (a change
  to a convention that *has a stored record*) and a **programmatic
  delivered-level receipt per cycle**: new record key/content PRESENT, old key
  ABSENT, plus the supersede receipt's status flip and `valid_to` (L85–97).
- **S2 — Stale-action events = 0**, with prominent failure reporting. Named
  post-hoc detection rule (artifact diff vs current record set; Cairn
  executes, Verity audits); zero is **necessary-but-not-sufficient**, and
  `n` (turns + post-supersede opportunities) is reported beside the 0
  (L99–110).
- **S3 — Burden ≤1 T1 confirm/day under tiering**, with denominator =
  working days with ≥1 capture-eligible event; n days + n confirms reported;
  **T0 misclassification rate reported beside the burden number**;
  "estimate-vs-measured" labeling kept forever; unclear count reported
  (L112–128).
- **S4 — Self-noticing split.**
  - **(a) Trigger fire-rate:** fraction of adjudicated stored-record-relevant
    turns where the trigger fired; **target ≥3/5**.
  - **(b) Application rate:** when fired/available, did the agent use the
    delivered content (descriptive).
  - **Mandatory false-fire count**; relevance adjudicated by Verity, blind to
    trigger state, under a rule frozen before the window; **delivered-level
    counting** (only retrievals whose toolResult delivered the relevant
    record). "Self-noticing" unqualified is reserved for trigger-OFF
    observation vs the F1 0/8 baseline (L130–149).
- **S5 — Overhead within +25%.** Pre-registered pairing (same task family,
  same worker, both turns completed, nearest-in-time; n pairs stated);
  **tokens primary, wall shown**; symmetric skepticism for a favorable
  direction (L151–160).
- **S6 — Capture-at-rest integrity, 0 unsanctioned demotions.** Scoped to
  *unsanctioned* transitions (a correct S1 supersession flip is expected and
  receipted); instrument = scan after every write, never the write receipt;
  CLI-write-only sub-check; "lost" defined (L162–176).
- **Mandatory scoreboard sub-count:** "TTL expiries with no operator
  acknowledgment observed," plus `delivered:false` notifier receipts and
  wrong-code destructions. Pre-registered interpretation: if expiries ≥
  confirmed cycles, that is a **gate-friction finding** for campaign-2, not a
  campaign failure (L178–189).

**The thesis being demonstrated** (L20–27): an agent demonstrably adapts when
its world changes — on real work, with the human paying roughly one
confirmation a day and **zero stale actions** — by closing the supersession
loop and making retrieval triggering change-aware. The anchor travels with
every citation: *demonstration = S1–S6, descriptive, small-n, no causal
claims.*

**Explicitly NOT success** (L31–42): closing this cycle **cannot show that
decision memory improves worker performance**; that sentence is required in
every window-end report. Also not success: a favorable retrieval score on its
own.

**Window / stop condition:** 10 confirmed T1 cycles OR 3 working days,
whichever first; Brian stop-anytime via kill switch `PI_PERSEUS_RECALL=0` or a
word (L191–193).

**Where it actually stands at scoreboard time** (SCOREBOARD L187–203): S1
**CLOSED — 2 cycles** (both T0, 0 Brian confirms); S6 **0 violations**; S4a/b
**counting since ~14:21**; S2, S3, S5 **pending** (blind pack built, not
adopted). So the campaign is **not yet complete** on the record.

---

## Q3 — What is the next executable action, and who owns it?

**Confidence: LOW–MEDIUM.** The phrase is not in the corpus; I inferred it
from the QUEUE snapshot (SCOREBOARD L221–248) and the Awaiting table
(L323–336). The corpus supports several defensible answers, and the
snapshot contradicts itself on some statuses (see notes).

**Primary answer — the only open, claimable, team-owned action:** **Assay
claims and runs QUEUE row 16** (S4 packet-builder dry-run, amended per fsync
B1/B6: sealed output outside `team/`, self-check result only). It is the one
row listed **open with an eligible seat** (SCOREBOARD L245; eligible Assay per
L245 and the roster L108). Rows 17 (Alice) and 18 (Stratum) are already
claimed/in-flight; row 4 is this drill; row 8 is a standing watch.

**Critical-path human action (the real blocker):** **Brian runs the R2 day-0
smoke receipt on his work machine** — R2 day-1 counting waits on it
(SCOREBOARD L326–327). No team seat can execute it.

**Close-time actions already pinned (not yet due):** Verity's **blind S4
adjudication** at window close (L200, L162–164); **row-9 adoption** (rater,
min-overlap, seed; S2 needs a non-Cairn rater) — GiLMore + Verity (L330);
**Corvid as pinned S4 B5 second rater** at close (L109, L164). Cairn is
building the `--window` stats export that feeds S5 close (L106, L202).

If forced to one line: **next executable = Assay on row 16; the schedule's
binding constraint = Brian's R2 smoke receipt.**

---

## Confidence notes — what I could and could not reconstruct

**Answer-level confidence**

| Question | Confidence | Basis |
|---|---|---|
| Q1 forbidden | **High** | CAMPAIGN-1 states guardrails/standing rules nearly verbatim (L195–248); scoreboard restates the row-16 hazard (L166–172). |
| Q2 success | **High on criteria; medium overall** | S1–S6 explicit and tightened (L83–177); "overall success" depends on close-time criteria still pending, and the board's status snapshot is mid-window. |
| Q3 next action | **Low–medium** | Inferred from open rows + Awaiting; corpus offers ≥3 valid candidates; some statuses internally inconsistent. |

**Reconstructed with high confidence**

- The mission: make a meaningful agentic-memory breakthrough, prove it with
  pre-registered benchmarks and receipts, run the fleet as a second
  self-organizing experiment; negative results are first-class; claims must
  survive real tasks and credible comparison (MISSION-20260912.md L8–24).
- The campaign's guardrails and the "receipts claim; state is" /
  delivery-level discipline (CAMPAIGN-1 L195–248).
- The pre-registered S1–S6 criteria, the T0/T1 tiering, the window and kill
  switch, and the small-n/no-causal-claims framing (CAMPAIGN-1 L20–193).
- The roster, seats, and lane types (SCOREBOARD L98–114) and the queue
  snapshot (L221–248).
- Current campaign state: S1 closed (2 cycles), S6 0 violations, S4 counting,
  S2/S3/S5 pending (L187–203).

**Could NOT reconstruct / low confidence**

1. **The drill's own question set.** The corpus does not contain the three
   questions or the phrase "cold-seat recall drill." A seat given only the
   three docs is asked to answer questions it was never given. This is the
   sharpest coordination finding: the instrument lives in
   `RETRO-1-worker-codex.md` §5 + `QUEUE.md` row 4, not in the corpus the
   instrument tests.
2. **Which "MISSION" is canonical.** The drill names `MISSION-20260912.md`
   (Brian's statement); the scoreboard references a different file,
   `team/MISSION.md` ("Program Mission," L3). Two mission documents exist. A
   cold seat told "MISSION" could read the wrong one.
3. **Exact next action.** No doc names a single "next executable action";
   row 16, Brian's R2 smoke, and the close-time S4/row-9 work are all
   defensible. Ownership of row 16 is also muddied: the amended task is a
   sealed dry-run, but the queue's "Artifact required" column still reads
   "rubric + sample adjudications" (SCOREBOARD L165–172, L328) — a live
   inconsistency the record itself flags.
4. **Counts and labels.** The scoreboard disputes its own numbers: fsync
   tick #11 says "15 done" vs 13 statuses (L92–94); "sprint-2" vs "Sprint-1"
   (L34–35); row statuses (17/18 in flight at 16:25) are a snapshot that
   later posts would change. So queue totals are approximate.
5. **Evidence behind the claims.** The corpus cites receipts by path
   (`WINDOW-OPENING.md`, `S4-ADJUDICATION.md`, probe findings, commits) but
   does not contain them. I can report what the record *asserts*; I cannot
   verify it from the three docs.
6. **Seat identities beyond name↔agent↔lane.** Fine-grained who-did-what and
   the reasoning behind decisions (e.g., why row 16 was assigned, why row 9
   is unadopted) require the cited files.
7. **Data unavailable/out of scope in the corpus:** the R2 proposal's actual
   contents, the portfolio charter's internal criteria, the S4 raw adjudication
   rule text, and the P1 discovery material.

**Validity caveat on this drill (honesty about the baseline).** This is not a
perfectly cold seat: I had just finished QUEUE row 14 (Q1.2), and I read
`QUEUE.md`, `BOARD.md`, and `RETRO-1-worker-codex.md` to learn the assignment.
The answer *content* above is cited only to the three-doc corpus, but the
drill cannot claim a pristine cold start. If a true cold-start baseline is
wanted, run the same three-doc prompt on a seat with no prior context and no
queue/board access; the expected additional failure is item 1 (the seat cannot
know the questions).

**Net:** the durable record is **serveable** for the mission, the guardrails,
the success criteria, and the current campaign state — a new seat could join
the *reasoning* from MISSION+SCOREBOARD+CAMPAIGN-1 alone. It is **not**
self-contained for *actioning*: the task questions, the canonical mission
file, the unambiguous next action, and the primary evidence all live outside
the three-doc corpus. That is a coordination/pointer gap, not a retrieval
failure of the three docs themselves.
