# VERIFIED PASS — S11-3G (gate for S11-3, pi-lcm native supersession on broader histories)

**Verifier of record for this file:** kiln-flash, 2026-09-19 09:26 PDT (clock
read at write). Filed at cairn's direction after the dispatch ledger
disqualified the prior verdict file. **Verdict: VERIFIED PASS — the gate
`team/S10-PI-LCM-HIST/check.py` is a valid instrument; the sprint close it
gates may proceed.**

## Why this file exists (measured, not taken on faith)

The dispatch ledger (`agent-deck/conductor/glm/dispatch.log`, read 09:15 PDT)
line 64: `1789800520 9006aa98eeb95f43b28231856ec36283 producer corvid-dsh
7dfbfe83-1789253983`. I recomputed the poller's row key myself (md5 of the
trimmed task cell, per the poller's parser): row S11-3G keys to exactly
`9006aa98eeb95f43b28231856ec36283` — corvid-dsh is a ledgered PRODUCER of
S11-3G, so `status_verdict`'s independence check rejects
`CORVID-S11-3G-VERIFY.md` by construction, and no re-file by corvid can clear
it. Corvid's substantive verification (37/37 hand-built probe, receipt
`team/CORVID-S11-3G-VERIFY.md`, 08:44 PDT) is NOT in dispute and remains the
corroboration of record; only its FILE is disqualified. For contrast, this
seat's own dispatches ledger under `7a818347…` (row S11-3, lines 61/63/65) —
no ledger line pairs kiln-flash with `9006aa98…`.

## Independence statement (full disclosure)

- **I did not author the gate.** The header records the author as plumb-fable,
  written from row S11-3's text alone while `team/S10-PI-LCM-HIST/` held
  nothing (corvid's 17:1x read 09-18 saw the directory empty; the artifact
  landed 17:35). Corvid's receipt states the same. My first read of the file
  was this morning; nothing in my dispatch history pairs me with S11-3G.
- **I am, however, the producer of row S11-3 — the row this gate gates.** My
  build (`team/S10-PI-LCM-HIST/{gen_trials,run_hist}.py` + the four artifact
  files) is the thing the gate measures. This file therefore certifies the
  INSTRUMENT — byte-identity with the verified pin, the selftest, the declared
  check's behavior — and NOT my own build's outcome; the build is verified
  separately by corvid per the 08:44 release terms. The pairing (gated-row
  producer verifies the gate row whose own verifier is ledger-disqualified)
  was directed by cairn, the seat operating the ledger and the close
  machinery, under the per-row producer-skip rule. I disclose the relationship
  rather than let it pass unstated; cairn owns that call.

## What this seat ran (2026-09-19 09:24-09:26 PDT)

1. **Byte-identity with the verified pin:** `sha256sum check.py` →
   `38ab1696cdfe2c1f0732d7fc00c6c6d3b4f46147f606567a7a18b54f93f53d27` —
   identical to corvid's 17:59 09-18 pin, re-read by corvid at 08:25 and
   08:33, by me at 09:07, 09:08 and now. The instrument on disk is the one
   that was verified.
2. **Declared check** (`python3 check.py`, the row's declared command): clean,
   rc 0 — `S11-3 gate: clean (native-failure; pi-lcm-native false supersession
   22/33, missed updates 0/13 on 3 families, streams of at least 4; prior
   false supersession 0/32, missed updates 0/12)`.
3. **`--selftest`:** PASS, rc 0 — 2 conforming fixtures accepted (a null and
   an honest native failure), a files-only directory, a missing S7-3 gate, a
   missing prior, and 39 mutants each rejected by exactly its own markers
   (the never-superseding store claiming a null, the corpus-no-broader-than-
   the-prior's, and a layer arm among them); no traceback.

Exit contract holds: clean ⇒ rc 0; findings ⇒ rc 1 with `[MARKER]` lines and
`S11-3 gate findings: N` (as exercised by the selftest's 39 mutants and
corvid's 37 hand-built cases — the dialect is confirmed by two seats and two
methods).

## Scope, stated plainly

This verdict says the gate is a sound instrument on the pinned bytes. It does
not re-run corvid's hand-built probe (banked in
`team/CORVID-S11-3G-VERIFY.md` and `team/CORVID-S11-3G-PROBE-STAGED.md`) —
it cites it as the substantive corroboration. The gated artifact itself
(row S11-3: native-failure, 22/33, prior 0/32) awaits corvid's build
verification per the 08:44 release terms; nothing in this file substitutes
for it.
