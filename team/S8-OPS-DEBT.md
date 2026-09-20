# S8-6 — restart-actor attribution and the headline-aging residual

Driver unit: fleet-poller.service

Prior: team/RETRO-4-SUMMARY.md — both items are its carried-forward entries:
the restart-actor question ("cleanly restarted (systemctl stop/start, no crash)
at 16:39:59 and 16:52:31 with no actor identifiable") and the headline-aging
residual ("open — mitigated, not eliminated").

Advances: neither a frozen goal nor a roadmap item. Fleet ops debt.

Built by the infra owner (the driving Claude session) outside the sprint, on
Brian's decision 2026-09-18, so kiln-flash's sequential budget returns to
S8-1..S8-5. That session is also a party to the finding below, which is why the
verdict stays with corvid-dsh and why every line quoted here is a `journalctl`
query that re-runs.

## One correction before the evidence

The two restarts this row records are **2026-09-16**, not 2026-09-17. They are
absent from the 09-17 journal; the gate's own docstring already assumed the
16th ("an export can be given with --journal once the live journal no longer
covers 2026-09-16"). The row does not carry the date, so it reads as recent.

## What the journal can and cannot say

`journalctl --user _COMM=systemctl --since "2026-09-16 00:00"` returns **no
lines**. systemd records this unit's own lifecycle and nothing about the D-Bus
peer that asked. So the actor of a past clean restart is not recoverable, and
`unattributed` below is a measurement, not a shrug.

It is also worth separating two things the journal shows. 2026-09-16 had **246
starts** of this unit. About 230 of them are one crash loop, 09:46:29 to
10:06:34, five seconds apart, each `status=2/INVALIDARGUMENT` — not restarts by
anyone, but `Restart=always` retrying a script that would not parse. The two
below are different: clean stop/start triples, seconds wide, no failure line.

Restart: 2026-09-16 16:39:59
Actor: unattributed
Evidence:
> Sep 16 16:39:59 strix-halo systemd[1604]: Stopping fleet-poller.service - Fleet poller — the only dispatcher in the loop...
> Sep 16 16:39:59 strix-halo systemd[1604]: Stopped fleet-poller.service - Fleet poller — the only dispatcher in the loop.
> Sep 16 16:39:59 strix-halo systemd[1604]: Started fleet-poller.service - Fleet poller — the only dispatcher in the loop.
Control added: /home/bmosher/.config/agent-deck/poller-restart-attribute

Restart: 2026-09-16 16:52:31
Actor: unattributed
Evidence:
> Sep 16 16:52:31 strix-halo systemd[1604]: Stopping fleet-poller.service - Fleet poller — the only dispatcher in the loop...
> Sep 16 16:52:31 strix-halo systemd[1604]: Stopped fleet-poller.service - Fleet poller — the only dispatcher in the loop.
> Sep 16 16:52:31 strix-halo systemd[1604]: Started fleet-poller.service - Fleet poller — the only dispatcher in the loop.
Control added: /home/bmosher/.config/agent-deck/poller-restart-attribute

## The control, and proof it works

It cannot be recovered afterwards, but it can be caught at the time: a blocking
`systemctl --user restart` stays alive until the job completes, so it is still
in /proc while this unit's `ExecStartPre` runs. The control looks for it there,
walks its parent chain, and logs the result to the journal — the same place
that could not answer before.

Wired as `ExecStartPre=-%h/.config/agent-deck/poller-restart-attribute`, with
the `-` prefix so attribution can never block a deploy. Proven on a live
restart at 07:41:17 on 2026-09-18:

> Sep 18 07:41:17 strix-halo restart-actor[1791717]: restart-actor: human:bmosher via 'systemctl --user restart fleet-poller.service' - parent chain systemctl[1791712] <- bash[1791701] <- claude[33991] <- bash[33507] <- conmon[33504]

The chain names the session, which is what was missing. (That line was first
TRANSCRIBED into this file by hand and one pid was wrong - the gate could not
catch it, because it verifies the lines inside a Restart block and this one
sits outside. It is now inserted from `journalctl` output directly.) Limits, on purpose:
`--no-block` is not caught; a separate `stop` then `start` logs only on the
start; and a `Restart=always` retry has no caller and is reported as
`service:systemd`.

Two other things were wrong and are fixed alongside, because they are what made
the crash loop invisible: `ExecStartPre=/bin/bash -n` on the script, so an
unparseable edit fails the start once instead of looping every five seconds,
and `StartLimitBurst=5` / `StartLimitIntervalSec=120` in `[Unit]`, so a
non-syntax crash lands in `failed` where it can be seen. Both verified with
`systemctl show` rather than by reading the file back — written under
`[Service]` the StartLimit pair is silently ignored, and `show` reported the
default 10s until they were moved.

## The residual

RETRO-4 left this open: "the headline class ('row X is now done') can still age
inside a queued prompt; the message tells the reader to trust the row over the
message." Telling a reader to distrust the headline is a mitigation — the false
claim is still the first thing read.

Disposition (headline-aging residual): fixed - the wake headline in /home/bmosher/conductor-chat/workers/fleet-poller.sh now states the ASK rather than a state, "[chain verdict-wanted] row N ... WANTS YOUR VERDICT ... Queued HH:MM:SSZ", which cannot age because the row still wants a verdict whatever it did since, and the stamp lets a reader judge the wake's age without trusting its claim.

## Re-run everything above

    journalctl --user -u fleet-poller.service --since "2026-09-16 16:38:00" --until "2026-09-16 16:54:00"
    journalctl --user _COMM=systemctl --since "2026-09-16 00:00"
    journalctl --user -u fleet-poller.service --since "2026-09-16 09:46:00" --until "2026-09-16 10:07:00"
    journalctl --user -u fleet-poller.service --since "2026-09-18 07:41:00" --until "2026-09-18 07:42:00"
    systemctl --user show fleet-poller.service -p ExecStartPre -p StartLimitBurst -p StartLimitIntervalUSec
