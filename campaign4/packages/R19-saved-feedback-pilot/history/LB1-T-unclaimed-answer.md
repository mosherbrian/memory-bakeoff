# Status page on strix-halo:8090

Minimal FastAPI app showing `uptime` output.

`app.py`:

```python
#!/usr/bin/env python
import subprocess
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def status():
    out = subprocess.run(["uptime"], capture_output=True, text=True)
    return {"uptime": out.stdout.strip()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
```

Run it:

```
pip install fastapi uvicorn
python app.py
```

Startup message:

```
Serving status page on http://strix-halo:8090 — open that from your desktop or phone.
```

Notes:
- Binds to `0.0.0.0` so it is reachable off-machine; open `http://strix-halo:8090` (not a loopback address).
- Uses `python` / `pip` so it works on your Windows machine.
