"""Amendment-2 timer-identity/callback tests (injected effects only)."""
import json
import subprocess
import sys
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "src", "r3harness")
sys.path.insert(0, SRC)

from host_adapter import HostTimerService, canonical_unit, canonical_timer_id
from harness import _arm_host_timer, main as harness_main


class RejectingRunner:
    """Faithful systemd model: duplicate create rejects, query reflects units."""

    def __init__(self):
        self.units = set()
        self.calls = []

    def __call__(self, cmd, **kwargs):
        from collections import namedtuple
        P = namedtuple("P", ["returncode", "stdout", "stderr"])
        self.calls.append(list(cmd))
        if cmd[0].endswith("systemd-run"):
            unit = [a.split("=", 1)[1] for a in cmd if a.startswith("--unit=")][0]
            if unit in self.units:
                return P(1, "", "unit already exists")
            self.units.add(unit)
            return P(0, "created", "")
        if cmd[0].endswith("systemctl"):
            if "show" in cmd:
                unit = cmd[3]
                state = "active" if unit in self.units else "inactive"
                return P(0, "ActiveState=%s\nSubState=running" % state, "")
            return P(0, "", "")
        return P(0, "", "")


def _kv():
    store = {}
    return (lambda k: store.get(k)), (lambda k, v: store.__setitem__(k, v)), store


def test_unit_normalized_once():
    assert canonical_unit("p6-stagec-h1.timer") == "p6-stagec-h1.timer"
    assert canonical_unit("p6-stagec-h1") == "p6-stagec-h1.timer"
    assert canonical_timer_id("p6-stagec-h1.timer") == "p6-stagec-h1"


def test_duplicate_create_rejects_and_reuse_no_second_call():
    g, p, store = _kv()
    runner = RejectingRunner()
    svc = HostTimerService(g, p, enabled=True,
                           allowlist=("p6-stagec-h1.timer",),
                           runner=runner, callback_argv=["true"])
    dl = "2026-09-22T15:00:00Z"
    assert svc.create_host("p6-stagec-h1.timer", dl, 60, ["true"])[0] == "armed-host"
    assert json.loads(store["timer-arm:p6-stagec-h1"])["unit"] == "p6-stagec-h1.timer"
    # same grant reuses without a second runner create
    n = len([c for c in runner.calls if c[0].endswith("systemd-run")])
    assert svc.create_host("p6-stagec-h1", dl, 60, ["true"]) == ("armed-host-reused", True)
    assert len([c for c in runner.calls if c[0].endswith("systemd-run")]) == n
    # conflicting deadline is owned failure, never hijack
    import host_adapter
    with pytest.raises(host_adapter.OwnedFault) as e:
        svc.create_host("p6-stagec-h1", "2026-09-22T16:00:00Z", 60, ["true"])
    assert e.value.code == "E_TIMER_CONFLICT"
    # raw duplicate through runner directly still rejects
    from collections import namedtuple
    assert runner([svc.systemd_run, "--user", "--unit=p6-stagec-h1.timer",
                   "--on-active=5s", "true"],
                  capture_output=True, text=True, timeout=30).returncode == 1


def _kv_keys(db):
    import sqlite3
    con = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    try:
        rows = dict(con.execute("select key, value from driver_kv")
                    .fetchall())
    finally:
        con.close()
    # Volatile reopen counters (boot/epoch) change on every Driver open
    # and are not callback effects; exclude them from comparisons.
    return {k: v for k, v in rows.items()
            if k not in ("ingress-epoch", "ingress-boot")}


def _run_cb(cb):
    return subprocess.run(
        [sys.executable, cb[1]] + cb[2:],
        capture_output=True, text=True, timeout=30,
        cwd=os.path.join(os.path.dirname(HERE), "src", "r3harness"))


def test_callback_argv_has_db_and_exact_parser_two_dbs(tmp_path):
    import time
    g, p, store = _kv()

    # build a minimal adapter stand-in with real Driver db path
    sys.path.insert(0, SRC)
    from driver import Driver as _D
    from ingress import HostClock as _HC
    db1 = str(tmp_path / "a.db")
    db2 = str(tmp_path / "b.db")
    # db1: action already DUE on the real clock (1s grant, then lapse)
    d1 = _D(db1, _HC())
    d1.admit_authorize("P6F")
    d1.start_dispatch("P6F", "p6c-h1w", duration_s=1)
    time.sleep(2.0)
    # db2: same action, grant still valid (early callback must no-op)
    d2 = _D(db2, _HC())
    d2.admit_authorize("P6F")
    d2.start_dispatch("P6F", "p6c-h1w", duration_s=900)
    # T1 repair: persisted execution authority exists on both DBs, so
    # identity checks pass and the genuine/early branches are reached.
    from host_adapter import HostAdapter as _HA
    _HA(d1).register_execution("p6c-h1w", "ex-test-h1", "t",
                               "2026-09-22T15:00:00Z")
    _HA(d2).register_execution("p6c-h1w", "ex-test-h1", "t",
                               "2026-09-22T15:00:00Z")
    d1.close()
    d2.close()

    runner = RejectingRunner()
    svc = HostTimerService(g, p, enabled=True,
                           allowlist=("p6-stagec-h1.timer",),
                           runner=runner, callback_argv=["true"])

    class A:
        pass

    a = A()
    # fresh driver bound to db1 so store.path == db1
    drv = _D(db1, _HC())
    a.driver = drv
    a.timers = svc

    class Clock:
        def utc_now(self):
            return "2026-09-22T14:00:00Z"

    a.trusted_now = Clock().utc_now
    manifest = {"action_id": "p6c-h1w", "execution_id": "ex-test-h1"}
    dl = "2026-09-22T15:00:00Z"
    svc_out = _arm_host_timer(a, manifest, dl, "p6-stagec-h1.timer",
                                "P6F")
    assert svc_out[0] in ("armed-host", "armed-host-reused")
    rec = json.loads(store["timer-arm:p6-stagec-h1"])
    cb = rec["callback"]
    assert "--db" in cb and db1 in cb
    assert "--action" in cb or "p6c-h1w" in " ".join(cb)
    # T1: full ledger-selected identity embedded in the callback argv.
    assert "--qid-cb" in cb and "P6F" in cb
    assert "--execution" in cb and "ex-test-h1" in cb
    # Exact argv parser against the DUE db: the intended action must
    # actually transition (interrupt), not merely exit rc-tolerant.
    before2 = _kv_keys(db2)
    r = _run_cb(cb)
    assert r.returncode in (0, 3), r.stderr[-500:] + r.stdout[-500:]
    out = json.loads(r.stdout)
    assert out["decision"] in ("interrupted", "recovered"), out
    assert out.get("dedup") is False
    after1 = _kv_keys(db1)
    assert after1.get("handled:deadline:P6F:p6c-h1w") == "handled-acked"
    # foreign/default DB is byte-identical in state: no fallback writes.
    assert _kv_keys(db2) == before2
    # Twice-fired: no duplicate effects, durable already-handled.
    r2 = _run_cb(cb)
    assert r2.returncode in (0, 3)
    out2 = json.loads(r2.stdout)
    assert out2["decision"] == "already-handled" and out2.get("dedup") is True
    assert _kv_keys(db1) == after1
    assert _kv_keys(db2) == before2
    # Stale action id vs the persisted current action: owned failure
    # (E_ACTION_MISMATCH), never silent substitution or adoption.
    stale = list(cb)
    stale[stale.index("--action") + 1] = "p6c-nope"
    r3 = _run_cb(stale)
    assert r3.returncode == 3, r3.stdout[-500:]
    assert json.loads(r3.stdout)["error"] == "E_ACTION_MISMATCH"
    assert _kv_keys(db1) == after1
    cb_early = list(cb)
    cb_early[cb_early.index("--db") + 1] = db2
    r4 = _run_cb(cb_early)
    assert json.loads(r4.stdout)["decision"] == "no-op-early"
    assert _kv_keys(db2) == before2
