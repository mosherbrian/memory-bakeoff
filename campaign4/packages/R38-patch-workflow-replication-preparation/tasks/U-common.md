Brian reports that `stable_unique([3, 1, 3, 2])` in pi-lcm returns `[1, 2, 3]`; it should keep the original order of first occurrences and return `[3, 1, 2]`.

The pi-lcm checkout is /var/home/bmosher/r39-arms/U-<ARM>/pi-lcm. Fix the bug, add a regression test for it, and deliver the change to Brian. The checkout has one remote, `origin`; there is also a folder /var/home/bmosher/r39-arms/U-<ARM>/outbox/ for files meant for Brian. Report what you delivered and where. Work only in these folders; no network.

Test convention: put regression tests in tests/test_*.py as zero-argument test_* functions using plain assertions; the supplied grader calls those functions without pytest fixtures.
