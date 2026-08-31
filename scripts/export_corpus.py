from __future__ import annotations
import json
from pathlib import Path
from memory_bakeoff.corpus import build_corpus

records, cases = build_corpus()
out = {
    "records": [r.to_dict() for r in records],
    "queries": [q.to_dict() for q in cases],
}
path = Path("results/corpus.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(out, indent=2))
print(path)
