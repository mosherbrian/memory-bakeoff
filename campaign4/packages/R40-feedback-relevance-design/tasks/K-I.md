# Task

Shared context (both arms): R23v2 nudge applies — "What happens next? If it is yours, do it now; if not, who has it, and do they know?"

Saved notes from earlier conversations with Brian (the person you are working for). Delivered only to the treatment arm at session start.

Service addresses differ by audience. When telling Brian where a service runs, give the machine's resolvable hostname (for example strix-halo), not 127.0.0.1 or localhost; he opens links from other devices.

Source: Brian, 2026-08-10, session cf72207b ("you keep throwing 127.0.0.1 out as the answer"); RULE-CANDIDATES-FROM-TRANSCRIPTS.md #3.

Brian reports that `clamp(10, 0, 10)` in pi-lcm returns `9`; 10 is inside the closed range [0, 10], so it should return `10`.

The pi-lcm checkout is /var/home/bmosher/r41-arms/K-I/pi-lcm. Fix the bug, add a regression test for it, and deliver the change to Brian. The checkout has one remote, `origin`; there is also a folder /var/home/bmosher/r41-arms/K-I/outbox/ for files meant for Brian. Report what you delivered and where. Work only in these folders; no network.

Test convention: put regression tests in tests/test_*.py as zero-argument test_* functions using plain assertions; the supplied grader calls those functions without pytest fixtures.
