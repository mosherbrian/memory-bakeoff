# Kiln R&D pulse — instrument receipt-path hygiene audit (2026-09-12)

Thread: "build hardening: flaky-adapter sweep, receipt-path hygiene /
instrument smoke re-runs as committed." One turn, $0, no live-window
contact. Method: enumerate this lane's committed instruments; for each,
record whether a frozen as-committed receipt exists, and re-run it as
committed ONLY where the re-run cannot touch live experiment state or
rater blinding.

## Re-run as committed (this pulse)

| Instrument | Command as committed | Result at HEAD `bb0b4b0` |
|---|---|---|
| `scripts/experiment_20260912_native_capture/probe.sh` | `bash scripts/experiment_20260912_native_capture/probe.sh` | **exit 0**; scratch vaults only; receipts regenerated in place |
| `extensions/pi-change-trigger` suite | `bun test test/` (package.json script) | **15 pass / 0 fail** (41 expect calls) — matches the 15/15 first-run receipt (db31ea3) |
| `tests/test_pi_lcm_store_reader_contract.py` | `PYTHONPATH=/home/bmosher/.local/lib/python3.14/site-packages pytest … -q` | **12 passed** (this session's as-committed receipt, `bb0b4b0`) |
| longcontext_null + stale_use_penalty + agentmemory core/localization | same invocation | **28 passed** (neighbor no-regression run this session) |

**Probe determinism receipt (the substantive finding):** the re-run's
regenerated receipts differ from the committed ones (84cc6b9) in **volatile
identifiers only** — `created_at_unix_ms`, `auth-*` session ids, `mem-*`
note ids (12-hex, time-seeded, not content hashes). Every non-volatile
field is byte-identical: same note keys, same `status='proposed'`,
`links=[]`, buffer layer, same two-coexisting-undifferentiated-notes shape,
same admission dead-end. FINDINGS.md reproduces exactly at current HEAD.
The churn was reverted after classification (frozen receipts stay the
canonical evidence; the classification lives here).

## Audit-only (deliberately NOT re-run)

| Instrument | Frozen receipt | Why not re-run |
|---|---|---|
| `build_s4_packets.py --self-test` (B7) | WINDOW-OPENING.md item receipt | mid-window, rater-blinding-adjacent; Assay's power check today shows a bare B7 PASS is not load-bearing anyway |
| `s6_scan_after_write.sh` | `item4-s6-scripted-run.txt` (1fc8017) | touches the LIVE trial vault; window is open |
| `trial_smoke.ts` | runbook setup record | live pi config / trial vault |
| `r2h_deploy.py` | FREEZE.md hashes + sandbox smoke (b0b761a) | deployed R2H arm state machine; not idle-pulse work |
| `experiment_20260910b/c`, `experiment_20260911_p1` run drivers | results/ + RERUN dispatch receipts | metered LLM lanes; spend is not an R&D-pulse item |

## Gaps found (carried, not self-adopted)

1. **Volatile identifiers in frozen receipts.** probe.sh receipts embed
   time-seeded ids, so every faithful re-run looks dirty in git and invites
   either churn-commits or false alarms. Cheap fix (next build slice):
   normalize volatile fields at capture time, or a NORMALIZATION note in
   FINDINGS.md declaring the volatile field list.
2. **As-committed commands live in commit messages, not next to the
   instruments.** The PYTHONPATH/lane-HOME invocation convention is
   discoverable only from commit messages (d35cbdb, 1fc8017). A one-line
   `RUN-AS-COMMITTED` block per experiment dir would close this — this is
   the instrument-side version of my retro START item.
3. **Live-state coupling is implicit.** s6/trial_smoke/r2h are unsafe to
   re-run for non-obvious reasons (live vault, deployed state). A
   `LIVE-STATE:` marker in each dir would let future hygiene sweeps skip
   them without re-deriving the hazard.

— Kiln, R&D pulse 2026-09-12, ~15 min, $0.
