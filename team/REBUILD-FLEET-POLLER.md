# REBUILD-FLEET-POLLER — resurrect the fleet pulse on the verified design

## Why

The poller died with its host loop; the only surviving scripts are two
/tmp copies, now preserved by GiLMore outside /tmp (hashes below).
Heartbeat (5-min, temporary) is the only wake source. Goal: a checked-in,
installed, self-restarting pulse matching the verified lean design.

## Sources

- Latest script (has the section-6 field-aware matcher + Corvid id +
  Aletheia alias): `/var/home/bmosher/.local/share/agent-deck/conductor/glm/fleet-poller.latest.sh` (sha256 `37a96a7f…`, 7697 B, 2026-09-13 21:29)
- Previous: `.../fleet-poller.prev.sh` (sha256 `8b90221c…`, 7570 B)
- Design of record: `team/PROPOSAL-RESEARCH-HEARTBEAT-20260914.md`
  (fsync; YOUR verify with 3 checks is still pending — verify FIRST,
  then build to the verified text, not to the draft)
- Brake contract: script exits at once if
  `~/.local/share/agent-deck/conductor/glm/fleet-poller.stop` exists
  (Brian's halt must keep working)

## Task

1. Verify the proposal (your 3 named checks). File the sign-off.
2. Rebuild: canonical script checked into version control (not /tmp),
   section-6 fix carried, GLM-era night guards RE-EXAMINED (fleet is
   Muse now — the 18:00-08:00 suppression must be re-derived, not
   copied), stop-file brake kept, install method that survives reboot
   (user unit + timer, or the mechanism you judge fittest).
3. Receipts: power check re-run (row 29 class: exactly the right seat
   wakes), a 10-minute live run with 0 false wakes, reboot-survival
   note (or honest gap).
4. When live: heartbeat timer goes back to 20 min (GiLMore's step on
   your report).

## Rules

- Verifier: fsync. No self-certified claims.
- Server.py: builder-lane freeze note stands — touch only with the
  standing freeze exception for your own lane files.
- Budget: <=1h agent. Report receipts, not narratives.
