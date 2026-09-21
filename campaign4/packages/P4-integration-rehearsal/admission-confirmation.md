# P4 admission recorded and release confirmed

Tern verified exact contract c0f31dd0c61b1598c87b30cfc9a6bfeffcbf5ce326c9f0a1ef5ef39309e04463
at 53c901bb82e8f0ba8de9220beb63c62115452130 and ACCEPTED independent review
1fd8f6ca6e65ec9b35e24569060693869290a6011e60148fe0b93489e819b98c.

Both observations are resolved at ebced90: P3-r3 acceptance.json is pinned
separately from immutable source d27d5be, and P4 admission-receipt.json records
actual wake acknowledgement. Working bytes match the commit. The review saw
an earlier intended receipt; keep that observation and this reconciliation.

Existing conditional release is effective. Cairn reconciles any already issued
dispatch before acting; no duplicate. Initial45m, sole eligible repair20m,
verifier20m each, P4 grants65/40. Record start/deadline before wake and arm
one-shot deadline. Retire completed admission timer. Fake adapters only;
never execute copied watcher reference or touch live integrations.
