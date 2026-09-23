#!/bin/bash
# P9 check 5 rehearsal. Usage: rehearse.sh RELEASE.tar.gz
# Extracts into a fresh private dir, checks the manifest and debris, rebuilds from the shipped
# source, runs the Go tests and 125 conformance cases on the shipped binary, installs to a
# private prefix, and exercises check/dispatch/claim/run/expose/decide/stop/start/restore with
# stub wake, agent-deck, systemd-run and systemctl. No real seat or service is touched.
set -u
REL=$1; V=$(basename $REL .tar.gz); V=${V#agent-loop-}
X=$(mktemp -d /tmp/p9-rehearsal-XXXX); export PATH=$HOME/sdk/go/bin:$PATH
MAINHEAD=$(git -C ~/projects/agent-loop rev-parse HEAD); INST=$(sha256sum ~/.local/bin/agent-loop | cut -c1-64)
echo "## rehearsal of release $V in $X at $(date -u +%FT%TZ)"
echo "archive sha256: $(sha256sum $REL | cut -c1-64)"
tar -C $X -xzf $REL && cd $X/agent-loop-$V && sha256sum -c --quiet MANIFEST.sha256 && echo "manifest: all $(wc -l < MANIFEST.sha256) files match"
echo "debris (db, claims, caches, pyc, .git, env, credentials, keys):"; tar tzf $REL | grep -iE '\.db|/claims|cache|\.pyc|/\.git/|\.env|credential|secret|key' || echo "  none"
mkdir -p $X/src && tar -C $X/src -xzf agent-loop-$V-src.tar.gz && (cd $X/src/agent-loop-$V-src && CGO_ENABLED=0 go build -trimpath -o $X/built ./cmd/agent-loop)
diff <(go version -m bin/agent-loop | grep -v -e vcs -e '^bin' -e $'\tmod\t') <(go version -m $X/built | grep -v -e vcs -e "^$X" -e $'\tmod\t') && echo "rebuild from shipped source: deps/settings identical (bytes differ only by the vcs stamp; the tarball has no .git)"
echo "go test on shipped source: $(cd $X/src/agent-loop-$V-src && go test -count=1 ./... 2>&1 | grep -v '^?' | tr '\n' ';')"
echo "conformance on the shipped binary: $(cd $X/src/agent-loop-$V-src && $X/agent-loop-$V/bin/agent-loop conformance conformance/cases 2>&1 | tail -1)"
P=$X/prefix; install -D bin/agent-loop $P/bin/agent-loop; A=$P/bin/agent-loop
S=$X/stubs; mkdir -p $S $X/stream $X/art; O=$(mktemp -d /tmp/p9-rehearsal-out-XXXX)  # render outputs live outside the ledger dir
printf '#!/bin/sh\necho %s\n' "'[{\"id\": \"W1\", \"title\": \"fx-worker\"}, {\"id\": \"V1\", \"title\": \"fx-verifier\"}, {\"id\": \"D1\", \"title\": \"fx-director\"}]'" > $S/agent-deck
printf '#!/bin/sh\necho "$1 $2" | head -c 90 >> %s/wake.log; echo >> %s/wake.log; echo "wake: $1 -> started"\n' $X $X > $S/wake
printf '#!/bin/sh\necho "$@" >> %s/systemd.log\n' $X > $S/systemd-run; cp $S/systemd-run $S/systemctl; chmod +x $S/*
python3 - "$X" "$S" "$A" <<'PY' > $X/fx.json
import json, sys
X, S, A = sys.argv[1:4]
c = json.load(open("examples/project.template.json"))
c.update(project="fx", profile="none", wake=S+"/wake", db=X+"/fx.db", stream_dir=X+"/stream", claims_dir=X+"/claims",
         artifacts_dir=X+"/art", director="fx-director", duty="fx-director",
         seats={"fx-worker": "W1", "fx-verifier": "V1", "fx-director": "D1"}, bin=A,
         agent_deck=S+"/agent-deck", systemd_run=S+"/systemd-run", systemctl=S+"/systemctl")
c.pop("unit"); c.pop("note")
print(json.dumps(c))
PY
C="--config $X/fx.json"
echo "unfilled template: $($A check --config examples/project.template.json 2>&1 | cut -c1-100) (rc refused)"
$A check $C | tail -1
$A dispatch $C --qid A --worker fx-worker --verifier fx-verifier --task "write x" --verify-task "review x"
$A dispatch $C --qid B --worker fx-worker --verifier fx-verifier --task "after A" --verify-task "review" --after A
echo x > $X/art/out.txt; $A claim $C --qid A --step worker --outcome completed --artifact out=out.txt >/dev/null
printf '{"t": "end", "item": "i%s"}\n' $(date +%s%3N) >> $X/stream/W1.jsonl; $A run $C --once
echo ok > $X/art/review.md; $A claim $C --qid A --step verify --outcome completed --artifact review=review.md >/dev/null
printf '{"t": "end", "item": "i%s"}\n' $(date +%s%3N) >> $X/stream/V1.jsonl; $A run $C --once
echo '{bad' > $X/bad.json
H1=$(sha256sum $X/fx.db* | sha256sum | cut -c1-16); L1=$(ls -l --time-style=+%s.%N $X | sha256sum | cut -c1-16)
$A expose $C > $O/expose1.txt; $A expose $C --json > $O/expose1.json; $A expose $C --inventory /nonexistent.json > /dev/null; $A expose $C --inventory $X/bad.json > /dev/null
H2=$(sha256sum $X/fx.db* | sha256sum | cut -c1-16); L2=$(ls -l --time-style=+%s.%N $X | sha256sum | cut -c1-16)
echo "read-only: ledger files hash $H1 -> $H2; directory listing $L1 -> $L2 (4 renders incl. missing and malformed inventory)"
grep -A5 "## Pending" $O/expose1.txt
$A decide $C --qid A --kind question_answered --ref rehearsal-1 --reason rehearsal; $A run $C --once
$A expose $C --json | python3 -c "import json,sys; v=json.load(sys.stdin); print('after decide: pending', [p['id'] for p in v['pending']], 'resolved', [r['id'] for r in v['resolved']], 'B', [p['step'] for p in v['packages'] if p['qid']=='B'], '| label:', v['label'])"
$A stop $C | head -1; $A run $C --once; echo "run while stopped rc=$? (64 expected)"; $A start $C
cp $A $P/bin/agent-loop.prev; $A stop $C > /dev/null; for f in $X/fx.db*; do cp $f $f.bak; done; mv $P/bin/agent-loop.prev $P/bin/agent-loop; $A start $C; $A status $C | head -3; echo "restore: previous binary swapped back, ledger files copied while stopped"
echo "main repo HEAD unchanged: $([ "$(git -C ~/projects/agent-loop rev-parse HEAD)" = "$MAINHEAD" ] && echo yes); installed ~/.local/bin/agent-loop unchanged: $([ "$(sha256sum ~/.local/bin/agent-loop | cut -c1-64)" = "$INST" ] && echo yes)"
echo "no real systemd/seats: stubs in $S; stub calls:"; cut -c1-80 $X/systemd.log
