#!/bin/sh
# R28 offline render witness: the exact pre-nudge agent-loop (47f69dfd) dispatches the six R27 arms
# into an isolated temp root. Every external effect (wake, systemd-run, systemctl, agent-deck) is a
# stub that records its argv; the config names only the stubs. No real socket, unit, DB or network.
#   sh render.sh OUTDIR
set -eu
OUT=$(realpath "$1"); BIN=${R28_BIN:-/home/bmosher/.local/bin/agent-loop.prev-r23-47f69dfd}
R27=/home/bmosher/memory-bake-off/campaign4/packages/R27-revised-persistence-design
ROOT=$(mktemp -d /tmp/r28-render-XXXX); S=$ROOT/stubs; mkdir -p $S $ROOT/stream $ROOT/claims $ROOT/art $OUT/texts
[ "$(sha256sum $BIN | cut -c1-8)" = "${R28_EXPECT:-47f69dfd}" ] || { echo "wrong binary" >&2; exit 1; }
python3 - "$ROOT" "$S" <<'PY'
import sys
ROOT, S = sys.argv[1], sys.argv[2]
for n in ("wake", "systemd-run", "systemctl"):
    open(f"{S}/{n}", "w").write(
        "#!/usr/bin/env python3\nimport json, sys\n"
        f"open({ROOT + '/calls.jsonl'!r}, 'a').write(json.dumps({{'stub': {n!r}, 'argv': sys.argv[1:]}}) + '\\n')\n"
        + ("print('wake: ' + sys.argv[1] + ' -> started')\n" if n == "wake" else ""))
PY
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"K\", \"title\": \"kiln\"}, {\"id\": \"C\", \"title\": \"corvid\"}, {\"id\": \"T\", \"title\": \"tern\"}, {\"id\": \"D\", \"title\": \"cairn\"}]'" > $S/agent-deck
chmod +x $S/*
cat > $ROOT/cfg.json <<J
{"project": "r28render", "profile": "none", "wake": "$S/wake", "db": "$ROOT/loop.db", "stream_dir": "$ROOT/stream",
 "claims_dir": "$ROOT/claims", "artifacts_dir": "$ROOT/art", "director": "tern", "duty": "cairn", "unit": "r28render.service",
 "seats": {"kiln": "K", "corvid": "C", "tern": "T", "cairn": "D"}, "agent_deck": "$S/agent-deck", "bin": "$BIN",
 "systemd_run": "$S/systemd-run", "systemctl": "$S/systemctl", "max_verify_s": 7200, "decision_window_s": 86400}
J
python3 - "$R27" "$ROOT" "${R28_NEG_EMPTY:-}" <<'PY'
import re, sys
R27, ROOT, NEG = sys.argv[1], sys.argv[2], sys.argv[3]
packet = open(f"{R27}/packet.md").read()
def quoted(t):
    return "\n".join(l[2:] for l in t.split("Common body")[1].splitlines() if l.startswith("> "))
A = quoted(open(f"{R27}/task-pair-A.md").read())
for pair in "ABC":
    t = open(f"{R27}/task-pair-{pair}.md").read()
    m = re.search(r"Common body as Pair A, with `--docs (fixtures/docs-[A-Z])`", t)
    # B/C declare "Common body as Pair A" with only the docs flag changed: expand that reference
    body = A.replace("--docs fixtures/docs-A", f"--docs {m.group(1)}") if m else quoted(t)
    if NEG == pair:
        body = ""
    docs = f"--docs fixtures/docs-{pair}"
    need = {"goal": "P-INDEX-7", "failed step": "step 2/4", "allowed command": "pindex_cli.py --action",
            "scope": "Scope: local files only", "correct docs": docs}
    miss = [k for k, v in need.items() if v not in body]
    wrong = sorted(set(re.findall(r"fixtures/docs-[A-Z]", body)) - {docs[7:]})
    if not body.strip() or miss or wrong:
        sys.exit(f"pair {pair}: body rejected: empty={not body.strip()} missing={miss} wrong_docs={wrong}")
    for arm in "CT":
        b = body.replace("<ARM>", arm).replace("<EXEC>", f"ex-R27-{pair}-{arm}-w1").replace("<OUT>", "out")
        head = packet if arm == "T" else "No additional notes."
        open(f"{ROOT}/task-{pair}-{arm}.md", "w").write(head.rstrip("\n") + "\n\n" + b + "\n")
PY
: > $OUT/commands.txt
for pair in A B C; do for arm in C T; do
  cmd="$BIN dispatch --config $ROOT/cfg.json --qid R27-$pair-$arm --worker kiln --verifier corvid --duration 10m --verify-window 5m --task @$ROOT/task-$pair-$arm.md --verify-task @$R27/verifier-task.txt"
  env -i HOME=$ROOT PATH=$S:/usr/bin $cmd > $ROOT/out-$pair-$arm.txt 2>&1; rc=$?
  echo "rc=$rc $cmd" >> $OUT/commands.txt
done; done
python3 - "$ROOT" "$OUT" <<'PY'
import json, sys, hashlib
ROOT, OUT = sys.argv[1], sys.argv[2]
calls = [json.loads(l) for l in open(f"{ROOT}/calls.jsonl")]
for c in calls:
    if c["stub"] == "wake" and c["argv"][0] == "K":
        try:
            p = json.loads(c["argv"][1]); text, qid = p["text"], p["package"]
        except Exception:
            text, qid = c["argv"][1], "unknown"
        open(f"{OUT}/texts/{qid}.txt", "w").write(text)
json.dump({"calls": [{"stub": c["stub"], "argv0": c["argv"][0]} for c in calls]}, open(f"{OUT}/stub-calls.json", "w"), indent=1)
PY
cp $ROOT/cfg.json $OUT/isolated-config.json
echo "$ROOT"
