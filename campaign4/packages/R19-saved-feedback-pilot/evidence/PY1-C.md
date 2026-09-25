# Inference Gateway Check — strix-halo:8300

## Script

Save as `check_gateway.py`:

```python
#!/usr/bin/env python3
"""Check inference gateway on strix-halo port 8300."""
import json
import sys
import urllib.request

HOST = "strix-halo"
PORT = 8300
TIMEOUT = 10

def get(path):
    url = f"http://{HOST}:{PORT}{path}"
    with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
        return r.status, r.read().decode()

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    base = f"http://{host}:{PORT}"
    print(f"Checking {base} ...")

    # 1. /health
    try:
        with urllib.request.urlopen(f"{base}/health", timeout=TIMEOUT) as r:
            body = r.read().decode()
            print(f"/health -> HTTP {r.status}: {body}")
    except Exception as e:
        print(f"/health FAILED: {e}")
        sys.exit(1)

    # 2. /v1/models
    try:
        with urllib.request.urlopen(f"{base}/v1/models", timeout=TIMEOUT) as r:
            data = json.loads(r.read().decode())
        models = data.get("data", data)
        print("Model IDs:")
        if isinstance(models, list):
            for m in models:
                print(" -", m.get("id", m) if isinstance(m, dict) else m)
        else:
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"/v1/models FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Run command

```bash
python3 check_gateway.py
```

Optional: check a different host (script defaults to `strix-halo`):

```bash
python3 check_gateway.py strix-halo
```

Requires only Python 3 stdlib, no extra packages.
