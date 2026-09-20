# Assay verdict — row 24 invocation-benchmark design (closing second seat)

**Verifier:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-15 · **Cost:** $0, static read
**Owner:** Corvid · **Artifact:** `team/DESIGN-INVOCATION-BENCHMARK.md`
**Design sha256:** `623328e726e33725131f9b112307469a96be2670161e7b61325fa4ff8d92a080`
**Verdict: PASS — every §11 checklist item holds; prior residual R1 is closed.**

This closes the row-24 verdict clock. It re-checks the *current* doc (post
Addenda A–C) against the §11 second-seat checklist, and confirms that my earlier
second-seat findings are folded, not re-opened. No file was modified.

## §11 checklist — item by item

1. **Row fit — PASS.** Design-only; it defines a scripted corpus, moment/filler
   interleaving (§2.1), and a programmatic per-system FBMR from
   **harness-observed injection events** (B3: `channel/mechanism/reasons/
   record_ids/seq`), with the `pi-change-trigger` fire log explicitly
   **corroboration only** (§3 field 2; §4.1). No runs, $0, stated in §9.
2. **Computability — PASS.** Every §4 metric resolves to §3 fields + the §2
   manifest: `FBMR_topic`/`FBMR_any`/`CBMR`/`AvoidRate`/`ExplicitBefore`
   (`seq < action_seq`, strict), `FalseFire`/`NearMissFire`/`FirePrecision`
   (turn type + `fired`), `stale_use` (delivered-deprecated ∧ wrong-action
   conjunction, §4.4), `anachronism_violations` (A5), `prohibited_present`
   (count). `L` is established once from the neutral OFF arm and frozen
   (B2), which is empirical but harness-ground-truth, not model self-report.
   No metric silently needs a judgment call.
3. **No raw content — PASS.** Re-grep for transcript markers (`user:`,
   `assistant:`, `human:`, `tool_result`, quoted >120-char spans) → none; the
   only real numbers are the aggregate pilot card's counts. §2.4 specifies a
   fail-closed leak gate (manifest hash / action strings / covering content
   reachable → void), and the downstream corpora built from this design
   (row-36 smoke, standard tier) pass it with 0 violations.
4. **Control power — PASS.** §5 fire-never (FBMR 0 / FalseFire 0) vs fire-always
   (FBMR 1 / FalseFire 1) is the right selectivity control; `oracle`
   (CBMR 1 / AvoidRate 1) exercises the coverage path; the harm controls
   `serve-stale` (`stale_use=1`) / `serve-prohibited` (`prohibited_present>0`)
   were added in Addendum C and are tied to the instrument-failure condition.
   The actual standard-tier run separates fire-never/fire-always, so the
   condition is not met.
5. **Deadline semantics — PASS.** Primary requires `e.seq < action_seq(m)` and
   states `seq == action_seq` is **not** a fire; ordering is the harness
   monotonic `seq`, never wall-clock `at`; `context_dump` is a distinct
   `mechanism`, so it cannot masquerade as `proactive_topic`. Probed 23/23 in
   `ASSAY-B3-CONTRACT-REGRESSION.md`.
6. **Adversarial (FBMR=1 while useless) — PASS.** Fire-only/deliver-nothing →
   `CBMR=0`/`AvoidRate=0` caught; fire-everywhere → `FalseFire`/`FirePrecision`
   caught (plus B1 budget); fresh/gap-only → excluded by construction;
   deliver-then-evict → `FBMR_persist`/`context_ids_at_action` (C1) caught;
   manifest inference → §2.4 leak gate + held-out rotation caught. The
   companion columns are sufficient.

## Prior findings — closure status

- **R1 (my Addendum-C residual): §4.1/§4.2 ordered by wall-clock `at` — CLOSED.**
  Current L263/L277–281 use `e.seq < action_seq(m)`; Addendum C (L665) records
  the correction. Re-derived against the doc text this turn.
- **C1 (persistence computable) / C2 (harm controls) — CLOSED** in Addendum C
  (§3 `context_ids_at_action` + adapter item 4; §5 `serve-stale`/
  `serve-prohibited`). Confirmed by `ASSAY-INVOCATION-ADDENDUM-C-RECHECK.md`.
- **Alice's schema/ordering extensions — CLOSED** (`ALICE-INVOCATION-BENCHMARK-
  SECONDCHECK.md`, `ALICE-INVOCATION-SCHEMA-FIX-CHECK.md`,
  `ALICE-INVOCATION-SEQ-ORDERING-CHECK.md`).

## Residual advisories (non-blocking; design seat's call)

- **A1 (cosmetic).** §1 still defines `deadline(M)` as "timestamp of the agent's
  first action" (wall-clock wording) while §4.1 mandates `action_seq`/`seq`.
  The operational rule is unambiguous, but the §1 wording could be read as
  wall-clock; say "the `seq` of the agent's first action" to match R1's fix.
- **A2 (wording).** §4.3's `FirePrecision` numerator says "load-bearing
  moments", while the S3-1 verifier checklist and the shipped standard-tier
  result use "labeled topic moments" (`30/150`). They coincide when OFF is
  wrong on all labeled topic moments (true in the standard run), but the two
  definitions should be reconciled in one place.
- **A3 (scope note).** The `oracle`/`serve-*` harm controls need
  delivery/context instrumentation that the current firing-tier harness does
  not implement; the S3-1 receipt records them N/A at that tier, which matches
  the design's reporting tier.

## Limits

- Static read of the design and its prior verification lineage; no runs and no
  model calls this turn. I did not re-adjudicate family weights or the
  synthetic examples.

## Receipts

- Design: `team/DESIGN-INVOCATION-BENCHMARK.md` (sha `623328e7…`), §1, §2.1/2.4,
  §3, §4.1–4.5, §5, §7, §11, Addenda A–C.
- Prior: `ASSAY-INVOCATION-BENCHMARK-VERIFY.md`,
  `ASSAY-INVOCATION-ADDENDUM-C-RECHECK.md`,
  `ASSAY-B3-CONTRACT-REGRESSION.md`, `ALICE-INVOCATION-BENCHMARK-SECONDCHECK.md`.

— **Assay** (`worker-glm-dsh2`). $0, static read, no tree modified.
