Save as `health.py` and run it (use python, not python3, on Windows):
```
#!/usr/bin/env python
import json, urllib.request
print(json.load(urllib.request.urlopen("http://strix-halo:8300/health")))
```
```
python health.py
```
