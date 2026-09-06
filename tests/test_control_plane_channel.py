"""control-plane/PENDING.json is the ONLY trigger. So it must never lie.

The webhook it replaces failed silently: a mis-titled doorbell meant the control
plane was never called for 6h47m and nothing checked whether the request had been
delivered. A scheduled task reading a file cannot be mis-addressed - but it can
be misled, so the file's invariants are the new attack surface.
"""
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PENDING = ROOT / "control-plane/PENDING.json"
PROMPT = ROOT / "control-plane/SCHEDULED_TASK_PROMPT.md"
HOOK = ROOT / ".githooks/pre-commit"


def load():
    return json.loads(PENDING.read_text())


def test_the_channel_exists_and_is_tracked():
    assert PENDING.exists()
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch",
                              "control-plane/PENDING.json"],
                             cwd=ROOT, capture_output=True).returncode == 0
    assert tracked, "an untracked trigger is invisible to a scheduled task"


def test_it_is_readable_on_origin_main():
    """A task reads it from GitHub, not from this working copy."""
    r = subprocess.run(["git", "show", "origin/main:control-plane/PENDING.json"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, "not published; a scheduled task would see nothing"
    json.loads(r.stdout)


def test_status_is_one_of_two_words():
    assert load()["status"] in ("awaiting", "answered")


def test_a_pending_request_pins_a_full_commit():
    d = load()
    assert len(d["source_commit"]) == 40
    assert d["requested_generation"] == d["source_generation"] + 1


def test_the_pin_is_a_real_commit():
    d = load()
    r = subprocess.run(["git", "cat-file", "-e", d["source_commit"] + "^{commit}"],
                       cwd=ROOT, capture_output=True)
    assert r.returncode == 0, f"{d['source_commit']} is not a commit in this repo"


def test_awaiting_requires_the_pin_to_be_origin_main():
    """The stale-pin failure: main advancing while a request is outstanding.

    It happened at Gen107->108 and three more times on 2026-09-06, once ten
    minutes after I wrote that I would stop. If this file says awaiting, the
    commit it names must still be the published tip.
    """
    d = load()
    if d["status"] != "awaiting":
        pytest.skip("no request outstanding")
    tip = subprocess.run(["git", "rev-parse", "origin/main"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    assert d["source_commit"] == tip, (
        f"PENDING pins {d['source_commit'][:12]} but origin/main is {tip[:12]}; "
        "the control plane is answering a commit that no longer exists as the tip")


def test_the_freeze_hook_exists_and_is_wired():
    assert HOOK.exists() and HOOK.stat().st_mode & 0o111, "hook not executable"
    configured = subprocess.run(["git", "config", "core.hooksPath"], cwd=ROOT,
                                capture_output=True, text=True).stdout.strip()
    assert configured == ".githooks", f"hooksPath is {configured!r}, hook is inert"


def test_the_freeze_can_always_release_itself():
    """A guard with no exit is one that gets bypassed wholesale."""
    src = HOOK.read_text()
    assert "control-plane/PENDING.json" in src
    assert "--no-verify" in src, "an override must exist and be named"


def test_the_scheduled_prompt_is_self_contained():
    """Five chats run this with no other context. It must decide alone."""
    p = PROMPT.read_text()
    assert "PENDING.json" in p and "main" in p
    assert "STOP" in p, "the common case is doing nothing; it must say so"
    assert "already carries an instruction" in p, "no-op on an answered request"
    assert "verbatim" in p or "copied verbatim" in p, "the commit pin must be exact"
    for field in ("generation:", "source_generation:", "source_commit:", "status:"):
        assert field in p, f"the required header field {field} is not specified"


def test_the_prompt_never_asks_the_task_to_trust_the_implementer():
    p = PROMPT.read_text()
    assert "from what is in the repository" in p or "rather than from memory" in p
