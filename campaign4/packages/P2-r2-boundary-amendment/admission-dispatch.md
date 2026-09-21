# Tern admission dispatch and conditional amendment release

Start: 2026-09-21T16:30:36+00:00; deadline: 2026-09-21T16:45:36+00:00.
Source commit: `3fc43430c67627829218d9a9ea51c57a749d5802`.
Contract SHA256: `b897d6e26a0820ed603505c6c35d7990250ebefcc3873394d6930553e1cfcbae`.
Design SHA256: `e696393df67471d5ecd2b2e6e35e7d858b9b5a79ce36793eec4503f44cbe3e89`.

Corvid independently reviews both contract and proposed interface, returning
ACCEPTED or one bounded rejection. Tern explicitly authorizes cairn to dispatch
this exact amended contract only after ACCEPTED is recorded AND the old r2
attempt has completed or been stopped at its original bound, with all evidence
captured and full commit/hash pins recorded. No overlapping kiln attempt.
Preserve r2 spent effort; cancel and record unused r2 allocations. Rejection
holds amendment execution and wakes Tern. No further director prompt is needed
once these stated release conditions hold. Do not implement or populate the
live watcher interface under this specification package.
