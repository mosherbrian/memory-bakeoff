import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "RESULTS.md"
LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
REQUIRED = ("Perseus", "Habitus", "MemBukkit", "Mem0", "Hindsight", "agentmemory", "Claude-Mem", "Graphiti", "observational-memory", "ROUND1_FINAL_READOUT.md")


def index_links():
    for target in LINK.findall(INDEX.read_text()):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        yield target.split("#", 1)[0]


def test_every_local_path_in_the_evidence_index_exists():
    missing = sorted({target for target in index_links() if not (ROOT / target).exists()})
    assert not missing, f"evidence index links to missing paths: {missing}"


def test_evidence_index_covers_every_major_evaluated_profile():
    text = INDEX.read_text()
    assert [name for name in REQUIRED if name not in text] == []


def test_entry_points_route_to_the_evidence_index():
    for name in ("README.md", "STATUS_AND_FINDINGS.md"):
        assert "RESULTS.md" in (ROOT / name).read_text(), f"{name} does not link the evidence index"
