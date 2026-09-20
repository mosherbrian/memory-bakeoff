# Assay — instrument power-check register (campaign-1)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~20:2x PDT · **Cost:** $0
**Purpose:** one index of every instrument Assay has independently exercised this
sprint, what it found, severity, and the proposed fix — so the fixes can be
adopted (or consciously deferred) before window close instead of living only in
the RD log. **Receipts claim; the power check is the check.**

## Findings (open / fix available)

| # | Instrument | Finding | Severity | Proposed fix / status |
|---|---|---|---|---|
| 1 | `build_s4_packets.py` B7 self-test | count parity uses the same predicate as redaction, so a classification miss is invisible; **PASS while substance leaks** | **high** (S4 blinding assurance) | **FIX VALIDATED (Assay, `s4-b7-leak-gate.diff` `5469a56c…`)** — emitted-packet leak scan wired into the builder gate (fail-closed, packet bytes unchanged); power check: canonical PASS+leak vs guarded PASS+`LEAK-SCAN FAIL` rc1; clean rc0 (`ASSAY-S4-B7-LEAK-GATE.md`); not applied to live instrument |
| 2 | `verify_s4.py` delivered classifier | docstring says "header-anchored"; unanchored `re.search` counts a body-quoted/mid-line header as delivered (2 FPs) | medium (A7 over-count, recall-body bounded) | **FIXED (Assay, `ba62c45e…`)** — anchored `(?m)^…`; power check 6/6 (`ASSAY-S4-CLASSIFIER-FIX.md`) |
| 3 | `blind_pack.py` scorer guard | valid-JSON **non-object** rating lines crash (`AttributeError`/`TypeError`) instead of refusing; self-test asserts only `missing_item` + `tampered_key` | medium (pending adoption) | **FIXED rev2 `e2d91e81`** (re-checked: no crash; self-test now asserts it) |
| 4 | S6 `s6_scan_after_write.sh` rule | empty/errored MCP scan marks every healthy ACTIVE row a violation — cannot say "scan unavailable" | medium | **FIX VALIDATED rev2 (Assay, `s6-empty-scan-guard.diff` `b2679e8f…`)** — empty scan → `INCONCLUSIVE` with machine-readable `unjudged: N` + rc 0/1/2; true classes still fire; power check 8/8 (`ASSAY-S6-EMPTY-SCAN-GUARD.md`); not applied to canonical (instrument hash / re-freeze is the owner's decision) |
| 5 | S5 sample / RUN-RECEIPT | headline reproduces but **population drifts**; `--window-end` bounds start, not completion | medium (close reproducibility) | `s5_freeze_inputs.py` **built + verified** (frozen re-runs byte-identical); freeze at close |
| 6 | `build_s4_packets.py` receipt parser | header with trailing text crashes `parse_iso` (`split(" ",3)[3]`) | low (emitter never does it) | `line.split()[3]`; route to unsupported, not crash |
| 7 | `blind_pack.py` build leak gate | hidden-value half excludes short sealed values (`len>=8`+digit), so a packet leaking the confirmer word `agent` passes | medium (pending adoption) | **FIXED rev2 `e2d91e81`** (bare `agent\|operator` scrub added; re-checked no gap) |
| 8 | `s5_pairing.py` nudge detector | text-only custom content item (`{"type":"custom","text":"[recall-nudge]…"}`) missed because `content_text` reads `content`, not `text`; a nudged zero-call turn could enter NO-MEMORY pairing (Note 2) | low-medium (latent shape) | **FIXED (Assay, `eb01800c…`)** — regression test + power check 12/12 (`ASSAY-S5-NUDGE-FIX.md`) |
| 9 | `r2h_deploy.py` `close` traces collection | `rglob("traces")` matches the directory then `is_file()` drops it, so trace files are never collected and the manifest records a **false-absent** entry | medium (return-evidence completeness) | **APPLIED as REV-2** (Assay's `r2h-close-traces.diff` `f4c4b938…`, adopted by Stratum in `team/R2H-FREEZE.md` REV-2; canonical sha `06823431…`) — `traces/**/*` + collision guard; power check 11/11, existing harness `traces_copied True`; deploy re-send to Brian's work machine required before day 1 |

## Verified, no finding (positive controls added)

| Instrument | Check | Verdict |
|---|---|---|
| `build_s4_packets.py` `record_set`/unsupported | 9/9 scenarios incl. boundary + no-scan control | correct |
| Q1.2 isolation probe (7 providers) | independent driver + raw recompute | zero delta confirmed |
| agentmemory 418/450 = 92.9% | raw lifecycle re-derivation ×3 runs | agree |
| pi-lcm store-reader receipt (12/28) | blob-pinned re-run | agree |
| P1 receipts (13, 15; license; pin) | re-run / recompute | agree |

## Not yet independently power-checked (named gaps)

1. ~~`blind_pack.py` **build-time leak gate, sealed-value half**~~ **closed**
   by `ASSAY-POWERCHECK-BLINDPACK-BUILDGATE.md` (gate passes a packet leaking
   the short sealed confirmer word `agent`; hidden-set length/digit filter
   excludes `confirmed_by`/`timing`/`old_is`).
2. ~~`s5_pairing.py` **family inference**~~ **closed** by
   `ASSAY-POWERCHECK-S5-FAMILY.md` (10/10; boundary: only uppercase `TASK-`
   matches). (Multi-candidate `pair_turns` also closed:
   `ASSAY-POWERCHECK-S5-PAIRING.md` — greedy is not minimum-total and pairing is
   not tie-unique, a stated property.)
3. ~~Frozen historical scores — perseus Hit@3 `0.434`, bm25 `0.226`~~ **closed
   at counts/provenance level** by `ASSAY-SECOND-DRIVER-GEN38-SCORES.md`
   (1142/2631, 594/2631, adapter/dataset pins match); a raw retrieval replay
   still needs the absent MemConflict gold.
4. ~~S4 builder window-entry filtering and draft-secret redaction on user
   turns~~ **closed** by `ASSAY-POWERCHECK-S4-WINDOW-USER.md` (8/8; new
   low-severity note: a timestamp-less entry bypasses the window filter).

Detail artifacts: `ASSAY-POWERCHECK-S4-B7.md`, `ASSAY-POWERCHECK-
BLINDPACK-SCORER.md`, `ASSAY-POWERCHECK-S4-RECORDSET.md`, `ASSAY-POWERCHECK-
S4-DELIVERED-CLASSIFIER.md`, `ASSAY-POWERCHECK-S6-INSTRUMENT.md`,
`ASSAY-SECOND-DRIVER-S5-SAMPLE.md`, `ASSAY-S5-FREEZE-INPUTS.md`.

## Priority for close

Before any S4 packet is handed to a rater: **#1**. Before S5 is cited: **#5**.
Both have built fixes; neither changes a frozen criterion.

— **Assay** (worker-glm-dsh2).

---

## Refresh — 2026-09-12 ~23:4x PDT (open items re-run against current code)

Instrument hashes at this refresh: `build_s4_packets.py` `96904d8a…`,
`s6_scan_after_write.sh` `40ad1d6d…`, `r2h_deploy.py` `74e7ae86…`,
`blind_pack.py` `e2d91e81…`, `verify_s4.py` `e95fbf55…`.

| # | Finding | Status at refresh |
|---|---|---|
| 1 | builder B7 count-parity blindness | **FIX VALIDATED** — leak gate wired into the builder (`s4-b7-leak-gate.diff` `5469a56c…`; sealed `a4948be7…`); canonical leaky PASS+leak/rc0 vs guarded PASS+FAIL/rc1; packet bytes unchanged; canonical unchanged pending owner |
| 2 | `verify_s4` unanchored delivered classifier | **OPEN** — 2 false positives reproduce (`4dfe611e…`) |
| 4 | S6 empty-scan = false violation | **FIX VALIDATED rev2** — guard patch + power check 8/8 (`s6-empty-scan-guard.diff` `b2679e8f…`; sealed `28624d1a…`), machine-readable `unjudged: N` + rc 0/1/2 (Alice's 07:50 boundary finding folded in); canonical unchanged pending owner |
| 6 | builder header parser `split(" ",3)[3]` | **OPEN** (builder unchanged) |
| 3, 7 | `blind_pack` scorer crash / build-gate confirmer leak | **FIXED in rev2** (`e2d91e81…`; `9e95509d…`, `00576c58…`) |
| — | R2H `close` traces false-absent | **APPLIED as REV-2** (canonical `06823431…`; `R2H-FREEZE.md` REV-2) — patch `r2h-close-traces.diff` `f4c4b938…`, power check 11/11 + existing harness `traces_copied True`; check made re-runnable via sealed rev-1 (`42609f01…`, applied re-derivation `77354d28…`); deploy re-send before day 1 |
| — | R2H `close` privacy path | good (store hashed only, no copy) |

Also current: S4 in-window readiness on a **frozen** snapshot = 19 sessions /
134 turns / 376 markers == 376 raw / B7 PASS / leak-scan PASS
(`sealed-s4-frozen-recheck-20260912/readiness.json` `7e5119ff…`).

Re-run bundle: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/sealed-register-refresh-20260912/`.

---

## Refresh — 2026-09-13 ~10:5x PDT (rev 3; current-afternoon work folded)

Instrument hashes at rev 3: builder `6616c48e…`, meta-guard `6cd289e7…`,
lifecycle guard `f58a61c6…`. Previous refresh table (23:4x) is superseded where
it disagrees.

| # | Finding | Status at rev 3 |
|---|---|---|
| 1 | builder B7 count-parity blindness | **APPLIED as a guard** (GiLMore ruling; commit `413de36`, builder `96904d8a…`→`6616c48e…`; QUEUE row 26) |
| 2 | `verify_s4` unanchored delivered classifier | **FIXED** (`ba62c45e…`; power 6/6) — the earlier refresh's "OPEN" is stale |
| 3 | `blind_pack` scorer crash on non-object JSON | FIXED in rev2 (`e2d91e81…`) |
| 4 | S6 empty-scan = false violation | FIX VALIDATED rev2 (`s6-empty-scan-guard.diff` `b2679e8f…`); still **not applied** (owner re-freeze decision) |
| 5 | S5 population drift | freeze built + verified (`s5_freeze_inputs.py`) |
| 6 | builder header parser trailing text + colon form | **FIX VALIDATED (v2; closes Alice's colon-form regression)** — `builder-receipt-parser.diff` `5a4c39cc…` (guarded `4715558d…`, base `6616c48e…`), power check **8/8**; **not applied** (frozen S4 instrument → needs a ruling + re-freeze) |
| 7 | `blind_pack` build-gate confirmer leak | FIXED in rev2 |
| 8 | `s5_pairing` nudge detector | FIXED (`eb01800c…`) |
| 9 | R2H `close` traces false-absent | APPLIED as REV-2 (`06823431…`) |

Post-register instruments (not among the original 9), all second-seat checked:
exit-contract driver coverage 16/16 (applied `6a072f30…`; completeness control
applied `6cd289e7…`), identifier-lifecycle guard rev 4 (`f58a61c6…`),
map-hash completeness (`cda1ee4a…`), cross-copy drift (`f683903b…`),
required-metrics schema shape (`3ae6cf05…`), orphan-evidence rev 3
(`5ebef46f…`), ledger-count rev 2 (`d74ab1e9…`), RD-thread-labels rev 4
(`33c3365f…`), LongMemEval sentence boundary (`55e94f16…`).

**Open instrument items at rev 3:** #4 (S6 empty-scan guard, owner decision) and
#6 (builder receipt parser, needs an S4 ruling before the frozen bytes move).
Nothing else in this register is open.

Artifacts: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-builder-receipt-parser/`
(diff `5a4c39cc…` + power check `ba49c25b…` + sealed result `61540e31…`; v1
`92cf3a63…`/`915c0aa4…`/`d7820dcd…`/`063dc53f…` superseded);
`.../verify-20260913-assay-lifecycle-rev4-secondcheck/`.

— **Assay** (`worker-glm-dsh2`).

---

## Refresh — 2026-09-13 ~18:3x PDT (rev 4; close hygiene)

Suite state: **18 guards**; meta `check_checker_exit_contracts.py` `956f5338…`
(self-test PASS, **17/17 hold**); guard 18 `check_record_text_identity.py`
`0b8fd3aa…` (U3, adopted from this seat's prototype); coverage-map Layer C empty.

Pending/unapplied patches re-checked against current bases
(`team/ASSAY-PENDING-PATCH-SWEEP.md`):

| patch | base | status |
|---|---|---|
| `builder-receipt-parser.diff` v2 | `6616c48e…` | **APPLIES** (S4 ruling needed) |
| `a2-buffer.diff` v3 | `905f604c…` | **APPLIES** (A2 apply + outside restart) |
| `meters-topup.diff` | `f2d5c8ea…` | **APPLIES** (Brian's budget rule) |
| `checker-exit-coverage.diff`, `meta-coverage-completeness.diff`, `split-cue.diff`, `crosscopy-u8-v2.diff` | — | **superseded / already applied — do not apply** |

Open instrument items at rev 4: #4 S6 empty-scan guard (owner decision), #6
builder receipt parser (S4 ruling), A2 framing (Kiln/Cairn), meters budget
(Brian/GiLMore).

— **Assay** (`worker-glm-dsh2`).

---

## Addendum — 2026-09-14 03:0x UTC (leakage-field guard-14 delta)

Power check #? (not renumbered): does the proposed `leakage@k` guard-14 delta
detect the failure it exists for? Verdict **PASS / proposal validated, not
applied**. Real committed probe (`23a640c8…`) driven through its own
`check_run()` over a 17-case matrix: its 8 known misbehaviours (Alice B1–B3)
reproduce; a candidate delta pinning them matches 17/17; patched guard
self-test PASS, real CLI rejects declared-missing (rc 1) and the three live
trees stay a no-op (0 findings). **B4 found:** the probe's own waiver fixture
used a format guard 14 never reads. Artifacts:
`team/ASSAY-LEAKAGE-DELTA-POWER.md`,
`implementer/repo-glm-dsh2/scripts/verify-20260914-assay-leakage-delta/`
(matrix `752817d0…`, probe diff `c6bc7a94…`, guard diff `f7b0ffeb…`, both
`git apply --check` clean on dsh3). Owner Corvid.

— **Assay** (`worker-glm-dsh2`).

---

## Addendum — 2026-09-14 03:4x UTC (fleet-poller section-6 QUEUE pulse)

Power check: the self-serve QUEUE-row pulse (`fleet-poller.sh` §6). Verdict
**PASS as a power check; the instrument fails it**. The shipped predicate
matches 0 rows on the real 7-column schema (no `| open |` cell; lowercase seat
names); the obvious fix false-wakes a gated row and any seat named in another
row's text; a field-aware predicate (Eligible-seats cell, Status `open`,
gated excluded) matches exactly QUEUE 29. Diff `poller-section6.diff`
(`288766b8…`) `bash -n` clean and dry-run-validated with `wake` stubbed.
Artifacts: `team/ASSAY-POLLER-QUEUE-PULSE-POWER.md`,
`implementer/repo-glm-dsh2/scripts/verify-20260914-assay-poller-power/`
(matrix `9e621cc7…`). Owner builder/GiLMore.

— **Assay** (`worker-glm-dsh2`).

**Rev 2 (2026-09-14 04:1x UTC):** poller section-6 diff updated to fold the
verifiers' corrections — live registry ids (Corvid `7dfbfe83…` replaces dead
`b521c03e…`) and the Alice/Aletheia alias; harness gains the alias control.
`poller-section6-v2.diff` `48aba312…`, harness `7979d0a4…`, `bash -n` clean,
live dry-run fires Verity row 29 only. Rev 1 `288766b8…` superseded.

**Rev 3 (2026-09-14 04:4x UTC):** applied-poller verification. Live
`fleet-poller.sh` `ddc484e9…` carries the fix and fired its **first-ever**
QUEUE-row wake at 04:39:46Z (Verity → row 29, claimed 04:41); applied loop
matches an independent QUEUE parse (0 claimable today), no false wakes;
residual: duplicate-id alias pair + `MIN_GAP` can starve the second name.
`verify_applied_poller.sh` `f94de8b9…`; harness `60f2eaec…` made
snapshot-independent.

**Addendum (2026-09-14 05:2x UTC):** sibling instrument apply + second driver.
Alice's `ALICE-INSTRUMENT-FIXES.diff` (`073376c2…`) landed in `repo-glm-dsh2`
(commits `8fcaf5a`, `810cdd3`); canonical re-driven 22→26, dsh2 15→19→26 after
syncing the canonical-only contract test; four files byte-identical to canonical
(`cf59db82…`, `a1576482…`, `24d90afb…`, `805e03b1…`). Receipt
`team/ASSAY-INSTRUMENT-FIXES-SIBLING.md`. Residual: dsh3 missing the contract
test; dsh2 row-12 pointers open.
