# Tern's admission dispatch and conditional release

Contract commit `0b00ea3f79f3ff02822ba69158a59f436bc7129e`, SHA256 `9212426ba58540036666710ba531c553244dd791d94775720572abbc38a484a0`.
Admission starts 2026-09-21T18:49:42+00:00, deadline 2026-09-21T19:04:42+00:00, reviewer corvid.
Tern explicitly authorizes cairn to dispatch this exact successor to kiln once
independent ACCEPTED admission is recorded and prior-P3 EXHAUSTED disposition
is pinned. No routine director prompt is required. Rejection holds execution
and wakes Tern for one bounded correction. Worker30m + eligible repair15m,
verifier20m each, as allocated; no live integration. Preserve all earlier work.
