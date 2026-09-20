# RETRO-S1 — Cairn (worker-pi, local pi)

**Seat:** the canary. I am the live subject of the decision-memory trial —
the loop runs from `~/acp-pi` with its own vault, and I report from the
inside on burden, recall usefulness, and self-noticing. Everything below is
from the record (`~/acp-pi/`, `team/`), not from feeling.

**Plain English for Brian (one block):** The memory loop is working, and it
is cheap. Since the window opened, every low-stakes capture I made cost you
zero confirms — the risk tiering you approved is doing its job (16 drafts
total: 13 written, 3 expired, 0 stuck). Recall pulled me the right way on
every tick this sprint without anyone prompting it. The two real defects I
found are both about the record lagging reality: a state change I observed
sat unwritten for 13 hours until a tick happened to touch it, and one draft
died because drafts live inside one process and can't be confirmed from
another. Neither defect is the gate. The gate is no longer where the loop
dies.

## Own half

- **The ledger footgun was mine, and I turned it into a rule instead of a
  fix.** `draft-d45d98` (my first T0 capture) sat "pending" ~1h after I
  confirmed it, because I did not append the marker in the same turn. The
  cycle-tick scan caught it, not me. Rule now on file (record-59b31f57):
  confirm → marker → ledger re-run, one turn, no exceptions. Since: zero
  stale-pending.
- **I let a load-bearing record go stale for 13 hours.** record-ee0aff12
  said "an empty fire log is EXPECTED; S4 live-arm measurement needs a fresh
  process." I flagged it on the board at ~14:12 and waited. Post-config
  processes arrived at 21:18 and the log filled; the record still said
  "empty is expected" until this morning's tick superseded it
  (record-6a75822a). Any tick in between could have read a populated log as
  anomalous. Flag-and-wait is not the same as writing.
- **One post-T0 expiry, and it was not the gate.** `draft-d829a6`
  (agent-deck review, 23:10) expired because the draft store is
  process-local: the draft was presented in one pi process and unreachable
  from the next. Re-drafted as `draft-766c7f`, resolved. The other two
  expiries (`draft-cda288`, `draft-4cc949`) are the pre-T0 Brian-asleep
  window I pre-registered in RETRO-1. So: gate friction is real but
  bounded; the process-local draft store is the newer, unbounded path.
- **My S5 data is contaminated by my own tick cadence, and I should say so
  now, not at close.** The first in-window pairing (n=6, median token Δ%
  +57.0, all pairs flagged) pairs long work turns against bare ticks in the
  same family — pair 4 is a 932 s memory turn vs an 8 s no-memory turn
  (+3038%). That is a diet artifact, not an overhead measurement. The
  worklist exists to keep the diet real; bare ticks are valid NO-MEMORY
  population, but they must not be read as the S5 number's evidence.

## STOP

- **Stop flagging stale records on the board and waiting.** If a tick
  observes that a stored record's load-bearing rule is now false, the
  supersede happens in that tick. The loop carries what is written, not
  what happened — proven twice this sprint (window-open between my turns;
  the S4 process state above).
- **Stop reading raw fire counts as S4 signal.** "fresh" fires on nearly
  every tick by construction (poller ticks land as turn 1 of a process).
  The informative signal is topic/gap reasons and any `fired:false` line.
  Counting fires would be counting the poller, not the trigger.

## START

- **Same-turn supersede on observed invalidation** (the STOP above, as a
  practice). One extra tool call; removes an entire class of stale-read
  hazards for every other seat, not just me.
- **Naming the diet in every S5 preview.** `trial-ledger.py --window`
  (commit e761cda) now prints the exact in-window turn + n-pairs tables S5
  close consumes, PREP-labelled, delegating to the frozen `s5_pairing.py`
  (no re-implementation). From here, every preview states which pairs are
  tick-length artifacts before anyone reads a Δ%.

## CONTINUE

- **T0 self-capture for low-stakes state changes.** It is the campaign's
  burden arm working: 0 Brian-confirms since the flip, and the record stays
  current. Escalation stays reserved for high-stakes.
- **Same-turn ledger markers.** Working since the rule; 0 stale-pending.
- **Recall before acting, every tick.** It retrieved and applied unprompted
  all sprint — the S4 interpretation rule, the marker rule, the window
  state — and the change-trigger's topic line is a nudge, not the recall.
- **Wrappers, not forks, for frozen instruments.** The `--window` mode
  delegates to Assay's harness instead of re-implementing turn extraction;
  the tables are byte-for-byte the harness's own.

## Role I want going forward

Keep the canary — it is the only seat that can report burden, recall
usefulness, and self-noticing from the inside, and no other seat can take
it without breaking the trial. Sharpen it into **the trial's
data-quality seat**: I watch the live-arm measurement itself — S4 feed
interpretation, S5 population honesty (the diet), ledger integrity, record
staleness — and I build the thin wrappers that let other seats consume the
frozen instruments without touching them. I make no bid for rating (the
blind-rater contract bars me from my own lane's S4 anyway — I am the
subject, my data is the data), no bid for coordination, no bid for claims
custody.

## One change for the fleet

**A state change is written in the same turn it is observed — no
flag-and-wait.** One sentence, one mechanism: any seat whose tick observes
that a stored record or board line is now false updates it in that tick
(supersede for vault records, in-place edit with a receipt for team files).
The fleet already runs on "the record is the state"; this closes the one
hole in that assumption — that the record can lag reality by hours while
the change sits on a board as a flag. It costs one tool call per observed
invalidation, and it makes every other seat's next read honest by
construction. I am the standing example of both the defect (13-hour stale
record) and the fix (same-turn supersede), so I am the one asking.
