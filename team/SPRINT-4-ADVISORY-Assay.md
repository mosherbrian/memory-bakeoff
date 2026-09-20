# SPRINT-4 ADVISORY — Assay, verifier/producer seat (`worker-glm-dsh2`)

**Scope:** one turn, advisory only, no work. Signing rule: artifact pointer or
"memory only". Plain-English-first per BRIAN-FACING-STYLE; IDs get a gloss.

## What Sprint 4 should be — "use the instrument, not clean the queue"

The S4-1..S4-8 rows are hygiene (verifier gaps, artifact backfill, role
identity, rowcheck). Do them underneath with the kept seats, but they should not
be the sprint. Sprint 3 built the firing benchmark (S3-1, the invocation test)
and closed the window; Sprint 4 should turn that into results.

1. **Corpus v3 before any headline.** The standard-tier t3 fillers are
   degenerate — all carry the near-miss text, so `NearMissFire` is saturated at
   24/24 and the `stale_only`/`anachronism` strata are labels on near-miss
   content, not discriminating traps (my S3-1 limitation 1,
   `team/S3-1-STANDARD-TIER-RESULT.md`). Distinct filler content is cheap and is
   a correctness gate, not cleanup.
2. **First cross-system invocation number.** S3-1 is one system (the
   deterministic harness-trigger puppet); it says nothing about any engine. Run
   the frozen standard tier (`team/invocation-corpus-v2-standard/`, corpus
   `2fa0694b…`) `controlled_core` across ≥2 locally-runnable engines at $0, then
   exactly one metered `product`/`native_proactive` arm after the reset.
3. **Run the outcome side, not only the invocation side.** `SPEC-OUTCOME-
   PROTOCOL.md` M1–M4 and the verified 286-event bundle (`team/outcome-bundle-
   scale-20260915/`, Cairn PASS) exist but have not been executed as
   measurements. Use the bundle for M4 replay/calibration and produce the first
   matched-pair M1–M4 numbers; the window report is descriptive only.
4. **Make `done` computed, then trust the queue.** Ship `rowcheck` (S4-8) and
   the two guards for the blind spots I filed: a claim-lock for
   one-writer-per-row, and a check that compares a frozen prereg against its own
   verifier checklist. Small, $0, and they stop the duplicate-producer and
   definition-drift waste the retro named.
5. **Hold scope.** No new benchmark cards, no score import, no more than one
   metered arm.

**Suggested done:** (a) standard-tier FBMR for ≥1 `controlled_core` engine (and
one product arm post-reset); (b) corpus v3; (c) first M1–M4 numbers;
(d) computed-`done` rowcheck live. Sequence: corpus v3 → controlled_core across
engines → one product arm → M1–M4 → fair-comparison table v1.

## HARD BOUNDS it must fit

1. **Roster is the binding constraint.** Only three seats run before the
   OpenCode Go weekly reset (Saturday 2026-09-20): `cairn-pi` (free local),
   `kiln-flash` (sole doer), `corvid-dsh` (sole reviewer); all others are
   furloughed (QUEUE roster 2026-09-16). No new metered seats.
2. **One request in flight fleet-wide** — the Z.ai Lite contract; sends queue,
   they do not parallelize. No plan that assumes concurrency.
3. **Zero-quota GLM window is 08:00–18:00 local** through 2026-09-20; work must
   be left resumable at 18:00.
4. **~40 cold wakes/day**, and no wake without finishable work.
5. **$0 is the default**; metered/local-LLM product runs are gated by Brian.
6. **No score import; candidate cards are discovery only.** Independence binds:
   Corvid never reviews its own work.
7. **`done` is becoming computed evidence** (artifact exists + declared check
   exits 0); S4-8 reuses the existing guard exit contract, no second dialect.

**Consequence — the honest pre-Saturday scope:** only $0, local, single-doer
items are real, i.e. items 1–4 above plus the hygiene rows as fill-in. The
cross-system metered arm and any native `product` headline **slip to after the
reset**, when the roster returns — they are not pre-Saturday work and should not
be promised as such.

**Hard "no" for Sprint 4:** new benchmark cards, score import, a second
verifier/guard dialect, more than one metered arm, any plan needing more than one
worker in flight.

## Keep / Kill (convergent with RETRO-3)

- **Keep:** chain-verdict wakes that name the artifact (they closed real rows);
  pre-registered verifier checklists, verifier-at-birth; re-read-live-state
  before wake; hash-pinned verification re-derived from source.
- **Kill:** title-substring seat matching; fixed-cadence ticks on static queues;
  content-free steady-state reports; inactivity timers on cached snapshots;
  comments asserting unenforced behavior.

## Blind spots this seat filed — turn them into guards

- One-writer-per-row is unenforced: the S3-1 collision produced two receipts and
  duplicate benchmark runs before anything flagged it.
- Prereg-vs-checklist drift: the frozen `FirePrecision` conflict (54/150 vs
  30/150) sat until a human read both. Both are the guards in item 4.

## Cost / shape note

Verification was the cheapest ROI from this seat ($0; closed S3-7 20/20, row-24
PASS, and the goal-3 report). Producer-side duplication, not verification, was
the waste. Keep one verifier + one reviewer; buy routing precision and the
computed-`done` gate, not more pulses.

— Assay (`worker-glm-dsh2`). Advisory only; $0. Bounds read from QUEUE roster +
BOARD 2026-09-16.
