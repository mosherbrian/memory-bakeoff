# D-10 verify — kiln-flash verification of corvid's R2H day-0 go-ahead

**Verdict on:** `team/INTAKE/r2h-go-ahead.md` (corvid-dsh, 14:50 PDT) + the
declared check `team/tools/check_r2h_smoke_receipt.py`, against Brian's receipt
`team/INTAKE/r2h-smoke-receipt.json` (his work machine, ts 18:46:49Z).
**Verifier:** kiln-flash — I authored none of the three; corvid produced the
go-ahead and the checker, Brian produced the receipt. The blind holds.
**Date:** 2026-09-17 15:01 PDT (clock read at write) · **Cost:** $0, read-only.

## Result: VERIFIED PASS — the GO is sound; day 1 counts

## What was re-derived, not trusted

1. **Declared check, explicit path:** `check_r2h_smoke_receipt.py
   team/INTAKE/r2h-smoke-receipt.json` → rc 0, prints GO-AHEAD. `--selftest`
   → rc 0.
2. **Independent re-derivation from the raw JSON, without the checker:** all
   four hard checks true (pi_ran, nudge_delivered, recall_registered,
   store_unmodified); all three warn checks ALSO true (recall_invoked,
   store_named, prior_id_surfaced — so corvid's "no warnings at all" is
   accurate); `store_sha_pre == store_sha_post` byte-identical
   (`77dac2dd2f02…`, both 64-hex); verdict field PASS consistent with the
   fields; ts, exit 0, duration_s 283.3, session_file all present. Corvid's
   four-row table is verbatim-accurate to the receipt.
3. **Runbook mapping:** the HARD set is exactly step 5's assertion list
   ("nudge delivered, tool registered, store unchanged — sha256 before/after,
   asserted not promised"); step 6's promise is answered by corvid's file in
   the promised one-word form; the day-1 ask (one `eval "$(… flip)"` line,
   days counted by flips not dates, `status`/`close` your own timing) matches
   the runbook's Days 1–10 section in substance.
4. **Adversarial mutants on COPIES OF THE REAL receipt** (beyond the checker's
   synthetic selftest): lying store hash → `[STORE-MODIFIED]` rc 1; hard check
   flipped false while keeping `verdict: PASS` → `[HARD-FAIL]` +
   `[VERDICT-DISAGREES]` rc 1; `checks` object removed → `[NO-CHECKS]` rc 1.
   Every rejection names the failure and tells Brian what to do. The checker
   cannot be fooled by the receipt's own verdict field — the exact
   self-declaring-done shape this fleet has been burned by.
5. **The day-10 gap is named and carried:** the go-ahead's final section states
   the blind-rater problem (Verity furloughed; no seat that has seen the arm
   map can rate the arm-stripped slice; successor before day 10, not on it) and
   carries it on this row. Corvid also correctly notes corvid itself cannot be
   the rater if corvid touched the arm map.

## Limits, stated

- **Transit integrity rests on Brian's channel.** The receipt is a copy of his
  work machine's `~/.r2h/smoke/smoke-receipt.json`; nothing proves the copy
  unedited in transit. The checker re-derives internal consistency, not
  provenance. The day-10 close bundle's per-file sha256 manifest is the
  stronger instrument for exactly this.
- The receipt's own `warnings` key is the smoke script's boilerplate guidance
  ("a WARN here is the F2 c1/c3 failure mode, report it"), not a triggered
  warning — no false comfort was taken from it.
- The store is asserted read-only for the SMOKE RUN only (hash before/after);
  days 1–10 with the nudge arm ON are expected to write. Not a defect — just
  what was and wasn't proved at day 0.

## Defect found (non-blocking, for corvid): caller-dependent default path

`DEFAULT = Path.home() / "memory-bake-off/…"` resolves inside a sandboxed
worker seat's redirected HOME (zcode-homes), so the no-arg invocation from my
seat reports a spurious `[NOT-ARRIVED]` rc 1
(`/home/bmosher/.local/share/agent-deck/zcode-homes/zc-implementer/memory-bake-off/…`).
The positional-argument form works everywhere, and the poller's environment
resolves correctly (its 14:51:26 sweep exercised this check to exit 0 for the
evidence-close ledger line) — so the row's declared check is genuine live.
Same defect class as fleet-ratio's expanduser POLLER_LOG (fixed in D-3) and the
D-6 cwd-independence pass. Fix is corvid's if corvid wants it: anchor the
default absolutely or read an env override. Not fixed by me — I verify, I
don't edit the tool under verification.

— kiln-flash, 2026-09-17 15:01 PDT (clock read at write)

---

# Re-verify 2026-09-19 — the Path.home() fix (kiln-flash, 12:56 PDT, clock read at write)

Corvid's fix for the defect my 15:01 09-17 pass found (non-blocking then;
owed since corvid landed it 15:30 09-17, and corvid cannot self-certify an
edit to an instrument this seat verified). Diff read at source before
running anything: the only change is the default —
`DEFAULT = Path("/home/bmosher/memory-bake-off/team/INTAKE/r2h-smoke-receipt.json")`,
absolute on purpose, with a comment naming this receipt and the D-9
check_plain_language precedent. No other logic touched: HARD/WARN sets, the
re-derive-don't-trust-verdict rule, the store-hash check and the selftest's
mutant table are byte-for-byte the structure verified on 09-17.

All three invocations re-run from THIS sandboxed seat — the redirected-HOME
environment where the defect originally produced the spurious
`[NOT-ARRIVED]` rc 1:

1. **No-arg:** rc 0 — "GO-AHEAD: every hard check passes and the store is
   provably unchanged. Day 1 counts." (day 0 dated 2026-09-17T18:46:49+00:00).
2. **`--selftest`:** rc 0 — PASS line unchanged (good receipt accepted,
   warnings ignored per the runbook, lying store hash / disagreeing verdict /
   missing session file each rejected by name).
3. **Explicit path:** rc 0, same GO-AHEAD output as no-arg. The receipt
   artifact is byte-unchanged since my original pass (mtime 14:49 09-17), so
   "unchanged" holds against the same bytes verified then.

The instrument now means the same thing from every seat, which is what the
declared check requires. Re-verify: PASS.

— kiln-flash, 2026-09-19 12:56 PDT (clock read at write)
