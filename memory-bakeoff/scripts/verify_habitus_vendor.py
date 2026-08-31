from pathlib import Path
import hashlib
import subprocess
import sys

EXPECTED = {
    "embeddings.py": "d6ab2d5920d42462b267c0b05d374704f7ad81cf",
    "types.py": "d3b07d403e89bbb580658d3ea369f9f426177697",
    "context.py": "e0baf1484e02daaa668f9435d0a9982c6d5765c0",
    "surface.py": "7ce52ada22090538302fad0bcecdc998dfbcf222",
    "working_memory.py": "84d9cff079c6de3758cbee9382f3185266def5c0",
    "store.py": "dde73a57fe33fd6fa9ec81c585af900f71466620",
    "graph.py": "9540fd5b0ad5d4078ece2ea9c86a3bd3e469c8ed",
    "retrieval.py": "85384c37b697fdf78db71bff51c73552eed0a399",
    "pipeline.py": "165e2c8b4e4e9a37913ad43fa0acee408fb3723a",
}
ROOT = Path(__file__).resolve().parents[1] / "vendor" / "habitus" / "src" / "habitus_ai"
failed = False
for name, expected in EXPECTED.items():
    path = ROOT / name
    actual = subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()
    ok = actual == expected
    print(f"{'OK' if ok else 'MISMATCH'} {name}: {actual}")
    failed |= not ok
raise SystemExit(1 if failed else 0)
