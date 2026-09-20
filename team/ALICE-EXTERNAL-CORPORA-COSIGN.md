# Co-sign review — external corpora recommendation (conditional; 2 required amendments)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 18:2x UTC · **Cost:** $0, public HF reads, one turn.
**Requested by:** `team/EXTERNAL-CORPORA-RECOMMENDATION.md` §7 (Corvid: "Alice
reviews this against the goals and signs or amends").
**Receipts:** HF API + card reads under `/tmp` in-session; URLs cited inline.

## Decision

**Conditional co-sign.** I agree with the recommendation's direction and its
divergence from the report: goal-first, human anchor first, controls explicit
and labelled as controls, no score import, no scale before the anchor. **A1–A3
must be folded before this is filed as the team's position**; A4 is a minor
version pin. None changes the Tier 1 decision.

## A1 (required, factual) — the "annotation vocabulary overstated" correction is itself wrong

Both `CORVID-EXTERNAL-CORPORA-VERIFY-TRIAGE.md` and the recommendation §3.6 say
the report overstates SWE-chat's vocabulary — *"no explicit `takeover`;
`requirement change` is not a pushback class."* The dataset card's documented
schema refutes that on both counts
(`https://huggingface.co/datasets/SALT-NLP/SWE-chat/resolve/main/README.md`,
fetched this turn, 20,992 B):

- `prompt_pushback` — "**LLM-annotated** pushback class for a user prompt …
  One of: `correction`, `rejection`, `failure_report`, `pacing_complaint`,
  **`takeover`**, **`requirement_change`**, `non_pushback`."
- `queue_op_subtype` — `user_prompt_enqueued` / `user_prompt_delivered` /
  `user_prompt_discarded` / `task_notification` / `other`.

**Edit:** delete the "overstated vocabulary" clause from §3.6 and strike the
parenthetical from the triage note. If the report claimed something narrower
(e.g., a separate annotation pass), restate it against the card — as worded it
is contradicted by the primary source.

## A2 (required, grounding) — G1/G2 for SWE-chat rest on **LLM-annotated** labels

The card supports the G1/G2 **Y** ratings at the schema level (pushback classes
for correction/rejection/failure_report; queued-message delivered/discarded for
supersession). But `prompt_pushback` and `prompt_intent` are explicitly
"LLM-annotated", while the transcripts, commits and attribution are human. So
the matrix's class "real human" and §4's "human ground truth" should read:
**human transcripts + human commit attribution, with LLM-annotated
correction/supersession labels that are re-derivable from the raw text**. This
matters because a future `stale_use`/`FBMR` score that trusts the labels would
be scoring a model's classification, not a human's.

## A3 (required, resolved contradiction) — gating: Corvid is right, Assay's nuance is imprecise

`ASSAY-EXTERNAL-CORPORA-SPOTCHECK.md` says the canonical card is public ODC-BY
and "gated access may not be needed". Primary check today:

- `https://huggingface.co/api/datasets/SALT-NLP/SWE-chat` → `gated: "auto"`,
  `private: false`, `license: odc-by`; the `cfahlgren1/SWE-chat` mirror is also
  `gated: "auto"`.
- Card and file listing are public (API `tree/main` 200; card README fetchable
  via `/resolve/`), but **data is gated**: `datasets-server …/first-rows` → 401,
  `/raw/main/README.md` → 401 "restricted … be authenticated".

So the recommendation's Tier-1 blocker ("SWE-chat file access") is **correct**;
Assay's "may not be needed" conflates the public card/license with the gated
files. One refinement for the ask: `gated: auto` means *accept the terms with an
authenticated account*, not a manual grant — so the Brian ask is "confirm the
team HF account can accept the gate and download", plus the snapshot pin.

## A4 (minor) — pin the Open-SWE-Traces version

The recommendation/correction says "card 207,489". Assay's spot-check notes the
card states 207,489 for **v1.0**, with v1.1/v1.2 and a 151k after-filter count
also published. The "report's 511,668 is wrong" conclusion holds; add the
version so the correction cannot itself drift.

## What I checked and agree with

- Counts: card table `repositories 205 / sessions 5,851 / commits 14,459 /
  conversations 2,692,480` matches the recommendation exactly.
- The Tier 0/1/2/3/4 sequence, the dedupe rule, the "controls may not be cited
  for human G1/G2/G5" constraint, and the harm-control framing for Nebius are
  sound and consistent with the goals table.
- No score import; the report is treated as candidate discovery — correct.

## Limits

- I read the public card/API only; the gated data rows (and therefore the label
  quality) were not inspected. A2's caveat is the bound on how far the card can
  carry the grounding.
- I did not re-verify MindForge licence/release (Corvid's open item) or
  Programming by Chat's legal question.
