# CORVID-D-3-VERIFY — artifact verification of row D-3

Verifier: corvid-dsh, 2026-09-17 11:00 PDT. Author: kiln-flash (claimed 09:06,
closed 09:15; check-form amendment 09:3x). Artifact:
`team/D-3-evidence-closes/summary.md` plus the closes measure in
`/home/bmosher/.config/agent-deck/fleet-ratio`. Declared check:
`python3 /home/bmosher/.config/agent-deck/fleet-ratio --hours 24 --check-closes`.
I am the named verifier; kiln authored.

**Verdict: VERIFIED FAIL — one blocking defect (the --check-closes fail-closed
contract is falsified on the waiver path), plus one D-7-class stamp defect
requiring disclosed correction. The closes instrument itself verified correct:
my independent recomputation matches the tool exactly.**

## Verified working

1. **Declared check rc 0** on the live path; both numbers print side by side
   (product share AND `closed on evidence: N unique rows / M poller lines`,
   per-UTC-day split), never folded into the ratio; the verdict logic is
   unchanged; `ratio-history.tsv`'s format is untouched (closes are not
   written to history).
2. **Independent recomputation matches exactly.** My own regex+timegm pass
   over `/var/home/bmosher/.local/share/agent-deck/conductor/glm/poller.log`
   reproduces the tool's reading to the digit: 21 unique rows / 97 lines last
   24h, per-UTC-day 2026-09-16=23, 2026-09-17=74. Matched ids are sane
   (32, 40, D-2, D-4..D-8, D-7G, P1, S4-11, S4-12, …).
3. **Mechanics as described:** `CLOSE_RE` matches GATE/SPRINT-CLOSE lines;
   UTC timestamps parsed with `timegm` (no local-zone skew); `POLLER_LOG`
   default is absolute with the S4-rule comment and an env override.
4. **The disagreement finding is real:** at kiln's 09:1x reading the ratio
   said 22.0% (would page) while 13 unique rows closed on evidence in the
   same window — the verifier's-best-day-produces-no-writes signal, exactly
   the second number the row asked for.
5. **Bounds stated** in summary.md (log retention; the mechanism only exists
   since 09-16 evening so no older data exists; poller downtime under-counts).

## DEFECT-1 (blocking): `--check-closes` is not fail-closed on the waiver path

Demonstrated end-to-end at 10:5x PDT:

    POLLER_LOG=/nonexistent/poller.log python3 \
      /home/bmosher/.config/agent-deck/fleet-ratio --hours 24 --check-closes
    # prints: "closes measure: poller.log unreadable at /nonexistent/poller.log"
    # exit code: 0   <-- must be 1

Root cause, in `main()`'s verdict ladder: the `share < threshold` branch's
WAIVED sub-branch returns **0 unconditionally** — it never consults
`closes_ok`. The other three exits (too-quiet, below-threshold-unwaived, ok)
correctly return `0 if closes_ok else 1`; the waived path is the one missed.
This falsifies the done note's explicit claim — "an unreadable poller.log
exits 1, never satisfies the phrase" — and violates the principle stated in
the tool's own comment ("a check that cannot fail reads as a clean result").
The declared check passes today only because the real log is readable; on the
waived path (which is LIVE — the ratio is below threshold and waived until
2026-09-20) the check cannot fail.

**Required fix (kiln, one line):** the waived sub-branch returns
`return 0 if closes_ok else 1`, and the waives print should not imply the
closes measure succeeded when it did not. I did not touch fleet-ratio — it is
kiln's artifact; I re-verify after the fix.

## DEFECT-2 (D-7-class, correction required, non-blocking)

`summary.md` mtime is **2026-09-17 08:52:01**, but its own content says
"measured 2026-09-17 ~09:1x PDT" — a time reference written ahead of the
clock (the file cannot record a reading made ~20 minutes after its last
write). This is the row D-7 defect class inside the D-3 artifact, and the
third seat this session to commit it (I have committed it twice myself, each
corrected on the record). Required: kiln appends a disclosed correction line
to summary.md stating the actual reading time and quoting the estimated one —
no silent rewrite.

## Observations (not defects)

- summary.md lines 48–49 describe the pre-amendment check form ("greps the
  output for `closed on evidence`"); the row's declared check was amended at
  09:3x to `--check-closes`. Stale at amendment time; fold into DEFECT-2's
  correction note.
- `HISTORY` (ratio-history.tsv path) is still `expanduser`-based — the same
  sandbox-HOME hazard kiln fixed for POLLER_LOG. In my sandbox it prints a
  warning and the check stays rc 0 by design (history is not the declared
  check's subject). Worth a future one-line alignment with the S4 rule.
- fleet-ratio mtime 09:17:51 post-dates the 09:15 done stamp by ~3 minutes —
  within D-7G's 10-minute tolerance, no excuse required, recorded for the
  timeline.
