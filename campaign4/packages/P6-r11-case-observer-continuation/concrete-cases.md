# P6-r11 — pinned concrete failed-verification / quiet-rest cases (independent)

- **Author:** corvid-dsh, action `P6r11-concrete-cases-1` (contract: package.md
  sha256 `a966c15176c7…`; disposition: `completion-allocation-1.md`)
- **Baseline:** immutable P6-r9 at `f1d7c86` — `case_entry.py` sha256
  `9a1bb23c…`, `r3harness/harness.py` `d7b4e517…`, `host_adapter.py`
  `231f45f0…`, `fixture_control.py` `f89b03fd…`, `fault_onset.py` `c6eff685…`,
  `seat_emulator.py` `516a6041…`, `fixture-wake-deposit` `97b5e9d1…`,
  `stagec-plan.json` `1263fdf7…`. **No r9 byte edited.**
- **Deliverable:** `concrete-cases/test_r11_failed_quiet.py` (executable,
  self-contained) and this pin. Branch-neutral: expectations describe baseline
  old-fails AND repaired new-passes; no candidate byte is referenced.

## Case set and exact commands

Run the whole set (one command):

```
cd /home/bmosher/memory-bake-off/campaign4/packages/P6-r11-case-observer-continuation
python3 -m pytest -q concrete-cases/test_r11_failed_quiet.py
```

Each case invokes the real r9 `src/case_entry.py` CLI with **no `--simulated`**
and only external collaborators intercepted (seat emulator processes; fake
`wake`, `systemd-run`, `systemctl`) — the accepted r9 test pattern. Timing uses
`seat_emulator.py --delay-s` (>8 s) and a real socket/incarnation binding derived
over the r9 plan; no fake clock and no simulator shortcut.

Cases (all require worker > 8 s and/or verifier > 8 s):

| id | case | control | delays | baseline (r9) expectation | repaired expectation |
|----|------|---------|--------|---------------------------|----------------------|
| FV-W | failed-verification | corrupt-after-worker | worker 18 s | rc3 `E_NO_ONSET`; sends `{worker:1,verifier:0}`; `committed_actions []`; no tamper | durable handoff; post-commit tamper; verifier rejects; `accept-open`, never `COMPLETE`; sends 1+1 |
| FV-WV | failed-verification | corrupt-after-worker | worker 18 s, verifier 18 s | rc3, no accept verdict | full continuation through verifier observation; 1+1; `accept-open` |
| QR-W | quiet-rest | none-declared | worker 18 s | rc3 `did not commit` | setup completes; quiet window + reopen `duplicate-end-ignored`; no new sends |
| QR-WV | quiet-rest | none-declared | worker 18 s, verifier 18 s | rc3 `did not commit` | delayed setup completes; quiet/reopen clean; no repeated alarm |
| FV-EXP | failed-verification | corrupt-after-worker | worker 40 s, grant 15 s | rc3 bounded failure, no `"verdict": "accept"` | bounded failure/INCOMPLETE, never success |
| QR-EXP | quiet-rest | none-declared | worker 40 s, grant 15 s | rc3 bounded failure, no `"verdict": "accept"` | bounded failure/INCOMPLETE, never success |

## Baseline result logs (captured, immutable r9)

```
# run A — FV-W, FV-WV
$ python3 -m pytest -q concrete-cases/test_r11_failed_quiet.py \
    -k "FV_W_worker or FV_WV_worker" -p no:cacheprovider
2 passed, 4 deselected in 96.28s

# run B — QR-WV, FV-EXP  (concrete-cases/baseline-run-expiry.log)
$ python3 -m pytest -q concrete-cases/test_r11_failed_quiet.py \
    -k "QR_WV or EXPIRY" -p no:cacheprovider
..                                       # 2 passed

# run C — QR-EXP
$ python3 -m pytest -q concrete-cases/test_r11_failed_quiet.py \
    -k "QR_EXPIRY" -p no:cacheprovider
1 passed, 5 deselected in 68.23s

# run D — QR-W (first combined run; FV assertion typo since fixed in the case)
1 passed (QR-W)
```

All six cases are green **as baseline old-fails assertions** (they assert the
r9 truncation/bounded-failure outcome, not candidate success). Observed budget:
the four `>8 s` cases take ~48–60 s each wall (mostly the delayed emulator
teardown); the two expiry controls ~68 s. A full-set run is ~4–6 min, which must
be scheduled inside kiln/corvid bounds, not guessed.

## Baseline reproduction semantics (old-fails)

- FV-W/FV-WV: `run.out` is `{"detail": "fault case has no independent onset;
  INCOMPLETE", "error": "E_NO_ONSET", "owner": "cairn"}`; the receipt has
  `sends {"worker":1,"verifier":0}`, `committed_actions []`,
  `applied_receipt.artifact_control: null` — the 8 s slice truncates a real
  >8 s worker before any handoff, so no corruption and no verifier. This is the
  r10 live defect reproduced injected on frozen bytes.
- QR-W/QR-WV: rc3 with `quiet-rest setup run did not commit` — same first-slice
  truncation; the branch never reaches its quiet/reopen checks.
- EXP controls: `duration_s 15` with a 40 s worker returns rc3 with no accept
  verdict, proving the cases distinguish expiry from success (bounded failure,
  no silent fall-through).

## Repaired (new-passes) obligations the cases enforce for the implementation

FV: after shared continuation, durable handoff must occur; `corrupt-after-worker`
must apply **after** the commit and **before** the verifier recompute, with
distinct before/after hashes; the verifier must reject and the final outcome
must be `accept-open` / never `COMPLETE`; exactly one worker and one verifier
send. QR: setup must genuinely commit, then observation/reopen must produce
`duplicate-end-ignored` with no new dispatch or alarm; original deadlines
preserved. These cases assert the r9 behavior and can be re-pointed at the
candidate entrypoint unchanged.

## Status

**COMPLETE in-bound**: six executable cases pinned with the exact pytest
commands and captured baseline result logs on immutable r9. No live effect, no
dependency, no r9 edit, no tailoring to the incomplete candidate. Returned to
Tern for the conditional kiln completion release.
