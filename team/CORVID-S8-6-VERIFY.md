# CORVID-S8-6-VERIFY — row S8-6 verified PASS with one recorded correction, 2026-09-18 08:34 PDT

Verifier: corvid-dsh. Author: infra-owner (the driving Claude session), taken
outside the sprint on Brian's 09-18 decision. Corvid authored neither the
artifact nor the gate; corvid is also not the suspected restart actor. Verify
claimed 08:28 PDT (clock read 08:28:51 at write). Artifact
`team/S8-OPS-DEBT.md` sha256 a4cde3e1607a66984c3a2d39d5f32889aa267f94cf6e8c38804cfbbc4cc1c21c.

Declared check re-run: `test -f /home/bmosher/memory-bake-off/team/S8-OPS-DEBT.md`
→ rc 0. Gate S8-6G closed VERIFIED PASS 08:22 (receipt
`team/CORVID-S8-6G-VERIFY.md`), clean on this artifact against the LIVE
journal.

Independent re-runs of every journal claim (the artifact invites exactly
this; all timestamps local, 2026):

1. **The two restarts are on 09-16, clean triples, as quoted.**
   `journalctl --user -u fleet-poller.service 16:38→16:54` shows exactly two
   stop/start triples, 16:39:59 and 16:52:31, seconds wide, no failure line;
   the artifact's quoted lines match verbatim. ✓
2. **No actor recoverable — "unattributed" is a measurement.**
   `journalctl --user _COMM=systemctl` for 09-16 returns NO ENTRIES (a first
   `wc -l` count of 1 was journald's "-- No entries --" placeholder; read
   before judging). systemd records no D-Bus peer for the restarts. ✓
3. **The crash loop is real and sized as claimed.** 232 starts in
   09:46:29–10:06:34 at a fixed ~5 s cadence ("Scheduled restart job,
   restart counter is at N" — Restart=always), 246 starts of the unit on
   09-16 in total. Artifact says "about 230 … 246 starts". ✓
4. **The control exists, is wired, and works.** `systemctl --user show`:
   ExecStartPre carries `/bin/bash -n …/fleet-poller.sh` (syntax gate,
   ignore_errors=no) AND `.config/agent-deck/poller-restart-attribute`
   (ignore_errors=yes — the `-` prefix); StartLimitBurst=5,
   StartLimitIntervalUSec=2min, visible to `show` (i.e. actually in [Unit]).
   The 07:41:17 proof line reproduces verbatim from the journal including
   the full parent chain `systemctl[1791712] <- bash[1791701] <-
   claude[33991] <- bash[33507] <- conmon[33504]` — the artifact's
   hand-transcription defect story checks out (the on-file line is now the
   journal's own bytes). Control file exists and names the driver. ✓
5. **Disposition "fixed" verified — live.** `fleet-poller.sh:1458` emits
   `[chain verdict-wanted] row … WANTS YOUR VERDICT (…) Queued HH:MM:SSZ; …
   deliberately does not quote it`; zero occurrences of "chain done" remain
   in the file. The ASK-not-state headline cannot age into a false claim.
   Live confirmation: the poller's own wake to this seat at 08:27 today
   arrived in exactly this format for exactly this row. ✓

**CORRECTION REQUIRED (non-blocking for the verdict, blocking for the
prose):** the artifact's clause "each `status=2/INVALIDARGUMENT`" does not
reproduce — zero INVALIDARGUMENT lines exist for 09-16 in ANY scope (user
journal, system journal, whole day), no "Main process exited"/"Failed with
result" line for fleet-poller survives, no suppression markers, and verbose
fields around loop starts carry no EXIT_STATUS. What the journal records is
the retry cadence, not the exit status. The "script that would not parse"
reading remains plausible (bash exits 2 on syntax error) but is an
inference, not a journaled fact. infra-owner to correct the sentence to what
the journal shows (e.g. "exit status not journaled; the 5-second
Scheduled-restart cadence is the record") or attribute it explicitly as
inference. The row's two verdicts do not depend on this clause.

## Verdict

S8-6 **VERIFIED PASS** (with the correction above to be applied by
infra-owner) — done: corvid-dsh 2026-09-18 08:34 PDT (verify claimed 08:28,
clock read at each write) — restart-actor question answered
`unattributed, measured`; headline-aging residual disposition `fixed`,
verified in file and in live delivery. Receipt this file.
