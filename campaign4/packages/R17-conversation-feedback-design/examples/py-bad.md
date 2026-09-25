```
#!/usr/bin/env python3
import json, urllib.request
print(json.load(urllib.request.urlopen("http://strix-halo:8300/health")))
```
```
python3 health.py
```
