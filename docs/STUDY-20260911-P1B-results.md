# STUDY-20260911-P1B — results (rerun on the delivered-level-integrated adapter)

Rerun of STUDY-20260911-P1 after the retrieval-without-delivery defect was
fixed (P1 root cause 1: the `pi-perseus-recall` adapter returned a bare
string that never reached model context; see
`/var/home/bmosher/memory-bake-off/implementer/repo/docs/STUDY-20260911-P1-results.md`
and `.../repo/scripts/experiment_20260911_p1/PHASE0B.md`). Conductor gate
on the re-smoke (commit `7acb72e`): PASS — delivered-level gate live, model
answer quoting the record.

Walk: 2026-09-11T16:30:53Z→16:38:40Z, 24/24 slots, SAME frozen scientific
content as freeze `4048e12` (per-case hashes verified IDENTICAL to the p1
prep manifest at setup), fresh per-slot worktrees/stores/vaults under
`/var/home/bmosher/.local/share/memory-bakeoff/experiment-20260911-p1b/`
(ledger: `.../experiment-20260911-p1b/ledger.jsonl`; delivery gates:
`.../experiment-20260911-p1b/delivery.jsonl`). Vault isolation 24/24,
nudge genuine-resume 16/16, supersession toggle receipted (B false /
C true).

**DELIVERED-LEVEL GATES 24/24 PASS** (G1 exec↔delivered parity per
toolCallId, G2 arm-A zero recall, G3 arms-B/C ≥1 record key delivered) —
every behavioral contrast below is unconfounded: B/C models demonstrably
received record content (mean 2–3 delivered recall results per slot).

## Ledger (frozen verifier outcomes)

| Case (kind) | A | B | C |
|---|---|---|---|
| P1-1 tessellate-export (history-needed) | fail / pass | pass / pass | pass / pass |
| P1-2 quarryline-ci (stale-prevention) | fail / fail | fail / fail | fail / fail |
| P1-3 gullwing-deploy (scope-preservation) | pass / pass | fail / pass | fail / pass |
| P1-4 cobalt-invoice (current-only-noise) | fail / pass | pass / pass | pass / pass |

**Every frozen-verifier FAIL decomposes to two verifier spelling artifacts
plus two stochastic A-arm runs — there is not one behavioral failure in
arms B or C:**

- **P1-2 R2 (12/12 slots, ALL arms, both reps):** every run wrote
  `"runner": "schedulerctl"` — the CLI named in MAINTENANCE.md's own
  `schedulerctl run maint` — and R2's frozen fullmatch
  `scheduler(?:-service)?` rejects it. NO_STALE_SELECTION PASS 12/12;
  job `maint` 12/12; R4 PASS 12/12. Same artifact as the p1 walk.
- **P1-3 R2 rep1 (B and C identically; A passed):** both wrote
  `"strategy": "flux-managed GitOps"` for production — DEPLOY.md's own
  heading phrase — and `strategy_denotes` accepts only exact tokens
  (`flux-managed`, `flux`, …). Staging `pull-deploy` correct; NO_STALE_ACTION
  and NO_OVER_APPLICATION PASS in all B/C slots (scope handling correct
  4/4). Rep2 (plain `flux-managed`) passed.
- **P1-1 a-rep1** (fail, wrote 4, no recall) and **a-rep2** (pass — wrote
  3 without any recall source, at 110,227 tokens / 44 s of exploration;
  a lucky baseline pass) → A fail/pass.
- **P1-4 a-rep1** (degenerate 5,077-token run wrote `csv`/`2`/90;
  a-rep2 normal pass) → A fail/pass. B/C passed 4/4 WITH the noise
  records delivered — the no-regression-from-noise control now reads
  unconfounded.

## Delivered-record evidence (supersession at MODEL level)

Keys present in DELIVERED toolResult text (delivery.jsonl):

| Slot family | B delivered | C delivered |
|---|---|---|
| P1-2 (both reps) | c1(stale) + c2 + d2-current | c2 + d2-current — c1 never |
| P1-3 (both reps) | c1(stale) + c2 + d1-staging + d2-current | c2 + d1-staging + d2-current — c1 never |
| P1-1 (both reps) | c1 + c2 | c1 + c2 |
| P1-4 (both reps) | c1 + c2 (noise) | c1 + c2 (noise) |

The deprecated record reached B's context in 4/4 supersession-case slots
and NEVER reached C's context (0/4), while the current replacement and the
differently-scoped still-valid record (d1-staging) reached C 4/4. This is
ROUND3's EXPLICIT_LINEAGE behavior replicated at the DELIVERED level on
this build (labeled per the provenance block: this linux-x86_64 binary is
source-identical, NOT byte-identical, to the Gen21-measured arm64
artifact).

## Decision-rule evaluation (planner's four; frozen decide_p1.py emission,
EXPERIMENT_P1_PRIVATE=…-p1b)

1. **C retrieves the applicable replacement without presenting the
   superseded instruction as current, while preserving valid
   differently-scoped records: MET** — and now evidenced at the delivered
   level (table above), not merely the adapter stream.
2. **C prevents a stale-action failure observed in B: NOT MET (frozen
   operationalization; C P1-2 fail/fail).** Corrected reading: **B never
   exhibited a stale-action failure** — NO_STALE_SELECTION 12/12 in P1-2,
   NO_STALE_ACTION 4/4 in P1-3 — with the stale records DELIVERED into
   B's context. Receipt (P1-2 b-rep1 final answer): "Runner:
   `schedulerctl` — The current process runs maintenance through the
   scheduler service, invoked via the `schedulerctl` CLI. The legacy
   bastion/cron path is decommissioned." B's models mention-and-reject
   the stale procedure (exactly the behavior the planner's verifier rule
   permits). Prevention is therefore NOT ESTABLISHABLE — branch (i)'s
   substance, now with delivered-level proof that the failure mode had
   its chance in B and did not fire.
3. **C improves ≥1 history-dependent case over A in BOTH repetitions, no
   regression elsewhere: NOT MET (frozen).** Corrected reading: the
   recall benefit is demonstrated in substance — P1-1 B/C 4/4 PASS with
   the seeded license decision applied verbatim (P1-1 c-rep1 final
   answer: "The license server hard-drops connections when more than 3
   concurrent exports are in flight… Capping concurrency at 3…", at ~9 s
   and ~11 K tokens vs A's 34–44 s and 68–110 K tokens flailing), but
   the frozen operationalization requires A to fail BOTH reps and A's
   rep2 passed without recall (lucky 3). The P1-3 "regression" is the
   R2 phrasing artifact above, hitting B and C identically — not a
   C-specific regression. Under the frozen letter: NOT MET; under the
   artifact-corrected reading: improvement present in P1-1 for B and C,
   no behavioral regression anywhere.
4. **Overhead within 25%: WITHIN (both comparators).** C vs B (5 pairs):
   wall −1.8%, tokens +1.7%. C vs A (3 pairs): wall −47.4%, tokens
   −66.9% — recall-equipped runs were faster and cheaper because A
   flailed without memory on the cases it failed. (Direction reversed
   from the p1 walk, where "overhead" measured empty-delivery protocol
   cost.)

**Frozen emission: BRANCH (ii) — retrieval success WITHOUT workflow
success.** Reported per the freeze; the corrected reading is that this
label does not describe the behavior: every C FAIL is a verifier spelling
artifact (P1-2 `schedulerctl` ×2, P1-3 `flux-managed GitOps` ×1), and C's
deliverables were semantically correct in 8/8 slots (right value, right
job, right per-environment strategies, right export profile). Frozen
verdicts stand in the ledger; both artifacts are documented for the
reviewer, who owns verifier recalibration.

## What the study establishes (bounded)

- **Mechanism (delivered level, this build):** explicit seed-time
  supersession removed the deprecated record from the model-visible
  recall path in C 4/4 while preserving the current replacement 4/4 and
  the differently-scoped valid record 2/2, and leaving B's identical
  vault fully co-returning stale+current 4/4. Suppression is at the
  delivery boundary, before model context — the stale instruction never
  exists in C's world.
- **Practical (bounded by what fired):** recall benefit realized and
  cheap (P1-1: 4/4 B/C vs 1/2 A, ~4–10× faster/cheaper than A's failed
  explorations); no noise regression with records delivered (P1-4 4/4);
  scope preserved under an explicit production-only replacement (P1-3
  staging correct 4/4 B/C). The stale-action failure the design meant to
  prevent never fired in B in either round (records delivered, models
  mention-and-reject, current doc followed), so prevention-of-failure is
  unproven by absence of the failure itself — what IS proven is that
  supersession changes what the model can see (stale record in B's
  context, never in C's).
- **Bounds:** 4 cases × 2 reps; A-arm stochasticity visible (one lucky
  P1-1 pass, one degenerate P1-4 run) — single-run effects can flip the
  frozen rule-3 operationalization, reported as-is; frozen verifiers
  certify spelling-strict outcomes (two documented artifacts); planner's
  "supersession given correct lineage" framing retained (discovery out
  of scope).

## Provenance (carried verbatim per PROVENANCE.md)

- Study binary: `/var/home/bmosher/perseus-build/src/target/release/perseus-vault`,
  sha256 `c8a222ec7077d713212c2414d440586f564338aaa153eeb13b08ebf14854a172`,
  self-reports `perseus-vault 2.23.2 (9c82920)` (sha asserted before any
  vault operation in phase0b and at p1b setup). Build: `build.sh` with
  `GIT_HASH=9c82920`, rust 1.97.1, bookworm (Debian), DEFAULT features.
  The Dockerfile lean build is FORBIDDEN — keyword-only wearing the
  version string (no inspect surfaces).
- Gen21 pinned artifact: official `perseus-vault-aarch64-apple-darwin.tar.gz`,
  sha256 `e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb`,
  source commit `9c829207a4b44a8e679ba912b4c1c5608c8f1e36` (annotated tag
  `4f405f53f4c9b6a403df0d42cf0d59bf80c64da4`), MIT. Study binary and
  Gen21 artifact are source-identical, NOT byte-identical.
- Adapter (p1b): `extensions/pi-perseus-recall/index.ts` returns
  `{content:[{type:"text",text}]}` at all return sites; sha256 after fix
  `9be99551cca4cf8ad566b0a1fe8db402e9cb393147e3d7237a61d5bea7731fc7`;
  byte-identical across arms B/C (single-variable discipline held).
- Supersede direction (standing trap): `perseus_vault_supersede`
  parameter descriptions are AUTHORITATIVE — `from_key`/`from_category` =
  the OLD entity superseded; `to_key`/`to_category` = the NEW one. The
  tool's summary text disagrees; measured behavior agrees with the
  parameters (inverted Gen102 run retained as evidence).

## Time account

Walk ≈ 8 min machine (24 slots, warm models, 16:30:53Z→16:38:40Z vs 43 min
cold in p1). This phase (walk supervision, analysis, decision run, doc,
commit): ≈ 0.5 h implementer agent. Study aggregate after the p1 phase
(≈ 2.4 h) + P1B prep (≈ 0.5 h) + this (≈ 0.5 h) ≈ 3.4 h of the 4 h
budget. Implementer token/cost figures: unavailable (logged as
unavailable, not zero). Quota: GLM quota reset confirmed by Brian via
conductor; no refusals this phase. Walk abort rule (delivery gate) never
triggered.
