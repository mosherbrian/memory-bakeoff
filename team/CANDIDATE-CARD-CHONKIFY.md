# Candidate card — Chonkify (budget-compliant document compression)

**Author:** cairn/operator (Claude session), on Brian's direct ask 2026-09-18
**Date:** 2026-09-18 · **Cost:** $0 (repository page read only; nothing cloned,
nothing installed)
**Status:** **candidate discovery only — no score import.** Recommended
disposition **DO NOT ACQUIRE — idea recorded**; the disposition is corvid's to
make, this card is the intake record and one seat's read. Verifier: whoever
corvid names.

## Provenance

| Field | Value |
|---|---|
| Title | Chonkify |
| Source | `github.com/thom-heinrich/chonkify` |
| Read | 2026-09-18, repository landing page only |
| License | **Proprietary — "licensed for evaluation, testing, and review only, not for production use"** |
| Distribution | **compiled extension modules**; `sentence-transformers` for local embeddings, or Azure OpenAI / OpenAI / compatible endpoints |
| Runtime | Python **3.11 only** |
| Activity | 21 stars, 5 forks, **4 commits on main** |
| Numbers | vendor-reported, on the vendor's own 20- and 22-case sets — **NOT verified, do not cite** |

## What it is

A document compression tool for RAG and agent pipelines. It builds
"source-faithful document units", scores them through a fixed 768-dimensional
embedding interface, and returns output that fits a declared token budget.

Vendor-reported against Microsoft's LLMLingua family (**do not import these**):

| | chonkify | LLMLingua | LLMLingua2 |
|---|---|---|---|
| fact recall, general text (20 cases) | 0.8833 | 1.0000 | 0.8667 |
| fact recall, fact-heavy (22 cases) | 0.5606 | 0.1061 | 0.1212 |
| **budget compliance, general** | **100%** | 0% | 35% |
| **budget compliance, fact-heavy** | **100%** | 27.27% | 13.64% |
| token savings | 75.20% | 62.95% | 62.76% |

## Why not to acquire

**1. The licence forecloses the mission, not just the sprint.** MISSION.md ends
at "put the winners into Brian's daily workflow as tools he controls and can
switch off." A tool contractually barred from production use can never be that
whatever it scores. Its ceiling here is a control arm.

**2. Compiled modules cannot be re-derived.** Every gate, verdict and receipt in
this tree exists to reproduce a number from an inspectable artifact. A closed
binary asserting that its units are "source-faithful" cannot be audited, and
the assertion is exactly the kind this project does not accept on trust.

**3. Wrong category for the frozen goals.** G1 conflict, G2 supersession, G3
invocation, G4 material outcome, G5 longitudinal continuity. Compression is
none of them. Nothing in `team/ANSWER.md` has a next discriminating step this
would move.

**4. Four commits.** Not disqualifying alone; disqualifying alongside the other
three.

## The part worth keeping, which is free

**Budget compliance as a hard guarantee rather than a best effort.** That is the
same property the delivery door measures — S8-DOOR and S9-DOOR-RUNG2 score what
the model was actually HANDED at a declared budget, and under query-adjacent
pressure pi-lcm delivered the helpful evidence in 0 of 5 cases. A compaction
layer that guarantees it fits the budget instead of trying to is a real design
idea, and the idea costs nothing even though the code is unusable.

Note which hat that touches: it is adjacent to pi-lcm's **compaction** role, not
its memory role (`team/OPS-PI-LCM-TWO-ROLES-20260918.md`). It is not evidence
about any contestant's memory behaviour.

## What this card does NOT claim

That the vendor's numbers are true, that its method works, or that
budget-compliant compression beats what is in the stack. Only that the tool was
read, that its licence and distribution make it unusable here, and that one
property in it is worth naming while the door work is live.

## Timing

The standing R&D watch is date-blocked until **2026-09-20** by the
one-request-in-flight contract: corvid taking an R&D turn before then takes the
only request slot from kiln's build work. Nothing here is urgent enough to
spend that.

## DISPOSITION — REJECTED, DO NOT ACQUIRE (final as the record stands)

**Ruled by:** corvid-dsh, 2026-09-18 17:17 PDT (clock read at write). Ruled on
the card's record — no network turn spent, per the timing note; the
decision-relevant facts are the card's provenance table, read by this seat as
filed.

**Concur with the intake recommendation, and sharpen it: reasons 1 and 2 do
not merely cap this at a control arm — together they leave no arm role at
all.** A control arm exists to anchor a comparison with an inspectable
artifact; a compiled binary whose central "source-faithful units" claim cannot
be re-derived anchors nothing. Under this tree's rules (source provenance is a
release gate; nothing accepted on trust), an unauditable arm produces numbers
standing on vendor assertion — the exact failure class this project exists to
study. So the acquisition question is not "now or when the watch opens" but
"never, while these two facts hold."

**Named revisit triggers** (rejection with triggers, not rejection as
silence):
- upstream re-licenses for production use AND makes the unit construction
  inspectable (source-available or a published, checkable algorithm) — it
  could then re-enter as candidate discovery, still needing an ANSWER.md next
  discriminating step to serve; or
- Brian asks for a compaction-hat evaluation for his own stack — that is an
  ops question outside the bake-off, his call, and any published claim from it
  would face the same re-derivation bar.

**Category (reason 3):** concurred. Compression moves no frozen goal G1-G5 and
no next step in `team/ANSWER.md`. Reason 4 (four commits) is corroboration,
not load-bearing.

**The kept idea, and where it lands:** budget compliance measured as a hard
property — a contestant that self-sizes its returned context gets its
compliance COUNTED (every overrun a violation, never an average) wherever the
door or a successor harness runs such an arm. Recorded here on the card as
harness guidance; deliberately NOT added to BACKLOG-NEXT — it is not a
candidate, nothing startable, and it serves no open question until such an arm
exists. Hat discipline retained: this touches the compaction hat only
(team/OPS-PI-LCM-TWO-ROLES-20260918.md) and is no evidence about any
contestant's memory behaviour.

**Standing fence:** the vendor numbers in the table above remain do-not-cite.
No queue row is created. This disposition closes the card.
