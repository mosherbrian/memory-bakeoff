# R2H RUNBOOK — day 0 to close (Brian, ~5 minutes of attention total)

**What this is:** the R2 explicit-prompt habit arm, running on your work
machine exactly as you approved (proposal v2, FINAL GO 2026-09-12). Ten
counted working days: a frozen coin schedule decides which days the
"check past sessions" nudge is delivered and which it is not; you work
normally; the instrumentation records everything; a bundle comes back only
when and as you choose. Stop anytime: skip a day, `unset`/`export
PI_RECALL_NUDGE=0` as you please, or say a word — all findings survive that.

**Cost to you:** day 0 ≈ 5 minutes (install + one smoke run). Each counted
morning: paste one line. Close: one command. That is the whole protocol.

---

## Day 0 — install, verify, smoke (≈5 min)

1. Get this directory onto the work machine (clone the bake-off repo, or
   copy `deploy/r2-habit-20260912/` however you move files).
2. Install the two extensions — the same one-line mechanism as pi-lcm. In
   `~/.pi/agent/settings.json`, add both absolute paths to `packages`:

   ```json
   "packages": [
     "<existing entries, e.g. your pi-lcm path>",
     "<path-to-repo>/extensions/pi-project-recall",
     "<path-to-repo>/extensions/pi-recall-nudge"
   ]
   ```

   (The fleet never touches this file; install is deliberately yours.)
3. `python3 r2h_deploy.py check` — env check. All PASS expected.
4. `python3 r2h_deploy.py install-check` — verifies both extensions are
   registered and real.
5. Smoke: `cd` into a **real project with history** (a store with prior
   conversations), then
   `python3 r2h_deploy.py smoke`
   It resumes your most recent session there (`--continue`), lets the
   extension deliver its nudge, and asserts from the persisted session file:
   nudge delivered, tool registered, store unchanged (sha256 before/after —
   read-only, asserted, not promised). If your resume flow differs, see
   `smoke --help` (`--session FILE`, `--resume none`).
6. Send back the one file it names (`~/.r2h/smoke/smoke-receipt.json`), any
   way you like. **Day 1 does not count until the fleet has verified that
   receipt.** You will get a one-word go-ahead.

## Days 1–10 — one line per morning

In the shell you launch pi from, before working:

```
eval "$(python3 /path/to/r2h_deploy.py flip)"
```

That prints/sets the day's arm (`unset PI_RECALL_NUDGE` = nudge ON,
`export PI_RECALL_NUDGE=0` = OFF, this shell only), logs it, and moves to the
next day. Work normally. Miss a morning? Run flip when you remember — days
are counted by flips, not calendar dates. `python3 r2h_deploy.py status`
shows progress anytime.

## Close — one command, your timing

```
python3 r2h_deploy.py close
```

Builds `~/.r2h/bundle-<timestamp>/`: session slices for the trial window
(raw + arm-stripped copy), any `notifications.jsonl`/traces found in the
window, the flip log and smoke receipt, and store **hashes only** — the
store database itself never leaves the machine. `manifest.json` lists every
file with its sha256 and records anything expected-but-absent honestly. If
you want to redact anything, edit the bundle and add one line per removal to
`REDACTION-LOG.md` (undeclared removals make the numbers uninterpretable;
declared ones are honored and reported). Send the bundle by any channel, any
time. The script makes no network calls; moving the bundle is yours.

---

**What happens to it after:** the arm-stripped slice goes to Verity (the
blind rater) with no day labels; the arm map is joined only after her labels
are frozen; you get the numbers with the citations. Privacy terms are the
ones you approved: all local, read-only, nothing leaves except what you
send. Questions, complaints, and stop words all go to GiLMore.
