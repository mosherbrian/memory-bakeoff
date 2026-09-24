# P13 receiver binding evaluator (pure; sourced by the driver, unit-tested). receiver_has RECORD KEY NEEDLE:
# rc 0 only if RECORD is an absolute path and has a JSON line whose "key" is exactly KEY and whose "text"
# contains NEEDLE. Independent of HOME and of the runtime instance id.
receiver_has() { [ "${1#/}" != "$1" ] || return 1; python3 - "$1" "$2" "$3" <<'PY'
import json, sys
path, key, needle = sys.argv[1:4]
try: rows = [json.loads(l) for l in open(path) if l.strip()]
except Exception: sys.exit(1)
sys.exit(0 if any(r.get("key") == key and needle in r.get("text", "") for r in rows) else 1)
PY
}
