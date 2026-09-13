"""Unit receipts for scripts/team_sync.py — the mirror discipline tool.

Locks: one-way direction (canonical root -> lane, never the reverse),
MATCH/DRIFT/MISSING classification, receipted pulls, manifest parsing,
and the exit-code contract (0 = all match, 1 = drift found, 2 = no
manifest).
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.team_sync import check, main, mirror_names, pull  # noqa: E402


@pytest.fixture()
def fleet(tmp_path):
    root, lane = tmp_path / "root-team", tmp_path / "lane-team"
    root.mkdir()
    lane.mkdir()
    (root / "CHARTER.md").write_text("canonical v1\n", encoding="utf-8")
    (root / "LOG.md").write_text("entry one\n", encoding="utf-8")
    (lane / "CHARTER.md").write_text("canonical v1\n", encoding="utf-8")
    (lane / "LOG.md").write_text("stale mirror\n", encoding="utf-8")
    manifest = tmp_path / "MIRRORS.txt"
    manifest.write_text("# canonical mirrors\nCHARTER.md\nLOG.md\n", encoding="utf-8")
    receipt_log = tmp_path / "sync-receipt.log"
    return root, lane, manifest, receipt_log


def _cli(argv):
    sys.argv = ["team_sync.py", *argv]
    return main()


def test_mirror_names_ignores_comments_and_blank_lines(tmp_path):
    manifest = tmp_path / "MIRRORS.txt"
    manifest.write_text("# comment\n\n  A.md  \nB.md # trailing\n", encoding="utf-8")
    assert mirror_names(manifest) == ["A.md", "B.md"]


def test_check_classifies_match_drift_and_missing(fleet):
    root, lane, manifest, _ = fleet
    rows = {r["file"]: r["status"] for r in check(root, lane, mirror_names(manifest))}
    assert rows["CHARTER.md"] == "MATCH"
    assert rows["LOG.md"] == "DRIFT"
    (root / "NEW.md").write_text("new canonical\n", encoding="utf-8")
    manifest.write_text(manifest.read_text() + "NEW.md\n", encoding="utf-8")
    rows = {r["file"]: r["status"] for r in check(root, lane, mirror_names(manifest))}
    assert rows["NEW.md"] == "LANE-MISSING"


def test_check_never_classifies_a_root_missing_file_as_pullable(fleet):
    root, lane, manifest, _ = fleet
    manifest.write_text("GHOST.md\n", encoding="utf-8")
    assert check(root, lane, mirror_names(manifest)) == [
        {"file": "GHOST.md", "status": "ROOT-MISSING"}
    ]


def test_pull_updates_lane_and_appends_a_receipt_but_never_touches_root(fleet):
    root, lane, manifest, receipt_log = fleet
    pulled = pull(root, lane, mirror_names(manifest), receipt_log)
    assert [p["file"] for p in pulled] == ["LOG.md"]  # CHARTER already matched
    assert (lane / "LOG.md").read_text(encoding="utf-8") == "entry one\n"
    receipts = [json.loads(line) for line in receipt_log.read_text(encoding="utf-8").splitlines()]
    assert receipts[0]["file"] == "LOG.md"
    assert receipts[0]["lane_sha_before"] != receipts[0]["lane_sha_after"]
    assert receipts[0]["root_sha"] == receipts[0]["lane_sha_after"]
    # a second pull repairs lane tampering; root bytes are never rewritten
    (lane / "CHARTER.md").write_text("lane tampering\n", encoding="utf-8")
    pull(root, lane, mirror_names(manifest), receipt_log)
    assert (lane / "CHARTER.md").read_text(encoding="utf-8") == "canonical v1\n"
    assert (root / "CHARTER.md").read_text(encoding="utf-8") == "canonical v1\n"
    assert len(receipt_log.read_text(encoding="utf-8").splitlines()) == 2


def test_pull_is_idempotent_when_everything_matches(fleet):
    root, lane, manifest, receipt_log = fleet
    pull(root, lane, mirror_names(manifest), receipt_log)
    assert pull(root, lane, mirror_names(manifest), receipt_log) == []
    assert receipt_log.read_text(encoding="utf-8").count("\n") == 1


def test_cli_exit_codes(fleet, tmp_path):
    root, lane, manifest, receipt_log = fleet
    base = ["--root", str(root), "--lane", str(lane),
            "--manifest", str(manifest), "--receipt-log", str(receipt_log)]
    assert _cli(["check", *base]) == 1  # LOG.md drifted
    assert _cli(["pull", *base]) == 0
    assert _cli(["check", *base]) == 0  # all match now
    assert _cli(["check", *base[:2], "--manifest", str(tmp_path / "ABSENT.txt")]) == 2  # no manifest
