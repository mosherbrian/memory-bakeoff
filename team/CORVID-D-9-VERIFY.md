# CORVID-D-9-VERIFY — verification of row D-9 (plain-English status for Brian)

Verifier: corvid-dsh. Producer: cairn-pi (the row is cairn's own standing
duty; the summary and the checker are cairn-side artifacts, neither authored
by this seat). Row evidence-closed by the poller ~12:40 — status cell never
said done, the declared check passed from the canonical view.

Real clock at write: 2026-09-17 12:4x PDT (read at the row edit).

## Verdict: VERIFIED FAIL — one blocking defect (pre-filed, unfixed); the substance itself verifies

## The blocking defect: the declared check is still caller-dependent

My 12:11 CNR finding, demanded "fix before first close":
`team/tools/check_plain_language.py` lines 33-36 still build the default
paths from `Path.home()`. Consequences, both re-demonstrated this hour:

1. From this sandboxed worker seat the declared check exits **1 [MISSING]** —
   it looks for `status-plain.md` inside this seat's sandbox HOME — while the
   same invocation exits 0 from the canonical view. A close earned on a check
   whose answer depends on who runs it is the S4-8/D-3 class exactly.
2. Worse than the hard fail: from a worker seat the FACTS file also resolves
   inside the sandbox, `fp.exists()` is False, and the INVENTED-NUMBER check
   silently DISABLES rather than failing — the same declared check is a
   weaker gate depending on the caller.

Fix required (one line, the fleet's own precedent): `DIR =
Path("/home/bmosher/.local/share/agent-deck/conductor/glm")` — the
check_external_cards precedent (absolute default path), the same treatment
kiln gave fleet-ratio's POLLER_LOG this morning. After the patch, my re-verify
runs the declared check from this seat with no overrides: its verdict must
match the canonical view's on identical file state.

## What verified (the substance is real and the duty is live)

- `status-plain.md` exists and is actively maintained: written 12:39:48,
  REWRITTEN 12:42:43 after the facts moved (72→73 finished, 33→35 confirmed
  between snapshots) — the standing duty is operating, not a one-shot close.
- Content rules all held on both versions read: leads with "Nothing needs you
  right now." (the row's lead-with-whether-Brian-is-needed rule); no banned
  vocabulary; no internal ids; ~50 words (cap 220); every number traced to
  the fact sheet snapshot of its moment; "The machine reports no problems"
  matches `Problems: none`.
- The canonical-view declared check exits 0 (run by me with the canonical
  HOME, 12:42:57).
- The invented-number treadmill is a feature working as written: a number-
  bearing summary goes stale the moment the 2-minute facts move, which
  mechanically enforces "refresh whenever the facts change materially" —
  observed live this hour (the rewrite landed 14 s before my check run and
  passes).
- FRESHNESS at check time: seconds old. WORD CAP: pass.

## Note on the close's nature

For a STANDING row the evidence-close means "passing now", not "finished" —
the duty (refresh at least every 30 minutes while a sprint is open) continues
regardless of this verdict. The FAIL above blocks the CHECK's
trustworthiness, not the writing; once the path fix lands, the close stands
on a check that means the same thing from every seat.

— corvid-dsh, 2026-09-17

## Re-verify — 2026-09-17 12:54 PDT: VERIFIED PASS, close now stands

The blocking defect is FIXED (checker touched 12:46:55): DIR is now
`Path("/home/bmosher/.local/share/agent-deck/conductor/glm")` — absolute,
with a comment citing this verify and the exact failure it removes. From this
sandboxed seat, default invocation, no overrides: exit 0, "plain enough" —
matching the canonical view's verdict on the same file state, which was the
pre-committed re-verify condition. Facts cross-check no longer silently
disables anywhere (the file now EXISTS from every seat's view). selftest rc 0.
rowcheck D-9: done-holds, check_exit 0, declares-done true. The 12:44 FAIL's
condition is discharged; D-9 is done+verified, and the standing refresh duty
continues as written.
