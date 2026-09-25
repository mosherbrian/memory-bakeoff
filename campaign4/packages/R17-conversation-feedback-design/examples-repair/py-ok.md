Save as `health.py`, then run `python health.py`.
```python
import json, urllib.request
print(json.load(urllib.request.urlopen("http://strix-halo:8300/health")))
```
