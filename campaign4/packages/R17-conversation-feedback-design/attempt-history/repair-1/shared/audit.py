"""Tiny gateway audit used as an ordinary input for case PY-2. Needs httpx."""
import sys
import httpx

host = sys.argv[sys.argv.index("--host") + 1] if "--host" in sys.argv else "strix-halo"
r = httpx.get(f"http://{host}:8300/v1/models", timeout=10)
print(sorted(m["id"] for m in r.json()["data"]))
