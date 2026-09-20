# kiln-flash second-seat verify — Alice's R&D checker duty (QUEUE row 22)

**Verifier:** kiln-flash (sole doer seat) · **Date:** 2026-09-17 · **Cost:** $0, local reads only
**Subject:** the folded 2026-09-12 second-seat check by Alice
(`CLAIMS-LEDGER.md` §R&D output check + `team/alice-rdcheck-receipts/`),
originally verifier GiLMore (furloughed, structurally unreachable) — reassigned
kiln-flash 2026-09-17.
**Independence:** I authored none of it. The probe is Corvid's, the B7 /
agentmemory receipts are Assay's, the demo is Stratum's, and the check being
verified is Alice's. Blind holds.

## Declared check

`test -f /home/bmosher/memory-bake-off/team/CLAIMS-LEDGER.md` → **exit 0**. ✓

## What I re-derived myself this pass

| Alice's claim | My re-derivation | Result |
|---|---|---|
| All receipt hashes match | Recomputed sha256 of `probe-rerun.txt`, `powercheck.json`, `second-driver-rerun.json` vs `MANIFEST.md` | all 3 exact ✓; byte counts match (467 / 804 / 1097) |
| Reruns byte-identical to stored originals | `diff -q` each receipt against the sealed/stored originals: `repo-glm-dsh3/scripts/probe_20260912_habitus_provenance/probe-output.txt`, `repo-glm-dsh2/scripts/verify-20260912-assay-row1/sealed-b7-powercheck-20260912/powercheck.json`, `…/sealed-agentmemory-lifecycle-20260912/second_driver.json` | all 3 byte-identical ✓; sealed originals hash to the same three MANIFEST values, so the rerun↔sealed chain is closed at both ends |
| `probe.py` sha256 `d130f76a…` | recomputed | exact ✓ |
| Probe claim as scoped | read `probe-rerun.txt`: `available True`, `raw=raw_product product=product`, ids M001–M003, `verified`/`publishable`/native 3, VERDICT native path | ✓ matches ledger §1 verbatim |
| B7 gap re-demonstrated | read `powercheck.json`: self-test PASS with markers 1 == raw 1, all three canaries in `turn-001.json` (`key=record-secret-xyz`, `key=record-novel`, `[perseus-maint]`), `power_gap: true`, verdict "GAP: self-test PASS while substance leaked" | ✓ internally consistent; gap visible from the sealed receipt alone |
| 418/450 = 0.928889 | arithmetic: 418/450 = 0.9288888… | ✓ rounds to 0.928889 |
| agentmemory numbers + denominator note | read `second-driver-rerun.json`: r1/r2/r3 core 50/0, distractor 32/418, `all_three_agree: true`, AGREE, note distinguishing `418/418 = 1.0` from the 450-distractor denominator | ✓ matches ledger §3 |
| Stratum: 14/14 cited paths exist | swept every backticked repo-path in `SPRINT-1-DEMO.md`, tested existence | 15 unique path refs found, all exist (my pattern catches one more than Alice's 14 — a self-reference, not a source); none missing ✓ |
| Minor finding: S3's 11/8 receipted in `ROW9-BLIND-HARNESS.md`, not §3's listed files | finding confirmed real: `ROW9-BLIND-HARNESS.md` line 19 "11 items = 8 agent-confirmed + 3 operator-confirmed" | ✓ — and **already fixed**: the demo's S3 row (line 134) now cites that file, with Stratum's fix note at lines 219–221 |
| Spot number trace ("13 tests PASS") | grep `PORTFOLIO-P1-ADAPTER-RECEIPTS.md` | "13 passed in 2.67s" verbatim ✓ |

One checked-and-cleared alarm, recorded for honesty: my first locate of the probe
original hit `team/row-instrument-verify/probe-output.txt` (hash `1a924106…`,
differs) — that file is Alice's *separate* 2026-09-13 pre-exposure instrument
check, not the probe original. The true original sits in the probe dir and
closes the chain exactly as claimed. No defect.

## What I did not re-derive

The live instrument re-runs themselves (probe.py, B7 powercheck, agentmemory
second-driver). Alice's receipts close them by hash-chain — rerun output
byte-identical to the sealed original, both ends hash-verified by me today —
and the row itself records that no live/blinding-coupled instrument was re-run.
Re-executing them would duplicate her non-destructive passes and touch
instruments this row deliberately left sealed.

## Verdict

**PASS.** Alice's 4/4 verdict stands under independent hash, byte-identity,
content-consistency, arithmetic, and path/citation re-derivation. Her single
minor finding (S3 citation omission) was real and has already been repaired by
Stratum. Row 22's unverified flag can be retired.

— **kiln-flash**, 2026-09-17. $0, one turn, no LLM calls, writes confined to
`team/`. Read-only in `implementer/repo-glm-dsh2|dsh3`.
