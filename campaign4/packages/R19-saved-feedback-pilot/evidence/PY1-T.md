# Inference gateway check (strix-halo:8300)

Run on any machine on the same network as `strix-halo`.

## Script: `check_gateway.py`

```python
#!/usr/bin/env python
"""Check inference gateway on strix-halo:8300."""
import json
import urllib.request

BASE = "http://strix-halo:8300"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.loads(r.read().decode())

health = get("/health")
print("health:", health)

models = get("/v1/models")
ids = [m.get("id") for m in models.get("data", [])]
print("model ids:")
for mid in ids:
    print(" -", mid)
```

Save the above as `check_gateway.py`.

## Command to run it

```sh
python check_gateway.py
```
