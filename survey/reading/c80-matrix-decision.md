# Decision note c80 — three boundaries from c74–79: what is contracted, where the seam is, what flips the pilot

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 80.**
Skeleton first; own c74–79 plus lead corrections only; no new source/probe; no universal
all-history requirement; absent outcome measurement ≠ proof of no value. Deliver: ≤3
decision-discriminating boundaries, one recommendation, one reversal, explicit cell-correction
statement.

*(decision appended below)*

## Boundary 1 — real scoped contracts exist, each ending at its own edge

Four complete-within-scope contracts, all verified in c74–79 (corrections applied): provider
**hard-rejects oversized received text** (400/413, c76); Letta **rejects over-budget direct
commits** (precommit exit, c74) — but not merge/fast-forward (c75); Perseus **accounts for
compile-path omissions** (missing include in-band, tier manifest, input-cap truncation warned)
and `render --strict` **can reject warning-bearing output** — but integrity-drift checking is
**opt-in, default off**, and neither gate is in the default hook command (c79 corrected); Pi
**canonical instructions survive compaction by construction** (per-request rebuild, c77). None is
rival-free end-to-end; each is worth crediting exactly at its boundary.

## Boundary 2 — the seam every assumption crosses: the last hop

All four contracts stop where **host-side pre-send assembly** begins. Claude's index truncation,
Pi's unaccounted detail loss at compaction, Letta's merge path, Perseus's downstream delivery —
Brian's 109/301 class lives precisely in the seam between "artifact produced and accounted" and
"intended content was in what the model saw." Nothing inspected closes it; InstructionsLoaded is
the only observation hook and fires on **successful loads only** — omission exposure needs a
diff against an expected set, which is **unbuilt glue**. Caller code that treats "rendered /
committed / accepted" as "delivered" is the recurring wrong assumption across every product
read.

## Boundary 3 — the fact that would change the pilot, not just confidence

The guard pilot tests **enforcement**; the sponsor's dominant report is **application failure
despite stored lessons**, and separately a **delivery** defect (truncation). Pilot-internal
observation that flips priority: if the InstructionsLoaded ledger shows declared lesson files
**not firing** at `session_start`/`compact` for exactly the scopes where violations recur,
**delivery precedes enforcement** and the first pilot should be load-scoped, not
action-scoped. That is one existing event plus one ledger, not a new experiment.

## Recommendation and reversal

**Recommend:** keep the one-project guard pilot as default; add the existing-event load ledger
as pilot observation (no new mechanism); hold Perseus as delivery candidate until Boundary 2 is
closed or shown immaterial. **Reverse** if pilot violations occur only where loads demonstrably
fired — then enforcement is the binding constraint and delivery demotes.

**Cell correction (wording only, no rating change):** my c79 proposed cell must read
*"compile-path omission visibility + strict-mode warning rejection; drift check opt-in; gates
outside default hook command; host delivery outside"* — per lead corrections.

**Confidence: high on the four contract boundaries (direct reads + lead checks), high on the
last-hop seam being common to all four (each traced to its edge), medium that the ledger
observation is sufficient to arbitrate delivery-vs-enforcement (design judgment).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, CAPABILITY-MATRIX.md,
RECOMMENDED-DESIGN.md, panel-response-c79.md.