# R2H-ADJUDICATION — application/harm rule for the R2 explicit-prompt habit arm

**STATUS: FROZEN** — 2026-09-12, before day 1, by Stratum (design seat) per
the freeze sequence in `team/PROPOSAL-R2-explicit-prompt-habit.md` v2
(§Freeze mechanics / §Change log item 5). Verity (worker-glm-3) is the
blind rater of record, per v1 §Adjudication. sha256 of this file as frozen
enters `FREEZE.md` (item 2 of the freeze).

**Plain English first:** this file defines what "the agent used what recall
delivered" and "the agent acted on stale memory" mean, how Verity labels
those without knowing which days were nudged, and what would prove a label
wrong. It exists so the arm's headline numbers cannot be made true by
moving their own definitions.

**Governs:** the APPLIED / NOT-APPLIED / UNDECIDABLE labels (v1 §Metrics 4),
the HARM label (v1 §Metrics 5), and the citation standard for both.
Everything else — invocation counts, false-nudge count, overhead pairing,
H1–H5 verdicts — is computed by GiLMore from the full bundle AFTER Verity's
labels are delivered and frozen. This file produces labels and citations,
not the arm's numbers.

**Freeze mechanics.** Rule-only; results land in the adjudication worksheet,
never here. Post-freeze edits: none. If Brian reshapes the arm, a v2 of this
rule is written BEFORE adjudication starts, superseding this file by name.
Editing after seeing data is the one move this file exists to make impossible.

## The material Verity sees

The arm-stripped slice of the returned bundle only: session files with every
line containing `recall-nudge` removed (this deletes the injected
`[recall-nudge]` messages and the extension's `pi-recall-nudge` durable
entries), sessions renamed to opaque ids. The `project_recall` tool events
(calls and results) remain — they are the substance being judged.
Statistical leakage (invocations clustering on ON days) is inferable in
principle; that is acceptable and is the same trigger-agnostic stance as
S4: labels are content-based, never arm-based.

**Blinding mechanics, stated honestly:** the arm map cannot be secret from
Brian (he flips the days) and the schedule is committed publicly in
`FREEZE.md`/`SCHEDULE.txt` for verifiability. Blinding is therefore enforced
by procedure, not cryptography: the rater receives only the stripped slice,
does not open the schedule, seed, arm map, or full bundle before labels are
delivered in writing, and says so when signing the label sheet.

## Labels (per session in the slice)

Verity labels each session that contains ≥1 `project_recall` execution:

- **APPLIED** — the assistant's subsequent output cites, quotes, or acts
  consistently with content **delivered by a `project_recall` result in this
  session that originates from a PRIOR conversation**. Citation = quote the
  delivered toolResult line and the output line that used it. Prior means a
  source conversation other than the live one (result text names the store
  plus a conversation id/timestamp from another session; live-session echoes
  do not count — the F2 c1/c3 lesson).
- **NOT-APPLIED** — recall ran, delivered prior content or not, and the
  output neither cites nor acts on delivered prior content. Citation = the
  output's actual basis.
- **UNDECIDABLE** — the trace does not settle it (truncated result, ambiguous
  reference). Recorded, never forced, counted in the denominator with its
  label.
- **HARM: yes/no** — independently of APPLIED: did the output commit a stale
  or wrong-scope action **attributable to recalled content** (acted on a
  superseded value, wrong-project constraint)? Citation = the delivered line
  and the acting line. "No recall-informed actions exist" is the trivial
  yes-no answer, recorded as such (R2's condition-3 discipline).

Sessions without recall executions get no labels; they are counted in the
denominators as no-recall sessions.

**Falsifiers (what would prove a label wrong):** a cited "prior" line that is
actually a live-session echo; an APPLIED citation where the output line
predates the recall call in the transcript; a HARM=no on a session where a
delivered superseded value appears verbatim in an acting line. Any of these,
found later, invalidates the label sheet and re-adjudication of the affected
sessions is mandatory, with the failure recorded.

**Substitute rater:** if Verity is unavailable when a bundle lands, the
substitute is named at that time by GiLMore from the flash lanes — named
before seeing the slice, never after.

— Design seat: Stratum, 2026-09-12. Sources: proposal v2 (change 5), v1
§Adjudication, S4-ADJUDICATION.md (pattern), F2/f3 sections of
RERUN-20260910-stageB-results.md, R2 result condition-3.
