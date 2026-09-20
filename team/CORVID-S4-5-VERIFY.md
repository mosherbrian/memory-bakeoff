# CORVID-S4-5-VERIFY.md — corvid-dsh verification of QUEUE row S4-5

**Verdict: PASS** — 2026-09-16 13:40 PDT. kiln-flash authored, corvid-dsh verifies
(independence holds: corvid did not author the edit, the done cell, or the policy text).

## Row terms

> edited conductor/glm/POLICY.md (check: `test 0 -eq $(grep -c quiet
> /home/bmosher/.local/share/agent-deck/conductor/glm/POLICY.md)`)

## What was checked, live, this pass

1. **Declared check re-run on the artifact: rc 0.** `grep -c quiet` on
   `/home/bmosher/.local/share/agent-deck/conductor/glm/POLICY.md` = 0;
   `test 0 -eq 0` exits 0.
2. **Artifact present and intact, not gutted.** 417 lines, 25,085 bytes,
   mtime Sep 16 12:24 — inside the claimed window (stamps bracketed by
   measured date calls 12:21→12:24). A zero grep count is trivially
   satisfiable by deleting content, so the sections were read.
3. **All three claimed rewrites are substantive.** (a) "Answering a fleet
   nudge" (~:91-103): act-or-escalate on every wake, "no log-only outcome",
   dated amendment note citing the Brian ruling and QUEUE S4-5. (b) Cycle
   checks / [THIN] (~:218-228): "All clean → one line saying so; anything
   not clean → act or escalate the same turn (2026-09-16, S4-5)". (c) Push
   semantics (~:351-361): with the marker stripped, "every conductor reply is
   reportable", bounded by the 180s floor + presence rule, and an explicit
   "do not reintroduce a mute prefix". Provenance (starving-instrument
   incident, surprise test) preserved in the amendment notes as claimed.
4. **Marker-variant sweep: zero instructional hits.** Patterns
   `[(quiet|hush|mute|silent|nopush|noring)]` and mute-prefix-as-instruction:
   nothing. The four remaining "mute-prefix" strings in the file are the
   provenance notes explaining what was removed — required by the row, not
   violations.
5. **Server-side note corroborated.** The push builder's `_reply_is_news`
   marker keying is external to the policy file (as the done cell states);
   not re-verified in builder source this pass — accepted as stated, and it
   is the conservative direction (more replies reportable, not fewer).

## Caveats (honest, non-blocking)

- **The "10 occurrences" figure is not independently re-countable.** The glm
  policy has no VCS history and no pre-edit snapshot survives; the sibling
  files are a different document (see below) and a stub. Verification is
  therefore **zero-remaining on the declared check**, not ten-removed. The
  three-section coverage is consistent with "all occurrences" but the exact
  count rests on the row author's pre-edit tally.
- **Scope finding for cairn (follow-up row candidate, NOT an S4-5 failure):**
  the base policy `conductor/POLICY.md` (mtime Sep 14 16:23, untouched) still
  instructs at :78 "Your `[quiet]` replies never push", and `glm/POLICY.md`
  declares it "Inherits `../POLICY.md`". The glm override countermands this
  in all three rewritten places, so live glm-conductor behavior is
  act-or-escalate. But the base file is now internally inconsistent, and
  `new-conductor` copies inherit the base — a fresh conductor would get the
  quiet protocol back. Recommend a row: strip :78 (and audit :122/:473
  context) from the base policy. The other two quiet hits in the base file
  are ordinary English ("quietly again", "goes quiet at 08:00"), not the
  protocol.

## Result

Row S4-5 declared check rc 0 on the real artifact; rewrites substantive;
provenance preserved; independence intact. Row moves done → **VERIFIED
(PASS)**. Verdict filed by corvid-dsh 2026-09-16 13:40 PDT.
