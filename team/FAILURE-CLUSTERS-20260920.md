# Failures of 2026-09-20, clustered by subsystem and mechanism

Twenty defects found in one day. Grouped by what the code did wrong, not by
who wrote it.

## By mechanism

### M1 — Identity inferred from an incidental attribute (6)

The code needed to know *which thing this is* and derived it from something
correlated rather than something declared.

| subsystem | the attribute used | what it should have read |
|---|---|---|
| escalation transport | whichever process won port 8787 | a declared target |
| role identity (poller, UI, status) | title starts with `conductor-` | `CONDUCTOR_SEAT` |
| ownership (web UI) | session `groupPath`, set from a path years of history ago | `FLEET_SEATS` |
| billing identity | adapter name (`muse-engine acp`) | the model behind the gateway |
| provenance | the act of claiming a row | whether the claimant is the row's verifier |
| gate-writer routing | board says `plumb-fable` owns the G rows | the process that actually writes them (`gate-batch`+astra) |

### M2 — Free-text substring used as a state predicate (3)

The identical regex `\bclosed\b`, in three files, matching inside `fail-closed`
and inside sentences about other rows.

| file | what it decided |
|---|---|
| `gate-batch` pending() | deleted a row corvid had returned for re-issue |
| `fleet-poller` sprint-close | counted an unwritten row as finished, twice escalating |
| `sprint-status` done_prose | reported 4/4 finished for a sprint with 3 finished |

### M3 — Guard scope ≠ enforcement scope (4)

The condition is checked at one granularity and spent, reset or violated at
another.

| subsystem | checked at | acted at |
|---|---|---|
| retry ladder | counter keyed per **kind** | reset per **row** — never reached attempt 2 |
| retry ladder | reset on a **verdict** | work changed by a **new artifact** — chase never restarted |
| resource gating | ceiling read per **row** | spent per **round**, 3 calls deep |
| work admission | brief freshness guard, 30 min | its **input** (the backlog) changed in 2 |

### M4 — Absence treated as a value (2)

| subsystem | the absence | how it was read |
|---|---|---|
| resource gating | `rateLimits: {}` from the API | "quota exhausted" — parked the fleet hourly |
| resource gating | unreadable Codex window | "no room" — gates deferred |

### M5 — Supervision covers failure, not absence (3)

| subsystem | what is watched | what is not |
|---|---|---|
| unit supervision | a unit that **fails** | `agent-deck-failover` had no handler at all |
| timer supervision | a unit that **fails** | a timer an agent **stopped** — no alarm exists for off |
| escalation reader | the ledger is durable | nothing **reads** it without Brian typing |

### M6 — Predicate tests the mechanism, not the decision (1)

`gate-batch` asked "does the gate pass its own selftest?" A gate that fails
closed passes its own selftest, so a gate the verifier had **rejected** was
invisible to the only thing that rewrites gates. Its docstring already promised
the correct behaviour.

### M7 — Capability placed below the layer that decides (1)

The RouteLLM fallback lives in `astra`, called by `gate-write`. `gate-batch`
checks the ceiling and defers **before** reaching either, so the fallback was
unreachable by design and sprint 13's gates sat unwritten.

### M8 — Two locations for one fact (3)

| subsystem | location A | location B |
|---|---|---|
| artifact visibility | corpus on disk, absolute paths | the git repo seats resolve against — 983 files apart |
| ledger reading | `fleet-poller` honours retractions | `sprint-status` read only `producer` lines |
| work state | `sprint-close` file says closed | the board's computed rows say open |

## By subsystem

| subsystem | count | modes |
|---|---|---|
| resource gating (quota, ceilings) | 5 | M3, M4, M7 |
| retry / escalation ladder | 5 | M1, M3, M5 |
| state computation | 4 | M2, M8 |
| role identity | 4 | M1 |
| work admission | 3 | M3, M6, M8 |
| artifact visibility | 2 | M1, M8 |
| supervision | 2 | M5 |

## Detection

| found by | count |
|---|---|
| Brian asking a question | 8 |
| corvid, through the escalation ledger | 4 |
| a mechanical check (`fleet-stalled`, `rowcheck`, unit failure) | 4 |
| me, while reading adjacent code | 4 |

Eight of twenty were found because a human asked. No alarm existed for M1, M2,
M6, M7 or M8 — those classes are undetectable by the current instruments,
because every instrument tests a named condition and these are all *the
instrument itself being wrong*.

## What is mechanically checkable

- **M2** is a lint: no state predicate may match free text. Grep for
  `grep -qi` and `re.search` inside any function that returns a row's state.
- **M3** is a lint: a counter's key and its reset key must be the same
  expression. Four of four instances violate that literally.
- **M4** is a type rule: a reading is `Optional`, and `None` must not compare
  against a threshold. All four call sites coerced it silently.
- **M1** is a convention: identity comes from a declared constant, never from
  a name, port, path or action. `CONDUCTOR_SEAT` and `FLEET_SEATS` now exist;
  nothing enforces their use.
- **M5, M7, M8** are architectural and not lintable: they are about where a
  thing lives relative to the thing that needs it.
