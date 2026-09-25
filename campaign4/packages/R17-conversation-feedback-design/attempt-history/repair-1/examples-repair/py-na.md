```bash
curl -s http://strix-halo:8300/health && curl -s http://strix-halo:8300/v1/models | jq -r '.data[].id'
```
