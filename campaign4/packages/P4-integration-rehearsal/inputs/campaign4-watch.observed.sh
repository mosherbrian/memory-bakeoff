#!/usr/bin/env bash
# Campaign 4 backstop. Fires ONLY on silence; it never drives work.
#
# Cairn wakes itself with one-shot `sleep` alarms, one per deadline. Those are
# detached processes: a reboot or a session restart loses them SILENTLY, and
# nothing else would notice. That is the supervisor-liveness hole Tern named
# and left unassigned, and P2 is meant to close it. Until then, this.
#
# A ladder, bounded, three rungs, then it stops escalating:
#   quiet >= STALL      -> wake cairn once, tell it to reconcile
#   quiet >= 2 x STALL  -> wake tern
#   quiet >= 3 x STALL  -> campaign4-pause, which Signals Brian
#
# This is NOT polling. Cairn is not asked anything while work is moving.
set -u
C4="${C4_DIR:-$HOME/memory-bake-off/campaign4}"
STATE="$HOME/.local/share/agent-deck/campaign4-watch.state"
STALL="${STALL_MIN:-45}"
AD="agent-deck -p campaign4"
# DRY=1 exercises the ladder without waking anyone. An alarm nobody has seen
# fire is not an alarm - and on 2026-09-21 a DRY run that was not dry stopped
# the live fleet, so this is set ONCE, above every use.
[ "${DRY:-0}" = 1 ] && AD="echo [DRY would send]"
wake_seat() {
    if [ "${DRY:-0}" = 1 ]; then
        echo "[DRY would wake] $*"
    else
        AGENTDECK_PROFILE=campaign4 "$HOME/.config/agent-deck/wake" "$@"
    fi
}
# DRY=1 exercises the ladder without waking anyone. An alarm nobody has seen
# fire is not an alarm.


# Newest change anywhere in campaign4 - the only measure of "moving".
# NOTHING IN FLIGHT is a different fault from SILENCE, and the fast one.
# 2026-09-21: Tern reached a package boundary, recorded a disposition and
# stopped without opening the successor she had authority to open. This check
# read "moving" because the disposition had JUST been written; it would have
# fired on silence ~45 minutes later. Brian noticed first. A rate check cannot
# see a state fault quickly - so read the state the fleet declares.
#
# state.json is written by cairn: {"in_flight": [...], "terminal": {"<pkg>":
# "<disposition>"}}. Absent = fall through to the silence check, never a
# silent pass. A terminal package with NO recorded disposition is invalid.
ST="$C4/state.json"
if [ -f "$ST" ]; then
    bad=$(python - "$ST" <<'PY' 2>/dev/null
import json,sys
try: d=json.load(open(sys.argv[1]))
except Exception: print("UNREADABLE"); raise SystemExit
# A REST STATE IS LEGITIMATE. "Nothing in flight" is only a fault when
# nothing explains it, or when a package says it opened a successor that is
# not actually running. Otherwise a finished campaign would alarm forever.
REST={"question answered, none warranted","budget spent"}
OK=REST | {"successor opened"}
fly=d.get("in_flight") or []
term=d.get("terminal") or {}
undecided=[k for k,v in term.items()
           if not (v or "").startswith("blocked on") and (v or "") not in OK]
claimed=[k for k,v in term.items() if v=="successor opened"]
if undecided:
    print("NO DISPOSITION: "+", ".join(undecided))
elif claimed and not fly:
    print("SUCCESSOR CLAIMED BUT NOTHING IN FLIGHT: "+", ".join(claimed))
PY
)
    if [ -n "$bad" ]; then
        echo "state fault: $bad"
        rung=$(cat "$STATE" 2>/dev/null || echo 0); rung=$((rung+1)); echo "$rung" > "$STATE"
        case "$rung" in
          1) $AD session send tern "STATE FAULT: $bad. If a successor is warranted, open it - that is yours. If none is, record which disposition applies. Do not wait to be asked." >/dev/null 2>&1
             echo "rung 1: woke tern" ;;
          2) "$HOME/.config/agent-deck/campaign4-pause" "Campaign 4 state fault unresolved: $bad. Tern was woken once and did not resolve it." ;;
          *) echo "already escalated" ;;
        esac
        exit 1
    fi
fi

newest=$(find "$C4" -type f -newermt "-${STALL} minutes" 2>/dev/null | head -1)
# status is a top-level string on this build - verified against the real JSON,
# not assumed. A miscounted "active" would make this alarm unable to fire.
active=$(AGENTDECK_PROFILE=campaign4 agent-deck list --json 2>/dev/null \
         | python -c 'import json,sys
try: xs=json.load(sys.stdin)
except Exception: print(0); raise SystemExit
xs = xs if isinstance(xs,list) else xs.get("sessions",[])
def st(x):
    v=x.get("status")
    return (v.get("type") if isinstance(v,dict) else v) or ""
print(sum(1 for x in xs if st(x) in ("active","running","busy")))' 2>/dev/null || echo 0)

if [ -n "$newest" ] || [ "${active:-0}" -gt 0 ]; then
    rm -f "$STATE"; echo "moving (changed=${newest:+yes} active=${active:-0})"; exit 0
fi

rung=$(cat "$STATE" 2>/dev/null || echo 0); rung=$((rung+1)); echo "$rung" > "$STATE"
case "$rung" in
  1) wake_seat cairn "LIVENESS: nothing in campaign4 has changed for ${STALL} minutes and no seat is active. Your one-shot deadline timers may have been lost. Reconcile: check packages/ for work that is waiting, re-arm any deadline you still owe, and dispatch or escalate. Do not assume a timer survived." >/dev/null 2>&1
     echo "rung 1: woke cairn" ;;
  2) wake_seat tern "LIVENESS: campaign4 has been silent for $((STALL*2)) minutes and cairn did not restart it after being woken. You own this. Reconcile the state, or pause with campaign4-pause if you cannot reasonably decide." >/dev/null 2>&1
     echo "rung 2: woke tern" ;;
  3) if [ "${DRY:-0}" = 1 ]; then echo "[DRY would pause and Signal Brian]"; else
     "$HOME/.config/agent-deck/campaign4-pause" "Campaign 4 has been silent for $((STALL*3)) minutes. Cairn did not recover after being woken and Tern did not either. Options: (a) you restart it yourself, (b) it waits for you, (c) you stop campaign 4 for today. Affected: every open package."
     fi
     echo "rung 3: paused and Signalled Brian" ;;
  *) echo "rung $rung: already escalated to Brian, staying quiet" ;;
esac
