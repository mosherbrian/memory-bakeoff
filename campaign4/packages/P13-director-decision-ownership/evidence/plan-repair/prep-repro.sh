#!/bin/bash
# Repro: P6 prepare_live.py non-dry-run manifest bug, then repaired local copy.
# Injected genuine-shaped launch responses (stub agent-deck + real sockets).
# Original raises KeyError full[worker]; repaired copy binds BOTH roles and
# handles partial-launch cleanup. No live seats, private dirs only.
set -uo pipefail
PKG=/var/home/bmosher/memory-bake-off/campaign4/packages/P13-director-decision-ownership
ORIG=/var/home/bmosher/memory-bake-off/campaign4/packages/P6-r6-live-preparation/src/prepare_live.py
LOCAL=$PKG/plans/prepare_live.py
EV=$PKG/evidence/plan-repair/prep-repro
rm -rf "$EV"; mkdir -p "$EV"
TMP=$(mktemp -d /tmp/p13prepro-XXXXXX)
export HOME="$TMP/home"; mkdir -p "$HOME"
SBIN=$TMP/stubbin; mkdir -p "$SBIN"
export STUB_REG="$TMP/reg.json"; echo '[]' > "$TMP/reg.json"
cat > "$SBIN/agent-deck" <<EOF
#!/bin/bash
R="$TMP/reg.json"
[ "\$1" = list ] && { cat "\$R"; exit 0; }
if [ "\$1" = launch ]; then
  title=""; cmdline=""; prev=""
  for a in "\$@"; do
    [ "\$prev" = "-t" ] && title="\$a"
    [ "\$prev" = "-cmd" ] && cmdline="\$a"
    case "\$a" in -t) prev="-t";; -cmd) prev="-cmd";; *) prev="\$a";; esac
  done
  case "\$title" in *-id) id="\$title";; *) id="\$title-id";; esac
  python3 -c "
import json, socket, os, sys
sockdir = os.path.join(os.environ['HOME'], '.config/agent-deck/acp-sock')
os.makedirs(sockdir, exist_ok=True)
p = os.path.join(sockdir, sys.argv[1] + '.sock')
try: os.remove(p)
except OSError: pass
socket.socket(socket.AF_UNIX).bind(p)
r = json.load(open(os.environ['STUB_REG']))
r.append({'id': sys.argv[1], 'title': sys.argv[2], 'profile': os.environ.get('AGENTDECK_PROFILE', 'campaign4'), 'command': sys.argv[3], 'status': 'idle'})
json.dump(r, open(os.environ['STUB_REG'],'w'))" "\$id" "\$title" "\$cmdline"
  echo "{\"id\": \"\$id\", \"title\": \"\$title\"}"; exit 0
fi
exit 1
EOF
chmod +x "$SBIN/agent-deck"
export PATH="$SBIN:/usr/bin:/bin" AGENTDECK_PROFILE=campaign4
pass=0; fail=0
ok() { pass=$((pass+1)); echo "PASS $1" | tee -a "$EV/repro.log"; }
no() { fail=$((fail+1)); echo "FAIL $1" | tee -a "$EV/repro.log"; }
# Original: genuine-shaped launches, then KeyError full[worker].
python3 "$ORIG" --profile campaign4 --worker-name p6-fixture-w --verifier-name p6-fixture-v --manifest-out "$EV/orig-manifest.json" >"$EV/orig.out" 2>&1
[ $? -ne 0 ] && grep -q "KeyError: 'worker'" "$EV/orig.out" \
  && ok "original raises KeyError full[worker] on genuine launches" \
  || no "original did not reproduce (rc/out)"
# Repaired local copy: both roles bound (fresh registry/HOME).
echo '[]' > "$TMP/reg.json"; rm -rf "$HOME/.config/agent-deck/acp-sock"
python3 "$LOCAL" --profile campaign4 --worker-name p6-fixture-w --verifier-name p6-fixture-v --manifest-out "$EV/fixed-manifest.json" >"$EV/fixed.out" 2>&1
[ $? -eq 0 ] && ok "repaired copy rc0" || no "repaired copy rc!=0"
python3 -c "
import json; m=json.load(open('$EV/fixed-manifest.json'))
assert m['worker']['session_id']=='p6-fixture-w-id', m['worker']
assert m['verifier']['session_id']=='p6-fixture-v-id', m['verifier']
assert m['launcher_source']=='live-agent-deck'" 2>>"$EV/repro.log" \
  && ok "repaired manifest binds BOTH roles" || no "repaired manifest wrong"
# Partial launch: verifier launch fails -> partial manifest retains worker, no retry.
echo '[]' > "$TMP/reg.json"; rm -rf "$HOME/.config/agent-deck/acp-sock"
cat > "$SBIN/agent-deck" <<'EOF2'
#!/bin/bash
if [ "$1" = list ]; then echo '[]'; exit 0; fi
exit 1
EOF2
chmod +x "$SBIN/agent-deck"
echo '[]' > "$TMP/reg.json"
python3 "$LOCAL" --profile campaign4 --worker-name p6-fixture-w --verifier-name p6-fixture-v --manifest-out "$EV/partial-manifest.json" >"$EV/partial.out" 2>&1
grep -q "E_LAUNCH_PARTIAL" "$EV/partial.out" \
  && ok "partial launch recorded (no blind retry)" || no "partial handling wrong"
echo "repro: $pass passed, $fail failed" | tee -a "$EV/repro.log"
[ "$fail" -eq 0 ]
