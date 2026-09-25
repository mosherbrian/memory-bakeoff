# Run audit.py against gateway on strix-halo

These steps install the one dependency (`httpx`) and run the audit.

## 1. Install dependency

```bash
pip install httpx
```

## 2. Run the audit

From this folder (`/tmp/r19-feedback-arms/PY2-C`):

```bash
python audit.py --host strix-halo
```

This queries `http://strix-halo:8300/v1/models` with a 10s timeout and prints the sorted model IDs.

## Notes

- No other packages are required; the script uses only the standard library plus `httpx`.
- Default host is `strix-halo` if `--host` is omitted, so `python audit.py` is equivalent.
