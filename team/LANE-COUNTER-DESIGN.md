# Lane task/spend counter — design note + sketch

**Author:** Corvid (worker-glm-dsh3, acp-dsh metered probe/eval seat)
**Task:** QUEUE row 3 — make "bounded" a number for metered lanes
**Date:** 2026-09-12 12:18 PDT
**Status:** design only — one bounded turn (this row's cap). No experiment,
pipeline, benchmark, or provider-API call was made, and no spawn beyond this
turn; all reads were local and read-only (files and one SQLite count). The
sketch is not installed or executed.

---

## Plain English (for Brian)

The three pay-per-token "dsh" research lanes (Aletheia, Assay, me) currently
operate under the rule "bounded tasks only" inside a $5 cap. Nothing counts
how much of that $5 a lane or a task uses. From the seat, that reads as "don't
start anything" — which is why three seats sat idle, not because they were
expensive. My own metered work this sprint cost about $0.002.

This note says where a real number can come from, defines "bounded" as three
specific numbers, and sketches a small read-only script that would print them.
Adopting it costs $0 and changes no engine, no pipeline, and no campaign
result. If you say no, nothing changes: lanes stay parked and the $5 is never
spent.

The one decision: **approve the per-row bound format (turns / tokens / dollars)
and the counter as the thing that reads it**, so a lane with a live hypothesis
can start against a number instead of a ban. Saying "keep the freeze" is also a
fine answer — it would only be explicit now, which is the point.

---

## 1. The problem, with receipts

- `team/CAMPAIGN-1.md:256-260`: the dsh lanes are *"metered with no counter →
  bounded tasks only… no further spend."*
- `team/RETRO-1-SUMMARY.md:51-57`: six seats independently diagnosed the same
  failure — an unmeasured bound cannot be obeyed, only over-obeyed. Assay,
  verbatim: *"the only defensible behavior … is to do nothing."*
- `team/BOARD.md:26-33` (mine): the only dollar figure in `team/` was a
  snapshot in a scorecard ("$16.38 remains"), scored **SILENT** for lack of a
  spend receipt. A counter that reads our own prose measures prose.

So the number has to come from state the lanes do not write.

## 2. What already exists (found before designing)

**A. The counter schema already exists — and is empty.** agent-deck's state DB
has exactly the table this task asks for:

```
agent-deck/profiles/default/state.db → cost_events
  (id, session_id, timestamp, model, input_tokens, output_tokens,
   cache_read_tokens, cache_write_tokens, cost_microdollars,
   budget_stop_triggered)
```

Read-only check this turn: **0 rows**. The platform chose the schema; nothing
emits to it. `~/.local/share/agent-deck/cost-events/` is also an empty
directory. That is why the spend figure was a snapshot, and it is the single
most useful fact in this note: the counter is missing an *emitter*, not a
schema. `recent_sessions(id, title, project_path, group_path, …)` already maps
a session to a lane.

**B. Account truth (dollars) — already implemented.** `~/conductor-chat/meters.py`
computes

```
spentUsd = (baseline.deepseekLeft − deepseek.left)
         + (openrouter.used − baseline.openrouterUsed)
cap      = min($25, spent + credit left)
```

Baseline lives in `~/.config/agent-deck/dsh-budget.json` (`capUsd: 25.0`,
`baseline.deepseekLeft: 16.55`, `baseline.openrouterUsed: 0.00532895`), and
`~/.config/agent-deck/dsh-lane:82-86` refuses to start a metered session when
`meters.py --check` fails closed. This is the external source the board post
asked for. It is **fleet-wide, not per-lane**, and it is already the hard stop.

**C. Lane attribution (tokens) — harness-written, currently unread.** Each dsh
session writes
`~/.dsh/storages/session_projcache/sessions/<session-id>.json` with
`record.rows.tokenUsage.val.totals = {uncachedInputTokens, outputTokens,
cacheReadTokens, cacheWriteTokens}` and `record.identity.cwd` plus
`record.rows.title` identifying the lane/seat. Written by the harness, not the
lane. No dollar value; it needs a declared price table.

**Read-only sample of that input (this turn; local file reads only):**

| lane cwd | sessions | uncached in | out | cache read |
|---|---|---|---|---|
| repo-glm-dsh3 (Corvid) | 4 | 158,027 | 72,463 | 4,527,616 |
| repo-glm-dsh2 (Assay) | 5 | 146,940 | 84,900 | 4,974,336 |
| conductor-chat-glm-dsh | 5 | 133,704 | 88,657 | 10,096,512 |

All-time, not campaign-only. Tokens are real; dollars are deliberately absent
because there is no versioned price table, and the standing rule is
`implementer/dispatch/MEMORY_BAKEOFF_RESET_PLAN.md:49` — *log unavailable
cost as unavailable, not zero.*

## 3. What "bounded" means as a number

A queue row is bounded iff it states all three, and each is readable from a
source the lane does not write:

| field | unit | source | readable now? |
|---|---|---|---|
| `cap_turns` | turns | `tokenUsage.val.last.turn` delta | yes |
| `cap_tokens` | tokens (primary) | `tokenUsage.val.totals` delta | yes |
| `cap_usd` | dollars | `meters.py` budget delta | account: yes; per-lane: after the price table |

Claim arithmetic — the whole point:

```
allow(lane, row)  iff  row.cap_usd    <= leftInBudgetUsd              # fleet ceiling
                  and  row.cap_turns  <= lane.turnEnvelope  − used    # fairness
                  and  row.cap_tokens <= lane.tokenEnvelope − used    # primary unit
```

Close arithmetic — what makes the bound falsifiable:

```
if actual > row.cap_* :  record a bound violation
                         block the lane's next claim until GiLMore resets
```

That is the difference between "bounded tasks only" (a mood) and *"this task is
≤2 turns, ≤120k tokens, ≤$0.05; here is what it actually used."*

## 4. Counter sketch

Two layers, on purpose. The account layer is money-exact but not
lane-attributable; the lane layer is attributable but token-based. Never let
one silently stand in for the other — report the residual.

```python
# team/lane-meter — SKETCH ONLY, not installed, not run. stdlib, read-only.
#   lane-meter                  print the table
#   lane-meter --check <usd>    exit 3 if <usd> would exceed the fleet budget
import glob, json, os, re, sqlite3, sys

DSH_SESSIONS = os.path.expanduser(
    "~/.dsh/storages/session_projcache/sessions/*.json")
STATE_DB = os.path.expanduser(
    "~/.local/share/agent-deck/profiles/default/state.db")
QUEUE = "/home/bmosher/memory-bake-off/team/QUEUE.md"

# model -> USD/token for {in, out, cache_read, cache_write}. MUST be versioned
# (source + date). Empty = report tokens and mark dollars unavailable.
PRICES = {}


def sessions_by_lane():
    """Fallback source: harness-written per-session token totals."""
    lanes = {}
    for p in glob.glob(DSH_SESSIONS):
        try:
            d = json.load(open(p))["record"]
        except (OSError, KeyError, ValueError):
            continue                      # unreadable = unknown, not zero
        lane = os.path.basename(d["identity"]["cwd"].rstrip("/"))
        tu = (d["rows"].get("tokenUsage") or {}).get("val") or {}
        tot = tu.get("totals")
        if not tot:
            continue
        c = lanes.setdefault(lane, dict(sessions=0, turns=0,
                                        in_=0, out=0, cr=0, cw=0))
        c["sessions"] += 1
        c["turns"] += tu.get("last", {}).get("turn", 0)
        c["in_"] += tot["uncachedInputTokens"]; c["out"] += tot["outputTokens"]
        c["cr"] += tot["cacheReadTokens"];      c["cw"] += tot["cacheWriteTokens"]
    return lanes


def dollars(c):
    """None (unavailable), never 0, when prices are absent."""
    if not PRICES:
        return None
    return (c["in_"] * PRICES["in"] + c["out"] * PRICES["out"]
            + c["cr"] * PRICES["cr"] + c["cw"] * PRICES["cw"])


def fleet():
    """Reuse the one existing meter; do not re-derive the baseline."""
    sys.path.insert(0, os.path.expanduser("~/conductor-chat"))
    import meters
    return meters.budget()   # {spentUsd, capUsd, leftInBudgetUsd, ...}


def emitted_cost_events():
    """Preferred source once something emits to it: cost_events is per-session
    and already carries model + cost_microdollars."""
    c = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
    try:
        return c.execute(
            "select session_id, model, cost_microdollars from cost_events"
        ).fetchall()
    finally:
        c.close()


def tasks_done():
    """Task count = QUEUE rows marked done whose artifact exists on disk.
    Lane attribution comes from the row; existence is the receipt."""
    out = {}
    for line in open(QUEUE):
        if "| done:" not in line:
            continue
        m = re.search(r"done:\s*(\S+)", line)
        if m and os.path.exists(m.group(1)):
            out["<seat column>"] = out.get("<seat column>", 0) + 1
    return out


# main(): print lane | tasks | turns | tokens(in/out/cache) | est_usd | fleet
#         row; then show fleet_spent − Σ lane_est_usd as the named residual.
# --check <usd>: exit 3 when <usd> > fleet()["leftInBudgetUsd"].
```

Notes that matter more than the code:

- It **imports `meters.py`** rather than re-deriving the baseline. One meter,
  one meaning.
- It reports **tokens primary, dollars secondary** (`CAMPAIGN-1.md:160`), and
  `unavailable` rather than a blended rate. Cache reads are ~10x cheaper than
  uncached input; a blended price would overstate every lane.
- It prefers `cost_events` when populated, falls back to the session store
  now. It never writes; running it costs nothing.
- The lane cannot edit its own number except by spending — the input files are
  written by the harness/deck, not by the lane. That is the whole test.

## 5. What it does not measure (honesty block)

- **Conductor/chat overhead is unattributed.** `conductor-chat-glm-dsh` spends
  against the same accounts but is not a lane. Show
  `fleet_spent − Σ lane_est_usd` as a named residual; never fold it into a lane.
- **No price table is committed.** Until one is, per-lane dollars read
  `unavailable`. Do not invent a rate.
- **`meters.py` is a cumulative balance delta**, not per-task. A per-row dollar
  actual is an attribution claim; turns and tokens are receipts.
- **Session-store coverage is unproven.** 27 files exist under
  `session_projcache`; whether every dsh session lands there was not tested
  this turn. A missing session is unknown, not zero.
- **Provider unreachable ⇒ fail closed** — already true in `meters.py`.

## 6. Adoption (one column, one emitter, one line)

1. Add `cap_turns` / `cap_tokens` / `cap_usd` to the QUEUE row format. The
   existing `Cost cap` cell already anticipated this; row 1's
   "1 turn, flash/metered ≤$0.05" is the shape.
2. Populate `cost_events` (the platform's own table) from the harness adapter,
   with a versioned price table; until then run the sketch on the session
   store.
3. Leave `dsh-lane`'s `meters.py --check` as the hard stop. Add
   `lane-meter --check` only for the account cap.
4. GiLMore enforces bound-violation → next-claim-blocked.

Cost of adoption: $0 generation. Benefit: a lane with a live hypothesis can
start against a number instead of a ban — the failure six seats reported.

— **Corvid** (worker-glm-dsh3). I'd rather bring back "did not answer" with
bytes than a confident story; here the bytes say the counter's schema exists,
its table is empty, and its dollar source is account-wide until someone
version-controls a price table.
