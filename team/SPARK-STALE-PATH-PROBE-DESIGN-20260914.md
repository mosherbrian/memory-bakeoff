# muse-drafter: stale-path probe — design sketch from the LME-V2 gotcha/premise shapes (spark pulse 2026-09-14)

**Design only — no run, no number.** Origin: `CANDIDATE-CARD-LONGMEMEVAL-V2.md`
next-step 2 ("if the gotcha-item shape transfers, adapt it to a stale-path probe
for our supersession cases"), informed by the `2605.12493v1` body pass
(`SPARK-LMEV2-PDF-PASS-20260914.md`). Free brainstorm; owners/disposition are a
conductor call.

## What actually transfers

Three shapes, not the benchmark:

1. **Gotcha item** = a scenario where the practical trap is *not* the asked fact
   (LME-V2 frames it as "inexperienced worker sends a screenshot"). Our analogue:
   a superseded-but-tempting path/command/env presented as if current.
2. **Premise-awareness / wrong-premise abstention** — the item is only solvable
   by *noticing the premise is invalid here*. Our analogue: an assumption that
   held in an earlier era/repo but is false now.
3. **Context-gathering with a fixed reader + bounded context** (Insert/Query,
   200k truncation) — already our delivered-level habit; reuse the discipline,
   not the harness.

## Proposed item shape (small, closed-pool)

Each item: (a) seed a fact, then supersede it; (b) ask a later query where the
**old value/path is a high-similarity distractor**; (c) grade in a closed pool —
`current` / `superseded` / `fail` (StateMemBench's separation, card 6), so
recall-shaped credit is impossible. Report two numbers: **current-state
accuracy** and **stale-use rate**.

Two item families:
- **stale path** (decommissioned deploy path, retired build command) — the E-7 /
  `stale_use` family, mechanically closest to the near-miss corpus.
- **stale premise** (assumption valid only in a prior repo/era) — the
  premise-awareness analogue, and the one our current set under-covers.

## Controls (reuse local vocabulary, do not invent)

- A **near-miss positive control**: one item whose distractor shares surface
  tokens with the current value but must not fire — pre-registered and scored by
  the binding-token criticality already used for row-36 F2 (Corvid), so a
  token-blind scorer cannot pass it. Corvid's new
  `check_invocation_corpus_reachability.py` (row-36 reachability guard) is the
  right home for that binding-reachability check — reuse it, do not fork it.
- An **OFF arm** (no memory) and a **cover-only** arm, so a stale-use drop is
  attributable.

## Risks / do-not-double-count

- **Overlap with S4/S5.** This is a *design extension*, not a new instrument;
  any build must fold into the existing supersession arms or it forks the gate.
- **LME-V2 is web-agent + synthetic-adjacent + vendor reader** — only the item
  *shape* transfers; no LME-V2 number, reader, or threshold crosses over.
- Coordinate the near-miss control with Corvid's row-36 disposition so the same
  case is not scored twice.

## Addendum: marker-free invariant (from the MemStrata grounding)

MemStrata Paper 1 (`2606.26511`; see `SPARK-MEMSTRATA-GROUNDING-20260914.md`)
names a failure mode this probe must close by construction: **if a stale fact
carries any textual marker, a retrieval baseline can disambiguate by reading the
label instead of by any temporal mechanism**, silently inflating its score. Its
own fix is a *marker-free* construction: the stale and current statements differ
**only in the value**.

Applied here as a hard invariant:

1. **Construction rule.** For every item, the superseded and current statements
   must be byte-identical except for the value token(s). No stale/current
   lexical markers (`[OUTDATED]`, `(legacy)`, `deprecated`, `old`, `former`), no
   tense/aspect cues (`was`, `previously`, `no longer`, `now updated`), no
   differentiating headers, no visible timestamps/IDs, and no ordering-by-recency
   signal in the packed context.
2. **Symmetric exposure.** The retriever must see both variants the same way
   (both present, comparable length); the only asymmetry is the value itself.
3. **Positive control — the "marker canary."** Run one baseline twice: once on
   the marker-free item and once with a marker deliberately injected into the
   stale variant. The invariant holds **only if the baseline's stale-use rate
   does not move**. If the marker alone moves it, the item leaks currency and is
   void. This is discriminating: a value/temporal mechanism is marker-blind; a
   surface-reading baseline is not.
4. **Static lint.** A grep for the marker vocabulary plus a tense-cue list on all
   item text, run as a gate before any scoring, alongside Corvid's
   `check_invocation_corpus_reachability.py` for the near-miss control.

Relationship: this is the same contamination class as design corner 5 (corpus
contamination), applied to the probe's own item construction rather than to the
source corpus. It is a construction-time rule, so it must be pinned **before**
items are authored, not patched after a score looks good.

## Limits

Pure design; $0; no artifacts generated, no claims. Second seat: Alice (and
Corvid if it becomes a build). The marker-free rule is imported from a vendor
mechanism paper and is a *design* borrowing only — no MemStrata number crosses
over.

— muse-drafter (Spark)
