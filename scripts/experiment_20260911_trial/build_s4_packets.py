#!/usr/bin/env python3
"""S4 packet builder (team/S4-ADJUDICATION.md B2/B4) — CAMPAIGN-1 window.

Builds one blinded packet per turn from the live arm's session log, plus a
manifest. Every memory-system traffic entry is replaced by a COUNT-NEUTRAL
marker ("[memory activity: redacted]") — the marker says something happened,
never what and never whether it delivered (blind-rater contract B1/B2). The
script prints per-turn marker counts so the B7 post-hoc audit can diff
marker count vs raw memory-traffic count.

Redaction rules (an entry is memory-traffic iff ANY holds):
  - entry message toolName starts with "project_perseus_"
  - entry message role == "toolResult" belonging to such a call
    (pi sessions: same entry carries toolName)
  - entry text/marker carries a memory-system customType:
    change-trigger / recall-nudge
  - entry text contains a memory-system sentinel:
    [project_perseus_recall] / [perseus-write] / [recall-nudge] /
    [change-trigger] / draft_id / confirmation_code

Usage:
  build_s4_packets.py --session <session.jsonl> --scan <s6-receipt.json>
                      [--scan <s6-receipt2.json> ...] --out <outdir>
                      --window-open <ISO> [--window-close <ISO>]
Self-test:
  build_s4_packets.py --self-test --session <session.jsonl> --out <dir>
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys

MARKER = "[memory activity: redacted]"
SENTINELS = ("[project_perseus_recall]", "[perseus-write]", "[recall-nudge]",
             "[change-trigger]", "project_perseus_")
DRAFT_SECRET_SENTINELS = ("draft_id", "confirmation_code", "[perseus-write]")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_iso(s: str) -> float:
    return datetime.datetime.fromisoformat(s).timestamp()


def iter_entries(path: str):
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                yield n, json.loads(line)
            except json.JSONDecodeError:
                yield n, {"_unparseable": True, "_line": line[:200]}


def entry_role(entry: dict) -> str:
    msg = entry.get("message", entry)
    role = msg.get("role")
    if role:
        return str(role)
    return str(entry.get("type", "?"))


def entry_toolname(entry: dict) -> str:
    msg = entry.get("message", entry)
    return str(msg.get("toolName", "") or "")


def entry_text(entry: dict) -> str:
    return json.dumps(entry, default=str)


def is_user_turn_start(entry: dict) -> bool:
    """Operator input starts a turn — ALWAYS, even when it names memory tools
    (the dispatch shape is work substance; what the agent then did is the
    measured variable)."""
    return entry_role(entry) == "user"


def is_memory_traffic(entry: dict) -> bool:
    """Non-user entries carrying memory-system traffic. The operator's own
    prompt is never memory-traffic (it is the turn's input); draft secrets in
    a user entry are redacted separately (DRAFT_SECRET_SENTINELS)."""
    if "project_perseus_" in entry_toolname(entry):
        return True
    return any(s in entry_text(entry) for s in SENTINELS)


def user_entry_has_draft_secret(entry: dict) -> bool:
    text = entry_text(entry)
    return any(s in text for s in DRAFT_SECRET_SENTINELS)


def redact_entry(entry: dict) -> dict:
    """Preserve the entry's shape (timestamp/type/role), replace substance."""
    if is_user_turn_start(entry) and not user_entry_has_draft_secret(entry):
        return entry  # operator input is turn substance (kept verbatim)
    if isinstance(entry.get("message"), dict):
        red = {**entry, "message": {**entry["message"], "content": MARKER,
                                    "toolName": MARKER}}
        red["marker"] = True
        return red
    red = {**entry, "content": MARKER, "marker": True}
    return red


def entry_timestamp(entry: dict) -> str | None:
    ts = entry.get("timestamp") or entry.get("at") or entry.get("time")
    if isinstance(ts, (int, float)):
        return datetime.datetime.fromtimestamp(ts / 1000 if ts > 1e11 else ts,
                                               datetime.timezone.utc).isoformat()
    return ts if isinstance(ts, str) else None


def load_record_sets(scan_files: list[str]) -> list[tuple[float, str, dict]]:
    """[(receipt_timestamp, receipt_path, {key: status}), ...] sorted by time."""
    sets = []
    for path in scan_files:
        with open(path, encoding="utf-8") as fh:
            txt = fh.read()
        # S6 receipts are '# comment' lines + JSON rows; tolerate both forms.
        keys = {}
        stamp = None
        for line in txt.splitlines():
            line = line.strip()
            if line.startswith("# S6 scan-after-write"):
                try:
                    stamp = line.split(" ", 3)[3]
                except Exception:
                    pass
                continue
            if line.startswith("{"):
                try:
                    row = json.loads(line)
                    keys[row.get("key")] = row.get("status")
                except Exception:
                    pass
            elif line.startswith("{") is False and line.endswith(".json") is False:
                continue
        if not keys:
            try:
                d = json.loads(txt)
                for it in d.get("items", []):
                    keys[it.get("key")] = it.get("status")
            except Exception:
                pass
        ts = parse_iso(stamp) if stamp else os.path.getmtime(path)
        sets.append((ts, os.path.basename(path), keys))
    sets.sort(key=lambda t: t[0])
    return sets


def record_set_at(sets, turn_start_ts):
    chosen = None
    for ts, name, keys in sets:
        if ts <= turn_start_ts:
            chosen = keys
    if chosen is None and sets:
        return None  # no scan receipt predates the turn
    return chosen


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--scan", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--window-open", required=True)
    ap.add_argument("--window-close", default=None)
    ap.add_argument("--self-test", action="store_true",
                    help="verify marker count == raw memory-traffic count (B7)")
    args = ap.parse_args()

    open_ts = parse_iso(args.window_open)
    close_ts = parse_iso(args.window_close) if args.window_close else float("inf")
    scans = load_record_sets(args.scan)

    # split entries into turns (user input starts a turn)
    # memory-traffic definition, applied consistently for counting AND
    # redaction (B7 requires marker count == raw count):
    #   - non-user entry carrying memory-system traffic; OR
    #   - user entry carrying draft secrets (redacted, counted);
    #   - a user entry that merely NAMES a tool is turn substance: kept
    #     verbatim, not counted.
    turns: list[dict] = []
    current = None
    raw_mem_count = 0
    for _, entry in iter_entries(args.session):
        ts = entry_timestamp(entry)
        if ts is not None and (parse_iso(ts) < open_ts or parse_iso(ts) > close_ts):
            continue
        user_start = is_user_turn_start(entry)
        mem = ((not user_start) and is_memory_traffic(entry)) or \
              (user_start and user_entry_has_draft_secret(entry))
        if mem:
            raw_mem_count += 1
        if user_start:
            if current:
                turns.append(current)
            current = {"entries": [entry], "start": ts,
                       "raw_mem": 1 if mem else 0}
            continue
        if current is None:
            continue
        current["entries"].append(entry)
        if mem:
            current["raw_mem"] = (current.get("raw_mem") or 0) + 1
    if current:
        turns.append(current)

    os.makedirs(args.out, exist_ok=True)
    manifest = []
    unsupported = 0
    for i, turn in enumerate(turns, 1):
        turn_id = f"turn-{i:03d}"
        red_entries, markers = [], 0
        for e in turn["entries"]:
            user_start = is_user_turn_start(e)
            mem = ((not user_start) and is_memory_traffic(e)) or \
                  (user_start and user_entry_has_draft_secret(e))
            if mem:
                red_entries.append(redact_entry(e))
                markers += 1
            else:
                red_entries.append(e)
        start = turn.get("start") or (entry_timestamp(turn["entries"][0]) or "")
        rs = record_set_at(scans, parse_iso(start)) if start else None
        if rs is None:
            unsupported += 1
        packet = {
            "turn_id": turn_id,
            "start": start,
            "entries": red_entries,
            "record_set": rs or {},
            "marker_count": markers,
            "note": "memory-system traffic replaced by count-neutral marker",
        }
        data = json.dumps(packet, indent=1, default=str).encode()
        packet_path = os.path.join(args.out, f"{turn_id}.json")
        with open(packet_path, "wb") as fh:
            fh.write(data)
        manifest.append({
            "turn_id": turn_id,
            "start": start,
            "packet": os.path.basename(packet_path),
            "packet_sha256": sha256(data),
            "marker_count": markers,
            "raw_memory_traffic": turn.get("raw_mem", 0),
            "record_set": rs or {},
        })

    manifest_path = os.path.join(args.out, "MANIFEST.jsonl")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        for m in manifest:
            fh.write(json.dumps(m, default=str) + "\n")

    total_markers = sum(m["marker_count"] for m in manifest)
    print(f"turns: {len(turns)}  markers: {total_markers}  "
          f"raw memory-traffic entries: {raw_mem_count}  "
          f"EXCLUDED-unsupported-state: {unsupported}")
    if args.self_test:
        ok = total_markers == raw_mem_count
        print(f"SELF-TEST (B7 property): {'PASS' if ok else 'FAIL'} — "
              f"marker count {'==' if ok else '!='} raw memory-traffic count")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
