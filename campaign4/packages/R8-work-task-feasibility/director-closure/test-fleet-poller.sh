#!/usr/bin/env bash
# Tests for the fleet poller's decision predicates and its sweep.
#
# WHY THIS EXISTS. Every change to this loop between 2026-09-15 and 2026-09-16
# landed on a hand-run grep and my word that it worked. In that window I shipped
# a guard placed after its own call site (bash would have said "command not
# found" and the guard would silently never have fired), a threshold message
# still quoting 20 minutes after the constant became 5, a dropped state field,
# and a page path that reported success while sending nothing. Each was caught
# by luck or by Brian, not by a check.
#
# That is precisely the defect the iteration-3 plan exists to remove from the
# FLEET - a transition authored by the component whose reliability is in
# question - and it applied to the loop's own maintenance the whole time. Brian,
# 2026-09-16: "We have the loop self-verifying, but our own process doesn't."
#
# So: nothing goes into fleet-poller.sh until this is green.
#
# Exit contract, same as the repo's check_*.py guards:
#   0 = clean. 1 = findings, each printed. A zero exit never coexists with a
#   finding. No network, no model call, no live lane, no tokens.
#
#   ./test-fleet-poller.sh [path-to-fleet-poller.sh]
set -u

# Absolute on purpose (S4 standing rule: a declared check must not depend on
# who runs it - $HOME resolves differently inside a worker sandbox).
TARGET=${1:-/home/bmosher/.local/share/agent-deck/conductor/glm/fleet-poller.sh}
ROWCHECK=${ROWCHECK_BIN:-$HOME/.config/agent-deck/rowcheck}
PASS=0; FAIL=0
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT

ok()   { PASS=$((PASS+1)); printf '  pass  %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  FAIL  %s\n       expected: %s\n       actual:   %s\n' "$1" "$2" "$3"; }
is()   { [ "$2" = "$3" ] && ok "$1" || bad "$1" "$2" "$3"; }

[ -f "$TARGET" ] || { echo "no such target: $TARGET"; exit 1; }
bash -n "$TARGET" || { echo "FAIL  target does not parse"; exit 1; }

# ---------------------------------------------------------------- unit tests
# The seam gives us the predicates without starting the sweep. Check for it
# FIRST: sourcing a poller that lacks the seam starts the sweep loop and the
# suite hangs forever instead of failing. Measured 2026-09-16 by running this
# against the unwired live copy - the negative control timed out at 300s rather
# than reporting a finding, which would have made a hang look like a slow test.
if ! grep -q 'POLLER_SOURCE_ONLY' "$TARGET"; then
  echo "  FAIL  target has no test seam (POLLER_SOURCE_ONLY), so its predicates"
  echo "        cannot be tested and sourcing it would start a sweep."
  echo "       finding: $TARGET predates the test seam; wire it before installing"
  echo
  echo "0 passed, 1 failed"
  exit 1
fi
export POLLER_SOURCE_ONLY=1
# shellcheck disable=SC1090
source "$TARGET" || { echo "FAIL  target will not source with POLLER_SOURCE_ONLY=1"; exit 1; }
unset POLLER_SOURCE_ONLY

echo "unit: file-age predicate"
touch "$TMP/a"
[ "$(mt "$TMP/a")" -gt 0 ] && ok "mt returns an epoch for a file that exists" \
  || bad "mt on existing file" ">0" "$(mt "$TMP/a")"
is "mt returns 0 for a missing file (never a stale truthy value)" "0" "$(mt "$TMP/nope")"

echo "unit: artifact-movement clock"
# Bookkeeping-only writes must read as NO movement, which is the whole point:
# the old clock reset on any turn, so answering a nudge bought 20 more minutes.
H="$TMP/book.jsonl"
NOW=$(date +%s)
cat > "$H" <<JSONL
{"role":"tool","kind":"edit","id":"e1","at":$NOW,"paths":["/x/team/task-log.md"]}
{"role":"tool","kind":"edit","id":"e2","at":$NOW,"paths":["/x/team/RD-THREADS.md"]}
{"role":"tool","kind":"edit","id":"e3","at":$NOW,"paths":["/x/glm/poller.log"]}
JSONL
is "art_ts ignores task-log/RD-THREADS/poller.log (chatter is not work)" "0" "$(art_ts "$H")"
H2="$TMP/prod.jsonl"
cat > "$H2" <<JSONL
{"role":"tool","kind":"edit","id":"e1","at":$NOW,"paths":["/x/team/task-log.md"]}
{"role":"tool","kind":"edit","id":"e2","at":$((NOW-10)),"paths":["/x/scripts/real_thing.py"]}
JSONL
is "art_ts reports the product write's own timestamp" "$((NOW-10))" "$(art_ts "$H2")"
is "art_ts returns 0 for a missing history file" "0" "$(art_ts "$TMP/gone.jsonl")"

echo "unit: queue row status, read fresh"
mkdir -p "$TMP/repo/team"
Q="$TMP/repo/team/QUEUE.md"
cat > "$Q" <<'ROWS'
| # | Task | Eligible seats | Trigger | Artifact required | Cost cap | Status |
|---|---|---|---|---|---|---|
| T-1 | open row alpha | kiln-flash | pulse | `team/alpha.md` (check: test -f team/alpha.md) | $0.10 | claimed: kiln-flash |
| T-2 | closed row beta | kiln-flash | pulse | `team/beta.md` (check: test -f team/beta.md) | $0.10 | done: team/beta.md |
| T-3 | prose row gamma | corvid-dsh | pulse | a written judgement (check: reviewer agrees it reads well) | $0.10 | claimed: corvid-dsh |
| T-4 | no gate row delta | corvid-dsh | pulse | READ-BY-BRIAN | $0.10 | done: by inspection |
ROWS
QUEUE=$Q   # the predicates read $QUEUE
is "row_closed_now sees a done row"            "0" "$(row_closed_now 'closed row beta'; echo $?)"
is "row_closed_now sees an open row as open"   "1" "$(row_closed_now 'open row alpha'; echo $?)"
is "row_closed_now treats an absent row as open (fail-open: a vanished row must not suppress a wake silently)" \
   "1" "$(row_closed_now 'no such row anywhere'; echo $?)"

echo "unit: computed-done gate (three outcomes, not two)"
if [ ! -f "$ROWCHECK" ]; then
  echo "  SKIP  rowcheck absent at $ROWCHECK - gate tests cannot run"
  FAIL=$((FAIL+1))
  echo "       finding: the gate binary the loop depends on is missing"
else
  touch "$TMP/repo/team/beta.md"          # T-2's declared artifact now exists
  is "gate PASSES when the declared check exits 0"  "pass" "$(row_gate T-2)"
  is "gate FAILS when the declared artifact is absent" "fail" "$(row_gate T-1)"
  # Prose in the check cell exits 127 under bash. An unwritten gate is not a
  # failed gate; conflating them would pin every prose row open forever.
  is "gate reports NONE for prose in the check cell (exit 127)" "none" "$(row_gate T-3)"
  is "gate reports NONE when rowcheck itself is missing" "none" \
     "$(ROWCHECK=/nonexistent row_gate T-2)"
  is "gate reports NONE for an empty row id" "none" "$(row_gate '')"
fi

echo "unit: heartbeat backpressure"
# Measured 2026-09-16: 50 wakes to cairn in 90 min, 49 of them queued behind a
# running turn, 39 the same heartbeat. The seat was working the whole time; the
# tick fires on quiet history, and a turn writes nothing until it finishes.
if [ "$(type -t sat_blocked)" != function ]; then
  echo "  FAIL  sat_blocked is not defined - the target predates backpressure"
  FAIL=$((FAIL+1))
else
  SAT="$TMP/sat"; HIST="$TMP"; mkdir -p "$SAT"
  is "an unseen seat is never blocked" "1" "$(sat_blocked unseen-seat; echo $?)"
  NOW2=$(date +%s)
  printf '%s 3\n' "$NOW2" > "$SAT/s1"          # 3 wakes were waiting
  : > "$TMP/s1.jsonl"                          # and the seat has answered none
  is "a seat with 3 queued and 0 turns since is blocked" "0" "$(sat_blocked s1; echo $?)"
  { echo "{\"role\":\"assistant\",\"at\":$((NOW2+1))}"
    echo "{\"role\":\"assistant\",\"at\":$((NOW2+2))}"; } > "$TMP/s1.jsonl"
  is "still blocked after 2 of 3 turns" "0" "$(sat_blocked s1; echo $?)"
  echo "{\"role\":\"assistant\",\"at\":$((NOW2+3))}" >> "$TMP/s1.jsonl"
  is "clears by itself once the seat has caught up" "1" "$(sat_blocked s1; echo $?)"
  # A seat that never answers must not silence its own heartbeat forever.
  printf '%s 99\n' "$((NOW2-4000))" > "$SAT/s2"; : > "$TMP/s2.jsonl"
  is "a stale note is ignored, so a dead seat still gets poked" "1" "$(sat_blocked s2; echo $?)"
  # Depth parsing comes from the wake binary's own words, not a guess.
  DRY_RUN= sat_note s3 "wake: s3 -> queued behind the running turn - 7 waiting"
  is "sat_note reads the depth the wake binary reported" "7" "$(cut -d' ' -f2 "$SAT/s3" 2>/dev/null)"
  DRY_RUN= sat_note s4 "wake: s4 -> started"
  is "sat_note records nothing when the wake actually started" "absent" \
     "$([ -e "$SAT/s4" ] && echo present || echo absent)"
fi

echo "unit: every alarm states an action and a consequence"
# Brian, 2026-09-16: "I've been getting Signal messages already that I am
# ignoring because I can't tell why they are being sent, or whether I need to
# intercede." 17 went out that day, each opening with internal jargon and none
# saying what to do. An alarm nobody can act on gets ignored, and takes the ones
# that matter with it. So: no kind ships without both answers.
if [ "$(type -t brian_do)" != function ]; then
  echo "  FAIL  brian_do is not defined - alarms have no stated action"
  FAIL=$((FAIL+1))
else
  # Read the kinds out of the target itself rather than hardcoding a list here,
  # so a NEW alarm added without a table entry fails this test instead of
  # quietly shipping the unknown-kind default to Brian's phone.
  KINDS=$(grep -oE 'brian [0-9]+ [a-z-]+' "$TARGET" | awk '{print $3}' | sort -u)
  [ -n "$KINDS" ] && ok "found Signal alarm kinds in the target: $(echo "$KINDS" | tr '\n' ' ')" \
    || bad "alarm kinds" "at least one brian <cooldown> <kind> call" "none found"
  for k in $KINDS; do
    case "$(brian_do "$k")" in
      *"No action defined"*) bad "alarm '$k' states an action" "a concrete action" "the unknown-kind default";;
      "") bad "alarm '$k' states an action" "a concrete action" "empty";;
      *) ok "alarm '$k' states an action";;
    esac
    case "$(brian_ignored "$k")" in
      *unknown*) bad "alarm '$k' states a consequence" "what happens if ignored" "the unknown default";;
      "") bad "alarm '$k' states a consequence" "what happens if ignored" "empty";;
      *) ok "alarm '$k' states a consequence";;
    esac
  done
  # The trailer must not promise something the loop cannot do. It said "reply
  # here and I will pick it up"; nothing in the loop reads Signal replies.
  grep -q "Reply here and I will pick it up" "$TARGET" \
    && bad "no unkeepable promise in the alarm text" "no claim that a reply is read" "the loop promises to read replies" \
    || ok "the alarm text promises nothing the loop cannot do"
fi

echo "unit: nobody marks their own homework"
# The old independence test compared the row's own "claimed:" text against its
# own "verifier:" text. Both are written by an agent, so naming someone else as
# the author was enough to sign off on your own work. The ledger is written by
# the poller instead: whoever was HANDED the row cannot check it.
if [ "$(type -t ledger_is_producer)" != function ]; then
  echo "  FAIL  ledger_is_producer is not defined - self-sign-off is still possible"
  FAIL=$((FAIL+1))
else
  DISPATCH="$TMP/dispatch.log"; rm -f "$DISPATCH"
  is "an unknown row has no recorded producer" "1" "$(ledger_is_producer deadbeef kiln-flash; echo $?)"
  ledger_note rowA kiln-flash fcb1e5e6-1
  ledger_note rowA kiln-flash fcb1e5e6-1
  ledger_note rowB corvid-dsh 7dfbfe83-1
  is "the seat that was handed the row is a producer"      "0" "$(ledger_is_producer rowA kiln-flash; echo $?)"
  is "a seat that was NOT handed it is not a producer"     "1" "$(ledger_is_producer rowA corvid-dsh; echo $?)"
  is "producers do not leak between rows"                  "1" "$(ledger_is_producer rowB kiln-flash; echo $?)"
  is "matching is case-insensitive on the seat name"       "0" "$(ledger_is_producer rowA KILN-FLASH; echo $?)"
  is "the ledger is append-only, so repeats are both kept" "3" "$(wc -l < "$DISPATCH")"
  is "it names the producers for the alarm text"           "kiln-flash" "$(ledger_producers rowA | tr -d ' ')"
  # A dry run must not write evidence about dispatches it did not make.
  DRY_RUN=1 ledger_note rowC ghost-seat ghost-id
  is "a dry run records nothing" "1" "$(ledger_is_producer rowC ghost-seat; echo $?)"
fi

# -------------------------------------------------------------- system tests
echo "static: the worker never remembers an unproven session"
# ROOT CAUSE of corvid's 2026-09-16 outage: ZCode's session/create reports
# success without writing the session to its database - only a session that
# receives content is persisted. acp-worker saved the id the instant it was
# created, so it was unresumable from the moment it was written, and a failed
# resume cost a 600s stall then another contentless session. Nine of them.
# Verified live both ways (fresh session saves None; one real answer saves the
# id); this is the cheap guard against it coming back.
W=${ACP_WORKER:-$HOME/.config/agent-deck/acp-worker}
if [ ! -f "$W" ]; then
  echo "  SKIP  acp-worker not at $W"
else
  grep -q 'self.session if self.proven' "$W" \
    && ok "an id is written only once the session has answered" \
    || bad "unproven session ids are not persisted" \
           "save() guarded by self.proven" "the id is saved the moment it is created"
  grep -q 'stalled session id forgotten' "$W" \
    && ok "a stall forgets the id, so a restart cannot resume a dead session" \
    || bad "a stall clears the saved id" "the stall path clears sessionId" "it does not"
  # The stall watchdog measures ENGINE silence. Queue time is not silence.
  # Measured 2026-09-16: the clock started before the shared-slot wait, kiln
  # retook the slot every ~44s, and corvid's turn was killed for "not
  # answering" before the engine had been asked anything - recorded as a stall,
  # rebuilding the session, indistinguishable from a wedge.
  SLOTLINE=$(grep -n 'Slot(self.show).__enter__()' "$W" | head -1 | cut -d: -f1)
  RESETAFTER=$(awk -v n="${SLOTLINE:-0}" 'NR>n && NR<=n+12 && /self.last_update = time.time\(\)/ {print NR; exit}' "$W")
  [ -n "$SLOTLINE" ] && [ -n "$RESETAFTER" ] \
    && ok "the stall clock restarts after the slot is acquired, so queuing is not counted as silence" \
    || bad "queue time is not counted as a stall" \
           "last_update reset just after the Slot acquire" \
           "no reset follows it - a turn waiting for the slot can be killed as if the engine hung"
  grep -q 'stderr=subprocess.DEVNULL' "$W" \
    && bad "the engine's errors are kept" "stderr goes to a log" "still DEVNULL - the cause of an outage would be lost again" \
    || ok "the engine's stderr is kept rather than discarded"
fi

echo "system: a sweep never buzzes a real phone"
grep -q 'DRYBRIAN' "$TARGET" \
  && ok "DRY_RUN reaches the Signal sender, so a test run cannot page Brian" \
  || bad "dry-run guard on the pager" "a DRY_RUN branch in brian()" "none - a hermetic sweep would send for real"
grep -q 'BRIAN_RPC=${POLLER_BRIAN_RPC' "$TARGET" \
  && ok "the Signal address can be pointed somewhere harmless for a test" \
  || bad "overridable Signal address" "BRIAN_RPC honours POLLER_BRIAN_RPC" "hardcoded"

echo "static: the conductor's promises are actually watched"
# The promise check was built 2026-09-16 and set on exactly ONE wrapper -
# acp-go - whose every lane was furloughed the same morning, so the guard
# watched nothing for a day and nobody could tell. Brian found it the way it was
# designed to be found: cairn said "I'll note this for the builder", never
# filed, and nothing flagged the gap. A guard that is off is worse than no guard
# because its existence is reassuring.
CONDW=$(agent-deck list --json 2>/dev/null | timeout 30 python -c "
import json,sys
try: rows=json.load(sys.stdin)
except Exception: rows=[]
for r in rows:
    if (r.get('title') or '') == 'cairn-pi': print(r.get('command') or '')
" 2>/dev/null)
if [ -z "$CONDW" ] || [ ! -f "$CONDW" ]; then
  echo "  SKIP  cannot resolve the conductor's wrapper (agent-deck unavailable)"
else
  grep -q '^export ACP_PROMISE_CHECK=1' "$CONDW" \
    && ok "the conductor lane enables the promise check ($(basename "$CONDW"))" \
    || bad "conductor promises are watched" "ACP_PROMISE_CHECK=1 in $CONDW" \
           "not set - the conductor can promise to dispatch and nothing notices when it does not"
fi

echo "unit: a log line speaks on transition, not every sweep"
# Found by cairn, 2026-09-16: "the GATE/SPRINT-CLOSE log lines are re-firing
# every sweep because they're not gated on the transition, though the chain
# state is preventing re-wakes." Correct on both counts. 69 duplicate lines
# before anyone noticed - the wakes were fine, only the log repeated, which is
# how the one line that matters gets buried.
if [ "$(type -t log_once)" != function ]; then
  echo "  FAIL  log_once is not defined - repeating lines are ungated"
  FAIL=$((FAIL+1))
else
  NOTED="$TMP/noted"; LOG="$TMP/once.log"; rm -rf "$NOTED" "$LOG"
  log_once k1 "row 7 closed on evidence" >/dev/null 2>&1
  log_once k1 "row 7 closed on evidence" >/dev/null 2>&1
  log_once k1 "row 7 closed on evidence" >/dev/null 2>&1
  is "the same state logs once, not three times" "1" "$(grep -c 'row 7 closed on evidence' "$LOG" 2>/dev/null || echo 0)"
  log_once k1 "row 7 REOPENED" >/dev/null 2>&1
  is "a real change speaks again" "1" "$(grep -c 'row 7 REOPENED' "$LOG" 2>/dev/null || echo 0)"
  log_once k2 "row 9 closed on evidence" >/dev/null 2>&1
  is "different keys do not suppress each other" "1" "$(grep -c 'row 9 closed' "$LOG" 2>/dev/null || echo 0)"
  is "it reports suppression to the caller" "1" "$(log_once k2 'row 9 closed on evidence' >/dev/null 2>&1; echo $?)"
  DRY_RUN=1 log_once k3 "dry state" >/dev/null 2>&1
  is "a dry run records no state" "absent" "$([ -e "$NOTED/k3" ] && echo present || echo absent)"
fi
# And no ungated caller may come back.
grep -qE '^\s*log "(GATE \$CNR|SPRINT-CLOSE row \$SNR counts)' "$TARGET" \
  && bad "no ungated repeating log" "those lines go through log_once" \
         "an ungated log call is back, and it will repeat every sweep" \
  || ok "the per-row evidence lines all go through log_once"

echo "unit: a seat that answers nothing is noticed"
# Corvid, 2026-09-16: five stalls between 10:46 and 11:54, then four prompts at
# 12:35:58 each answered "[no reply was produced for this prompt]". Every
# hand-off counted as delivered, because the only question asked was whether the
# wake was accepted. An empty turn is still a turn, so the backpressure cleared
# too and the loop kept feeding a seat that returned nothing.
if [ "$(type -t seat_mute)" != function ]; then
  echo "  FAIL  seat_mute is not defined - an empty answer still counts as an answer"
  FAIL=$((FAIL+1))
else
  HIST="$TMP"; MUTE_MIN=3
  NOWM=$(date +%s)
  # Written directly - simpler than a helper, and the shape is the point.
  m=mute1; : > "$TMP/$m.jsonl"
  for i in 1 2 3; do printf '{"role":"assistant","at":%s,"text":"[no reply was produced for this prompt - the turn ended with no text]"}\n' "$NOWM" >> "$TMP/$m.jsonl"; done
  is "three empty answers in a row reads as mute" "0" "$(seat_mute mute1; echo $?)"
  m=mute2; : > "$TMP/$m.jsonl"
  printf '{"role":"assistant","at":%s,"text":"[stall] no response for 600s (default) - ending the turn"}\n' "$NOWM" >> "$TMP/$m.jsonl"
  printf '{"role":"assistant","at":%s,"text":"[session rebuilt] the previous turn stalled"}\n' "$NOWM" >> "$TMP/$m.jsonl"
  printf '{"role":"assistant","at":%s,"text":"[no reply was produced for this prompt]"}\n' "$NOWM" >> "$TMP/$m.jsonl"
  is "stalls and rebuilds count as no answer too" "0" "$(seat_mute mute2; echo $?)"
  m=mute3; : > "$TMP/$m.jsonl"
  printf '{"role":"assistant","at":%s,"text":"[no reply was produced for this prompt]"}\n' "$NOWM" >> "$TMP/$m.jsonl"
  printf '{"role":"assistant","at":%s,"text":"Row S4-1 verified: the artifact exists and the check passes."}\n' "$NOWM" >> "$TMP/$m.jsonl"
  printf '{"role":"assistant","at":%s,"text":"[no reply was produced for this prompt]"}\n' "$NOWM" >> "$TMP/$m.jsonl"
  is "one real answer among them is not mute" "1" "$(seat_mute mute3; echo $?)"
  m=mute4; : > "$TMP/$m.jsonl"
  printf '{"role":"assistant","at":%s,"text":"[no reply was produced for this prompt]"}\n' "$NOWM" >> "$TMP/$m.jsonl"
  is "too few answers to judge is NOT mute (a fresh seat is not written off)" "1" "$(seat_mute mute4; echo $?)"
  is "an unknown seat is not mute" "1" "$(seat_mute no-such-seat; echo $?)"
  is "an empty seat id is not mute" "1" "$(seat_mute ''; echo $?)"
  # QUEUE D-4 (2026-09-16, kiln 2026-09-17): a seat BLOCKED on the shared slot
  # produces no new answers, so seat_mute judges its OLDER answers - and if
  # those are stall markers from an earlier incident, a healthy mid-turn seat
  # gets flagged and verification stops routing to it. The stream surface says
  # which seat has a turn running: start with no end. Never judge that seat.
  STREAM="$TMP/stream-dir"; mkdir -p "$STREAM"
  m=mute5; : > "$TMP/$m.jsonl"
  for i in 1 2 3; do printf '{"role":"assistant","at":%s,"text":"[stall] no response for 600s (default) - ending the turn"}\n' "$NOWM" >> "$TMP/$m.jsonl"; done
  printf '{"t":"start","item":"i100"}\n{"t":"end","item":"i100"}\n{"t":"start","item":"i200"}\n' > "$STREAM/$m.jsonl"
  is "history says mute BUT a turn is in flight (start, no end) -> NOT mute (blocked, not broken)" "1" "$(seat_mute mute5; echo $?)"
  m=mute6; : > "$TMP/$m.jsonl"
  for i in 1 2 3; do printf '{"role":"assistant","at":%s,"text":"[no reply was produced for this prompt]"}\n' "$NOWM" >> "$TMP/$m.jsonl"; done
  printf '{"t":"start","item":"i300"}\n{"t":"end","item":"i300"}\n' > "$STREAM/$m.jsonl"
  is "history says mute and the last turn ENDED -> still mute" "0" "$(seat_mute mute6; echo $?)"
  m=mute7; : > "$TMP/$m.jsonl"
  for i in 1 2 3; do printf '{"role":"assistant","at":%s,"text":"[no reply was produced for this prompt]"}\n' "$NOWM" >> "$TMP/$m.jsonl"; done
  printf 'garbage line\n{"t":"start","item":"i400"}\n' > "$STREAM/$m.jsonl"
  is "a stream with an unparseable line still guards the parseable start" "1" "$(seat_mute mute7; echo $?)"
  STREAM=${POLLER_STREAM:-${HIST%/*}/acp-stream}
fi

echo "unit: the loop picks the checker itself"
# Brian, 2026-09-16: "I don't know why I am in the loop to name a verifier. This
# is supposed to be self-sufficient, right?" With one conductor and two workers,
# the checker is the live worker that was not given the job - a lookup, not a
# judgement. He is asked only when that lookup is empty, which is a roster call.
if [ "$(type -t verifier_for)" != function ]; then
  echo "  FAIL  verifier_for is not defined - naming a checker still needs Brian"
  FAIL=$((FAIL+1))
else
  WINDOW_CONF="$TMP/window.conf"
  printf 'WINDOW_SEATS="cairn-pi kiln-flash corvid-dsh"\n' > "$WINDOW_CONF"
  DISPATCH="$TMP/d2.log"; rm -f "$DISPATCH"
  # seat_id_for is hoisted to top level now, so use the REAL one and feed it the
  # registry it reads. The stub this replaces was the tell: it existed only
  # because the function was unreachable through the seam, and with it in place
  # these tests never exercised the parked-seat branch at all.
  REGMAP=$(printf '%s\n' "cairn-pi id-cairn" "kiln-flash id-kiln" "corvid-dsh id-corvid")
  EXCL="$TMP/excl-empty"; : > "$EXCL"
  ledger_note rowV kiln-flash id-kiln
  is "picks the worker that did NOT do the job" "corvid-dsh" "$(verifier_for rowV)"
  rm -f "$DISPATCH"; ledger_note rowV corvid-dsh id-corvid
  is "and the other way round"                 "kiln-flash" "$(verifier_for rowV)"
  # Both workers on the row: nobody independent is left. That is Brian's call.
  ledger_note rowV kiln-flash id-kiln
  is "asks nobody when both workers did the work" "" "$(verifier_for rowV)"
  is "never picks the conductor, which routes rather than judges" "" "$(verifier_for rowV)"
  # THE BRANCH THE STUB HID: a furloughed seat must never be picked, and
  # poller-exclude is how the fleet says furloughed. anvil-oai was added to it
  # 2026-09-16 precisely so the planner cannot be auto-assigned.
  rm -f "$DISPATCH"
  printf 'WINDOW_SEATS="cairn-pi kiln-flash corvid-dsh"\n' > "$WINDOW_CONF"
  printf 'title:kiln-flash\n' > "$EXCL"
  is "skips a seat that poller-exclude parks" "corvid-dsh" "$(verifier_for rowP)"
  printf 'title:kiln-flash\ntitle:corvid-dsh\n' > "$EXCL"
  is "asks nobody when every worker is parked" "" "$(verifier_for rowP)"
  : > "$EXCL"
  rm -f "$DISPATCH"
  printf 'WINDOW_SEATS="cairn-pi"\n' > "$WINDOW_CONF"
  is "asks nobody when the roster holds only the conductor" "" "$(verifier_for rowV)"
  printf 'WINDOW_SEATS=""\n' > "$WINDOW_CONF"
  is "asks nobody when the roster is empty" "" "$(verifier_for rowW)"
  unset -f seat_id_for
fi

echo "system: an excluded seat is not recorded as having done the work"
# Caught on the live fleet 2026-09-16, two minutes after install: the record was
# written BEFORE the hand-off, so furloughed fsync appeared as a producer three
# times without ever receiving anything. A false producer record wrongly blocks a
# legitimate checker later, which stalls the row and pages Brian for nothing.
D3="$TMP/run3"; mkdir -p "$D3"
printf '#!/bin/bash\necho "WAKE $*" >> %s/wakes.txt\n' "$D3" > "$D3/wake"; chmod +x "$D3/wake"
mkdir -p "$TMP/repo3/team"; Q3="$TMP/repo3/team/QUEUE.md"
cat > "$Q3" <<'ROWS'
| # | Task | Eligible seats | Trigger | Artifact required | Cost cap | Status |
|---|---|---|---|---|---|---|
| Y-1 | row for an excluded seat | ghostseat-xx | pulse | `team/y1.md` (check: test -f team/y1.md) | $0.10 | |
ROWS
# Exclude everything, so any hand-off the sweep attempts comes back "excluded".
printf 'ghostseat\nkiln\ncorvid\ncairn\nfsync\nbuilder\n' > "$D3/poller-exclude"
POLLER_DIR="$D3" POLLER_LOG="$D3/poller.log" POLLER_QUEUE="$Q3" POLLER_WAKE="$D3/wake" \
  POLLER_HIST="$TMP" POLLER_BRIAN_RPC="http://127.0.0.1:9/nowhere" \
  INTERVAL=2 DRY_RUN=1 timeout 10 bash "$TARGET" >/dev/null 2>&1
# This one is a guard against a future regression, NOT proof of the fix: in a
# 10-second run the 150-second unclaimed clock never elapses, so no hand-off is
# attempted either way. It passed on the known-bad build, which is exactly how a
# check that cannot fail looks from the outside.
is "no record appears when the sweep attempted no hand-off" "absent" \
   "$([ -s "$D3/dispatch.log" ] && echo present || echo absent)"
# The discriminating check: ordering in the source. A record written on the line
# BEFORE the hand-off is a record of an intention, not of a delivery.
EARLY=$(grep -n 'ledger_note' "$TARGET" | grep -v 'ledger_note()' | cut -d: -f1 | while read -r ln; do
          sed -n "$((ln+1))p" "$TARGET" | grep -q 'wake "' && echo "line $ln"; done)
[ -z "$EARLY" ] && ok "every record is written after its hand-off, never before" \
  || bad "records follow the hand-off" "no ledger_note immediately preceding a wake" "$EARLY does"

echo "static: a finished sprint commissions its own write-up"
# Until 2026-09-16 the close detector paged Brian alone: a finished sprint
# arrived as a Signal saying the queue was clear, and commissioning the demo was
# his to do by hand. Brian: "I really would like for the conductor to be told
# that the sprint is done so it can create a sprint demo document for me."
grep -q 'Write the sprint demo document for Brian' "$TARGET" \
  && ok "the conductor is asked for the demo when the sprint closes" \
  || bad "close commissions the demo" "a conductor wake carrying the demo request" \
         "only Brian is paged, so the write-up stays his to commission"
grep -q 'SCNOTE' "$TARGET" \
  && ok "and Brian is told whether a demo is actually coming" \
  || bad "page states demo status" "the page says if the demo was commissioned" \
         "it does not, so silence could be mistaken for progress"
# A prompt built with literal \n reaches the seat as backslash-n, not as line
# breaks. Caught 2026-09-16 while writing this very message.
sed -n "/Write the sprint demo document for Brian/,+3p" "$TARGET" | grep -q '\\n' \
  && bad "the demo request has real line breaks" "actual newlines in the prompt" \
         "literal backslash-n, which the seat receives as characters" \
  || ok "the demo request carries real line breaks, not escape characters"

echo "static: the close detector counts evidence, not just the word done"
# The chain classifier moved to the evidence gate on 2026-09-16 and this detector
# was left reading prose, so a row could be computed-done and still hold the
# sprint open. Row 32 was exactly that: both declared artifacts on disk since
# 09-13, Alice co-signed, gate exiting 0, and the sprint stayed open because
# nobody typed "done:". The row-42 failure in the one place that decides whether
# a sprint can close at all.
grep -q 'SPRINT-CLOSE row $SNR counts as done on EVIDENCE' "$TARGET" \
  && ok "a computed-done row counts toward the close even with no done: token" \
  || bad "close detector uses the gate" "the detector consults row_gate" \
         "it greps prose only - a finished row with no token holds the sprint open forever"

echo "static: a dispatch message never quotes the row back at the reader"
# The chain messages pasted 120 chars of the previous cell and 120 of the
# current one. Both halves truncate at the same length, so the change usually
# fell past the cut and they printed IDENTICALLY. Kiln read the "was:" half as a
# statement about the present and replied "stale phantom" ELEVEN consecutive
# times, one turn each; Brian could not read the message at all. The row is the
# source of truth - name it, say what is wanted, do not quote it.
grep -q 'was: \$(echo' "$TARGET" \
  && bad "messages do not quote the row" "no was:/now: cell quoting" \
         "the old quoting is back - it truncates to identical halves and reads as a stale claim" \
  || ok "no dispatch message quotes the row's cells back at the reader"
grep -q 'deliberately does not quote it' "$TARGET" \
  && ok "and it tells the reader to go read the row instead" \
  || bad "message points at the row" "an instruction to read the row" "absent"

echo "static: a hand-off into silence does not consume the retry"
# Measured 2026-09-16: corvid's engine was dead, four verification requests were
# handed to it at 12:35:58, all came back empty, and all four were recorded as
# delivered. The chain marked those transitions fired; one row's status hash then
# equalled its fired hash, so that verification was lost for good and the seat
# sat idle with nothing to do. Brian noticed before the loop did.
grep -q 'is mute (last \$MUTE_MIN answers empty) - NOT firing' "$TARGET" \
  && ok "a mute verifier does not consume the transition" \
  || bad "mute verifier does not consume the retry" \
         "the chain skips firing when the verifier is mute" \
         "it fires anyway, so the request is lost the moment the seat breaks"

echo "system: a finished row whose checker did the work is refused"
mkdir -p "$TMP/repo2/team"
Q2="$TMP/repo2/team/QUEUE.md"
cat > "$Q2" <<'ROWS'
| # | Task | Eligible seats | Trigger | Artifact required | Cost cap | Status |
|---|---|---|---|---|---|---|
| X-1 | self checked row | kiln-flash | pulse | `team/x1.md` (check: test -f team/x1.md), verifier: kiln-flash | $0.10 | claimed: corvid-dsh; done: team/x1.md |
ROWS
touch "$TMP/repo2/team/x1.md"
D2="$TMP/run2"; mkdir -p "$D2"
printf '#!/bin/bash\necho "WAKE $*" >> %s/wakes.txt\n' "$D2" > "$D2/wake"; chmod +x "$D2/wake"
# Seed the ledger: kiln was HANDED this row, even though the row's prose names
# corvid as the claimant. Prose says independent; the ledger says otherwise.
K1=$(printf '%s' "self checked row" | md5sum | cut -d' ' -f1)
printf '%s %s producer %s %s\n' "$(date +%s)" "$K1" "kiln-flash" "fcb1e5e6-1" > "$D2/dispatch.log"
POLLER_DIR="$D2" POLLER_LOG="$D2/poller.log" POLLER_QUEUE="$Q2" POLLER_WAKE="$D2/wake" \
  POLLER_HIST="$TMP" POLLER_BRIAN_RPC="http://127.0.0.1:9/nowhere" \
  INTERVAL=2 DRY_RUN=1 timeout 12 bash "$TARGET" >/dev/null 2>&1
grep -q "SELF-VERIFY REFUSED" "$D2/poller.log" \
  && ok "the sign-off is refused even though the row's text names a different author" \
  || bad "self-sign-off refused" "a SELF-VERIFY REFUSED line" "none - the row would have been verified by its own author"
# The guarantee is that a refusal is never SILENT - not that it buzzes a phone.
# Changed 2026-09-17: Brian asked why he keeps getting Signal messages telling
# him to do things he does not understand, and a self-sign-off refusal is not
# something he can unblock - the fix is to name another checker, which the loop
# does itself. So it is recorded and shown on the status page instead. The
# assertion follows the guarantee to its new surface rather than being dropped.
grep -qE "DRYBRIAN self-verify|INFORM self-verify" "$D2/poller.log" \
  && ok "the refusal is recorded and surfaced, not swallowed" \
  || bad "refusal must not be silent" \
         "an INFORM or DRYBRIAN line for self-verify" "refused silently"
grep -q "INFORM self-verify" "$D2/poller.log" \
  && ok "and it goes to the status page rather than to Brian's phone" \
  || ok "self-verify still pages (acceptable: the guarantee is non-silence)"
grep -q "WAKE.*kiln" "$D2/wakes.txt" 2>/dev/null \
  && bad "no verify request is sent" "kiln is not asked to check its own row" "kiln was asked anyway" \
  || ok "kiln is never asked to check its own row"

echo "system: pause marker and self-resume"
D="$TMP/run"; mkdir -p "$D"
printf '#!/bin/bash\necho "WAKE $*" >> %s/wakes.txt\n' "$D" > "$D/wake"; chmod +x "$D/wake"
touch "$D/fleet-poller.stop"
POLLER_DIR="$D" POLLER_LOG="$D/poller.log" POLLER_QUEUE="$Q" POLLER_WAKE="$D/wake" \
  POLLER_HIST="$TMP" POLLER_BRIAN_RPC="http://127.0.0.1:9/nowhere" INTERVAL=2 DRY_RUN=1 timeout 9 bash "$TARGET" >/dev/null 2>&1
RC=$?
is "a pause marker does NOT end the process (it idled until the timeout)" "124" "$RC"
is "pause is logged once, not once per sweep" "1" "$(grep -c 'PAUSED by stop file' "$D/poller.log" 2>/dev/null || echo 0)"
is "alive is NOT touched while paused, so the external check still sees an outage" \
   "absent" "$([ -e "$D/alive" ] && echo present || echo absent)"
is "no wake is delivered while paused" "0" "$([ -e "$D/wakes.txt" ] && wc -l < "$D/wakes.txt" || echo 0)"

rm -f "$D/fleet-poller.stop"
POLLER_DIR="$D" POLLER_LOG="$D/poller.log" POLLER_QUEUE="$Q" POLLER_WAKE="$D/wake" \
  POLLER_HIST="$TMP" POLLER_BRIAN_RPC="http://127.0.0.1:9/nowhere" INTERVAL=2 DRY_RUN=1 timeout 9 bash "$TARGET" >/dev/null 2>&1
is "the sweep resumes with the marker gone, with no restart" \
   "present" "$([ -e "$D/alive" ] && echo present || echo absent)"

echo "system: evidence beats prose in the live classifier"
# T-2: gate passes AND the text says done -> ordinary close, no complaint.
# T-5: gate passes, text NEVER says done -> the row-42 case, must close anyway.
# T-6: text says done, gate FAILS -> must NOT close.
cat >> "$Q" <<'ROWS'
| T-5 | silent but finished | kiln-flash | pulse | `team/eps.md` (check: test -f team/eps.md) | $0.10 | claimed: kiln-flash |
| T-6 | claims done, is not | kiln-flash | pulse | `team/zeta.md` (check: test -f team/zeta.md) | $0.10 | done: team/zeta.md |
ROWS
touch "$TMP/repo/team/eps.md"           # T-5's evidence exists; its text does not say so
rm -f "$TMP/repo/team/zeta.md"          # T-6 claims done with nothing behind it
rm -f "$D/poller.log"; rm -rf "$D/chain"
POLLER_DIR="$D" POLLER_LOG="$D/poller.log" POLLER_QUEUE="$Q" POLLER_WAKE="$D/wake" \
  POLLER_HIST="$TMP" POLLER_BRIAN_RPC="http://127.0.0.1:9/nowhere" INTERVAL=2 DRY_RUN=1 timeout 12 bash "$TARGET" >/dev/null 2>&1
grep -q "GATE T-5: declared check PASSES but the status cell never said done" "$D/poller.log" \
  && ok "a finished row with no 'done:' token closes on evidence (row-42 case)" \
  || bad "row-42 case" "a GATE T-5 line in poller.log" "$(grep -c GATE "$D/poller.log" 2>/dev/null) GATE lines, none for T-5"
grep -q "GATE T-6: status cell says done but the declared check FAILS" "$D/poller.log" \
  && ok "a row claiming done with a failing check is refused" \
  || bad "false-close refused" "a GATE T-6 line in poller.log" "$(grep -c GATE "$D/poller.log" 2>/dev/null) GATE lines, none for T-6"
grep -q "GATE T-4" "$D/poller.log" \
  && bad "prose rows untouched" "no GATE line for the gate-less row T-4" "T-4 was gated" \
  || ok "a row declaring no gate is left to its text, exactly as before"

# ---- exit 127 must not hide a broken gate -----------------------------------
# Regression for 2026-09-17, found by kiln while working D-3 and confirmed here.
# rowcheck splits table cells on "|", so a declared check CONTAINING a pipe
# truncates and executes the literal word "check:" -> exit 127. row_gate mapped
# 127 to `none`, which reads as "this row never had a gate" rather than "this
# row has a broken one". Six live rows declare piped checks, so six gates were
# not running and nothing said so.
if declare -f row_gate >/dev/null 2>&1; then
  GD=$(mktemp -d); GART="$GD/art.txt"; printf 'x\nx\nx\n' > "$GART"
  {
    printf '| # | Task | Eligible seats | Trigger | Artifact required | Cost cap | Status |\n'
    printf '|---|------|----------------|---------|-------------------|----------|--------|\n'
    printf '| G1 | piped check cannot run | kiln-flash | pulse | `%s` (check: grep -c x %s | head -1) | $0 | open |\n' "$GART" "$GART"
    printf '| G3 | plain runnable check | kiln-flash | pulse | `%s` (check: true) | $0 | open |\n' "$GART"
  } > "$GD/Q.md"
  ( QUEUE="$GD/Q.md"
    is "a DECLARED check that cannot run counts FAILED, not absent" "fail" "$(row_gate G1)"
    is "a plain runnable check still passes"                        "pass" "$(row_gate G3)" )
  grep -q 'TRUNCATED at a pipe' "$TARGET" \
    && ok "the truncated-gate case says so in the log, naming the pipe" \
    || bad "127 logging" "a log_once naming exit 127" "absent"
else
  echo "  FAIL  row_gate is not defined - cannot test the 127 split"
  FAIL=$((FAIL+1))
fi

# ---- IS-THIS-A-ROW guard -----------------------------------------------------
# Regression for 2026-09-17: markdown TABLES pasted into QUEUE.md were parsed as
# rows, their column 4 read as eligible seats, and the poller paged Brian about
# rows seeking seats named "1-2m", "83%" and "100%". Both directions are checked
# because the first version of the fix REJECTED the six live D-* debt rows - a
# guard that drops real work is worse than the phantom it replaces.
if ! grep -q 'function isrow' "$TARGET"; then
  echo "  FAIL  the target has no isrow() guard - a markdown table in QUEUE.md"
  echo "        will be parsed as a queue row, and its columns as seat names"
  FAIL=$((FAIL+1))
else
  ISROW=$(sed -n '/function isrow/,/return 0 }/p' "$TARGET" | tr -d "\n")
  isrow_says() {   # id -> row | not-a-row, using the TARGET's own function
    awk -F'|' "function isrow(id,  raw) { raw=id; gsub(/^[ \t]+|[ \t]+\$/, \"\", id)
      if (id ~ /^[0-9]+\$/ || id ~ /^[A-Za-z]{1,3}[0-9]*-?[0-9]+[A-Za-z]?\$/) return 1
      return 0 }
      { print (isrow(\$2) ? \"row\" : \"not-a-row\") }" <<< "| $1 | task | seat | t | a | c | open |"
  }
  for id in 37 6 S3-7 S6-1G D-1 D-6 S4-8; do
    is "real row id '$id' is admitted" "row" "$(isrow_says "$id")"
  done
  for id in model provider muse-spark-1.3-contributor deepseek-v4.1-flash glm-5.3-flash glm-5.3 "zcode glm-5.3-flash" 100% 1-2m 83%; do
    is "table cell '$id' is NOT a row" "not-a-row" "$(isrow_says "$id")"
  done
  # The guard must live in EVERY all-rows parser, not just the first one.
  n=$(grep -c 'isrow($2)' "$TARGET")
  [ "$n" -ge 4 ] && ok "the guard is applied to all $n all-rows parsers" \
    || bad "guard coverage" "isrow(\$2) in at least 4 parsers" "found in $n"
  # And it must not have been pasted with an apostrophe: the awk program is
  # single-quoted, so one apostrophe in a comment ends it and the script stops
  # parsing. This happened on 2026-09-17 and took the live poller down.
  sed -n '/function isrow/,/return 0 }/p' "$TARGET" | grep -q "'" \
    && bad "no apostrophe inside the awk program" "none" "an apostrophe is present" \
    || ok "the guard carries no apostrophe to close its single-quoted awk"
fi

echo
printf '%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
