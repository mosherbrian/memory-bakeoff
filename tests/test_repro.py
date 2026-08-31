from __future__ import annotations

from pathlib import Path

from memory_bakeoff.repro import capture_manifest, corpus_sha256, source_tree_sha256


def test_corpus_hash_is_stable():
    assert corpus_sha256() == corpus_sha256()
    assert len(corpus_sha256()) == 64


def test_manifest_omits_secrets(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENAI_API_KEY", "secret-value")
    monkeypatch.setenv("AGENTMEMORY_SECRET", "also-secret")
    monkeypatch.setenv("OPENAI_MODEL", "reader-model")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "x.py").write_text("x=1\n")
    m = capture_manifest(tmp_path, llm_label="test-reader")
    assert m["environment"]["OPENAI_MODEL"] == "reader-model"
    assert "OPENAI_API_KEY" not in m["environment"]
    assert "AGENTMEMORY_SECRET" not in m["environment"]
    assert m["llm_label"] == "test-reader"


def test_source_hash_changes_when_source_changes(tmp_path: Path):
    (tmp_path / "src").mkdir()
    p = tmp_path / "src" / "x.py"
    p.write_text("x=1\n")
    a = source_tree_sha256(tmp_path)
    p.write_text("x=2\n")
    b = source_tree_sha256(tmp_path)
    assert a != b
