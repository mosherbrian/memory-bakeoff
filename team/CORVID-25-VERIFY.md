# CORVID-25-VERIFY — verdict on QUEUE row 25

**Verdict: VERIFIED PASS** (design fidelity, per the row's design-only scope)
**Verifier:** corvid-dsh · 2026-09-17 16:23 PDT (clock read at write)
**Independence:** the spec was authored by Assay (furloughed 2026-09-15); corvid
authored neither the spec nor any gate for this row. Corvid's only prior touch
of this row was the 2026-09-16 S4-3 audit line noting the verification had NOT
been performed ("declared Corvid UNSIGNED") — this receipt discharges exactly
that. This verification was lost to the 09-17 engine-stall loop and re-sent
directly by cairn; filed now from the live session.

## Declared check

`test -f /home/bmosher/memory-bake-off/team/SPEC-OUTCOME-PROTOCOL.md` → **rc 0**.
Spec sha256 prefix `ad1e4b865327cd1b`, 383 lines, mtime 2026-09-13 (pre-dating
no relevant event; design doc, no runs).

## What I checked, against the row's terms

1. **Matched-pair unit** — §1 defines task / task instance / matched pair /
   condition, with the arm label as harness-assigned condition "never the
   worker's or the system's self-report". §1.1 gives design A (within-worker
   ON/OFF, pre-committed schedule) and design B (across systems,
   counterbalanced order). §2 freezes the matching rule before data:
   family (frozen S5 rule, non-day-scoped override frozen explicitly),
   worker/system identity, starting state (commit/tree hash — drift is
   candidate-invalidating), size band frozen in advance, nearest-time with the
   S5 greedy tie-break and pair identity reported, no reuse. Minimum n ≥ 8 for
   any sign test, below that medians only with no significance language.
   Complete and computable.
2. **M1–M4 operationalized** — §3 gives each metric a unit, start/stop,
   detection source, and anti-gaming rule. M1: tokens primary from harness
   `tokenUsage`, DONE observed in state, not claimed; log-ratio pair statistic.
   M2: frozen failure kinds each mapping to a receipt; self-report excluded;
   counts, not rates. M3: redundant re-discovery split `redundant_delivered` vs
   `redundant_available_only`, state-scan record existence (not write
   receipts), canonical-id matching only (fuzzy = exploratory_only), false
   merges explicitly never rewarded. M4: Kiln's classes, raw AND
   high-confidence counts, `i_said` excluded, de-dup (60-char prefix, ≥2
   turns) and deliberate-probe exclusion with the exclusion count reported.
   §3.1 freezes the reporting table shape with arm purity and exclusions as
   columns. All computable from the named instruments.
3. **§5 de-identified correction-event schema + leak gate** — §5.1's JSON
   schema carries only salted hashes, opaque pseudonyms, and structural
   metadata; raw text/quoted spans absent by construction (explicit
   absence list). §5.2 leak gate fails closed: substring check against the raw
   corpus, bounded n-gram prefix check against a local-only reference, and
   count reconciliation to the pilot's aggregate card. §5.3 defines the two
   permitted uses (M4 calibration set; harness replay test — not a transcript
   re-run). §5.4 pins "aggregates only": excerpts stay local, only numbers
   travel.
4. **Prereg freeze checklist** — §6: five artifacts sha256-frozen and
   published before the first scored instance (spec, commit-reveal seed,
   adjudication rules, analysis plan + minimum-n, leak gate + schema version);
   nothing moves after the first instance; a needed change restarts the pair
   set and is reported as a restart.

## Source cross-checks (row's hard rule respected)

- `team/TRANSCRIPT-MINING-PILOT.md` read — **aggregates only**, per the row's
  own permission; no raw transcript content was read on this lane. Every
  spec claim about the pilot matches the card verbatim: the five correction
  classes (spec excludes `i_said`, matching the card's "fired 0 genuine
  times"); precisions (negation/`actually` ≈100%, `env_fact_correction` ≈5/7
  with quoted third-party speech as the residual noise, facts ≈85–90%);
  the six exclusion filters named in §5.1's `exclusion_filters_applied` are
  the card's six filter rows (isMeta, tool_result, subagent JSONLs,
  continuation summaries, task-notifications, seat-dispatch); the 60-char
  prefix de-dup and the "list the integers 1 to 60" probe exclusion both come
  from the card; the quote-aware matcher the spec wants before scale is the
  card's own named upgrade.
- AGENTS rules carried into the spec body: harness owns ground truth (§4),
  delivered-level counting (§4), false merges not rewarded (M3), exact
  context size + harmful/prohibited presence in a companion table (§3.1, §7).

## Limits

Design-only verification: there are no runs to re-derive and none are
authorized (§0, §9). Execution quality, and the future leak-gate script's
behavior on real bundles, are unverifiable until those artifacts exist. The
spec's own §10 verifier duties (matching-rule completeness, computability, §5
cannot carry raw content) are the basis of this PASS, and all three hold.
