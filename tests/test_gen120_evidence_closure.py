"""Gen120: the raw response bytes must be manifest-bound, and the marker must be
derived from an observation rather than authored.

Sol found the hole at the Gen119 freeze: `reader_raw.jsonl` was written with a
bare `write_text`, its hash stored in `raw_seal.json`, and never registered in
`MANIFEST.json`. `EV.verify` walks the manifest and nothing else, so the single
most important file in an experimental run - the verbatim reader responses -
could be edited afterwards and verification would still report success. A hash
in a seal is not manifest-binding.

The second hole was next to it: the runner passed `manifest_ok=True` into the
marker gate, so "the evidence is intact" was an assertion by the author of the
run rather than a measurement of it.

These tests exercise the real write/verify/marker path. A test that only checks
a helper's return value would have passed against the defective code.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV  # noqa: E402

RUNNER = ROOT / "scripts/run_reader_v6.py"
REQUIRED = ("preflight.json", "execution_contract.json", "reader_raw.jsonl",
            "raw_seal.json", "graded_rows.json", "control_gates.json",
            "estimands.json")


def _head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def _run_like_evidence(d: Path) -> None:
    """Everything a real run writes before its marker, by the real helpers."""
    for name in ("preflight.json", "execution_contract.json", "graded_rows.json",
                 "control_gates.json", "estimands.json"):
        EV.write_evidence(d, name, {"stub": name})
    raw = '{"case_id": "c1", "text": "current"}\n'
    EV.write_raw(d, "reader_raw.jsonl", raw)
    EV.write_evidence(d, "raw_seal.json",
                      {"file": "reader_raw.jsonl", "sha256": EV.digest(raw),
                       "sealed_before_parse": True})


# ------------------------------------------------------------------ F1 witnesses
def test_raw_jsonl_is_listed_in_the_manifest(tmp_path):
    _run_like_evidence(tmp_path)
    manifest = json.loads((tmp_path / EV.MANIFEST).read_text())
    assert "reader_raw.jsonl" in manifest["artifacts"], (
        "the raw responses are not manifest-bound; EV.verify would never look at "
        "them, which is the Gen119 defect")
    assert EV.verify(tmp_path)["verified"] is True


def test_changing_one_raw_byte_fails_verification(tmp_path):
    _run_like_evidence(tmp_path)
    raw = tmp_path / "reader_raw.jsonl"
    body = raw.read_text()
    raw.write_text(body.replace("current", "currenT"))   # one byte
    result = EV.verify(tmp_path)
    assert result["verified"] is False
    assert "reader_raw.jsonl" in result["mismatched"]


def test_deleting_raw_jsonl_fails_verification(tmp_path):
    _run_like_evidence(tmp_path)
    (tmp_path / "reader_raw.jsonl").unlink()
    result = EV.verify(tmp_path)
    assert result["verified"] is False
    assert "reader_raw.jsonl" in result["missing"]


def test_a_seal_that_disagrees_with_the_bytes_is_detectable(tmp_path):
    """The seal, the manifest and the disk must all agree - three sources.

    Comparing only two is how a hash in a seal came to be mistaken for binding.
    """
    _run_like_evidence(tmp_path)
    seal = json.loads((tmp_path / "raw_seal.json").read_text())
    disk = EV.digest((tmp_path / "reader_raw.jsonl").read_text())
    entry = json.loads((tmp_path / EV.MANIFEST).read_text())["artifacts"]["reader_raw.jsonl"]
    assert seal["sha256"] == entry["sha256"] == disk

    lying = dict(seal, sha256="0" * 64)
    (tmp_path / "raw_seal.json").write_text(json.dumps(lying))
    reread = json.loads((tmp_path / "raw_seal.json").read_text())
    assert reread["sha256"] != entry["sha256"], "a lying seal must be visible"
    assert EV.verify(tmp_path)["verified"] is False, (
        "rewriting the seal must also break the seal file's own manifest entry")


def test_raw_capture_refuses_to_overwrite(tmp_path):
    _run_like_evidence(tmp_path)
    with pytest.raises(FileExistsError):
        EV.write_raw(tmp_path, "reader_raw.jsonl", "different bytes")


def test_the_manifest_digest_comes_from_disk_not_from_the_argument(tmp_path):
    """A manifest entry may never describe bytes that are not the ones on disk."""
    EV.write_raw(tmp_path, "raw.jsonl", "abc\n")
    entry = json.loads((tmp_path / EV.MANIFEST).read_text())["artifacts"]["raw.jsonl"]
    assert entry["sha256"] == EV.digest((tmp_path / "raw.jsonl").read_text())


# ------------------------------------------------------------------ F2 witnesses
def test_closure_reports_a_complete_required_set(tmp_path):
    _run_like_evidence(tmp_path)
    assert EV.verify_closed(tmp_path, REQUIRED)["closed"] is True


def test_an_incomplete_pre_marker_set_denies_closure(tmp_path):
    _run_like_evidence(tmp_path)
    (tmp_path / "estimands.json").unlink()
    closure = EV.verify_closed(tmp_path, REQUIRED)
    assert closure["closed"] is False
    assert "estimands.json" in closure["missing"]


def test_an_unmanifested_artefact_denies_closure(tmp_path):
    """A file the manifest never listed is exactly the F1 shape."""
    for name in REQUIRED:
        if name != "reader_raw.jsonl":
            EV.write_evidence(tmp_path, name, {"stub": name})
    (tmp_path / "reader_raw.jsonl").write_text("smuggled\n")   # bare write, no record
    closure = EV.verify_closed(tmp_path, REQUIRED)
    assert closure["closed"] is False
    assert "reader_raw.jsonl" in closure["missing_required"]


def test_an_unexpected_artefact_denies_closure(tmp_path):
    _run_like_evidence(tmp_path)
    EV.write_evidence(tmp_path, "surprise.json", {"not": "required"})
    closure = EV.verify_closed(tmp_path, REQUIRED)
    assert closure["closed"] is False
    assert "surprise.json" in closure["unexpected"]


def test_the_marker_gate_is_never_handed_an_authored_true():
    source = RUNNER.read_text()
    assert "manifest_ok=True" not in source, (
        "the strongest claim in the apparatus - the evidence is intact - was "
        "authored as a literal instead of measured")
    assert "manifest_ok=closure[" in source, (
        "manifest_ok must come from an actual verification of the pre-marker set")


def test_the_marker_is_written_after_the_closure_check():
    """Order is the property. A marker inside its own required set verifies itself."""
    source = RUNNER.read_text()
    assert "REQUIRED_PRE_MARKER" in source
    checked = source.index("closure = EV.verify_closed(")
    written = source.index('EV.write_evidence(out, f"{marker[\'marker\']}.json"')
    assert checked < written, "closure must be observed before the marker is written"
    marker_names = ("RUN_EVIDENCE.json", "NON_EVIDENCE.json")
    required_block = source[source.index("REQUIRED_PRE_MARKER"):source.index("def main")]
    assert not any(n in required_block for n in marker_names), (
        "the marker may not be part of the set whose closure decides the marker")


def test_seal_agreement_is_a_three_way_check():
    source = RUNNER.read_text()
    assert "seal_ok = seal_agrees(out)" in source
    assert "seal_ok=bool(" not in source, "seal_ok must not be derived from truthiness"


# ------------------------------------------------------------------ F3 witnesses
def _refuses(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(RUNNER), *args], cwd=ROOT,
                          capture_output=True, text=True, timeout=300)


def test_a_stale_authorisation_generation_fails_with_zero_calls():
    r = _refuses(["--fire", "--generation", "121", "--authorised-by", "120",
                  "--source-commit", _head()])
    assert r.returncode != 0
    assert "generation" in (r.stderr + r.stdout).lower()
    assert not (ROOT / "results/gen121").exists(), "no attempt may be written"


def test_authorisation_must_be_more_than_a_non_empty_string():
    r = _refuses(["--fire", "--generation", "120", "--authorised-by", "yes please",
                  "--source-commit", _head()])
    assert r.returncode != 0, "any non-empty string used to be accepted"


def test_fire_without_a_source_commit_is_refused():
    r = _refuses(["--fire", "--generation", "120", "--authorised-by", "120"])
    assert r.returncode != 0
    assert "source-commit" in (r.stderr + r.stdout)


def test_head_differing_from_the_authorised_commit_fails_before_any_call():
    r = _refuses(["--generation", "120", "--source-commit", "0" * 40])
    assert "not the authorised source commit" in (r.stdout + r.stderr)
    assert "DRY RUN" in r.stdout and "No attempt written, no calls made" in r.stdout


def test_the_runner_carries_no_hardcoded_generation_or_commit():
    source = RUNNER.read_text()
    assert "GENERATION = 119" not in source
    assert "1c36483e835732364145d551d25a8144ce44bd09" not in source
    assert "--generation" in source and "--source-commit" in source


def test_the_output_path_follows_the_authorised_generation():
    source = RUNNER.read_text()
    assert "EV.next_attempt(ROOT, args.generation)" in source, (
        "evidence must be filed under the generation that actually ran it")


def test_the_contract_records_the_runtime_authorisation():
    """Build a real contract and inspect it, rather than grepping the source.

    The first version asserted `"authorised_by_generation" in source`. When the
    attempt7 repair renamed the live fields, that string survived only in a
    COMMENT explaining the rename - so the check passed no matter what the
    contract actually contained. A check that cannot fail reads exactly like a
    check that passes, which is the disease this very file was written about.
    Found by glm-5.3 at Gen120.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("runner_under_test", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    schedule = json.loads((mod.CANONICAL / "reader_interference_v6_schedule.json").read_text())
    contract = mod.freeze_contract(schedule["cases"], 123, "deadbeef" * 5, "123")

    auth = contract["authorisation"]
    assert auth["authorisation_generation"] == "123"
    assert auth["execution_generation"] == 123
    assert auth["required_to_match"] is True
    assert auth["source_commit"] == "deadbeef" * 5
    assert auth["supplied_at_runtime_not_hardcoded"] is True
    assert contract["generation"] == 123, "the contract must carry the RUNTIME generation"
    assert "authorised_by_generation" not in auth, (
        "the conflated field name is back")
    assert "v5_module_sha256" not in contract, "v5 naming vestige returned"
    assert contract["v6_module_sha256"]


# ------------------------------------------------- prior evidence stays immutable
@pytest.mark.parametrize("attempt", [1, 2, 3, 4, 5, 6, 7])
def test_every_prior_gen118_attempt_still_verifies(attempt):
    d = ROOT / f"results/gen118/attempt{attempt}"
    if not d.exists():
        pytest.skip(f"attempt{attempt} does not exist")
    assert EV.verify(d)["verified"] is True, f"attempt{attempt} no longer verifies"


@pytest.mark.parametrize("attempt", [1, 2, 3, 4, 5, 6, 7])
def test_no_prior_attempt_contains_a_reader_result(attempt):
    d = ROOT / f"results/gen118/attempt{attempt}"
    if not d.exists():
        pytest.skip(f"attempt{attempt} does not exist")
    assert not (d / "reader_raw.jsonl").exists(), "a freeze may not hold reader output"
    assert (d / "NON_EVIDENCE.json").exists()
    assert json.loads((d / "NON_EVIDENCE.json").read_text())["reader_calls"] == 0


# ------------------------------------------------------- the gate on the gate
def test_the_id_balance_gate_is_exact_not_within_one():
    """7/12 must FAIL, asserted against THE GATE, not a copy of it.

    The gate read `abs(id_first - 6) > 1`, so 7/12 passed - the exact imbalance
    attempt1 was superseded for, and the number every handoff since called a hard
    gate. No published artifact was wrong; the gate was weaker than every claim
    made about it. Found by glm-5.3.

    The first version of this control defined its own lambda with the corrected
    rule and asserted against that, which proves only that the test agrees with
    itself. Found by glm-5.3-flash. It now imports the freeze module and calls the
    same function `main` calls.
    """
    import importlib.util
    freeze = ROOT / "scripts/run_gen118_freeze.py"
    spec = importlib.util.spec_from_file_location("freeze_under_test", freeze)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert "abs(id_first - len(V6.CORES) // 2) > 1" not in freeze.read_text(), "tolerance is back"
    assert mod.id_balance_ok(6, 12) is True, "6/12 must be accepted"
    assert mod.id_balance_ok(7, 12) is False, "7/12 must be rejected - attempt1 died on it"
    assert mod.id_balance_ok(5, 12) is False, "5/12 must be rejected"
    assert mod.id_balance_ok(0, 12) is False
    src = freeze.read_text()
    assert "id_balance_ok(v, cores)" in src, (
        "main must gate on the function this test exercises, not an inline copy")
    # EVERY published balance is gated, not just the one that was caught. Three
    # were computed, printed and shipped un-gated, so a refreeze could have passed
    # with 8/12 length balance while reporting "balanced".
    for invariant in ("id_sorts_first", "value_longer", "value_lexicographically_larger"):
        assert invariant in src, f"{invariant} is not gated"
    assert 'not fx_audit["conflict_order_counterbalanced"]' in src, (
        "the conflict-order counterbalance is computed but not gated")


def test_the_sealed_contract_hash_actually_recomputes():
    """The preflight check used to compare a field against itself.

    It read `contract["contract_sha256"]` and compared it to a helper that read
    the same field from the same file, while its comment claimed it verified a
    recomputation. Nothing in the run path ever recomputed the sealed hash.
    Found by glm-5.3-flash at Gen120.
    """
    import hashlib
    d = ROOT / "results/gen118" / (ROOT / "results/gen118/CANONICAL_ATTEMPT.md").read_text().split("`")[1]
    contract = json.loads((d / "reader_interference_v6_contract.json").read_text())
    payload = json.loads((d / "reader_interference_v6_contract_payload.json").read_text())
    recomputed = hashlib.sha256(json.dumps({**payload, "source_sha256": contract["source_sha256"]},
                                           sort_keys=True, default=str).encode()).hexdigest()
    assert recomputed == contract["contract_sha256"], "the sealed hash does not recompute"

    # It must be able to FAIL: perturb one source pin and the hash must move.
    tampered = dict(contract["source_sha256"]); k = sorted(tampered)[0]
    tampered[k] = "0" * 64
    moved = hashlib.sha256(json.dumps({**payload, "source_sha256": tampered},
                                      sort_keys=True, default=str).encode()).hexdigest()
    assert moved != contract["contract_sha256"], "the recomputation ignores the source pins"

    src = (ROOT / "scripts/run_reader_v6.py").read_text()
    assert "SEALED CONTRACT HASH DOES NOT RECOMPUTE" in src
    assert 'if contract["contract_sha256"] != _expected_contract():' not in src, (
        "the tautological self-comparison is back")


def test_gen117_raw_evidence_is_honestly_described():
    """gen117/attempt1 holds the only real reader run, and it PREDATES F1.

    Its reader_raw.jsonl is not in its manifest, so it verifies under EV.verify
    (which walks the manifest) but would NOT pass verify_closed's directory scan.
    That attempt is sealed and may not be altered, so the honest move is to state
    the limit rather than let 'all attempts verify' imply more than it does.
    Raised by glm-5.3-flash at Gen120.
    """
    d = ROOT / "results/gen117/attempt1"
    if not d.exists():
        pytest.skip("gen117/attempt1 absent")
    manifest = json.loads((d / EV.MANIFEST).read_text())["artifacts"]
    raw = d / "reader_raw.jsonl"
    if not raw.exists():
        pytest.skip("no raw capture in gen117/attempt1")
    assert "reader_raw.jsonl" not in manifest, (
        "if this is now manifested, a sealed attempt was modified")
    seal = json.loads((d / "raw_seal.json").read_text())
    assert seal["sha256"] == EV.digest(raw.read_text()), (
        "the seal no longer matches the bytes - the pre-F1 evidence has changed")
    assert EV.verify(d)["verified"] is True


# ------------------------------------- the malformed-answer repair, witnessed
def _call_once_with(monkeypatch, body: str, fail_times: int = 0):
    """Drive the REAL call_once against a fake endpoint. No network."""
    import importlib.util, io, urllib.request
    spec = importlib.util.spec_from_file_location("runner_mw", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    calls = {"n": 0}

    class _Resp(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen(req, timeout=None):
        calls["n"] += 1
        if calls["n"] <= fail_times:
            raise OSError("connection reset")
        return _Resp(body.encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    schedule = json.loads((mod.CANONICAL / "reader_interference_v6_schedule.json").read_text())
    return mod.call_once(schedule["cases"][0]), calls


def test_a_malformed_answer_is_terminal_and_is_never_retried(monkeypatch):
    """The server answered. Answering badly is a SCIENTIFIC outcome.

    The parse used to sit inside the transport handler, so a malformed 200 was
    classified as a connection failure, RETRIED, and its bytes discarded - keeping
    only the exception type. That is sampling until a favourable answer appears,
    forbidden by the same contract promising raw evidence sealed as it arrives.
    Found by glm-5.3 at Gen120 round 4; this witness added at round 5 after
    glm-5.3-flash observed the repair shipped without one, so a regression would
    have passed the whole suite.
    """
    result, calls = _call_once_with(monkeypatch, "this is not json at all")
    assert result["terminal_disposition"] == "TERMINAL_MALFORMED_RESPONSE"
    assert calls["n"] == 1, f"a malformed answer was retried {calls['n']} times"
    assert result["raw_response"] == "this is not json at all", (
        "the raw bytes must be KEPT - they are the evidence of what arrived")
    assert result["parse_error"]
    assert result["retry_history"] == []


def test_a_transport_failure_is_still_retried(monkeypatch):
    """The negative control: the retry path must still work for real transport."""
    good = json.dumps({"choices": [{"message": {"content": "x"}, "finish_reason": "stop"}],
                       "model": "test-model"})
    result, calls = _call_once_with(monkeypatch, good, fail_times=2)
    assert result["terminal_disposition"] == "COMPLETED"
    assert calls["n"] == 3, "two transport failures should have been retried"
    assert len(result["retry_history"]) == 2


def test_transport_exhaustion_is_terminal_and_distinct(monkeypatch):
    result, calls = _call_once_with(monkeypatch, "{}", fail_times=99)
    assert result["terminal_disposition"] == "TERMINAL_TRANSPORT_FAILURE"
    assert result["raw_response"] is None
    assert calls["n"] == 3, "transport retries are bounded at TRANSPORT_RETRIES + 1"
    assert len(result["retry_history"]) == 3


def test_the_parse_is_outside_the_transport_handler():
    src = RUNNER.read_text()
    assert "# TRANSPORT only - retryable" in src
    assert "TERMINAL_MALFORMED_RESPONSE" in src
    transport = src.index("# TRANSPORT only - retryable")
    parse = src.index("obj = json.loads(raw)")
    assert transport < parse, "the parse must sit outside the transport handler"
