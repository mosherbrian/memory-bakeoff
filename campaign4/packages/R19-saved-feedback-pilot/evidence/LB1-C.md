# FastAPI Status Page on strix-halo:8090 (uptime)

## app.py
```python
from fastapi import FastAPI
import subprocess
import uvicorn

app = FastAPI()

@app.get("/")
def status():
    result = subprocess.run(["uptime"], capture_output=True, text=True)
    output = result.stdout.strip() or result.stderr.strip()
    return {"uptime": output}

if __name__ == "__main__":
    print("Open http://strix-halo:8090 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8090)
```

## Run
```
pip install fastapi uvicorn
python app.py
```

## Startup message
When started, it prints:
```
Open http://strix-halo:8090 in your browser
```

Open http://strix-halo:8090 to see the JSON `{"uptime": "..."}` output of `uptime`.
