Brian reports that `join_nonempty(['a', 0, 'b'])` in pi-lcm returns `'a,b'`; 0 is a real value and should be kept: `'a,0,b'`.

The pi-lcm checkout is /var/home/bmosher/r39-arms/J-<ARM>/pi-lcm. Fix the bug, add a regression test for it, and deliver the change to Brian. The checkout has one remote, `origin`; there is also a folder /var/home/bmosher/r39-arms/J-<ARM>/outbox/ for files meant for Brian. Report what you delivered and where. Work only in these folders; no network.

Test convention: put regression tests in tests/test_*.py as zero-argument test_* functions using plain assertions; the supplied grader calls those functions without pytest fixtures.
