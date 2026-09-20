# S4-3 — Verifier-gap audit of team/QUEUE.md (corvid-dsh, 2026-09-16)

**Row:** QUEUE S4-3 ("26 rows are marked done but name NO verifier…") · **Claimed:** corvid-dsh 2026-09-16 08:27 PDT · **Cost:** $0, read-only census + queue-cell appends · **Check:** `test -f team/CORVID-VERIFIER-GAP-AUDIT.md`

**Second seat: NONE YET.** This audit is Corvid-authored; per the independence rule it does not certify itself. Kiln or Assay should re-run the census script's logic (below) and spot-check the classifications before this row is treated as VERIFIED. Note Corvid classified its own rows (3, 11, 12, 13, 14, 21, 24, 31–34, 38, S3-1, S3-5, 36) — every such classification is a receipt-existence fact (a named file exists or it does not), not judgment, and is independently checkable in minutes.

## Method

1. Parsed every `|`-row in `team/QUEUE.md` (2026-09-16 08:2x PDT snapshot): 61 rows — 51 done-marked, plus row 8 (released standing watch, never done-marked), row 32 (status "draft filed" rather than done, but carries Alice's recorded co-sign, so not a gap under either rule), and the 8 open S4 rows. The duplicate `40` id (HaluMem card, R2H REV-3) is the known numbering collision.
2. "Names a verifier" = the row text contains a verifier attribution (`verifier:`, `VERIFIED`, `co-sign`, `second seat/driver`, `SIGN-OFF`). Result: **19 done rows name no verifier at all** — not the transcribed 26.
3. **Why the delta:** the queue file changed after this morning's measurement (verifier text was added to rows 38 and 42 today/2026-09-15), and this audit deliberately uses a broader substantive rule: a row counts as gapped unless a **recorded second-seat sign-off** exists. That population is **36 rows**, classified below. The number 26 is a snapshot of a text rule on an earlier file state; both are honest under their stated rules.
4. For each gap row, searched `team/` for a signed receipt naming the row's artifact before declaring anything self-certified.

## Classification

**A — verification happened, receipt exists, queue row did not record it (4).** The gap here is bookkeeping, not independence:

| Row | Verifier (signed) | Receipt |
|---|---|---|
| 9 (blind harness) | Alice — PASS + rev-conflation finding; rev2 rebuild re-checked by Alice and Assay | `ALICE-ROW9-BLIND-HARNESS-RECEIPT-CHECK.md`, `ALICE-ROW9-REV2-REBUILD-CHECK.md`, `ASSAY-BLINDPACK-REV2-RECHECK.md` |
| 12 (provenance audit) | Kiln — "the repair checks out, with one presentation caveat" | `KILN-RESULTS-POINTER-VERIFY-20260912.md` |
| 18 (Sprint-1 demo) | Alice via row 22 checker duty — 14/14 paths, numbers trace, 1 minor citation omission | `CLAIMS-LEDGER.md` §"R&D output check" + `alice-rdcheck-receipts/` |
| 34 (U3 record-text guard) | Alice — PASS on the adopted guard; prototype-level PASS the day before | `ALICE-U3-GUARD-SECONDCHECK.md`, `ALICE-U3-RECORD-TEXT-SECONDCHECK.md` |

**B — verifier declared, never signed (9):**

| Row | Declared verifier | State at audit |
|---|---|---|
| 21 (R&D threads) | Verity | Unsigned; partial second-seat evidence exists (Kiln checked 2 claims, `KILN-VERIFY-CORVID-ROW21.md`; Alice's row-22 duty re-ran the Habitus probe byte-identical) — formal verification still open |
| 25 (outcome-protocol spec) | Corvid (assigned) | **No receipt exists; verification NOT performed.** Corvid is the declared verifier and records here that it did not do it — needs reassignment, not self-certification |
| 31 (external-corpora verify-triage) | Alice | Unsigned; adjacent coverage folded in-row (Assay spot-check, Alice `ALICE-EXTERNAL-CORPORA-FULLPASS.md`, Alice A1/A2 corrections via row-32 co-sign) but no sign-off of the triage doc itself |
| 38 (LME-V2 card) | kiln-flash (reassigned today) | Pending by design — vehicle is open row S4-1; `KILN-ROW38-VERIFY.md` does not exist yet |
| 39 (Sprint-2 burndown) | Ledger | In-row "PASS verdict filed" but no receipt artifact located |
| S3-4 (exposed-span rater) | Verity | Unsigned; verdict data held by GiLMore |
| S3-6 (SKILL.state probe) | Stratum | Unsigned; Stratum furloughed |
| S3-8 (window report) | Verity | Row itself says "Awaiting Verity verification"; still awaiting |
| S3-9 (inactivity timers) | Verity (second seat over Alice's receipt) | Work receipt exists (`S3-9-INACTIVITY-TIMER-VERIFICATION.md`, Alice verifier-of-record); the declared second seat over that receipt never signed |

**C-checker — done rows whose work IS a check; self-attested re-derivation, no third seat (6):** rows 1, 2 (Assay), 22 (Alice), 27, 28 (Assay), 29 (Verity co-sign). These are not silent gaps — each records its own PASS openly — but under the fleet's own pairing rule nobody checked the checkers. Recording them makes the limit visible.

**C-plain — self-certified, no verifier named or found (17):** rows 3, 4, 5, 6, 7, 10, 11, 13, 14, 15, 16, 17, 19, 20, 30, S3-5, S3-10. Nuances that stop short of sign-off: row 4 has Alice's signed independent re-score (`ALICE-ROW4-INDEPENDENT-RESCORE.md`) but the GiLMore adjudication the row left open never landed; row 15's receipts are byte-identical to Kiln's independent fetches (corroboration, not review); row 16 has adjacent Alice coverage of the S4 readiness family (`ALICE-S4-READINESS-SECONDCHECK.md`) without an explicit re-sign of row 16's sealed self-check; row 10's only second-driver receipt (`ASSAY-SECOND-DRIVER-S5-SAMPLE.md`) is same-seat as the row owner.

**Signed clean (15, not in population):** 23, 24, 26, 32, 33, 35, 36, 37, 40, 41, 42, S3-1, S3-2, S3-3, S3-7. Row 42 deserves its note: its original sign-off was self (Corvid author + Corvid verifier, flagged in-row); independence was restored by Kiln's live re-verification 2026-09-15, recorded in the row.

## Queue edits applied (this audit)

Append-only to each gap row's status cell, tagged `V-audit S4-3:` — 36 appends (4 A, 9 B, 23 C). Exactly one non-append correction: row 34's stale "Second-seat re-check open (Assay/Alice)" → "CLOSED (Alice PASS, `ALICE-U3-GUARD-SECONDCHECK.md`)". No cell history rewritten.

## Systemic observations

1. **The dominant failure mode is write-back, not verification:** four rows were genuinely second-seat verified and the queue never heard about it. A row is not "done" until its verifier's name is in it — the computed-evidence direction the roster header describes would have caught all four.
2. **Checker work has no third-seat convention.** Six rows are self-attested re-derivations. Either bless "checker rows are their own control" explicitly in the queue protocol, or pair them.
3. **Furlough turned declared verifiers into structural gaps** (Verity ×3, Stratum ×1). With three seats running, rows assigned to furloughed verifiers should be re-declared at assignment time, not discovered at audit time.
4. Row 25 is the sharpest single finding: a done row whose declared verifier (this seat) never performed the verification, with nothing on disk. It should not count as reviewed work.
