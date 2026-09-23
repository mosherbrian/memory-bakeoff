# P12-repair-1 — independent repair review (corvid)

- **Action:** `P12-repairreview-1`, start `17:24:04Z`, deadline `17:49:04Z`.
- **Claim:** `repair-1-claim.json` against `repair-1-decision.json` (`8da41851…`)
  and `repair-1-receipt.json` (`d4d4a29d…`).
- **Verdict: PASS.** Both defects are fixed and independently reproduced; frozen Go
  `cbfe3d9` and binary `cf54a94a` unchanged (no source repair/rebuild).

## Pins / integrity

- **47/47** claim hashes match (11 plans + 34 evidence + 2 decision); decision and
  receipt match the claim.
- Source `cbfe3d91d02c86942e7640cbd0fe41027bfcbad0`; release binary
  `cf54a94a…` — both unchanged from the initial candidate. Initial claim preserved
  (`completion-claim.json 2f597065…`).

## Fix 1 — conformance capture (P12-CONFORMANCE-EVIDENCE): PASS

- Shipped binary, pinned cases, cwd `agent-loop-p12`, **no checkout/rebuild**:
  `agent-loop conformance conformance/cases` → **rc=0, stdout 0 bytes, stderr
  `conformance: 125/125 cases ok, 1751 steps`**.
- My fresh run's stderr hash `46160253…` **equals** the persisted
  `evidence/conformance-release-binary/stderr.txt` (`46160253…`); `stdout.txt`
  `e3b0c442…`; `rc.txt`. The original 0-byte file is preserved at
  `attempt-history/initial-evidence-superseded/conformance-cbfe3d9-EMPTY-stdout-only.txt`.
- **Root cause confirmed:** the summary is written to **stderr**; the initial
  stdout-only capture was empty. (Claim distinguishes 125 cases from 126 Go test
  functions — my earlier `go test ./internal/conform` count was 126 functions.)

## Fix 2 — L6 detection-to-ack bound (P12-L6-INTERVAL): PASS

Corrected `l6_eval` (`plans/live-driver.sh:134-146`):
`0 <= det <= 30 and 0 <= gap <= 60 and own <= 90`, where `gap = ack − settled`,
`own = ack − deadline`; no ack → FAIL; missing deadline/settled → INCOMPLETE.

Independent negatives I executed directly against the repaired predicate (deadline
`16:00:00Z`):

| det | ack | gap | expected | got |
|---|---|---|---|---|
| 25 | 88 | 63 | FAIL | **FAIL** |
| 25 | 85 | 60 | PASS | **PASS** (exact 60) |
| 25 | 86 | 61 | FAIL | **FAIL** |
| 30 | 90 | 60 | PASS | **PASS** |
| 30 | 91 | 61 | FAIL | **FAIL** |
| 31 | 31 | 0 | FAIL | **FAIL** |
| 10 | 100 | 90 | FAIL | **FAIL** |
| 10 | 89 | 79 | FAIL | **FAIL** |
| −10 | 30 | 40 | FAIL | **FAIL** |
| 10 | none | — | FAIL | **FAIL** |
| (no deadline) | 20 | — | INCOMPLETE | **INCOMPLETE** |

**Old predicate reproduced:** `r1-repair-tests.sh` on
`attempt-history/initial/plans/live-driver.sh` (`c2f80e2f…`) → **55 PASS / 3 FAIL**,
the three exactly the defect cases:
`ack 61 s after detection`, `detection 25 s ack 88 s (63 s gap)`,
`detection 10 s ack 90 s (80 s gap)` — all wrongly accepted before.
**Repaired driver:** `r1-repair-tests.sh plans/live-driver.sh` → **58 PASS / 0 FAIL**.

## Regressions on the repaired driver

- `f1-helpers.sh` → **29 PASS / 0 FAIL**.
- `e-wall-reload-p12.txt` re-run with the repaired driver: 3 real reloads,
  schedule unchanged, `LATE_FROM_DEADLINE=0`, WALLSTOP 1, cleanup 1, driver gone.
- Go `cbfe3d9`/binary `cf54a94a` unchanged; conformance 125/125; host parity and
  mutation from the initial candidate stand.

## Prior intake focus — each as evidence / result / remaining gap

1. **Ack ≤60 from detection and ≤90 total:** *fixed* (table above). No gap.
2. **Missing-ack / no-notification liveness:** `l6_eval` FAILs a delivery-only
   timeout (evidence). **Remaining gap:** the product never escalates a timeout
   nobody acknowledges (`waiting_on=director`); not ack/recovery — carried.
3. **Current principal/session authority:** `timeout_p12_test.go` rejects a
   changed-principal (forged) and conflicting ack; my CLI run refused wrong
   actor/action. No new gap.
4. **Replay — duplicate notice vs dispatch identity:** replay is `already-handled`
   with stable `T-<action>` identity and no new wake (A). **Remaining gap:** a
   duplicate director *notice* is possible after a failed-cancel settlement plus a
   later successful replay — never a duplicate cancel/dispatch.
5. **Calendar backward-clock:** **not exercised**; needs controlled injected
   clock/schedule evidence without changing the host clock. Not auto-accepted —
   carried to live signature.
6. **Empty conformance log:** *fixed* (shipped-binary replay, above).
7. **Hygiene:** real argv; isolated real stop/reload; profile-safe cleanup; no
   leftover transient units; installed preview `221bb3aa…` unchanged (main stays
   preview).

## Effect

**PASS** on both repairs, with the carried gaps (2, 4, 5) explicitly listed for the
live signature — none blocks this repair. No new source edits by corvid; no
live/main/install. Returned to Tern.
