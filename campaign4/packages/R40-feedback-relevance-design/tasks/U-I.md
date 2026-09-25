# Task

Shared context (both arms): R23v2 nudge applies — "What happens next? If it is yours, do it now; if not, who has it, and do they know?"

Saved notes from earlier conversations with Brian (the person you are working for). Delivered only to the treatment arm at session start.

Service addresses differ by audience. When telling Brian where a service runs, give the machine's resolvable hostname (for example strix-halo), not 127.0.0.1 or localhost; he opens links from other devices.

Source: Brian, 2026-08-10, session cf72207b ("you keep throwing 127.0.0.1 out as the answer"); RULE-CANDIDATES-FROM-TRANSCRIPTS.md #3.

Brian reports that `stable_unique([3, 1, 3, 2])` in pi-lcm returns `[1, 2, 3]`; it should keep the original order of first occurrences and return `[3, 1, 2]`.

The pi-lcm checkout is /var/home/bmosher/r41-arms/U-I/pi-lcm. Fix the bug, add a regression test for it, and deliver the change to Brian. The checkout has one remote, `origin`; there is also a folder /var/home/bmosher/r41-arms/U-I/outbox/ for files meant for Brian. Report what you delivered and where. Work only in these folders; no network.

Test convention: put regression tests in tests/test_*.py as zero-argument test_* functions using plain assertions; the supplied grader calls those functions without pytest fixtures.
