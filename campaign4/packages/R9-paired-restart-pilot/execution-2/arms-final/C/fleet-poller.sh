#!/bin/bash
# fleet-poller v3.0 — no-limits-engine pulse for the memory-bake-off fleet.
# Design of record: team/PROPOSAL-RESEARCH-HEARTBEAT-20260914.md Rev 2
# (verified by builder 2026-09-14; sign-off filed in that file).
# Detects stalled lanes via acp-history mtime (last real activity), wakes the
# time-based duties, flags stalls for GiLMore. NOT a registered session: this
# is fleet infrastructure. Stop: touch fleet-poller.stop (checked every sweep;
# Brian's halt keeps working).
# v1.1: Ledger anti-spam (BOARD excluded, 30min margin). v1.2: builder ticket
# intake. v1.3: section-6 self-serve row pulse. v1.6: section-7 live-id R&D
# pulse. v1.8.1: GLM night guards.
# v3.0 (2026-09-14): rebuilt to Rev 2 (no-limits engine, Brian's catch) —
#   single Spark class on a 5 min poll, NO night backoff (quota cost is zero;
#   binding constraint is attention, and the matcher only fires on real rows);
#   rater-path + stratum event-only exclusions enforced at the wake() choke
#   point from $DIR/poller-exclude (titles + id prefixes, GiLMore maintained —
#   the blind seat is dynamic, so a static list would rot); stratum removed
#   from all poll seat lists; meter wiring kept as fail-closed plumbing only.
# v3.1 (2026-09-15, event-driven trial): §7 generic pulse replaced by gated
# wakes (fire only on new content, fingerprint per lane); §6 row pulse
# fingerprinted (one in-flight per seat). §1-4 duties untouched.
# ---------------------------------------------------------------------------
# BUILD CONSTRAINT FOR EVERY CLOCK IN THIS FILE
# A clock needs a predicate that can come back false without anyone's
# cooperation. A word in a row's status text is NOT a predicate - it is a
# sentence a seat can type. Before adding a clock, name what makes it fire and
# what makes it stop, and check that neither is a string a seat can write.
# If the stop condition is prose, the clock reports healthy forever.
# Measured 2026-09-15: the 10/20 inactivity timer fired 12 times and escalated
# ZERO, because "a posted reason resets the clock" is satisfied by ordinary
# chatter - RD-THREADS.md took 606 edits in 24h, one post every five minutes.
# Prefer: a file that exists, an mtime, a hash change, a counter. Avoid: a
# verdict word, a status phrase, a transcript timestamp that any turn refreshes.
# ---------------------------------------------------------------------------
export HOME=/home/bmosher
# Testability: DIR/HIST/WAKE_BIN/QUEUE/GATED honor env overrides so the
# gated engine runs hermetically (fixtures + temp state, no live registry,
# no sends). Unset in production → byte-identical behavior.
DIR=${POLLER_DIR:-/var/home/bmosher/.local/share/agent-deck/conductor/glm}
LOG=${POLLER_LOG:-$DIR/poller.log}
STOP=$DIR/fleet-poller.stop
EXCL=$DIR/poller-exclude
WAKE_BIN=${POLLER_WAKE:-$HOME/.config/agent-deck/wake}
HIST=${POLLER_HIST:-/home/bmosher/.config/agent-deck/acp-history}
# Turn-in-flight surface (QUEUE D-4): the worker emits {"t":"start"|"end"}
# records here per turn. A seat whose newest stream item has a start with no
# end has a turn RUNNING - it is blocked (e.g. on the shared Z.ai slot), not
# broken, and must never be judged on its older answers.
STREAM=${POLLER_STREAM:-${HIST%/*}/acp-stream}
BOARD=/var/home/bmosher/memory-bake-off/team/BOARD.md
TICKDIR=/var/home/bmosher/.local/share/agent-deck/support-tickets
METERS=/var/home/bmosher/conductor-chat/meters.py
METER_STATE=$DIR/poller-meter-hold
METER_TTL=300          # re-run meters.py --check at most every 5 min
CAIRN_HIST=$(ls -t $HIST/721125ec-*.jsonl 2>/dev/null | head -1)
FSYNC_HIST=$(ls -t $HIST/14f7d808-*.jsonl 2>/dev/null | head -1)
LEDGER_HIST=$(ls -t $HIST/72180e11-*.jsonl 2>/dev/null | head -1)
BUILDER_HIST=$(ls -t $HIST/cecd108c-*.jsonl 2>/dev/null | head -1)
CAIRN=721125ec-1788910840
FSYNC=14f7d808-1789196406
# LEDGER names ledger-claude's session (72180e11), matching LEDGER_HIST above.
# PO ROUTING FALLBACK, explicit per QUEUE D-1 (2026-09-17): ledger-claude is
# furloughed (2026-09-15 roster) and sits in poller-exclude, so PO-bound
# notices are NOT sent to $LEDGER - they go to Brian via brian_do() (Signal
# RPC, per-kind cooldown), with cairn-pi ($CAIRN) conducting and holding the
# PO role until Ledger is unparked. The pre-D-1 line set LEDGER to cairn's
# id, so the variable's name lied about its value and the fallback
# was an accident of that alias (the old line pointed LEDGER at cairn's id,
# 721125ec). Routing itself is unchanged.
LEDGER=72180e11-1789149653
PO_ROUTE=$CAIRN   # explicit recipient of PO-bound lines while Ledger is parked
BUILDER=cecd108c-1788910839
# metered-dsh seat prefixes: held while meters.py --check refuses (stop rule).
# 2026-09-15: EMPTIED on Go migration — assay/aletheia/corvid now run
# acp-go-deepseek (opencode-go subscription model, off the $25 metered card),
# so a meter-refuse must not hold them. Restore prefixes only if a lane
# returns to DeepSeek/OpenRouter pay-as-you-go spend.
DSH_IDS=""
INTERVAL=60           # seconds between sweeps; per-class thresholds dominate
MIN_GAP=90           # never wake the same lane more than once per 90 s

# ---- clock thresholds, at MACHINE scale --------------------------------------
# These were 10/20/30/60 MINUTES, which are human numbers. Measured unit of work
# on this fleet: a GLM-5.3-Flash turn is 6-12 s and cairn's median turn is 14 s.
# Ten minutes is forty turn-lengths; the old 20-minute claimed-dark clock let a
# row sit through a hundred of them before anyone was told. MIN_GAP=90 is the
# floor - a threshold below it cannot fire twice anyway - so these are set at
# roughly 2x to 10x MIN_GAP rather than at human patience.
#
# Proper exponential backoff with an attempt counter is plan section 4 and is
# not built yet; these keep the existing one-fire semantics and simply stop
# measuring computer time in coffee breaks.
T_UNCLAIMED=150      # open row, eligible seat, nobody took it (was 600)
T_CLAIMED_DARK=300   # claimed, owner has written nothing since (was 1200)
T_VERDICT=450        # done, no verdict filed (was 1800)
T_VERDICT_ESC=900    # done, no verdict, verifier dark -> tell a human (was 3600)
STALL_CAIRN=120      # 2 min without trial activity = tick (local lane: free)
STALL_FSYNC=300      # 5 min without watch line = duty due
SCORE_FRESH=7200     # scoreboard max age while window open (event-refresh on top)
TICKET_SETTLE=60     # ticket change must be >=1 min old before waking builder

declare -A LASTWAKE
METER_HOLD=0
EXCL_IDS=""
now() { date +%s; }
log() { echo "$(date -u +%FT%TZ) $*" >> "$LOG"; }
mt() { stat -c %Y "$1" 2>/dev/null || echo 0; }
# HOISTED 2026-09-16. Both of these lived inside the sweep loop, so sourcing
# this file through the POLLER_SOURCE_ONLY seam left them UNDEFINED and every
# call failed silently - which made a correct poller-exclude entry read as "not
# excluded" and made verifier_for return nothing, both of which I nearly
# reported to Brian as real findings. It also meant the suite's checker-picking
# tests ran against a STUBBED seat_id_for and never exercised the parked-seat
# branch at all. seat_id_for still reads $REGMAP, which the sweep rebuilds each
# pass; a test supplies its own.
is_parked() { # seat name -> 0 when that title sits in poller-exclude
  local nm
  nm=$(echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/([^)]*)//g; s/^ *//; s/ *$//')
  [ -z "$nm" ] && return 1
  [ "${#nm}" -lt 3 ] && return 1
  grep -qi "^title:.*${nm}" "$EXCL" 2>/dev/null
}
seat_id_for() { # free-text name -> session id via title match, "" if none
  local nm
  nm=$(echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/([^)]*)//g; s/^ *//; s/ *$//')
  [ -z "$nm" ] && return 1
  [ "${#nm}" -lt 3 ] && return 1
  [ "$nm" = "alice" ] && nm="aletheia"
  [ "$nm" = "gilmore" ] && nm="conductor-glm"
  echo "$REGMAP" | awk -v nm="$nm" '
    { title=$1; id=$2; base=title; sub(/-(dsh|claude|flash|muse)$/, "", base)
      if (index(title, nm) || index(nm, title) || index(nm, base)) { print id; exit } }'
}
# LOG ONCE PER STATE. Found by cairn, 2026-09-16: "the GATE/SPRINT-CLOSE log
# lines are re-firing every sweep because they're not gated on the transition,
# though the chain state is preventing re-wakes." Exactly right, and exactly my
# bug - both lines were added that day and neither was gated. 69 duplicate lines
# in the log before it was noticed, ~2 per sweep. The WAKES were fine; only the
# log repeated, which is the kind of noise that buries the line that matters.
#
# Keyed by caller-chosen id: logs only when the text for that id CHANGES, so a
# steady state is silent and a real transition still speaks. Returns 1 when it
# suppressed, in case a caller wants to know.
NOTED=${POLLER_NOTED:-$DIR/noted}
log_once() {   # key, text
  local f="$NOTED/$1" prev
  mkdir -p "$NOTED" 2>/dev/null
  prev=$(cat "$f" 2>/dev/null)
  [ "$prev" = "$2" ] && return 1
  [ -n "${DRY_RUN:-}" ] || printf '%s' "$2" > "$f" 2>/dev/null
  log "$2"
}
# Artifact movement, per owner. The darkness test used to be the owner's
# transcript mtime, which ANY turn refreshes - including the one-line reply
# to the nudge itself. So a seat that answered "still working on it" looked
# alive for another 20 minutes without moving anything. This asks a
# different question: when did this owner last WRITE something that is not
# bookkeeping? Tool records carry kind="edit" and the paths they touched.
art_ts() { # history-file -> epoch of newest non-bookkeeping write, or 0
  [ -z "$1" ] || [ ! -f "$1" ] && { echo 0; return; }
  python3 - "$1" <<'ARTPY'
import json, os, re, sys
BOOK = re.compile(r"(task-log\.md|RD-THREADS\.md|QUEUE\.md|BOARD\.md|"
                r"LEARNINGS\.md|state\.json|poller\.flags|\.log$|"
                r"/inactivity/|/acp-history/|/acp-stream/)", re.I)
edits, best = set(), 0.0
try:
  rows = [json.loads(l) for l in open(sys.argv[1], errors="ignore") if l.strip()]
except Exception:
  print(0); raise SystemExit
for d in rows:
  if not isinstance(d, dict) or d.get("role") != "tool":
      continue
  if d.get("kind") == "edit" or d.get("diffs"):
      if d.get("id"):
          edits.add(d["id"])
for d in rows:
  if not isinstance(d, dict) or d.get("role") != "tool":
      continue
  if d.get("id") not in edits:
      continue
  paths = [p for p in (d.get("paths") or []) if p and not BOOK.search(str(p))]
  if paths and d.get("at"):
      best = max(best, float(d["at"]))
print(int(best))
ARTPY
}
# Event-only exclusions (Rev 2 §2b): rater path + stratum never wake from any
# poll. Resolved to ids each sweep (titles survive recreations); enforced HERE
# so no section can originate a rater/Brian-facing wake by any path.
# Exclusion file format, one per line (# comments, blanks ignored):
#   title:<registry title, lowercase>   (survives session recreations)
#   id:<session-id prefix>              (pins one incarnation)
excl_poll() {
  EXCL_IDS=""
  [ -f "$EXCL" ] || return 0
  local clean titles prefixes
  clean=$(grep -v '^[[:space:]]*#' "$EXCL" 2>/dev/null | grep -v '^[[:space:]]*$')
  titles=$(echo "$clean" | grep '^title:' | cut -d: -f2)
  prefixes=$(echo "$clean" | grep '^id:' | cut -d: -f2)
  if [ -n "$titles" ]; then
    EXCL_IDS="$EXCL_IDS $(agent-deck list --json 2>/dev/null | python3 -c '
import json,sys
want=set("""'"$titles"'""".split())
try:
    rows=json.load(sys.stdin)
except Exception:
    rows=[]
for r in rows:
    if (r.get("title","").lower() in want): print(r["id"])
' 2>/dev/null)"
  fi
  EXCL_IDS="$EXCL_IDS $prefixes"
}

# RE-READ LIVE STATE BEFORE WAKING (RETRO-3 "Keep", filed by fsync).
# Theorem 1 in the iteration-3 plan assumed the inputs are read and acted on
# atomically. They are not: the sweep reads QUEUE at its top and wakes later,
# so the snapshot is stale by decision time. That missing assumption is why
# corvid saw four "claimed-dark wake read its pre-done snapshot" events on
# 2026-09-16 while the clock remained provably live - liveness was proved,
# soundness never was.
row_status_now() {   # task text -> that row's CURRENT status cell, or empty
  awk -F'|' -v t="$1" '/^\|/ && $0 !~ /\|---/ {
      task=$3; gsub(/^[ \t]+|[ \t]+$/,"",task)
      if (task==t) { st=""; for(i=8;i<NF;i++){ st=st ((i>8)?"|":"") $i }; print st; exit }
    }' "$QUEUE" 2>/dev/null
}
row_closed_now() { grep -qi "done:" <<<"$(row_status_now "$1")"; }
# THE DISPATCH LEDGER. A record of who was handed which row, kept by the poller
# rather than by the seats it describes.
#
# The problem it solves: independence was checked by comparing the row's own
# "claimed:" text against its own "verifier:" text. Both are written by an
# agent, so a seat that did the work could name someone else as the author and
# sign off on itself, and the loop could not tell. That is the defect the whole
# iteration-3 plan exists to remove, still live in the one place it matters most.
#
# Append-only, never rewritten, and NOTHING the agents can reach writes to it.
# A file an agent can edit is not evidence about that agent.
DISPATCH=${POLLER_DISPATCH:-$DIR/dispatch.log}
ledger_note() {   # rowkey, seat-name, seat-id : record a PRODUCER dispatch
  [ -n "$1" ] && [ -n "$2" ] || return 0
  [ -n "${DRY_RUN:-}" ] && return 0
  printf '%s %s producer %s %s\n' "$(now)" "$1" "$2" "${3:--}" >> "$DISPATCH" 2>/dev/null || true
}
ledger_is_producer() {   # rowkey, seat-name-or-id : 0 if that seat was sent to
                         # PRODUCE this row, so it may not verify it
  local key="$1" who="$2" wid
  [ -f "$DISPATCH" ] && [ -n "$key" ] && [ -n "$who" ] || return 1
  # seat_id_for is defined inside the sweep loop, so it is absent when these
  # helpers are sourced for a unit test. Name matching alone is still correct;
  # the id is a second chance to match, not the basis of the check.
  wid=$(seat_id_for "$who" 2>/dev/null || true)
  awk -v k="$key" -v n="$(echo "$who" | tr '[:upper:]' '[:lower:]')" -v i="$wid" '
    BEGIN { found = 0 }
    $2 == k && $3 == "producer" {
      if (tolower($4) == n || (i != "" && $5 == i)) { found = 1; exit }
    }
    END { exit(found ? 0 : 1) }' "$DISPATCH"
}
ledger_producers() {   # rowkey : the seats sent to produce it, for the message
  [ -f "$DISPATCH" ] && [ -n "$1" ] || return 0
  awk -v k="$1" '$2 == k && $3 == "producer" { print $4 }' "$DISPATCH" | sort -u | tr '\n' ' '
}
# WHO CHECKS THE WORK. Not a judgement, a lookup: the live worker that was not
# handed this row. Until 2026-09-16 the loop paged Brian whenever a finished row
# had no reachable verifier named, which made him the router for a decision with
# exactly one possible answer.
#
# Excluded from the candidates, each for a stated reason:
#   the conductor  - it routes and escalates, it does not judge state (plan §6)
#   any producer   - cannot mark its own homework (the dispatch ledger knows)
#   parked seats   - furloughed, so asking them stalls the row silently
#   unresolvable   - a name with no live session cannot be woken
#
# Empty result means the sprint has nobody independent left, which is a roster
# decision and therefore genuinely Brian's.
WINDOW_CONF=${POLLER_WINDOW_CONF:-$HOME/.config/agent-deck/fleet-window.conf}
# A SEAT THAT ANSWERS NOTHING. An empty turn still counts as a turn, so every
# instrument the loop had read corvid as healthy while it returned nothing to
# five stalls and four prompts in a row (2026-09-16). The wake was accepted, so
# the hand-off was "delivered"; the backpressure saw turns, so it kept feeding.
#
# The markers are the worker's own, written when a turn produces no text or the
# watchdog ends it. Mechanical: no judgement about whether an answer was any
# good, only whether there WAS one.
MUTE_MIN=${POLLER_MUTE_MIN:-3}
seat_mute() {   # session-id -> 0 when its last $MUTE_MIN answers were all empty
  local h="$HIST/$1.jsonl"
  [ -n "$1" ] && [ -f "$h" ] || return 1
  timeout 30 python3 - "$h" "$MUTE_MIN" "$STREAM/$1.jsonl" <<'MUTEPY'
import json, sys
need = int(sys.argv[2])
stream = sys.argv[3] if len(sys.argv) > 3 else ""
marks = ("[no reply was produced", "[stall] no response", "[session rebuilt]")
says = []
for line in open(sys.argv[1], errors="ignore"):
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    if isinstance(d, dict) and d.get("role") == "assistant":
        says.append(str(d.get("text") or ""))
# D-4 guard: NEVER judge a seat that has a turn in flight. A turn running now
# (stream shows a start with no matching end) means the seat is BLOCKED - e.g.
# waiting on the shared Z.ai slot - not broken; its older stall markers say
# nothing about this turn, and muting it would stop the loop routing
# verification to a healthy seat. In-flight always reads as NOT mute.
inflight = False
if stream:
    try:
        started = set()
        for sline in open(stream, errors="ignore"):
            sline = sline.strip()
            if not sline:
                continue
            try:
                d = json.loads(sline)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            item, kind = d.get("item"), d.get("t")
            if kind == "start":
                started.add(item)
            elif kind == "end":
                started.discard(item)
        inflight = bool(started)
    except Exception:
        inflight = False   # an unreadable stream never makes things worse
if inflight:
    raise SystemExit(1)
tail = says[-need:]
# Too few answers to judge is NOT mute: a fresh seat must not be written off.
if len(tail) < need:
    raise SystemExit(1)
raise SystemExit(0 if all(any(m in t for m in marks) for t in tail) else 1)
MUTEPY
}
verifier_for() {   # rowkey -> name of an eligible independent seat, or nothing
  local key="$1" seats s
  [ -n "$key" ] || return 0
  seats=$(sed -n 's/^WINDOW_SEATS="\(.*\)"/\1/p' "$WINDOW_CONF" 2>/dev/null)
  [ -n "$seats" ] || return 0
  for s in $seats; do
    case "$s" in cairn*|conductor*) continue;; esac
    ledger_is_producer "$key" "$s" && continue
    is_parked "$s" 2>/dev/null && continue
    # A mute seat accepts the work and returns nothing, which looks identical
    # to success from here. Skip it so the check goes somewhere that answers.
    if seat_mute "$(seat_id_for "$s" 2>/dev/null)"; then
      log "VERIFY skip $s: its last $MUTE_MIN answers were empty or stalled"
      continue
    fi
    [ -n "$(seat_id_for "$s" 2>/dev/null)" ] || continue
    echo "$s"; return 0
  done
}
QUEUE=${POLLER_QUEUE:-/var/home/bmosher/memory-bake-off/team/QUEUE.md}
GATED=${POLLER_GATED:-$DIR/gated}
# BACKPRESSURE. wake()'s contract counts the wake binary's 3 (queued) as
# delivered, which is right for an event that must not be lost and wrong for a
# heartbeat. A heartbeat says "keep going"; queueing a fourth one behind three
# unread copies tells the seat nothing it has not already been told, and the
# depth is invisible to the sender because rc=3 and rc=0 are flattened.
#
# Measured 2026-09-16 over 90 minutes: 50 wakes to cairn, 49 rc=3, 1 rc=0, 39 of
# them the same trial-cycle tick. Cairn's median turn is 140s and the tick fires
# after 120s of quiet history, so the tick fired DURING most turns. Backlog: 21.
#
# So: remember how deep a seat's queue got, and hold droppable heartbeats until
# the seat has produced as many turns as it had waiting. Mechanical and
# self-clearing - no status word, no agent's opinion of whether it is busy.
SAT=${POLLER_SAT:-$DIR/saturation}
SAT_STALE=${POLLER_SAT_STALE:-1800}   # ignore a note older than this: a seat
                                      # that never answers must not silence its
                                      # own heartbeat forever.
turns_since() {   # history-file, epoch -> assistant records newer than epoch
  [ -f "$1" ] || { echo 0; return; }
  timeout 30 python3 - "$1" "$2" <<'TSPY'
import json, sys
cut = float(sys.argv[2]); n = 0
for line in open(sys.argv[1], errors="ignore"):
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    if isinstance(d, dict) and d.get("role") == "assistant" and (d.get("at") or 0) > cut:
        n += 1
print(n)
TSPY
}
sat_note() {   # id, wake output -> record the depth the seat reported
  local n
  n=$(echo "$2" | sed -n 's/.*- \([0-9][0-9]*\) waiting.*/\1/p' | head -1)
  [ -n "$n" ] || return 0
  [ "$n" -gt 0 ] 2>/dev/null || return 0
  [ -n "${DRY_RUN:-}" ] && return 0
  mkdir -p "$SAT" 2>/dev/null && echo "$(now) $n" > "$SAT/$1"
}
sat_blocked() {   # id -> 0 while the seat has unconsumed queued wakes
  local f="$SAT/$1" t n c
  [ -f "$f" ] || return 1
  t=$(cut -d' ' -f1 "$f" 2>/dev/null); n=$(cut -d' ' -f2 "$f" 2>/dev/null)
  [ -n "$t" ] && [ -n "$n" ] || return 1
  [ $(( $(now) - t )) -gt "$SAT_STALE" ] && return 1
  c=$(turns_since "$HIST/$1.jsonl" "$t")
  [ "$c" -lt "$n" ]
}
mute_watch() {   # seat-name, session-id : page once if it answers nothing
  [ -n "$2" ] || return 0
  seat_mute "$2" || return 0
  brian 3600 seat-mute "$1 is accepting work and returning nothing - its last $MUTE_MIN replies were empty or ended by the stall watchdog. Its engine log is at ~/.config/agent-deck/acp-adapter-err/$2.err. Work routed to it is being swallowed, so I am routing checks elsewhere." || true
}
tick() {   # a DROPPABLE heartbeat. Never stack it on a seat that is behind.
  if sat_blocked "$1"; then
    log "TICK-HELD $1: $(cut -d' ' -f2 "$SAT/$1" 2>/dev/null) queued wake(s) not yet consumed - heartbeat dropped rather than stacked"
    return 3
  fi
  wake "$1" "$2"
}

# COMPUTED DONE (plan §1/§3). Until 2026-09-16 the chain classifier below read
# `grep -qi "done:"` on the status cell an agent had typed. That is the single
# defect the iteration-3 plan exists to remove: the transition was authored by
# the component whose reliability is in question, which is how a self-verified
# row passed unnoticed and how row 42 sat finished-but-open because nobody
# typed the token.
#
# The gate is kiln-flash's rowcheck, built as QUEUE row S4-8 (309 lines, no LLM
# in it): given a row id it resolves that row's DECLARED artifact and DECLARED
# check and exits 0 only when they hold.
#
# THREE outcomes, not two, and the third one is measured rather than assumed:
#   pass  rowcheck exits 0 - the row's own declared gate holds.
#   fail  the gate ran and returned non-zero, or a declared artifact is absent.
#   none  the row declares no runnable gate. check_exit 127 means the "check"
#         cell holds prose, not a command (measured on S4-11 and S4-13, whose
#         cells read "guard rejects one representative bad input..."). An
#         unwritten gate is not a failed gate; collapsing the two would pin
#         every prose row open forever.
#
# Forward-only, as the plan requires: 13 of 66 rows declare a gate. Those close
# on evidence. The rest keep closing on their text, exactly as before, because
# freezing 53 rows to force a retrofit is the apparatus-before-science trap the
# project already walked into once.
ROWCHECK=${ROWCHECK_BIN:-$HOME/.config/agent-deck/rowcheck}   # rowcheck: the computed-done gate
row_gate() {   # row-id -> pass | fail | none
  [ -f "$ROWCHECK" ] && [ -n "$1" ] || { echo none; return; }
  local J RC CE
  J=$(timeout 90 python3 "$ROWCHECK" "$1" --queue "$QUEUE" --json 2>/dev/null)
  RC=$?
  [ "$RC" = 0 ] && { echo pass; return; }
  CE=$(echo "$J" | sed -n 's/.*"check_exit": *\([0-9-]*\).*/\1/p' | head -1)
  if [ "$CE" = "127" ]; then
    if echo "$J" | grep -qE '"path": *"'; then
      log_once "rowgate-127-$1" "rowgate $1: declared check TRUNCATED at a pipe, exit 127 — counts FAILED, not absent" >/dev/null 2>&1 || true
      echo fail; return
    fi
    echo none; return
  fi
  echo "$J" | grep -qE '"declared_check": *"|"path": *"' && { echo fail; return; }
  echo none
}
# Fingerprint helpers: a wake goes out only when the fingerprint CHANGES,
# so timestamps bump only on triggers and one pulse stays in flight per
# seat. State files are keyed by lane title (lane-qualified, no collisions).
# Under DRY_RUN nothing is stored, so self-tests never advance live state.
gfp() { cat "$GATED/$1" 2>/dev/null; }
gset() { [ -n "${DRY_RUN:-}" ] && return 0; mkdir -p "$GATED" && echo "$2" > "$GATED/$1"; }
# Return contract (gated sections branch on it — keep honest):
# 0 = sent (or DRYWAKE logged), 1 = send FAILED (retry next sweep), 2 = excluded, 3 = min-gap skip, 4 = meter held.
# The wake binary itself returns 0 started / 3 queued / 1 failed; both 0 and 3
# count as delivered here, so normalize to 0/1.
wake() {
  local id="$1" text="$2" t gap pfx
  for pfx in $EXCL_IDS; do
    case "$id" in "$pfx"*) log "EXCLUDED $id (event-only): ${text:0:60}"; return 2;; esac
  done
  t=$(now); gap=$(( t - ${LASTWAKE[$id]:-0} ))
  if [ "$gap" -lt "$MIN_GAP" ]; then log "SKIP $id gap=${gap}s"; return 3; fi
  if [ "$METER_HOLD" = 1 ]; then
    for pfx in $DSH_IDS; do
      case "$id" in "$pfx-"*) log "HELD $id (metered cap): ${text:0:60}"; return 4;; esac
    done
  fi
  LASTWAKE[$id]=$t
  log "WAKE $id: ${text:0:80}"
  if [ -n "${DRY_RUN:-}" ]; then log "DRYWAKE $id (not sent)"; return 0; fi
  # T-001: `agent-deck session send` blocks up to 60 s per wake on ACP panes
  # and always false-alarms "never confirmed submitted". The socket path
  # returns started/queued at once. Fall back to session send only for seats
  # with no worker socket (non-ACP), which have no other way in.
  out=$("$WAKE_BIN" "$id" "$text" 2>&1); rc=$?
  log "wake-rc=$rc $id: ${out:0:100}"
  case "$out" in
    *"no worker socket"*)
      log "no socket for $id, falling back to session send"
      timeout 60 agent-deck session send "$id" "$text" >>"$LOG" 2>&1; rc=$?;;
  esac
  # A FAILED send must NOT consume the trigger: callers store the fingerprint
  # only when wake() returns 0, so return nonzero here and the next sweep
  # retries (MIN_GAP still paces it). The wake binary's 3 (queued) counts as
  # delivered alongside 0 (started).
  # Still delivered for the caller's purposes - a queued event is not a lost
  # event - but the DEPTH is recorded so droppable heartbeats can back off.
  # Flattening 0 and 3 without recording anything is what let a 21-deep
  # backlog build unseen.
  [ "$rc" = 3 ] && sat_note "$id" "$out"
  case "$rc" in 0|3) return 0;; *) return 1;; esac
}
flag() { log "FLAG $*"; echo "$(date -u +%FT%TZ) $*" >> "$DIR/poller.flags"; }

# FURLOUGH 2026-09-15 (Brian verdict via GiLMore turn): Ledger is parked, so
# Ledger-bound notices route to Brian instead — routine via Signal RPC with a
# 60-min per-kind cooldown, sprint-close to the phone (one-fire via its own
# state file, cooldown 0 here). Same envelope as clawdbot trigger scripts.
# WHAT EACH ALARM MEANS, in Brian's words rather than the loop's. Keyed by the
# same `kind` the cooldown uses, so a new kind without an entry still sends -
# it just says so, which is better than a silent drop.
brian_do() {   # kind -> the single action
  case "$1" in
    claimed-dark)   echo "Reassign the row or clear the claim.";;
    ghost-both)     echo "Free up or add a seat that can check this row - every live one either did the work or is furloughed.";;
    ghost-verifier) echo "Free up or add a seat that can check this row - every live one either did the work or is furloughed.";;
    verifier-dark)  echo "Reassign the verification, or tell me to wait.";;
    unroutable)     echo "Fix the seat name on the row so a live session matches it.";;
    sprint-close)   echo "Confirm the close, or say what still needs staffing.";;
    self-verify)    echo "Name a different seat to check the row - one that was not given the work.";;
    seat-mute)      echo "Restart that seat (agent-deck session restart <name>), then read its engine log if it recurs.";;
    *)              echo "No action defined for this alarm - tell me and I will fix the alarm.";;
  esac
}
brian_ignored() {   # kind -> what happens if he does nothing
  case "$1" in
    claimed-dark)   echo "the row stays claimed and no other seat will pick it up";;
    ghost-both|ghost-verifier)
                    echo "the row can never reach verified, so the sprint cannot close";;
    verifier-dark)  echo "the row sits done-but-unverified indefinitely";;
    unroutable)     echo "no nudge can ever reach anyone for that row";;
    sprint-close)   echo "the sprint stays open and the next one cannot start";;
    self-verify)    echo "the row stays unverified, because the only check on offer is the author's own";;
    seat-mute)      echo "every job handed to that seat is silently swallowed, and the loop cannot tell";;
    *)              echo "unknown - this alarm has no stated consequence yet";;
  esac
}
BRIAN_RPC=${POLLER_BRIAN_RPC:-"http://127.0.0.1:8081/api/v1/rpc"}
BRIAN_ACCT="+15412836540"
BRIAN_UUID="fce1cf17-5846-43ba-a065-78a54182ca4d"
BRIAN_CD=$DIR/brian-notify-cool
brian() {
  local cool="$1" kind="$2" text="$3" t last rc body
  t=$(now); last=$(mt "$BRIAN_CD/$kind")
  if [ $(( t - last )) -lt "$cool" ]; then log "BRIAN-SKIP $kind cooldown"; return 1; fi
  # DRY_RUN must reach here too. Until 2026-09-16 it did not, so any hermetic
  # run of the sweep would have buzzed Brian's phone for real - which is why
  # the sweep was never run hermetically.
  if [ -n "${DRY_RUN:-}" ]; then log "DRYBRIAN $kind: ${text:0:80}"; return 0; fi
  # One envelope for every kind. Written here and not at the call sites so a
  # message cannot go out without saying what to do about it.
  body="[Fleet - ACTION NEEDED]
$text

Do: $(brian_do "$kind")
If ignored: $(brian_ignored "$kind").

(alarm: $kind. Repeats at most hourly while it persists. Nothing in the loop
reads a Signal reply, so acting means editing the row or telling Claude.)"
  text="$body"
  rc=$(python3 - "$BRIAN_RPC" "$BRIAN_ACCT" "$BRIAN_UUID" "$text" <<'PY' 2>&1
import json,sys,urllib.request
url,acct,uuid,text=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
body=json.dumps({"jsonrpc":"2.0","id":1,"method":"send","params":{"account":acct,"recipient":[uuid],"message":text}}).encode()
try:
  r=urllib.request.urlopen(urllib.request.Request(url,data=body,headers={"Content-Type":"application/json"}),timeout=10)
  d=json.load(r)
  print("OK" if not d.get("error") else "ERR:"+str(d.get("error"))[:80])
except Exception as e:
  print("FAIL:"+str(e)[:80])
PY
)
  log "brian-rc $kind: ${rc:0:60}"
  case "$rc" in OK*) mkdir -p "$BRIAN_CD"; touch "$BRIAN_CD/$kind"; return 0;; *) return 1;; esac
}


# Stop rule, cached: meters.py --check exits 3 when the $25 envelope is spent
# AND when neither provider answers (fail-closed). Either way a held meter
# must not start metered work, so dsh-seat wakes wait for the next window.
meter_poll() {
  local t last
  t=$(now); last=$(mt "$METER_STATE")
  if [ $(( t - last )) -lt "$METER_TTL" ]; then
    [ -f "$METER_STATE" ] && METER_HOLD=1 || METER_HOLD=0
    return
  fi
  if python3 "$METERS" --check >/dev/null 2>&1; then
    METER_HOLD=0; rm -f "$METER_STATE"
  else
    METER_HOLD=1; touch "$METER_STATE"
    log "METER held (meters.py --check refused)"
  fi
}

# TEST SEAM. Sourcing this file with POLLER_SOURCE_ONLY=1 yields the helper
# definitions above without starting the sweep, so every predicate the loop
# decides on can be unit-tested directly. Added 2026-09-16 because the loop was
# being held to a written checker while the changes TO the loop were landing on
# my word that they worked. See workers/test-fleet-poller.sh.
if [ -n "$POLLER_SOURCE_ONLY" ]; then return 0 2>/dev/null || exit 0; fi
log "poller start (pid $$, interval ${INTERVAL}s)"
# PAUSE MARKER vs. SUPERVISION. The marker predates systemd: the loop exited 0
# the moment it appeared. Under Restart=always that turned "pause" into a
# restart every 5 seconds with dispatch silently off - 43 restarts and 4 pages
# to Brian on 2026-09-16 before anyone looked at why. A pause must be a pause,
# so the marker now idles the sweep in place and the loop resumes by itself
# when the marker is removed. No hand-restart, no storm.
#
# $DIR/alive is deliberately NOT touched while paused. The external check must
# keep reporting the truth - nothing is dispatching - because a pause nobody
# remembers setting is indistinguishable from a dead driver, and that is
# exactly how this morning went.
PAUSED=0
while true; do
  if [ -f "$STOP" ]; then
    [ "$PAUSED" = 1 ] || log "poller PAUSED by stop file ($STOP): no dispatch, no clocks, alive not touched. Remove the file to resume - no restart needed."
    PAUSED=1; sleep "$INTERVAL"; continue
  fi
  [ "$PAUSED" = 0 ] || log "poller RESUMED (stop file removed)"
  PAUSED=0
  T=$(now)
  # Liveness for the supervisor (plan §8). Every property of the loop assumes
  # this sweep runs, and until 2026-09-15 nothing checked: the poller was an
  # orphan bash process reparented to systemd with no restart policy, and it
  # died twice in one day. An external timer reads this mtime; a value older
  # than two intervals means the driver is gone, which is the one failure no
  # amount of in-loop machinery can report on its own.
  touch "$DIR/alive" 2>/dev/null || true
  meter_poll
  excl_poll

  # 1. Cairn — trial cycles are continuous; >10 min silent = wake next cycle
  A=$(mt "$CAIRN_HIST")
  GAP=$(( T - A ))
  if [ "$GAP" -gt "$STALL_CAIRN" ]; then
    tick "$CAIRN" "Cairn — trial cycle tick (last activity ${GAP}s ago): continue the next live-arm cycle per WINDOW-OPENING gate state. — fleet-poller for GiLMore"
  fi

  # 1b. A seat that answers nothing. Checked every sweep for the live roster,
  # because this failure is invisible from every other angle: the wake is
  # accepted, a turn is recorded, and the reply is empty. Corvid swallowed five
  # stalls and four prompts on 2026-09-16 before a human noticed.
  for MSEAT in $(sed -n 's/^WINDOW_SEATS="\(.*\)"/\1/p' "$WINDOW_CONF" 2>/dev/null); do
    case "$MSEAT" in cairn*|conductor*) continue;; esac
    is_parked "$MSEAT" 2>/dev/null && continue
    mute_watch "$MSEAT" "$(seat_id_for "$MSEAT" 2>/dev/null)"
  done

  # 2. fsync — watch line due if BOARD has no new fsync post in 15 min
  B=$(mt "$BOARD"); F=$(mt "$FSYNC_HIST")
  GAP=$(( T - F ))
  if [ "$GAP" -gt "$STALL_FSYNC" ] && [ $(( T - B )) -gt 900 ]; then
    wake "$FSYNC" "fsync — watch tick: post your one-line utilization report (seats idle with claimable rows? flags for GiLMore?). — fleet-poller"
  fi

  # 3. Ledger — STALENESS TRIGGER RETIRED 2026-09-15 (Brian+Ledger): it
  # re-woke Ledger on every artifact churn. Ledger wakes only on PO-worthy
  # content now: queue claims/completions (via §7a, which covers ledger-claude)
  # and BOARD.md mentions/questions (checked here — recent tail only, so old
  # mentions age out; fingerprinted per BOARD mtime so one mention wakes once).
  if [ -n "$LEDGER_HIST" ] && [ -f "$BOARD" ]; then
    LT=$(mt "$LEDGER_HIST"); BM=$(mt "$BOARD")
    if [ "$BM" -gt "$LT" ] && tail -40 "$BOARD" 2>/dev/null | grep -qiE "(^|[^a-z0-9])(ledger)([^a-z0-9]|$)"; then
      FP="board:$BM"
      if [ "$(gfp "board-ledger")" != "$FP" ]; then
        # DEMOTED out of Signal 2026-09-16. This fires when BOARD.md merely
      # MENTIONS the parked PO's name in the last 40 lines - a guess, not an
      # event. It wanted to send 102 times today and its own text admitted the
      # content only "may need" Brian. An alarm that cannot be acted on is how
      # the ones that can get ignored. The genuine cases it was groping for -
      # a row done with no reachable verifier - are covered by ghost-both and
      # ghost-verifier, which name the row and the action.
      if flag "board-ledger: BOARD mentions the parked PO; logged, not paged" "Fleet: BOARD.md mentions Ledger (parked) in the last 40 lines — PO-worthy content (claim, completed row, direct question) may need Brian. — fleet-poller"; then
          gset "board-ledger" "$FP"
        fi
      fi
    fi
  fi

  # 4. builder — ticket intake: wake when a ticket file/index changed AFTER his
  # last activity. His own ACK edits age his history past the files he wrote, so
  # he is never woken by his own writes. Settle delay avoids mid-turn writes;
  # MIN_GAP caps repeats. Send may report the #1973/#1978 false alarm — it lands.
  if [ -n "$BUILDER_HIST" ] && [ -d "$TICKDIR" ]; then
    BH=$(mt "$BUILDER_HIST")
    NEWT=$(ls -t "$TICKDIR"/T-*.md "$TICKDIR"/TICKETS.md 2>/dev/null | head -1)
    if [ -n "$NEWT" ]; then
      NM=$(mt "$NEWT"); AGE=$(( T - NM ))
      if [ "$NM" -gt "$BH" ] && [ "$AGE" -gt "$TICKET_SETTLE" ]; then
        CHANGED=$(find "$TICKDIR" -maxdepth 1 -name 'T-*.md' -newer "$BUILDER_HIST" 2>/dev/null | while read -r f; do
          echo "- $(basename "$f") [$(grep -m1 '^SEVERITY' "$f" | cut -c1-60)]"
        done | head -3)
        wake "$BUILDER" "builder — ticket intake changed:
${CHANGED}
Index: /home/bmosher/.local/share/agent-deck/support-tickets/TICKETS.md — ACK/work per BRIEF. — fleet-poller for GiLMore"
      fi
    fi
  fi

  # 6. self-serve row pulse: idle roster seats with an unclaimed row
  # naming them get ONE pointer wake per 30 min of continued idleness.
  # Stratum is NOT listed (Rev 2: Brian-interface is event-only — no poll may
  # originate a Brian-facing draft); the wake() exclusion file backs this.
  for pair in "7dfbfe83-1789253983:Corvid" "65f34e15-1789165087:Alice" "cfe6bf17-1789195234:Assay" "86c6f6ff-1789232263:Verity"; do
    SID="${pair%%:*}"; SNAME="${pair##*:}"
    H=$(ls -t $HIST/${SID%%-*}-*.jsonl 2>/dev/null | head -1)
    [ -z "$H" ] && continue
    # One-in-flight across §6/§7 (GiLMore design): a §7 gated wake newer than
    # this seat's last activity is still outstanding — no second wake while
    # one is unanswered.
    case "$SNAME" in
      Corvid) T6TITLE="corvid-dsh";; Alice) T6TITLE="aletheia-dsh";;
      Assay) T6TITLE="assay-dsh";; Verity) T6TITLE="verity-flash";;
      *) T6TITLE="";;
    esac
    if [ -n "$T6TITLE" ] && [ "$GATED/$T6TITLE" -nt "$H" ]; then
      log "SKIP $SID ($SNAME): §7 wake outstanding"; continue
    fi
    GAP=$(( T - $(mt "$H") ))
    if [ "$GAP" -gt 120 ]; then
      # field-aware: match the Eligible-seats cell only (not the whole line),
      # case-insensitively; require Status to start "open" and neither Status
      # nor Trigger to be gated. "Alice" also matches the row name "Aletheia".
      # Assay power check: queue_pulse_power.sh.
      # ID-AGNOSTIC, not [0-9]+ (2026-09-15). The old pattern required the
      # first cell to be digits, so every Sprint row - | S3-1 | ... | S3-7 | -
      # was INVISIBLE to §6 and both §7 paths. 43 of 51 rows matched; the 7
      # S3-* rows never did. Effect: Kiln had 2 open rows naming him and Assay
      # 1, and the poller could not nudge either, ever. Before the event-driven
      # cutover the blind Spark pulse woke seats anyway and they found the work
      # themselves; removing it removed the only channel that reached the
      # sprint, and the replacement was blind to it from the moment it shipped.
      # Must start alphanumeric so the |---| separator row is not a match.
      ROW=$(awk -F'|' -v name="$SNAME" '
        /^\| *[A-Za-z0-9][A-Za-z0-9._-]* *\|/ {
          seats=$4; trigger=$5; status=$8
          gsub(/^[ \t]+|[ \t]+$/, "", seats); gsub(/^[ \t]+|[ \t]+$/, "", trigger); gsub(/^[ \t]+|[ \t]+$/, "", status)
          low=tolower(seats)
          if (tolower(name)=="alice") nm="alice|aletheia"; else nm=tolower(name)
          word = (low ~ ("(^|[^a-z0-9])(" nm ")([^a-z0-9]|$)"))
          if (word && tolower(status) ~ /^open/ && tolower(status) !~ /gated/ && tolower(trigger) !~ /gated/)
            print NR": "$0
        }' "$QUEUE" 2>/dev/null | head -1)
      [ -n "$ROW" ] && {
        # One-in-flight: the ROW line (number + status text) is the
        # fingerprint, keyed per seat. A changed status (claimed/done/edited)
        # re-fires; an unchanged one stays silent no matter how long the
        # idleness. Skip rows this seat already claimed or that are done.
        case "$ROW" in *claimed:*$SNAME*|*done:*) ;;
        *)
          FP="q6:$(echo "$ROW" | md5sum | cut -d' ' -f1)"
          if [ "$(gfp "q6-$SNAME")" != "$FP" ]; then
            if wake "$SID" "$SNAME - open QUEUE row matches your seat (idle ${GAP}s): claim it per queue protocol. - fleet-poller"; then
              gset "q6-$SNAME" "$FP"
            fi
          fi;;
        esac
      }
    fi
  done

  # 7. Gated wakes (event-driven trial, v3.1 — REPLACES the v3.0 generic
  # pulse): fire ONLY on new content. No idle timers here at all; each
  # seat's fingerprint in $DIR/gated/<title> advances only when a wake is
  # actually sent, so repeats, restarts-from-same-state, and content-identical
  # sweeps are all silent. Rater-path + stratum stay absent by design (the
  # want map never lists them); wake() excludes them anyway.
  # Triggers per seat (any one fires):
  #   (a) QUEUE row names the seat (eligible or verifier) AND is open AND
  #       unclaimed-by-this-seat — fingerprint = row number + status text;
  #   (b) the seat is named in an ELIGIBLE-SEATS cell ($4) of a LIVE QUEUE row
  #       (status without done:) AND QUEUE.md is newer than the seat's last
  #       activity — narrowed per GiLMore design (was: any mention anywhere in
  #       the file; then: any cell match — but done rows naming the seat
  #       re-woke it with no actionable row, verity proof 2026-09-15). A claim
  #       or status edit on the seat's own live row still re-wakes it; chatter
  #       elsewhere does not. Fingerprint = file mtime;
  #   (c) the seat's own registry tree has files newer than its last
  #       activity (someone else touched its work) — fingerprint = newest
  #       mtime, search bounded at maxdepth 3, dotpaths pruned (.git churn is
  #       not signal).
  gname() { # match-names for a class title (lowercase title in $1)
    case "$1" in
      aletheia-dsh) echo "alice|aletheia";;
      assay-dsh) echo "assay";;
      corvid-dsh) echo "corvid";;
      kiln-flash) echo "kiln";;
      plumb-fable) echo "plumb";;
      verity-flash) echo "verity";;
      ledger-claude) echo "ledger";;
      fsync-claude) echo "fsync";;
      builder-claude) echo "builder";;
    esac
  }
  GATED_ROWS=$(agent-deck list --json 2>/dev/null | python3 -c '
import json,sys
try:
    rows=json.load(sys.stdin)
except Exception:
    rows=[]
want={"aletheia-dsh","assay-dsh","corvid-dsh","kiln-flash","verity-flash","ledger-claude","fsync-claude","builder-claude","plumb-fable"}
for r in rows:
    t=(r.get("title","")).lower()
    if t in want: print(r["id"], t, (r.get("path","") or ""), sep=" ")
')
  # NOTE: herestring, not a pipe — the loop must run in THIS shell so the
  # wake() MIN_GAP memory (LASTWAKE) survives between sweeps (v1.x bug).
  while read -r SID TITLE SPATH; do
    [ -z "$SID" ] && continue
    H=$(ls -t $HIST/${SID%%-*}-*.jsonl 2>/dev/null | head -1)
    [ -z "$H" ] && continue
    HT=$(mt "$H")
    NM=$(gname "$TITLE")
    [ -z "$NM" ] && continue
    # One-in-flight across §6/§7 (GiLMore design): a §6 row-pulse wake newer
    # than this seat's last activity is still outstanding — stay silent.
    case "$TITLE" in
      corvid-dsh) Q6KEY="q6-Corvid";; aletheia-dsh) Q6KEY="q6-Alice";;
      assay-dsh) Q6KEY="q6-Assay";; verity-flash) Q6KEY="q6-Verity";;
      *) Q6KEY="";;
    esac
    if [ -n "$Q6KEY" ] && [ "$GATED/$Q6KEY" -nt "$H" ]; then
      log "SKIP $SID ($TITLE): §6 wake outstanding"; continue
    fi
    FP=""; TEXT=""
    # (a) QUEUE row naming this seat, open, not claimed by it, not done.
    # (a) QUEUE rows naming this seat (eligible or verifier), open,
    # unclaimed-by-it, not done. The fingerprint covers the whole SET, so
    # any added/claimed/done row re-fires while an unchanged set — even
    # across days of idleness — stays silent. Precedence: (a) owns the fp
    # whenever actionable rows exist; (b)/(c) are evaluated only when no
    # actionable row exists (a bare mention with nothing to claim is not a
    # wake — §2/§3 own board-churn, and ping-per-edit is what we retired).
    QROWS=$(awk -F'|' -v nm="$NM" '
      /^\| *[A-Za-z0-9][A-Za-z0-9._-]* *\|/ {
        seats=$4; status=$8
        gsub(/^[ \t]+|[ \t]+$/, "", seats); gsub(/^[ \t]+|[ \t]+$/, "", status)
        lowseats=tolower(seats); lowstatus=tolower(status); line=tolower($0)
        if (lowseats ~ ("(^|[^a-z0-9])(" nm ")([^a-z0-9]|$)") \
            || line ~ ("verifier[^a-z0-9].{0,40}(" nm ")([^a-z0-9]|$)")) {
          if (lowstatus ~ /^open/ && lowstatus !~ /gated/ && lowstatus !~ /done:/ \
              && line !~ ("claimed:[^|]*(" nm ")")) print NR": "$8
        }
      }' "$QUEUE" 2>/dev/null)
    if [ -n "$QROWS" ]; then
      FP="a:$(echo "$QROWS" | md5sum | cut -d' ' -f1)"
      N=$(echo "$QROWS" | wc -l)
      TEXT="$N open QUEUE item(s) name you ($(echo "$QROWS" | head -1 | cut -c1-80)): claim per queue protocol."
    fi
    # (b) RETIRED 2026-09-15 (verifier seat-a, pulses 116-118): "seat named in
    # an eligible-seats cell + QUEUE.md newer" is noise by construction. Trigger
    # (a) already fires on every OPEN row naming the seat, so (b) could only
    # fire when NO actionable row existed — measured 8 false wakes across 5
    # seats in 8 minutes, e.g. row 54 status "draft filed:" (no `done:` token).
    # No token tweak fixes the closed-state vocabulary. (a) + (c) are the real
    # triggers; builder/GiLMore may re-introduce a scoped version if wanted.
    # (c) owned-tree activity newer than the seat's last activity.
    # Dotpaths pruned: .git internals churn on every git op by anyone in the
    # tree (proven: kiln's repo/.git retouch re-fired (c) every sweep) and are
    # never someone-editing-your-work signal.
    if [ -z "$FP" ] && [ -n "$SPATH" ] && [ -d "$SPATH" ]; then
      NT=$(find "$SPATH" -maxdepth 3 -name '.*' -prune -o -newer "$H" -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d. -f1)
      if [ -n "$NT" ]; then
        FP="c:$NT"
        TEXT="files under your tree changed while you were idle — check for sibling/conductor edits needing you."
      fi
    fi
    if [ -n "$FP" ] && [ "$(gfp "$TITLE")" != "$FP" ]; then
      if wake "$SID" "[$TITLE] gated wake: $TEXT — fleet-poller"; then
        gset "$TITLE" "$FP"
      fi
    fi
  done <<<"$GATED_ROWS"

  # 8. Inactivity timers (10/20, Brian-approved 2026-09-15, PO Ledger).
  #   10min: an unclaimed, undone, ungated QUEUE row (numeric or S3-N) stays
  #     unclaimed 10+ min → nudge one eligible seat.
  #   20min: a claimed-not-done row whose owner is dark 20+ min (and the claim
  #     itself is 20+ min old) → wake the owner AND Ledger (PO).
  #   Reset: any status-text change restarts that row's clock ("one posted
  #     reason resets with justification" — a reason posted into the row, or a
  #     BOARD post by the owner carrying a reason word, restarts the claimed
  #     clock from that edit).
  #   Cost: zero tokens — local text matching + state files only; wakes are
  #     fingerprinted one-fire events on the existing wake path (MIN_GAP paces
  #     any repeat). New per-sweep work: one `agent-deck list` (local socket),
  #     one QUEUE scan (already read by §6/§7), ls/stat mtimes (already read).
  INACT=${POLLER_INACT:-$DIR/inactivity}
  mkdir -p "$INACT" 2>/dev/null
  REGMAP=$(agent-deck list --json 2>/dev/null | python3 -c '
import json,sys
try: rows=json.load(sys.stdin)
except Exception: rows=[]
for r in rows:
    t=(r.get("title") or "").lower()
    if t and r.get("id"): print(t, r["id"])
' 2>/dev/null)
  LIVEKEYS=""
  while IFS=$(printf '\037') read -r TASK SEATS STATUS; do
    [ -z "$TASK" ] && continue
    KEY=$(echo -n "$TASK" | md5sum | cut -d' ' -f1)
    LIVEKEYS="$LIVEKEYS $KEY"
    # Fingerprint covers the SEATS field too. Measured 2026-09-15: row 42
    # fired once while its seat read worker-glm-2 (unresolvable), logged
    # "no eligible seat resolves" and set FIRED=1. Reassigning it to a live
    # seat changed field 4, not the status, so the fingerprint held and the
    # only actionable row in the queue could never be nudged again. A change
    # of owner is the most dispatch-relevant change there is.
    SM=$(echo -n "$STATUS|$SEATS" | md5sum | cut -d' ' -f1)
    ST="$INACT/$KEY"
    if grep -qi "done:" <<<"$STATUS"; then rm -f "$ST"; continue; fi
    if grep -qi "claimed:" <<<"$STATUS"; then
      OWNER=$(echo "$STATUS" | sed -n 's/.*[Cc][Ll][Aa][Ii][Mm][Ee][Dd]: *\([A-Za-z][A-Za-z0-9_-]*\).*/\1/p' | head -1)
      [ -z "$OWNER" ] && continue
      OLD=$(cat "$ST" 2>/dev/null)
      # Was: any status-text change ($SM) restarted the clock from now,
      # so the dead-man switch could be held off by editing the row.
      # Only a genuinely new claim (different owner) restarts it now.
      if [ "$(echo "$OLD" | cut -d' ' -f1)" != "claimed" ] || [ "$(echo "$OLD" | cut -d' ' -f3)" != "$OWNER" ]; then
        echo "claimed $T $OWNER $SM 0 0" > "$ST"; continue
      fi
      FIRST=$(echo "$OLD" | cut -d' ' -f2); FIRED=$(echo "$OLD" | cut -d' ' -f5)
      # One reason per claim. Unlimited resets are how this switch
      # never fired: 9 of 12 logged events were a reason reset.
      REASONS=$(echo "$OLD" | cut -d' ' -f6); REASONS=${REASONS:-0}
      # posted-reason reset: BOARD newer than the claim clock names the owner
      # beside a justification word → restart the clock from the board edit.
      BM=$(mt "$BOARD")
      if [ "$REASONS" -lt 1 ] && [ "$BM" -gt "$FIRST" ] && tail -60 "$BOARD" 2>/dev/null | grep -qiF "$OWNER" \
        && tail -60 "$BOARD" 2>/dev/null | grep -qiE "reason|because|blocked|waiting|justif|hold|pause"; then
        log "INACT $KEY ($OWNER): posted reason, clock reset (1 of 1 allowed this claim)"
        echo "claimed $BM $OWNER $SM 0 1" > "$ST"; continue
      fi
      OID=$(seat_id_for "$OWNER")
      OH=$(ls -t $HIST/${OID%%-*}-*.jsonl 2>/dev/null | head -1)
      OHT=$(mt "$OH"); [ -z "$OH" ] && OHT=0
      # OAT, not OHT: last non-bookkeeping WRITE by this owner. OHT is
      # any turn at all, which the reply to the nudge satisfies.
      OAT=$(art_ts "$OH"); [ -z "$OAT" ] && OAT=0
      # Conductor exemption (ratified 2026-09-15): a conductor's artifacts ARE
      # the bookkeeping set, so the artifact-dark test is tautologically failed
      # for them. Conductor-owned claims skip this branch; conductors are
      # judged on row movement instead (§9 transitions, §10 verdicts, §11
      # close already watch every row regardless of owner). Marked fired so
      # the exemption logs once instead of every sweep; a new owner reseeds.
      OTITLE=$(echo "$REGMAP" | awk -v id="$OID" '$2==id{print $1; exit}')
      case "$OTITLE" in
        conductor-*) [ "$FIRED" != "1" ] && log "INACT $KEY ($OWNER): conductor-owned — exempt from artifact branch, judged on row movement"
          echo "claimed $FIRST $OWNER $SM 1 $REASONS" > "$ST"; continue;;
      esac
      if [ $(( T - FIRST )) -ge "$T_CLAIMED_DARK" ] && [ $(( T - OAT )) -ge "$T_CLAIMED_DARK" ] && [ "$FIRED" != "1" ]; then
          if row_closed_now "$TASK"; then
            log "INACT $KEY ($OWNER): row closed since this sweep read it - wake suppressed (stale-snapshot guard)"
            rm -f "$ST"; continue
          fi
          DARKMIN=$(( T_CLAIMED_DARK / 60 ))
        # Recorded only AFTER the hand-off actually lands. Recording first
        # logged dispatches that were then EXCLUDED - furloughed fsync showed up
        # as a producer three times in the first 2.5 minutes live - and a false
        # producer record wrongly blocks a legitimate checker later, which
        # stalls the row and pages Brian for nothing.
        [ -n "$OID" ] && wake "$OID" "[$OWNER] claimed-dark ${DARKMIN}min: your QUEUE claim on '$(echo "$TASK" | cut -c1-70)' has produced no non-bookkeeping write for ${DARKMIN}+ min — post progress/a reason or release it. Ledger looped in. — fleet-poller" && ledger_note "$KEY" "$OWNER" "$OID"
        if brian 3600 claimed-dark "[Fleet] claimed-dark ${DARKMIN}min: $OWNER's claim has produced nothing for ${DARKMIN}+ min. Ledger parked — Brian call. — fleet-poller"; then
          echo "claimed $FIRST $OWNER $SM 1 $REASONS" > "$ST"
        fi
      fi
    else
      # unclaimed: gated rows sit out (their own triggers own them).
      if grep -qi "gated:" <<<"$STATUS"; then rm -f "$ST"; continue; fi
      OLD=$(cat "$ST" 2>/dev/null)
      if [ "$(echo "$OLD" | cut -d' ' -f1)" != "open" ] || [ "$(echo "$OLD" | cut -d' ' -f4)" != "$SM" ]; then
        echo "open $T - $SM 0" > "$ST"; continue
      fi
      FIRST=$(echo "$OLD" | cut -d' ' -f2); FIRED=$(echo "$OLD" | cut -d' ' -f5)
      if [ $(( T - FIRST )) -ge "$T_UNCLAIMED" ] && [ "$FIRED" != "1" ]; then
        # first resolvable eligible name wins (parentheticals stripped; split
        # on word-boundary "or" only — a char-class split mangles names
        # containing "or" ("GiLMore" -> "GiLM"+"e", and "e" matches everything).
        EID=""
        for cand in $(echo "$SEATS" | sed 's/([^)]*)//g; s/\b[Oo][Rr]\b/\n/g; s/[,;+]/\n/g'); do
          EID=$(seat_id_for "$cand"); [ -n "$EID" ] && break
        done
        if [ -n "$EID" ]; then
          if wake "$EID" "[$EID] inactivity nudge: QUEUE row '$(echo "$TASK" | cut -c1-70)' unclaimed 10+ min and names you eligible — claim per protocol or post a reason. — fleet-poller"; then
            ledger_note "$KEY" "$cand" "$EID"
            echo "open $FIRST - $SM 1" > "$ST"
          fi
        else
          # A log line nobody reads is how this stayed invisible:
          # rows naming "worker-glm-2" (not a session title) were
          # counted as nudged while no seat was ever woken. Tell the
          # PO, once per row, so the row gets fixed or reassigned.
          log "INACT $KEY: 10min unclaimed but no eligible seat resolves (seats: $(echo "$SEATS" | cut -c1-60))"
          brian 3600 unroutable "[Fleet] unroutable QUEUE row (seats match no session). Ledger parked — Brian call. — fleet-poller" || true
          echo "open $FIRST - $SM 1" > "$ST"
        fi
      fi
    fi
  done < <(awk -F'|' '
    # IS THIS A ROW AT ALL? Added 2026-09-17 after the unroutable alarm paged
    # Brian about rows seeking seats named `1-2m`, `83%` and `100%`. Those were
    # columns of MARKDOWN TABLES pasted into QUEUE.md: every line starting with
    # "|" was read as a row and column 4 as its eligible seats. The tables were
    # moved out, and this stops the next one silently becoming a row.
    # NOT a column count - six real rows carry 10 or 11 fields because their
    # cells contain backticked pipes, so NF==9 would have dropped genuine work.
    # The row ID is the discriminator: digits, or letters followed by a digit
    # (37, S3-7, D-3, S6-1G) - which "model", "provider" and
    # "muse-spark-1.3-contributor" all fail.
    # Real ids on this board: digits (37), or a short letter prefix with a digit
    # and an optional -part and trailing letter (D-1, S3-7, S6-1G, S4-8). A
    # first attempt allowed any letters followed by a digit and REJECTED the six
    # live D-* debt rows, because D-1 has a separator before its digit; allowing
    # any separator then admitted `glm-5.3-flash` from a table. Requiring the
    # whole cell to match this shape admits every real row and rejects every
    # table heading and data cell measured on 2026-09-17.
    # A rejected line is printed to stderr (journald keeps it) because a row
    # made INVISIBLE by a mis-shaped id is worse than a phantom one: the phantom
    # pages Brian, the invisible row just never gets worked.
    function isrow(id,  raw) { raw=id; gsub(/^[ \t]+|[ \t]+$/, "", id)
      if (id ~ /^[0-9]+$/ || id ~ /^[A-Za-z]{1,3}[0-9]*-?[0-9]+[A-Za-z]?$/) return 1
      print "NOT-A-ROW id=[" id "] - ignored by the poller" > "/dev/stderr"
      return 0 }
    BEGIN{OFS="\037"} /^\|/ && $0 !~ /\|---/ && $3 !~ /^[ \t]*$/ && $3 !~ /Task/ && isrow($2) {
    task=$3; seats=$4; status=""; for(i=8;i<NF;i++){status=status ((i>8)?"|":"") $i}
    gsub(/^[ \t]+|[ \t]+$/, "", task); gsub(/^[ \t]+|[ \t]+$/, "", seats); gsub(/^[ \t]+|[ \t]+$/, "", status)
    print task, seats, status }' "$QUEUE" 2>/dev/null)
  # drop state for rows gone from the queue (claims keyed by task text).
  for st in "$INACT"/*; do
    [ -f "$st" ] || continue
    case "$LIVEKEYS" in *"$(basename "$st")"*) ;; *) rm -f "$st";; esac
  done

  # 9. Completion chaining (Brian-approved 2026-09-15). One transition-watch:
  #   done-transition (row → done/receipt-filed) → wake the named verifier
  #     directly with the artifact pointer. A transition IS new content, so
  #     this bypasses the §7 fingerprint-quiet by design — but each unique
  #     transition fires exactly once (chain state), so repeats stay silent.
  #   claim-transition (row → claimed) → wake the claimant-as-producer once
  #     with the contract (task + verifier + row terms live in QUEUE).
  #   Deploy safety: open/claimed rows seed silently on first sight; unseen
  #   DONE rows backfill once (cold-start gap) — a restart wakes nobody for
  #   history it already fingerprinted, only for completions it never saw.
  #   Chain amplifier guard (cost review 2026-09-15 — fleet is 89% machine-
  #   prompted, so chained wakes must not cascade): at most CHAIN_MAX fired
  #   transitions per row per CHAIN_WINDOW seconds (over-cap transitions are
  #   logged and consumed, never queued); and no-self-notify — a done row
  #   whose verifier IS the owner wakes nobody about their own receipt.
  #   Packed payload: every chained wake carries row id, old→new class AND
  #   old/new status text plus the artifact path, so the woken lane can act
  #   without reading QUEUE. (Previous status rides in $CHAIN/<key>.prev.)
  #   Pipe-parse note (Aletheia pulse-123): QUEUE cells carry literal pipes
  #   (row 6's backticked filters, rows 38/39), so status is rejoined from
  #   fields 8..NF-1 here and in §8. §6/§7 still read $8 — same latent defect,
  #   flagged for a follow-up, out of this batch's scope.
  #   Composes: wake() still enforces exclusions + MIN_GAP; §8 clocks reseed
  #   on the same status changes independently. Zero tokens: local text only.
  CHAIN=${POLLER_CHAIN:-$DIR/chain}
  CHAIN_MAX=3; CHAIN_WINDOW=3600
  mkdir -p "$CHAIN" 2>/dev/null
  CHAINLIVE=""
  while IFS=$(printf '\037') read -r CTASK CSTATUS CNR CLINE; do
    [ -z "$CTASK" ] && continue
    CKEY=$(echo -n "$CTASK" | md5sum | cut -d' ' -f1)
    CHAINLIVE="$CHAINLIVE $CKEY"
    CSM=$(echo -n "$CSTATUS" | md5sum | cut -d' ' -f1)
    # Evidence first, text second, and the DISAGREEMENT is the finding.
    # Only rows that declare "(check:" cost a subprocess here.
    CGATE=none
    case "$CLINE" in *'(check:'*) CGATE=$(row_gate "$CNR");; esac
    CPROSE=open
    if grep -qi "done:" <<<"$CSTATUS"; then CPROSE=done
    elif grep -qi "claimed:" <<<"$CSTATUS"; then CPROSE=claimed; fi
    CCLASS=$CPROSE
    case "$CGATE" in
      pass)
        CCLASS=done
        if [ "$CPROSE" != done ]; then
          log_once "gate-$CKEY" "GATE $CNR: declared check PASSES but the status cell never said done - closing on evidence. This is the row-42 case, which could not close before."
        fi
        ;;
      fail)
        if [ "$CPROSE" = done ]; then
          CCLASS=claimed
          log_once "gate-$CKEY" "GATE $CNR: status cell says done but the declared check FAILS - NOT closing. Evidence beats prose; the row stays claimed."
        fi
        ;;
    esac
    CST="$CHAIN/$CKEY"; PREV="$CHAIN/$CKEY.prev"
    OPREV=$(cat "$PREV" 2>/dev/null)
    COLD=$(cat "$CST" 2>/dev/null)
    if [ -z "$COLD" ] && [ "$CCLASS" != "done" ]; then echo "$CCLASS $CSM 0 0 $T" > "$CST"; echo "$CSTATUS" | cut -c1-200 > "$PREV"; continue; fi
    if [ -z "$COLD" ]; then
      # Backfill sweep (cold-start gap, Brian-approved 2026-09-15): a done row
      # with no chain state is an unseen completion, not history — treat it as
      # a fresh transition once, so every restart closes the pre-live gap.
      # Open/claimed rows still seed silently (their timers live in §8).
      # State persists on disk, so later restarts see FIRED_SM match and stay
      # silent; only genuinely-unseen completions fire, one each.
      OCLASS="unseen"; OFIRED=""; COUNT=0; WSTART=$T
      [ -z "$OPREV" ] && OPREV="unseen — backfill sweep"
    else
      OCLASS=$(echo "$COLD" | cut -d' ' -f1); OFIRED=$(echo "$COLD" | cut -d' ' -f3)
      COUNT=$(echo "$COLD" | cut -d' ' -f4); WSTART=$(echo "$COLD" | cut -d' ' -f5)
      COUNT=${COUNT:-0}; WSTART=${WSTART:-$T}
    fi
    if [ "$CSM" = "$OFIRED" ]; then echo "$CSTATUS" | cut -c1-200 > "$PREV"; continue; fi
    if [ "$CCLASS" = "$OCLASS" ]; then
      # same class, edited text, no transition: refresh the hash silently.
      echo "$CCLASS $CSM $OFIRED $COUNT $WSTART" > "$CST"; echo "$CSTATUS" | cut -c1-200 > "$PREV"; continue
    fi
    if [ $(( T - WSTART )) -gt "$CHAIN_WINDOW" ]; then COUNT=0; WSTART=$T; fi
    if [ "$COUNT" -ge "$CHAIN_MAX" ]; then
      log "CHAIN $CKEY row $CNR: hop cap ($CHAIN_MAX/$CHAIN_WINDOW s) — transition $OCLASS->$CCLASS consumed silently"
      echo "$CCLASS $CSM $CSM $COUNT $WSTART" > "$CST"; echo "$CSTATUS" | cut -c1-200 > "$PREV"; continue
    fi
    fired() { echo "$CCLASS $CSM $CSM $(( COUNT + 1 )) $WSTART" > "$CST"; }
    if [ "$CCLASS" = "done" ]; then
      VNAME=$(echo "$CLINE" | sed -n 's/.*[Vv][Ee][Rr][Ii][Ff][Ii][Ee][Rr]: *\([A-Za-z][A-Za-z0-9_-]*\).*/\1/p' | head -1)
      ART=$(echo "$CSTATUS" | sed -n 's/.*[Dd][Oo][Nn][Ee]: *\([^|]*\).*/\1/p' | head -1 | awk '{print $1}' | cut -c1-80)
      OWNER=$(echo "$CSTATUS" | sed -n 's/.*[Cc][Ll][Aa][Ii][Mm][Ee][Dd]: *\([A-Za-z][A-Za-z0-9_-]*\).*/\1/p' | head -1)
      VID=$(seat_id_for "$VNAME"); OID=$(seat_id_for "$OWNER")
      # NO was:/now: QUOTING. The old form pasted 120 characters of the previous
      # cell and 120 of the current one. Three separate failures came from it:
      # both halves truncate at the same length so the change usually fell past
      # the cut and they printed IDENTICALLY (conveying nothing); kiln read the
      # "was:" half as a claim about the present and answered "stale phantom"
      # ELEVEN consecutive times, burning a turn each; and Brian could not read
      # the message at all. The row is the source of truth - name it and say
      # what is wanted, and let the reader look.
      PACK="[chain done] row $CNR '$(echo "$CTASK" | cut -c1-70)' is now done (owner: ${OWNER:-unnamed}, verifier: ${VNAME:-unnamed}, artifact: ${ART:-see the row}). Read the row for its current state - this message deliberately does not quote it."
      # Independence, checked against the ledger and not against prose. The
      # old test compared the row's own "claimed:" text with its own
      # "verifier:" text - both agent-written, so naming someone else as the
      # author was enough to sign off on your own work. Now: if this seat was
      # ever HANDED this row to produce, it cannot verify it, whatever the row
      # says. Refusing silently would just stall the row, so Brian is told.
      if [ -n "$VNAME" ] && ledger_is_producer "$CKEY" "$VNAME"; then
        log "CHAIN $CKEY row $CNR: SELF-VERIFY REFUSED - $VNAME was dispatched to produce this row (ledger: $(ledger_producers "$CKEY"))"
        brian 3600 self-verify "Row $CNR '$(echo "$CTASK" | cut -c1-70)' is finished, but the seat named to check it ($VNAME) is a seat that was given the row to do. It cannot mark its own homework, so the row is not verified and I have not woken anyone." || true
        fired
      elif [ -n "$VID" ] && [ -n "$OID" ] && [ "$VID" = "$OID" ]; then
        log "CHAIN $CKEY row $CNR: no-self-notify (verifier is owner $OWNER)"
        fired
      elif [ -n "$VID" ] && seat_mute "$VID"; then
        # DO NOT mark this transition fired. Measured 2026-09-16: corvid's
        # engine was dead, four verification requests were handed to it at
        # 12:35:58, each came back empty, and every one was recorded as
        # delivered - so the chain marked the transitions fired and will never
        # ask again. One row (S4-12) had its status hash equal to its fired
        # hash, which means that verification was lost permanently and the seat
        # sat there with nothing to do. A hand-off into silence is not a
        # hand-off, and the retry has to survive the seat being broken.
        log "CHAIN $CKEY row $CNR: verifier $VNAME is mute (last $MUTE_MIN answers empty) - NOT firing, will retry when it answers"
        mute_watch "$VNAME" "$VID"
      elif [ -n "$VID" ]; then
        if wake "$VID" "[$VNAME] $PACK — verify per row terms. — fleet-poller"; then fired; fi
      elif [ -n "$(verifier_for "$CKEY")" ]; then
        # Self-sufficient path: the row named nobody reachable, but exactly one
        # live worker did not do this job, so ask it and record who was asked.
        # This used to page Brian to make a choice with one possible answer.
        AUTOV=$(verifier_for "$CKEY"); AUTOVID=$(seat_id_for "$AUTOV")
        log "CHAIN $CKEY row $CNR: no verifier named; auto-assigned $AUTOV (live, not a producer of this row)"
        if wake "$AUTOVID" "[$AUTOV] $PACK — no verifier was named on this row and you did not do the work, so this check is yours. Verify per row terms. — fleet-poller"; then
          printf '%s %s verifier %s %s\n' "$(now)" "$CKEY" "$AUTOV" "${AUTOVID:--}" >> "$DISPATCH" 2>/dev/null || true
          fired
        fi
      else
        log "CHAIN $CKEY: done, no verifier named AND no eligible independent seat — Brian call (roster decision)"
        if [ -z "$OID" ]; then
          # Ghost both ways (Brian-approved 2026-09-15): no reachable verifier
          # AND no owner — the conductor owns it. Same packed format, same
          # one-fire rule. Ledger keeps verifier-less, GiLMore gets ownerless.
          CID=$(seat_id_for "cairn-pi")   # conductor is cairn since 2026-09-16
          # FURLOUGH fallthrough: CID wake may EXCLUDE (conductor parked) —
          # an excluded/failed conductor wake must fall through to Brian,
          # never drop silently.
          if wake "$CID" "[conductor-glm] $PACK (owner field: ${OWNER:-none} — ghost both ways). Assign verification. — fleet-poller"; then fired
          elif brian 3600 ghost-both "[Fleet] $PACK (verifier: ${VNAME:-none}, owner: ${OWNER:-none}). Assign verification. — fleet-poller"; then fired; fi
        elif brian 3600 ghost-verifier "[Fleet] $PACK (verifier field: ${VNAME:-none}). Assign verification. — fleet-poller"; then fired; fi
      fi
      echo "$CSTATUS" | cut -c1-200 > "$PREV"
    elif [ "$CCLASS" = "claimed" ]; then
      OWNER=$(echo "$CSTATUS" | sed -n 's/.*[Cc][Ll][Aa][Ii][Mm][Ee][Dd]: *\([A-Za-z][A-Za-z0-9_-]*\).*/\1/p' | head -1)
      VNAME=$(echo "$CLINE" | sed -n 's/.*[Vv][Ee][Rr][Ii][Ff][Ii][Ee][Rr]: *\([A-Za-z][A-Za-z0-9_-]*\).*/\1/p' | head -1)
      OID=$(seat_id_for "$OWNER")
      PACK="[chain claim] row $CNR '$(echo "$CTASK" | cut -c1-70)' is now claimed by ${OWNER:-unnamed} (verifier: ${VNAME:-see the row}). Read the row for its current state - this message deliberately does not quote it."
      if [ -n "$OID" ]; then
        if wake "$OID" "[$OWNER] $PACK — deliverable per QUEUE row terms. — fleet-poller"; then
          ledger_note "$CKEY" "$OWNER" "$OID"; fired
        fi
      else
        log "CHAIN $CKEY: claimed by unresolvable owner ($OWNER) — no ack possible"
        fired
      fi
      echo "$CSTATUS" | cut -c1-200 > "$PREV"
    else
      echo "$CCLASS $CSM $OFIRED $COUNT $WSTART" > "$CST"; echo "$CSTATUS" | cut -c1-200 > "$PREV"
    fi
  done < <(awk -F'|' '
    # IS THIS A ROW AT ALL? Added 2026-09-17 after the unroutable alarm paged
    # Brian about rows seeking seats named `1-2m`, `83%` and `100%`. Those were
    # columns of MARKDOWN TABLES pasted into QUEUE.md: every line starting with
    # "|" was read as a row and column 4 as its eligible seats. The tables were
    # moved out, and this stops the next one silently becoming a row.
    # NOT a column count - six real rows carry 10 or 11 fields because their
    # cells contain backticked pipes, so NF==9 would have dropped genuine work.
    # The row ID is the discriminator: digits, or letters followed by a digit
    # (37, S3-7, D-3, S6-1G) - which "model", "provider" and
    # "muse-spark-1.3-contributor" all fail.
    # Real ids on this board: digits (37), or a short letter prefix with a digit
    # and an optional -part and trailing letter (D-1, S3-7, S6-1G, S4-8). A
    # first attempt allowed any letters followed by a digit and REJECTED the six
    # live D-* debt rows, because D-1 has a separator before its digit; allowing
    # any separator then admitted `glm-5.3-flash` from a table. Requiring the
    # whole cell to match this shape admits every real row and rejects every
    # table heading and data cell measured on 2026-09-17.
    # A rejected line is printed to stderr (journald keeps it) because a row
    # made INVISIBLE by a mis-shaped id is worse than a phantom one: the phantom
    # pages Brian, the invisible row just never gets worked.
    function isrow(id,  raw) { raw=id; gsub(/^[ \t]+|[ \t]+$/, "", id)
      if (id ~ /^[0-9]+$/ || id ~ /^[A-Za-z]{1,3}[0-9]*-?[0-9]+[A-Za-z]?$/) return 1
      print "NOT-A-ROW id=[" id "] - ignored by the poller" > "/dev/stderr"
      return 0 }
    BEGIN{OFS="\037"} /^\|/ && $0 !~ /\|---/ && $3 !~ /^[ \t]*$/ && $3 !~ /Task/ && isrow($2) {
    task=$3; status=""; for(i=8;i<NF;i++){status=status ((i>8)?"|":"") $i}
    gsub(/^[ \t]+|[ \t]+$/, "", task); gsub(/^[ \t]+|[ \t]+$/, "", status)
    rid=$2; gsub(/^[ \t]+|[ \t]+$/, "", rid)
    # NR is the awk record number, not the row id. Every escalation named
    # the wrong thing: row 43 was line 43, which holds row 21, and no row
    # 43 exists. Measured from a real page sent to Brian 2026-09-15.
    print task, status, rid, $0 }' "$QUEUE" 2>/dev/null)
  for st in "$CHAIN"/*; do
    [ -f "$st" ] || continue
    case "$st" in *.prev) continue;; esac
    case "$CHAINLIVE" in *"$(basename "$st")"*) ;; *) rm -f "$st";; esac
  done

  # 10. Verdict-due clock (Brian-approved 2026-09-15). A done row with a named,
  #   resolvable verifier and no verdict artifact starts a clock at first sight
  #   (DONE_AT; rows done long before deploy get 30 min grace — surfacing stale
  #   unverified receipts once is intended, not a bug):
  #   30min with no verdict → wake the verifier (row id + artifact pointer).
  #   60min with no verdict AND a dark verifier → escalate to Ledger + conductor.
  #   "Verdict filed" (clock stops, heuristic — flag for PO if it misfires):
  #     status text carries verifi|cosign|pass|fail|approved|rejected, OR a
  #     team/ file newer than DONE_AT is named *verif*|*verdict*|*cosign*|
  #     *approv*. Residual blind spot, documented: the file leg is scoped by
  #     verifier name only, so one verifier's verdict file also stops their
  #     OTHER rows' clocks (status words stay per-row precise). Fail-quiet =
  #     a missed nudge, never a false wake.
  #   "Dark" mirrors §8: verifier history older than 60 min. An active but
  #   silent verifier gets the 30-min nudge only — escalation is for dark ones.
  #   No-self: verifier == owner rows sit out (self-verify needs no chase).
  #   Hop-cap is structural here: one 30-fire + one 60-fire per row, ever.
  #   Zero tokens: local text + mtimes only.
  VERD=${POLLER_VERD:-$DIR/verdict}
  TEAMDIR=$(dirname "$QUEUE")
  mkdir -p "$VERD" 2>/dev/null
  status_verdict() { # status text -> 0 if it carries a filed-verdict marker
    local vt
    vt=$(echo "$1" | sed 's/[Vv][Ee][Rr][Ii][Ff][Ii][Ee][Rr]: *[A-Za-z][A-Za-z0-9_-]*//')

    grep -qiE "verifi|cosign|\bpass(es|ed)?\b|\bfail(s|ed|ure)?\b|approv|reject" <<<"$vt" || return 1
    grep -qiE "pending|awaiting" <<<"$1" && return 1
    return 0
  }
  VERDLIVE=""
  while IFS=$(printf '\037') read -r VTASK VSTATUS VNR VLINE; do
    [ -z "$VTASK" ] && continue
    VKEY=$(echo -n "$VTASK" | md5sum | cut -d' ' -f1)
    VERDLIVE="$VERDLIVE $VKEY"
    grep -qi "done:" <<<"$VSTATUS" || { rm -f "$VERD/$VKEY"; continue; }
    VNAME=$(echo "$VLINE" | sed -n 's/.*[Vv][Ee][Rr][Ii][Ff][Ii][Ee][Rr]: *\([A-Za-z][A-Za-z0-9_-]*\).*/\1/p' | head -1)
    VID=$(seat_id_for "$VNAME")
    [ -z "$VID" ] && { rm -f "$VERD/$VKEY"; continue; }
    OWNER=$(echo "$VSTATUS" | sed -n 's/.*[Cc][Ll][Aa][Ii][Mm][Ee][Dd]: *\([A-Za-z][A-Za-z0-9_-]*\).*/\1/p' | head -1)
    OID=$(seat_id_for "$OWNER")
    if [ -n "$OID" ] && [ "$VID" = "$OID" ]; then rm -f "$VERD/$VKEY"; continue; fi
    ART=$(echo "$VSTATUS" | sed -n 's/.*[Dd][Oo][Nn][Ee]: *\([^|]*\).*/\1/p' | head -1 | awk '{print $1}' | cut -c1-80)
    VST="$VERD/$VKEY"
    # status-word verdicts block seeding too (a row already carrying PASS must
    # never start a clock); the file probe needs DONE_AT so it runs post-seed.
    if status_verdict "$VSTATUS"; then rm -f "$VST"; continue; fi
    # A furloughed verifier cannot file anything, so escalating is noise: it
    # pages Brian about a seat deliberately off until the window resets. Mark
    # both stages fired and log it, so the row stays visibly unverified in
    # QUEUE.md without generating a page nobody can act on.
    if is_parked "$VNAME"; then
      log "VERDICT $VKEY row $VNR: verifier $VNAME is parked - deferred, no page"
      echo "$T $VNAME 1 1" > "$VST"; continue
    fi
    VOLD=$(cat "$VST" 2>/dev/null)
    if [ -z "$VOLD" ]; then echo "$T $VNAME 0 0" > "$VST"; continue; fi
    DONE_AT=$(echo "$VOLD" | cut -d' ' -f1); F30=$(echo "$VOLD" | cut -d' ' -f3); F60=$(echo "$VOLD" | cut -d' ' -f4)
    # verdict filed? status verdict-words without a pending marker, or a fresh
    # verdict-named team/ file FROM THIS VERIFIER (basename must carry the
    # verifier's name — fleet convention is seat-named receipts. An unscoped
    # probe lets one row's verification silence every other row's clock).
    if status_verdict "$VSTATUS"; then rm -f "$VST"; continue; fi
    VFILE=0; VLOW=$(echo "$VNAME" | tr '[:upper:]' '[:lower:]')
    VALT=""; [ "$VLOW" = "alice" ] && VALT="aletheia"; [ "$VLOW" = "aletheia" ] && VALT="alice"
    while read -r vf; do
      bl=$(basename "$vf" | tr '[:upper:]' '[:lower:]')
      # Scoped to the ROW as well as the seat. Name-only matching let one
      # receipt silence every other pending clock for the same verifier - the
      # bug the comment above warns about, fixed for the seat but not the row.
      VROW=$(echo "$VNR" | tr '[:upper:]' '[:lower:]')
      if [[ "$bl" == *"$VROW"* ]] && { [[ "$bl" == *"$VLOW"* ]] \
           || { [ -n "$VALT" ] && [[ "$bl" == *"$VALT"* ]]; }; }; then VFILE=1; fi
      [ "$VFILE" = "1" ] && break
    done < <(find "$TEAMDIR" -maxdepth 1 -type f -newermt "@$DONE_AT" \( -iname '*verif*' -o -iname '*verdict*' -o -iname '*cosign*' -o -iname '*approv*' \) 2>/dev/null)
    if [ "$VFILE" = "1" ]; then rm -f "$VST"; continue; fi
    VH=$(ls -t $HIST/${VID%%-*}-*.jsonl 2>/dev/null | head -1)
    VHT=$(mt "$VH"); [ -z "$VH" ] && VHT=0
    # "Dark" must mean the verifier produced nothing, not that it said nothing.
    # VHT is any turn, which the reply to our own nudge refreshes - the same
    # defect that made the 10/20 clock escalate zero times in 12 firings.
    VAT=$(art_ts "$VH"); [ -z "$VAT" ] && VAT=0
    VPACK="[chain verdict] row $VNR '$(echo "$VTASK" | cut -c1-70)': unverified $(( (T - DONE_AT) / 60 ))min since this clock first saw it, no verdict filed (owner: ${OWNER:-?}, verifier: $VNAME, artifact: ${ART:-see QUEUE row})"
    if [ $(( T - DONE_AT )) -ge "$T_VERDICT_ESC" ] && [ "$F60" != "1" ]; then
      if [ $(( T - VAT )) -ge "$T_VERDICT_ESC" ]; then
        CID=$(seat_id_for "cairn-pi")   # conductor is cairn since 2026-09-16
        sent=0
        brian 3600 verifier-dark "[Fleet] $VPACK — verifier dark 60+ min. Ledger parked — Brian call. — fleet-poller" && sent=1
        [ -n "$CID" ] && wake "$CID" "[conductor-glm] $VPACK — verifier dark 60+ min. Reassign or chase. — fleet-poller" && sent=1
        [ "$sent" = "1" ] && echo "$DONE_AT $VNAME $F30 1" > "$VST"
      fi
    elif [ $(( T - DONE_AT )) -ge "$T_VERDICT" ] && [ "$F30" != "1" ]; then
      if [ -n "$VNAME" ] && ledger_is_producer "$VKEY" "$VNAME"; then
        log "VERDICT $VKEY row $VNR: SELF-VERIFY REFUSED - $VNAME was dispatched to produce this row (ledger: $(ledger_producers "$VKEY"))"
        brian 3600 self-verify "Row $VNR is waiting on a check from $VNAME, but that seat was given the row to do. It cannot check its own work, so nobody has been chased." || true
      elif wake "$VID" "[$VNAME] $VPACK — file your verdict or post a reason. — fleet-poller"; then
        echo "$DONE_AT $VNAME 1 $F60" > "$VST"
      fi
    fi
  done < <(awk -F'|' '
    # IS THIS A ROW AT ALL? Added 2026-09-17 after the unroutable alarm paged
    # Brian about rows seeking seats named `1-2m`, `83%` and `100%`. Those were
    # columns of MARKDOWN TABLES pasted into QUEUE.md: every line starting with
    # "|" was read as a row and column 4 as its eligible seats. The tables were
    # moved out, and this stops the next one silently becoming a row.
    # NOT a column count - six real rows carry 10 or 11 fields because their
    # cells contain backticked pipes, so NF==9 would have dropped genuine work.
    # The row ID is the discriminator: digits, or letters followed by a digit
    # (37, S3-7, D-3, S6-1G) - which "model", "provider" and
    # "muse-spark-1.3-contributor" all fail.
    # Real ids on this board: digits (37), or a short letter prefix with a digit
    # and an optional -part and trailing letter (D-1, S3-7, S6-1G, S4-8). A
    # first attempt allowed any letters followed by a digit and REJECTED the six
    # live D-* debt rows, because D-1 has a separator before its digit; allowing
    # any separator then admitted `glm-5.3-flash` from a table. Requiring the
    # whole cell to match this shape admits every real row and rejects every
    # table heading and data cell measured on 2026-09-17.
    # A rejected line is printed to stderr (journald keeps it) because a row
    # made INVISIBLE by a mis-shaped id is worse than a phantom one: the phantom
    # pages Brian, the invisible row just never gets worked.
    function isrow(id,  raw) { raw=id; gsub(/^[ \t]+|[ \t]+$/, "", id)
      if (id ~ /^[0-9]+$/ || id ~ /^[A-Za-z]{1,3}[0-9]*-?[0-9]+[A-Za-z]?$/) return 1
      print "NOT-A-ROW id=[" id "] - ignored by the poller" > "/dev/stderr"
      return 0 }
    BEGIN{OFS="\037"} /^\|/ && $0 !~ /\|---/ && $3 !~ /^[ \t]*$/ && $3 !~ /Task/ && isrow($2) {
    task=$3; status=""; for(i=8;i<NF;i++){status=status ((i>8)?"|":"") $i}
    gsub(/^[ \t]+|[ \t]+$/, "", task); gsub(/^[ \t]+|[ \t]+$/, "", status)
    rid=$2; gsub(/^[ \t]+|[ \t]+$/, "", rid)
    # NR is the awk record number, not the row id. Every escalation named
    # the wrong thing: row 43 was line 43, which holds row 21, and no row
    # 43 exists. Measured from a real page sent to Brian 2026-09-15.
    print task, status, rid, $0 }' "$QUEUE" 2>/dev/null)
  for st in "$VERD"/*; do
    [ -f "$st" ] || continue
    case "$VERDLIVE" in *"$(basename "$st")"*) ;; *) rm -f "$st";; esac
  done

  # 11. Sprint-close detector (Brian-approved 2026-09-15). When every build row
  #   reads done-or-closed, wake Ledger once with the tally: rows done,
  #   verifiers confirmed (status_verdict reuse), spend if available.
  #   Standing rows (task or status carrying STANDING — steward/watch duties
  #   never close) are excluded from the all-done computation. Fires on the
  #   TRANSITION into all-done (state file tracks the last verdict), so a
  #   reopened row re-arms and the next close fires again — one-fire per close
  #   event, never a repeat while closed. No-self is vacuous here and stated
  #   as such: the close is collective state with no single actor to suppress;
  #   the only recipient is Ledger (PO). Zero tokens: local text + one
  #   meters.py read (already fail-soft everywhere else it is used).
  SCST="$DIR/sprint-close"
  SCDONE=0; SCTOT=0; SCVER=0; SCOPEN=""
  while IFS=$(printf '\037') read -r STASK SSTATUS SNR SLINE; do
    [ -z "$STASK" ] && continue
    if grep -qi "standing" <<<"$STASK $SSTATUS"; then continue; fi
    SCTOT=$(( SCTOT + 1 ))
      # EVIDENCE FIRST, the same rule as the chain classifier. This detector
      # was left reading prose when the classifier moved to the gate on
      # 2026-09-16, so a row could be computed-done and still hold the sprint
      # open. Row 32 was exactly that: both declared artifacts on disk since
      # 09-13, Alice co-signed, its gate exiting 0 - and the sprint stayed open
      # because nobody typed the word "done:". That is the row-42 failure
      # wearing a different hat, in the one place that decides whether a
      # sprint can close at all.
      SCGATE=none
      case "$SLINE" in *'(check:'*) SCGATE=$(row_gate "$SNR");; esac
      if [ "$SCGATE" = pass ] || grep -qiE "done:|\bclosed\b" <<<"$SSTATUS"; then
        if [ "$SCGATE" = pass ] && ! grep -qiE "done:|\bclosed\b" <<<"$SSTATUS"; then
          log_once "scev-$SNR" "SPRINT-CLOSE row $SNR counts as done on EVIDENCE - its declared check passes and its status cell never said so"
        fi
      SCDONE=$(( SCDONE + 1 ))
      if status_verdict "$SSTATUS"; then SCVER=$(( SCVER + 1 )); fi
    else
      SCOPEN="$SCOPEN $SNR"
    fi
  done < <(awk -F'|' '
    # IS THIS A ROW AT ALL? Added 2026-09-17 after the unroutable alarm paged
    # Brian about rows seeking seats named `1-2m`, `83%` and `100%`. Those were
    # columns of MARKDOWN TABLES pasted into QUEUE.md: every line starting with
    # "|" was read as a row and column 4 as its eligible seats. The tables were
    # moved out, and this stops the next one silently becoming a row.
    # NOT a column count - six real rows carry 10 or 11 fields because their
    # cells contain backticked pipes, so NF==9 would have dropped genuine work.
    # The row ID is the discriminator: digits, or letters followed by a digit
    # (37, S3-7, D-3, S6-1G) - which "model", "provider" and
    # "muse-spark-1.3-contributor" all fail.
    # Real ids on this board: digits (37), or a short letter prefix with a digit
    # and an optional -part and trailing letter (D-1, S3-7, S6-1G, S4-8). A
    # first attempt allowed any letters followed by a digit and REJECTED the six
    # live D-* debt rows, because D-1 has a separator before its digit; allowing
    # any separator then admitted `glm-5.3-flash` from a table. Requiring the
    # whole cell to match this shape admits every real row and rejects every
    # table heading and data cell measured on 2026-09-17.
    # A rejected line is printed to stderr (journald keeps it) because a row
    # made INVISIBLE by a mis-shaped id is worse than a phantom one: the phantom
    # pages Brian, the invisible row just never gets worked.
    function isrow(id,  raw) { raw=id; gsub(/^[ \t]+|[ \t]+$/, "", id)
      if (id ~ /^[0-9]+$/ || id ~ /^[A-Za-z]{1,3}[0-9]*-?[0-9]+[A-Za-z]?$/) return 1
      print "NOT-A-ROW id=[" id "] - ignored by the poller" > "/dev/stderr"
      return 0 }
    BEGIN{OFS="\037"} /^\|/ && $0 !~ /\|---/ && $3 !~ /^[ \t]*$/ && $3 !~ /Task/ && isrow($2) {
    task=$3; status=""; for(i=8;i<NF;i++){status=status ((i>8)?"|":"") $i}
    gsub(/^[ \t]+|[ \t]+$/, "", task); gsub(/^[ \t]+|[ \t]+$/, "", status)
    rid=$2; gsub(/^[ \t]+|[ \t]+$/, "", rid)
    # NR is the awk record number, not the row id. Every escalation named
    # the wrong thing: row 43 was line 43, which holds row 21, and no row
    # 43 exists. Measured from a real page sent to Brian 2026-09-15.
    print task, status, rid, $0 }' "$QUEUE" 2>/dev/null)
  SCOLD=$(cat "$SCST" 2>/dev/null)
  # A SPRINT DOES NOT CLOSE ON THE AUTHOR'"'"'S WORD. Until 2026-09-17 this fired on
  # SCDONE == SCTOT and merely REPORTED SCVER in the message, so a sprint could
  # close with zero independent verdicts. Found the same morning by a Fable
  # review of the whole arrangement, and confirmed live: S6-1 and S6-2 were
  # both counted done with kiln as the only author and no corvid verdict on
  # either. That is the S4-12 failure - author and verifier the same seat -
  # reproduced with a better-looking certificate, in the one place that decides
  # whether a sprint is finished. The gates cannot catch it: a gate checks that
  # a review file EXISTS, and kiln'"'"'s own review.json said in plain words that
  # verification was still pending. Existence is not independence.
  if [ "$SCTOT" -gt 0 ] && [ "$SCDONE" -eq "$SCTOT" ] && [ "$SCVER" -lt "$SCDONE" ]; then
    log_once "scunver-$SCDONE-$SCVER" "SPRINT-CLOSE HELD: $SCDONE/$SCTOT rows done but only $SCVER carry an independent verdict. Not closing."
    if [ "$SCOLD" != "held-$SCVER" ]; then
      VNEED=$(( SCDONE - SCVER ))
      brian 3600 verifier-dark "[Fleet] the sprint is finished but NOT verified: $SCDONE of $SCTOT rows done, $VNEED with no independent verdict. Held rather than closed. — fleet-poller" || true
      echo "held-$SCVER" > "$SCST"
    fi
  fi
  if [ "$SCTOT" -gt 0 ] && [ "$SCDONE" -eq "$SCTOT" ] && [ "$SCVER" -eq "$SCDONE" ]; then
    if [ "$SCOLD" != "closed" ]; then
      # Spend read lives INSIDE the firing branch (Aletheia §11 verdict):
      # meters.budget() makes live HTTPS calls, and the zero-token rule means
      # the steady-state sweep must never pay for a tally nobody will read.
      SPEND=$(python3 -c 'import sys,os; sys.path.insert(0,os.path.dirname("'"$METERS"'")); import meters; b=meters.budget(); print("$%.4f of $%.2f" % (b["spentUsd"], b["capUsd"]))' 2>/dev/null)
      [ -z "$SPEND" ] && SPEND="unavailable"
      SCPACK="[chain sprint-close] $SCDONE/$SCTOT build rows done-or-closed (standing excluded; verifiers confirmed on $SCVER/$SCDONE; spend $SPEND)"
        # THE CONDUCTOR WRITES THE DEMO, NOT BRIAN. Until 2026-09-16 this
        # detector paged Brian alone, so a finished sprint arrived as a Signal
        # saying the queue was clear, and commissioning the write-up was his to
        # do by hand. Conductor first, then Brian - and Brian is told whether
        # the demo is actually coming, so silence is never mistaken for it.
        SCID=$(seat_id_for "cairn-pi")
        SCDEMO=0
        if [ -n "$SCID" ] && wake "$SCID" "[conductor] $SCPACK

The queue is clear, so the sprint is done. Write the sprint demo document for Brian and file it at team/SPRINT-<N>-DEMO.md, where <N> is one past the highest existing SPRINT-*-DEMO.md. Read the sprint goal block at the top of QUEUE.md first: the demo is judged against that goal, not against row count.

Three requirements Brian set, in his words:

1. EVERY ITEM MUST SAY WHAT IS BEING ASKED OF HIM. His complaint about the last demo was "I do not understand everything, or exactly what is being asked in each case." If an item needs no decision, say so explicitly. If it needs one, state the options and what each costs.

2. PLAIN LANGUAGE, per team/PO-COMMUNICATION-CONTRACT.md. No internal coinage without a definition on first use. Say what changed FOR BRIAN, not what the fleet did.

3. CITE, DO NOT ASSERT. You dispatch the work, so you are not an independent check on it. For every result name the verifier and the artifact. Where nothing independent verified a result, say so plainly rather than papering it.

The demo REPORTS. It does NOT propose the next sprint - that is the council's job (sprint-council: three contributors advise, Astra decides at high effort, Brian reviews), and a demo-authored plan is a competing proposal nobody adjudicates. DO still surface decisions waiting on Brian: the portfolio charter sat four days because nothing raised it. Separate results from scaffolding, and put any caveat in the same breath as the number it qualifies. Last sprint reported two memory systems at 0/30, which was a configuration artifact already recorded in team/ECOSYSTEM-MAP.md three days earlier. - fleet-poller"; then SCDEMO=1; fi
        if [ "$SCDEMO" = 1 ]; then
          SCNOTE="Cairn has been asked to write the demo; it will appear as team/SPRINT-*-DEMO.md."
        else
          SCNOTE="The conductor could not be reached, so NO demo is being written - that part is on you."
        fi
      if brian 0 sprint-close "[Fleet] $SCPACK — sprint reads complete. $SCNOTE Confirm close or staff the remainder. — fleet-poller"; then
        echo "closed" > "$SCST"
      fi
    fi
  else
    [ "$SCOLD" != "open" ] && echo "open" > "$SCST"
  fi

  # 5. dead-man: watched lanes missing from history = session gone
  for pair in "CAIRN:$CAIRN_HIST" "FSYNC:$FSYNC_HIST" "LEDGER:$LEDGER_HIST" "BUILDER:$BUILDER_HIST"; do
    n="${pair%%:*}"; h="${pair##*:}"
    [ -z "$h" ] && flag "$n lane history file missing — session may be gone"
  done

  sleep "$INTERVAL"
done
log "poller exit (loop ended - not the stop file; that pauses in place now)"
