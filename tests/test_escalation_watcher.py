"""The watcher replaces a judgement with a clock, so the clock must be tested.

Every guard ships its positive AND negative control. A guard that fires on
nothing reads as passing, which is worse than absent - four of this project's own
tests were wrong that way in a single afternoon.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WATCHER = ROOT / "scripts" / "await-instruction"
DOORBELL = ROOT / "scripts" / "doorbell"
SRC = WATCHER.read_text()

REAL_MISTITLED_PR = "15"   # "Doorbell: Gen115 complete..." - the actual failure
GEN115_SHA = "90eb9b680bbe1ebf47f1e8e886d1958d08d8cd2b"


def run(args, timeout=240):
    return subprocess.run(["bash", str(WATCHER), *args], cwd=ROOT,
                          capture_output=True, text=True, timeout=timeout)


def test_watcher_exists_and_parses():
    assert WATCHER.exists()
    assert subprocess.run(["bash", "-n", str(WATCHER)]).returncode == 0


def test_missing_arguments_refuse():
    assert run([], timeout=60).returncode != 0


def test_it_checks_the_REQUEST_channel_not_only_the_answer():
    """Nothing checked the request channel for 6h47m. That is the whole point.

    The channel changed on 2026-09-06 when the PR trigger was disabled: a
    well-formed PR now summons nothing, so checking its title would be theatre.
    The request now lives in control-plane/PENDING.json, read on a schedule.
    """
    assert "PENDING.json" in SRC, "the watcher must read the state file"
    assert "REQUEST NOT VISIBLE" in SRC and "REQUEST STALE" in SRC
    assert "git show origin/main:control-plane/PENDING.json" in SRC
    assert "gh pr view" not in SRC, "the inert PR check must be gone, not dormant"


def test_positive_control_a_stale_pin_is_caught():
    """main advancing while a request is outstanding is the Gen107->108 failure,
    and it happened again today. A watch expecting a commit the state file does
    not pin must refuse rather than wait."""
    r = run(["117", "16", "0" * 40])
    assert r.returncode == 2, r.stdout + r.stderr
    assert "REQUEST STALE" in r.stdout or "REQUEST NOT VISIBLE" in r.stdout


def test_positive_control_no_pending_request_is_caught():
    """If nothing is asking, waiting is not 'blocked' - it is nothing happening."""
    import json as _json, subprocess as _sp
    pending = _json.loads(_sp.run(
        ["git", "show", "origin/main:control-plane/PENDING.json"],
        cwd=ROOT, capture_output=True, text=True).stdout or "{}")
    assert "status" in pending, "PENDING.json must exist on origin/main to be a channel"
    assert pending["status"] in ("awaiting", "answered")
    assert len(pending.get("source_commit", "")) == 40


def test_negative_control_a_current_pin_is_not_flagged_stale():
    """If it flagged everything, exit 2 would carry no information.

    This control deliberately does NOT depend on the live control-plane mailbox.
    An earlier version asserted that a specific generation verified, and it
    rotted the moment the control plane answered the next question - a test
    pinned to external mutable state fails for reasons that are not defects.
    """
    import subprocess as _sp
    # The watcher's staleness rule, applied directly rather than by running a
    # 5-minute poll loop. NOT strict equality against the tip: recording the
    # request is itself a commit, so that invariant is broken by the act of
    # satisfying it. Bookkeeping commits do not change what the control plane is
    # being asked about; anything else does.
    r = _sp.run(["scripts/pin-is-current"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    # And the rule itself must be present, so this control is testing something.
    # Both staleness questions must be present. Collapsing them into one -
    # keeping only the content check - made a bogus expected SHA loop instead of
    # failing, and the positive control caught it.
    assert "REQUEST STALE" in SRC
    assert 'PSHA" != "$SHA' in SRC, "must check the pin matches THIS watch"
    assert "pin-is-current" in SRC, "must also check content has not moved"


def test_the_rungs_are_fixed_intervals_not_inference():
    """A 'smart' stall detector re-creates the failure it is meant to prevent."""
    assert re.search(r"RUNG3=900\b", SRC), "agent rung must be a fixed 15 minutes"
    assert re.search(r"RUNG4=2700\b", SRC), "human rung must be a fixed 45 minutes"
    assert "sleep 300" in SRC


def test_each_rung_carries_the_one_permitted_action():
    """A wake-up that does not say what to do reproduces 'blocked'."""
    assert "open the Work chat" in SRC and "CONTROL-PLANE RETRY 1" in SRC
    assert "Send Brian on Signal" in SRC
    assert "--since" in SRC, "relaunching must not reset the clock"


def test_ringing_arms_the_watcher_in_the_same_call():
    """There must be no second decision about whether to watch."""
    d = DOORBELL.read_text()
    assert "await-instruction" in d
    assert "systemd-run" in d
    i_post = d.index("urlopen(request)")
    assert d.index("await-instruction") > i_post, "arm AFTER the ring succeeds"


def test_doorbell_verifies_its_own_title_back_from_github():
    """A declared title becomes an observed one."""
    d = DOORBELL.read_text()
    assert "RANG BUT MALFORMED" in d
    assert 'title_back.startswith("BAKEOFF_HANDOFF")' in d
