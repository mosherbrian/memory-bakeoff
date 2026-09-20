# Muse ideation batch 8 — verifier independence, auditable signatures, probe promotion

**Tag:** `batch8` · **Prompt sha256:** `cf3dc7376611f2a220fa8cee0a1015af3775691ac175e24facdf6c00c122277b` (`PROMPT8.txt`, recorded before send) · **Date:** 2026-09-14
**Authorization:** standing Muse cadence (Corvid thread, `RD-THREADS.md`; original Brian/GiLMore approval 2026-09-12, `scripts/experiment_20260912_muse_ideation/PROTOCOL.md`).
**Fitted cause:** the blinded S4/S5 evaluation has lost raters to exposure/recusal (QUEUE row 37: no unexposed rater on the metered lane; Corvid and Assay recused/exposed), and the new cross-tree parity probe (batch 7) sits built-but-unwired pending an owner decision. Both are live instances of the general problems below.
**Content policy:** public methodology only; no project detail, paths, results, or strategy.
**Cost:** one batched call; expected «$0.01 (openrouter `$0.00 today` before send).

## Prompt (verbatim, preregistered)

See `PROMPT8.txt` (sha above): five numbered public questions —
(1) failure modes and controls when a blinded evaluation's independent-rater
pool shrinks by recusal/exposure/conflict; (2) detecting verification collapse
to an allied verifier with no declared conflict; (3) making a verification
signature auditable (who/when/prior exposure); (4) edge cases when verifying a
deliberately-failing artifact, so red is neither called a bug nor normalized;
(5) failure modes and controls when promoting a one-off probe into a standing
check.

## Receipt

One tagged call, `ready=true`, `end_seen=true`, latency 23.67 s, 5,825 assistant
chars, no block signals. Meter `spent $0.0248` before and after; `openrouter
$0.00 today` — cost ≈ $0.00. Receipts:
`scripts/experiment_20260912_muse_ideation/receipts/batch8-*`.

## Dispositions (Muse proposes, Corvid disposes)

1. **Shrinking rater pool → quorum + non-overlap rule, `INCONCLUSIVE` branch**
   — **ACCEPT** `[E]`. Strongest item: our blinded S4/S5 pool has no unexposed
   rater (QUEUE row 37), and the honest answer is not to seat a friendly rater
   but to record the blind quorum as **failed**. Bounded probe: a blind-quorum
   register — publish seated raters with pairwise affiliation and an
   `exposure-flag`, and if the quorum rule (N independent, no shared
   affiliation) cannot be met, emit `INCONCLUSIVE — quorum failed` instead of a
   pass/fail. Owner Verity/GiLMore.
2. **Producer–verifier separation graph, no reciprocity** — **ACCEPT** `[I]`,
   narrowed. The affiliation half has no local data source (named limit), but
   the **reciprocity** half is checkable from our own pairings: no verifier
   should have been verified by the producer within K rounds (`COLLAPSED —
   reassign`). Bounded probe: a reciprocity check over `CLAIMS-LEDGER.md`
   verification cells.
3. **Fixed 6-field verification signature with `exposure-flag`** — **ACCEPT**
   `[I]`. Directly usable: `(verifier-id, artifact-hash, check-id/version,
   timestamp, exposure-flag, result)`, flag ∈ {`blind`,`saw-output`,`saw-key`},
   hash must match cited bytes, and any non-blind signature cannot count toward
   the blind quorum. Bounded probe: a signature lint over verification receipts
   (missing field / hash mismatch = invalid). Owner Corvid.
4. **Pre-registered expected-failure manifest with a distinguishing signal** —
   **ACCEPT** `[E]`, partial duplicate. Our `KNOWN_FAILURES.json` pins test
   identity and cause but no positive `expected: FAIL` signal, so a red-by-design
   artifact (e.g. the dsh3 parity probe before the `src` sync) is indistinguishable
   from a bug, and a green would read as "good news." Bounded probe: extend the
   manifest to `{id, expected, reason-code, distinguishing-signal}`; fail on
   `UNEXPECTED-FAIL` (wrong signal) and on `UNEXPECTED-PASS` (green on an
   expected-fail). The identity/cause half is DUPLICATE of the existing baseline.
5. **Probe→guard promotion gate** — **ACCEPT** `[I]`, one sub-point DUPLICATE.
   Checklist: owner + cadence + alert route; determinism trial 3/3 clean **plus
   one seeded bad input**; pinned threshold/data-version with review date;
   read-only or sandboxed. Bounded probe: a promotion-gate template, applied to
   `probe_crosstree_parity.py` as case 1. The "seeded bad input" sub-point
   duplicates the standing RESET_PLAN §7 critical-check rule (merged, not
   re-proposed).

**Net:** 5 ACCEPT / 0 REJECT / 0 DUPLICATE (two merged sub-points). No ACCEPT is
a finding until its probe runs with a receipt. Second seat open (Alice/Assay).

**Probe status (2026-09-14, Corvid):** disposition 1's probe is **built** —
`team/CORVID-BLIND-QUORUM-REGISTER.md` records 0 eligible blind raters on the
metered lane and the honest `INCONCLUSIVE — quorum failed` branch for the
exposed span. Items 2–5 remain unbuilt.
