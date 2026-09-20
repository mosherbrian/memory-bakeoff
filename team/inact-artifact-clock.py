#!/usr/bin/env python3
"""Make the 10/20 inactivity clock reset on artifact movement, not on words.

WHY. Measured 2026-09-15 on the live poller log and the fleet's own writes:

  - 9 of the 12 inactivity events ever logged read "posted reason, clock
    reset". The switch has never escalated once.
  - RD-THREADS.md took 34 edits in 3 hours, about one post every 5 minutes,
    so the reset condition is satisfied continuously by ordinary chatter.
  - Of 186 write operations in 3 hours, 72 were task-log.md, 34 RD-THREADS.md,
    15 QUEUE.md, 14 poller.log and 13 fleet-poller.sh. Three went to product
    code. The four build seats managed 37 turns between them and three had
    been dark over an hour.

There were THREE independent ways to reset the clock by typing:
  1. any status-text edit restarted it from now (the $SM comparison),
  2. a posted reason restarted it, with no cap,
  3. the darkness test used the owner's transcript mtime, so answering the
     nudge itself bought another 20 minutes.

All three are satisfiable without moving any work. This closes all three.

USAGE
  python3 inact-artifact-clock.py --check <file>   # report, change nothing
  python3 inact-artifact-clock.py --apply <file>   # apply in place

Idempotent: applying twice is a no-op. Exits non-zero if an anchor is missing,
so a drifted file fails loudly instead of being half-patched.
"""
import argparse
import re
import sys

HELPER = r'''
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
'''

EDITS = [
    # 1. the helper, placed just before the row loop that uses it
    dict(
        name="art_ts helper",
        find='  LIVEKEYS=""\n',
        repl=HELPER.lstrip("\n") + '  LIVEKEYS=""\n',
        guard="art_ts()",
    ),
    # 2. claimed branch: only a genuinely new claim restarts the clock
    dict(
        name="claimed clock no longer resets on status text",
        find=(
            '      OLD=$(cat "$ST" 2>/dev/null)\n'
            '      if [ "$(echo "$OLD" | cut -d\' \' -f1)" != "claimed" ] || '
            '[ "$(echo "$OLD" | cut -d\' \' -f4)" != "$SM" ]; then\n'
            '        echo "claimed $T $OWNER $SM 0" > "$ST"; continue\n'
            '      fi\n'
        ),
        repl=(
            '      OLD=$(cat "$ST" 2>/dev/null)\n'
            '      # Was: any status-text change ($SM) restarted the clock from now,\n'
            '      # so the dead-man switch could be held off by editing the row.\n'
            '      # Only a genuinely new claim (different owner) restarts it now.\n'
            '      if [ "$(echo "$OLD" | cut -d\' \' -f1)" != "claimed" ] || '
            '[ "$(echo "$OLD" | cut -d\' \' -f3)" != "$OWNER" ]; then\n'
            '        echo "claimed $T $OWNER $SM 0 0" > "$ST"; continue\n'
            '      fi\n'
        ),
        guard='cut -d\' \' -f3)" != "$OWNER"',
    ),
    # 3. read the reason counter alongside the rest of the state
    dict(
        name="reason counter read",
        find=(
            '      FIRST=$(echo "$OLD" | cut -d\' \' -f2); '
            'FIRED=$(echo "$OLD" | cut -d\' \' -f5)\n'
            '      # posted-reason reset: BOARD newer than the claim clock names the owner\n'
        ),
        repl=(
            '      FIRST=$(echo "$OLD" | cut -d\' \' -f2); '
            'FIRED=$(echo "$OLD" | cut -d\' \' -f5)\n'
            '      # One reason per claim. Unlimited resets are how this switch\n'
            '      # never fired: 9 of 12 logged events were a reason reset.\n'
            '      REASONS=$(echo "$OLD" | cut -d\' \' -f6); REASONS=${REASONS:-0}\n'
            '      # posted-reason reset: BOARD newer than the claim clock names the owner\n'
        ),
        guard="REASONS=${REASONS:-0}",
    ),
    # 4. cap the posted-reason reset at one per claim
    dict(
        name="posted-reason reset capped",
        find=(
            '      if [ "$BM" -gt "$FIRST" ] && tail -60 "$BOARD" 2>/dev/null '
            '| grep -qiF "$OWNER" \\\n'
            '        && tail -60 "$BOARD" 2>/dev/null | '
            'grep -qiE "reason|because|blocked|waiting|justif|hold|pause"; then\n'
            '        log "INACT $KEY ($OWNER): posted reason, clock reset"\n'
            '        echo "claimed $BM $OWNER $SM 0" > "$ST"; continue\n'
            '      fi\n'
        ),
        repl=(
            '      if [ "$REASONS" -lt 1 ] && [ "$BM" -gt "$FIRST" ] && '
            'tail -60 "$BOARD" 2>/dev/null | grep -qiF "$OWNER" \\\n'
            '        && tail -60 "$BOARD" 2>/dev/null | '
            'grep -qiE "reason|because|blocked|waiting|justif|hold|pause"; then\n'
            '        log "INACT $KEY ($OWNER): posted reason, clock reset '
            '(1 of 1 allowed this claim)"\n'
            '        echo "claimed $BM $OWNER $SM 0 1" > "$ST"; continue\n'
            '      fi\n'
        ),
        guard='[ "$REASONS" -lt 1 ]',
    ),
    # 5. darkness measured by writes, not by turns
    dict(
        name="darkness test uses artifact movement",
        find=(
            '      OHT=$(mt "$OH"); [ -z "$OH" ] && OHT=0\n'
            '      if [ $(( T - FIRST )) -ge 1200 ] && [ $(( T - OHT )) -ge 1200 ] '
            '&& [ "$FIRED" != "1" ]; then\n'
        ),
        repl=(
            '      OHT=$(mt "$OH"); [ -z "$OH" ] && OHT=0\n'
            '      # OAT, not OHT: last non-bookkeeping WRITE by this owner. OHT is\n'
            '      # any turn at all, which the reply to the nudge satisfies.\n'
            '      OAT=$(art_ts "$OH"); [ -z "$OAT" ] && OAT=0\n'
            '      if [ $(( T - FIRST )) -ge 1200 ] && [ $(( T - OAT )) -ge 1200 ] '
            '&& [ "$FIRED" != "1" ]; then\n'
        ),
        guard='OAT=$(art_ts "$OH")',
    ),
    # 6. an unresolvable seat name becomes a visible fault
    dict(
        name="unresolvable seat raises a fault",
        find=(
            '          log "INACT $KEY: 10min unclaimed but no eligible seat '
            'resolves (seats: $(echo "$SEATS" | cut -c1-60))"\n'
            '          echo "open $FIRST - $SM 1" > "$ST"\n'
        ),
        repl=(
            '          # A log line nobody reads is how this stayed invisible:\n'
            '          # rows naming "worker-glm-2" (not a session title) were\n'
            '          # counted as nudged while no seat was ever woken. Tell the\n'
            '          # PO, once per row, so the row gets fixed or reassigned.\n'
            '          log "INACT $KEY: 10min unclaimed but no eligible seat '
            'resolves (seats: $(echo "$SEATS" | cut -c1-60))"\n'
            '          wake "$LEDGER" "[Ledger] unroutable QUEUE row: '
            '\'$(echo "$TASK" | cut -c1-70)\' has been unclaimed 10+ min and its '
            'eligible seats ($(echo "$SEATS" | cut -c1-60)) match no agent-deck '
            'session, so no nudge can ever reach anyone. Fix the seat name or '
            'reassign. — fleet-poller" || true\n'
            '          echo "open $FIRST - $SM 1" > "$ST"\n'
        ),
        guard="unroutable QUEUE row",
    ),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    # --check is the default and exists only because the usage text above
    # promised it; without it, the documented invocation fails with
    # "unrecognized arguments". Found by running my own instructions.
    ap.add_argument("--check", action="store_true",
                    help="report only (default)")
    ap.add_argument("--apply", action="store_true", help="write in place")
    a = ap.parse_args()
    src = open(a.file).read()
    out, done, skipped, missing = src, [], [], []
    for e in EDITS:
        if e["guard"] in out:
            skipped.append(e["name"])
            continue
        if e["find"] not in out:
            missing.append(e["name"])
            continue
        out = out.replace(e["find"], e["repl"], 1)
        done.append(e["name"])
    for n in done:
        print(f"  apply   {n}")
    for n in skipped:
        print(f"  already {n}")
    for n in missing:
        print(f"  MISSING ANCHOR  {n}")
    if missing:
        print("\nRefusing to write a partial patch. The file has drifted from "
              "the version this was written against; re-anchor before applying.")
        return 2
    if a.apply and done:
        open(a.file, "w").write(out)
        print(f"\nwrote {a.file}")
    elif not a.apply:
        print("\n(--check only, nothing written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
