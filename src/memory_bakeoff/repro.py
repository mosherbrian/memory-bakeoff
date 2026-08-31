from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
from typing import Iterable

from memory_bakeoff.corpus import build_corpus


PACKAGE_NAMES = (
    "memory-bakeoff",
    "numpy",
    "scikit-learn",
    "pandas",
    "requests",
    "pytest",
    "matplotlib",
    "mem0ai",
    "membukkit",
    "hindsight-client",
)

SAFE_ENV_KEYS = (
    "AGENTMEMORY_URL",
    "AGENTMEMORY_PROJECT",
    "CLAUDE_MEM_URL",
    "CLAUDE_MEM_WORKER_PORT",
    "CLAUDE_MEM_PROJECT",
    "HINDSIGHT_URL",
    "HINDSIGHT_BANK",
    "HINDSIGHT_API_LLM_PROVIDER",
    "HINDSIGHT_RAW_LLM_PROVIDER",
    "MEMBUKKIT_LLM",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "ANTHROPIC_MODEL",
    "CHATGPT_SIDECAR_DIR",
)

# Never add API keys, bearer secrets, passwords, or auth files here.


def _version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _hash_bytes(parts: Iterable[bytes]) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update(part)
    return h.hexdigest()


def corpus_sha256() -> str:
    records, cases = build_corpus()
    payload = {
        "records": [r.to_dict() for r in records],
        "cases": [c.to_dict() for c in cases],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def source_tree_sha256(root: str | Path = ".") -> str:
    root = Path(root).resolve()
    selected: list[Path] = []
    for rel in ("src", "tests", "scripts", "research"):
        base = root / rel
        if base.exists():
            selected.extend(p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    for rel in ("pyproject.toml", "README.md", "EXPERIMENT_PLAN.md", "RUN_EXTERNAL.md", "BUILD_MANIFEST.md"):
        p = root / rel
        if p.exists():
            selected.append(p)
    selected = sorted(set(selected), key=lambda p: p.relative_to(root).as_posix())
    parts: list[bytes] = []
    for path in selected:
        rel = path.relative_to(root).as_posix().encode("utf-8")
        parts.extend((rel, b"\0", path.read_bytes(), b"\0"))
    return _hash_bytes(parts)


def capture_manifest(root: str | Path = ".", *, llm_label: str | None = None) -> dict:
    root = Path(root).resolve()
    records, cases = build_corpus()
    return {
        "schema_version": 1,
        "python": {
            "version": sys.version,
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "packages": {name: _version(name) for name in PACKAGE_NAMES},
        "benchmark": {
            "records": len(records),
            "queries": len(cases),
            "corpus_sha256": corpus_sha256(),
            "source_tree_sha256": source_tree_sha256(root),
        },
        "llm_label": llm_label,
        "environment": {key: os.environ[key] for key in SAFE_ENV_KEYS if key in os.environ},
        "notes": [
            "Environment capture intentionally excludes API keys, bearer secrets, passwords, and auth material.",
            "External engine version/commit must also be captured on the host that actually runs that engine.",
        ],
    }


def write_manifest(path: str | Path, root: str | Path = ".", *, llm_label: str | None = None) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(capture_manifest(root, llm_label=llm_label), indent=2, ensure_ascii=False) + "\n")
    return path
