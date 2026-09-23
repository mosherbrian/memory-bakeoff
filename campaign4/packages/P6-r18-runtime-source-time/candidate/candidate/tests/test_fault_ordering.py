"""P6-r8 causal-race regression: corrupt-after-worker is a post-COMMIT
fault. The producer publishes artifact -> claim -> end sequentially, so
a tamper applied on mere claim observation can land between publication
and the worker handoff's artifact recompute, failing the worker handoff
the fault was meant to follow (expect_open then sees latency but zero
worker success rows -> INCOMPLETE). The gate must wait for the durable
handoff-done commit record, which is written only after claim validation
+ artifact recompute + ledger drive. Injected effects only."""
import json
import os
import sqlite3
import sys

import pytest

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, SRC)

import case_entry as ce


def make_gate_root(tmp_path, committed):
    root = str(tmp_path)
    art = os.path.join(root, "art")
    os.makedirs(art, exist_ok=True)
    with open(os.path.join(art, "w-out.txt"), "wb") as fh:
        fh.write(b"pinned-worker-bytes")
    db_path = os.path.join(root, "fixture.db")
    con = sqlite3.connect(db_path)
    con.execute("create table driver_kv(key text primary key, value text)")
    if committed:
        con.execute(
            "insert into driver_kv(key,value) values(?,?)",
            ("handoff-done:p6c-w:ex-1", '{"next":"verifier-dispatch"}'))
    con.commit()
    con.close()
    cdirs = {"art": art}
    manifest = {"action_id": "p6c-w", "execution_id": "ex-1"}
    intervention = {"control": "corrupt-after-worker", "case": "c",
                    "induced": True}
    claim = {"outcome": "completed"}
    return cdirs, manifest, db_path, intervention, claim


def test_tamper_waits_for_commit(tmp_path):
    # Claim observed but no durable commit: fault must wait (None),
    # artifact bytes untouched.
    cdirs, manifest, db_path, intervention, claim = make_gate_root(
        tmp_path, committed=False)
    before = open(os.path.join(cdirs["art"], "w-out.txt"), "rb").read()
    assert ce._maybe_apply_corrupt_tamper(cdirs, manifest, db_path,
                                          intervention, claim) is None
    assert open(os.path.join(cdirs["art"], "w-out.txt"), "rb").read() \
        == before


def test_tamper_applies_after_commit(tmp_path):
    # Same observation with the commit record present: fault applies,
    # artifact bytes change, record carries the tamper proof.
    cdirs, manifest, db_path, intervention, claim = make_gate_root(
        tmp_path, committed=True)
    rec = ce._maybe_apply_corrupt_tamper(cdirs, manifest, db_path,
                                         intervention, claim)
    assert rec is not None and rec.get("induced") is True
    assert rec["before_sha256"] != rec["after_sha256"]
    assert open(os.path.join(cdirs["art"], "w-out.txt"), "rb").read() \
        == b"tampered-by-fixture-control"


def test_tamper_ignores_other_controls(tmp_path):
    cdirs, manifest, db_path, intervention, claim = make_gate_root(
        tmp_path, committed=True)
    intervention = dict(intervention, control="transport-queued-first")
    assert ce._maybe_apply_corrupt_tamper(cdirs, manifest, db_path,
                                          intervention, claim) is None
