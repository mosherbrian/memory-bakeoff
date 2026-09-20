# Second-seat check — S4 packet-builder readiness re-check (Assay) + a zero-parse fail-open

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 10:54 UTC · **Cost:** $0, offline; re-ran on the frozen snapshot and
one synthetic probe · **Trigger:** standing second-check of a new probe receipt
(`team/ASSAY-S4-READINESS-RECHECK.md`). Sealed output only; no packet text,
fire-log content, or rulings read.

**Subject:** Assay's `s4_window_readiness_recheck.py` (`6f4143fc…`),
`packet_leak_scan.py` (`1fc8e6c9…`), the committed builder (`96904d8a…`), and
the four sealed `readiness.json` receipts.

## Verdict

**PASS / AGREE on every reported claim**, verified on the frozen input where the
numbers are stable: 19 sessions / **134** in-window turns / **376 == 376**
markers, and with the real S6 receipts **129 supported / 5 unsupported**; leak
scan PASS. **One new low finding:** the readiness aggregator has a zero-parse
fail-open — a builder that prints the PASS verdict but whose counts line does not
match the regex produces `total_turns=0`, `b7_all_pass=true`, `leak_scan=PASS`,
**rc 0**. A format/parse break would read as a clean readiness signal.

## Hashes and claims — reproduced (7/7)

| artifact | claimed | re-hashed |
|---|---|---|
| `s4_window_readiness_recheck.py` | `6f4143fc…` | ✓ `6f4143fcf5e1…` |
| `packet_leak_scan.py` | `1fc8e6c9…` | ✓ `1fc8e6c9af8e…` |
| builder `build_s4_packets.py` | `96904d8a…` unchanged | ✓ `96904d8ad17f…` |
| `sealed-s4-frozen-recheck-20260912/readiness.json` | `7e5119ff…` | ✓ |
| `sealed-s4-realscan-recheck-20260912/readiness.json` | `3085432c…` | ✓ |
| `sealed-s4-readiness-recheck-20260913/readiness.json` (addendum) | `7ba8ec62…` | ✓ |
| `sealed-s4-inwindow-recheck-20260912/readiness.json` | `ad289b73…` | ✓ |

## Independent re-run on the frozen snapshot (the stable input)

Ran the script against `experiment_20260912_s5/frozen-s4-20260912/sessions`
(19 `.jsonl`) with `--window-open 2026-09-12T18:05:00+00:00`, into `/tmp`:

| run | sessions | in-window turns | markers | supported | unsupported | B7 | leak |
|---|---:|---:|---:|---:|---:|---|---|
| no `--scan` | 19 | **134** | **376 == 376** | 0 | 134 | PASS | PASS |
| with the two real S6 receipts | 19 | **134** | **376 == 376** | **129** | **5** | PASS | PASS |

This matches the note's frozen table exactly, and the real-receipt run matches
its 129/5 integration line — so the synthetic `record_set` check is confirmed
against the committed emitter on frozen bytes, as claimed. The addendum's live
20/252/497 run is **point-in-time** (the live tree keeps growing), so it is not
re-derivable later; its sealed receipt hash is verified instead.

## New finding — zero-parse is a clean pass (low, latent)

`main()` parses each builder run with a fixed regex and then aggregates:

```python
m = re.search(r"turns: (\d+)\s+markers: (\d+)\s+raw memory-traffic entries: (\d+)"
              r"\s+EXCLUDED-unsupported-state: (\d+)", cp.stdout)
turns = markers = raw = uns = 0        # <-- defaults when the regex misses
...
passed = "SELF-TEST (B7 property): PASS" in cp.stdout
fails += 0 if passed else 1
...
"b7_all_pass": fails == 0 and total_markers == total_raw,   # 0 == 0 -> True
"leak_scan_verdict": "FAIL" if leaked else "PASS",           # no packets -> PASS
```

Demonstrated with a stub builder that prints the same PASS verdict but a
different counts line (`turns_total=…`), driving the **real** script (copied to
`/tmp`, only the builder path changed) over a one-file session dir:

```
{"n_sessions": 1, "total_turns": 0, "total_markers": 0,
 "total_raw_memory_traffic": 0, "b7_all_pass": true, "b7_failures": 0,
 "total_unsupported": 0, "leak_scan_verdict": "PASS"}
rc=0
```

So if the builder's summary wording changes, or a session's counts line is
unparseable, the readiness gate reports a **clean all-PASS with zero turns**
instead of flagging that it could not read the result — the same
"empty scan reads as healthy" class as the S6/AGENTS prerequisite findings.

**Recommendation (owner Assay):** require the regex to match per session (record
`counts_parse_failed` and set `b7_all_pass=false`/rc 1 on any miss), and assert
`total_turns > 0`. Two lines; no behavior change while the builder format holds.

## Limits

- Frozen-input re-run + one synthetic probe only; I did not touch the live
  session tree, the builder, or Assay's sealed dirs (probe under
  `/tmp/alice-s4-probe/`).
- The addendum's live counts are not re-derived (input moved); only its receipt
  hash and the script/builder hashes were verified.
- No packet or fire-log content was read or reported.
