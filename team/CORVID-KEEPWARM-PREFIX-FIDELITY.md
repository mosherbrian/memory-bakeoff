# Keep-warm prefix fidelity — the system prompt embeds a changing date

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0, local (`strings` on the installed client)
**Why:** `BILLING-CACHE-FINDINGS-20260915.md` §4 proposes an out-of-band
keep-warm proxy and names prefix fidelity as "the hard part — a refresh only
works if it reproduces byte-for-byte what the lane will send next". Static
inspection of the client shows one field that is **guaranteed to change**, so the
naive replay will break.

## Evidence — the `<env>` block in the system prompt

From `opencode-ai` 1.18.30 (the installed binary):

```
"Here is some useful information about the environment you are running in:",
"<env>",
`  Working directory: ${h.directory}`,
`  Workspace root folder: ${h.worktree}`,
`  Is directory a git repo: ${h.project.vcs==="git"?"yes":"no"}`,
"  Platform: linux",
`  Today's date: ${new Date().toDateString()}`,
"</env>"
```

So the prefix includes **`Today's date: <toDateString()>`** (and cwd/worktree,
stable per lane). There is also a runtime update path:

```
baseline: `Today's date: ${date}`
update:   `Today's date is now: ${next}`
```

i.e. the client can **rewrite the date within a live session**.

## What this means for keep-warm

1. **A replay captured before midnight primes the wrong prefix.** At 00:00 local,
   the lane's system prompt becomes a new date; a warm-up that re-sends the old
   body writes a *second* cache entry, and the lane's next request still misses —
   paying for the warm-up and the miss. The proxy must regenerate the body with
   the current date (or drive the client's update path), not replay verbatim.
2. **The date-update event can cold a session with no idle gap.** If the client
   emits `Today's date is now:` at a rollover, that changes the cached prefix
   mid-session. Any miss-rate-by-gap analysis (including the fine ladder in
   `BILLING-CACHE-FINDINGS-20260915.md` §1) should either avoid a midnight
   crossing or treat it as a known outlier. It is a candidate mechanism for the
   one early-eviction anomaly (130 s miss among 140/150 s hits) if that run
   crossed a boundary; worth checking the probe timestamps.
3. **Everything else in `<env>` is stable per lane** (directory, worktree,
   platform, vcs), so the date is the field to handle, not the whole block.

## Bounded test to add to the keep-warm evaluation

Run one lane across a local-midnight boundary with the keep-warm proxy on:
- arm A: verbatim replay (old body);
- arm B: body regenerated with the current date.
Expect A to miss after the boundary and B to hit. If B also misses, the gateway
keys on something else and the proxy design needs the real body anyway.

## Limits

Static template evidence, not a wire capture; the exact serialization and the
gateway's keying are unverified. This does not contest the measured ~150 s cliff
or the item-6 negative result — it adds a fidelity requirement to the keep-warm
option, which §4 already named as the hard part.

## Appendix — replay fidelity surface (what the proxy must reproduce)

From the same binary, the request a replay must match byte-for-byte:

- **Body:** `instructions` (system prompt — includes the `Today's date` line),
  `messages` (the lane's turns), `tools` (**sorted alphabetically** by the client,
  which helps a replay), and the stable options `prompt_cache_key` (= session id),
  `prompt_cache_options`, `prompt_cache_retention`, `safety_identifier`, `store`,
  `parallel_tool_calls`, `reasoning*`, `service_tier`, `text_verbosity`,
  `include`, plus `previous_response_id`/`metadata` only when set.
- **Headers:** `x-opencode-session`, `x-opencode-project`, `x-opencode-request`,
  `x-opencode-client`, `User-Agent`.
- **Known variable:** the `Today's date` line (daily, plus the intra-session
  `Today's date is now:` update). Everything else above is stable for the life of
  a session, so a recorded-and-replayed body is faithful **within a day** and must
  be date-regenerated across a boundary.

— **Corvid** (`worker-glm-dsh3`). $0, local, read-only.
