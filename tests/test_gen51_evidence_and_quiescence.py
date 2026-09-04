"""Gen51: the retention contract must fail closed, and the replay must be honest."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from memory_bakeoff.pi_state_control import raw_evidence as R

RESULTS = ROOT/"results/pi_gen51"


@pytest.fixture
def archived(tmp_path):
    capture = tmp_path/"capture"; capture.mkdir()
    archive = tmp_path/"archive"; archive.mkdir()
    source = capture/"stdout.txt"; source.write_bytes(b"stream bytes\n" * 10)
    stream = R.archive_stream(source, archive, "01-T1-r1-arm")
    return capture, archive, source, stream


def test_archive_leaves_the_capture_alone(archived):
    _capture, _archive, source, stream = archived
    assert source.exists()
    assert stream.sha256 == R.sha256_file(source)
    assert stream.bytes == source.stat().st_size


def test_manifest_generation_does_not_touch_the_archived_bytes(archived):
    _capture, archive, _source, stream = archived
    before = (stream.archive_path.stat().st_ino, R.sha256_file(stream.archive_path))
    first = R.build_manifest([stream], archive)
    second = R.build_manifest([stream], archive)
    assert first["streams"] == second["streams"]
    assert (stream.archive_path.stat().st_ino, R.sha256_file(stream.archive_path)) == before


def test_retention_is_unverified_until_it_is_checked(archived):
    _capture, archive, _source, stream = archived
    manifest = R.build_manifest([stream], archive)
    assert manifest["retention_verified"] is False
    assert R.verify_retention(manifest, archive)["retention_verified"] is True


def test_a_deleted_stream_fails_closed(archived):
    _capture, archive, _source, stream = archived
    manifest = R.build_manifest([stream], archive)
    stream.archive_path.unlink()
    with pytest.raises(R.RetentionError):
        R.assert_retained(manifest, archive)


def test_a_modified_stream_fails_closed(archived):
    _capture, archive, _source, stream = archived
    manifest = R.build_manifest([stream], archive)
    stream.archive_path.write_bytes(b"quietly different\n")
    with pytest.raises(R.RetentionError):
        R.assert_retained(manifest, archive)


def test_cleanup_keeps_a_capture_whose_archive_is_missing(archived):
    capture, archive, source, stream = archived
    manifest = R.build_manifest([stream], archive)
    stream.archive_path.unlink()
    report = R.cleanup_capture([source], manifest, archive)
    assert report["removed_capture_files"] == []
    assert source.exists(), "an unverified capture must never be deleted"


def test_empty_and_large_streams_round_trip(tmp_path):
    capture = tmp_path/"capture"; capture.mkdir()
    archive = tmp_path/"archive"; archive.mkdir()
    streams = []
    for name, blob in (("empty", b""), ("large", b"x" * (2 * 1024 * 1024))):
        path = capture/f"{name}.txt"; path.write_bytes(blob)
        streams.append(R.archive_stream(path, archive, name))
    manifest = R.verify_retention(R.build_manifest(streams, archive), archive)
    assert manifest["retention_verified"] is True


def test_verify_command_exits_non_zero_when_a_stream_is_gone(archived, tmp_path):
    _capture, archive, _source, stream = archived
    manifest_path = tmp_path/"manifest.json"
    manifest_path.write_text(json.dumps(R.build_manifest([stream], archive)))
    command = [sys.executable, str(ROOT/"scripts/verify_raw_evidence_retention.py"),
               str(manifest_path), str(archive)]
    assert subprocess.run(command, capture_output=True).returncode == 0
    stream.archive_path.unlink()
    assert subprocess.run(command, capture_output=True).returncode == 1


# --- the recorded Gen51 results -----------------------------------------------

@pytest.fixture(scope="module")
def replay():
    path = RESULTS/"quiescence_replay_48_runs.json"
    if not path.exists():
        pytest.skip("Gen51 replay has not been generated")
    return json.loads(path.read_text())


def test_replay_covers_every_gen47_and_gen49_run(replay):
    assert len(replay["runs"]) == 48
    assert {r["generation"] for r in replay["runs"]} == {47, 49}


def test_reconstructed_receipts_agree_with_every_recorded_harness_receipt(replay):
    agreement = replay["receipt_reconstruction"]["agreement_with_recorded_harness_receipts"]
    assert agreement["compared"] == 36
    assert agreement["agree"] == agreement["compared"]
    assert replay["instrumentation_blocker"] is False


def test_arm_b_receipts_are_labelled_as_reconstructions(replay):
    for run in replay["runs"]:
        expected = ("harness_validation_record" if run["arm"] != "pi_state_control_v1"
                    else "offline_reconstructed_observable_receipt")
        assert run["receipt_source"] == expected


def test_the_hidden_verifier_is_never_an_input_to_the_rule(replay):
    assert replay["contract"]["hidden_verifier_is_never_an_input"] is True
    source = (ROOT/"scripts/run_gen51_quiescence_replay.py").read_text()
    rule = source.split("def replay(")[1].split("\ndef ")[0]
    assert "verifier" not in rule


def test_no_k_was_tuned_live_or_baked_into_an_arm(replay):
    assert replay["contract"]["k_sweep"] == [1, 2, 3, 5, 10]
    assert replay["contract"]["no_live_tuning"] is True
    assert replay["contract"]["no_k_baked_into_any_arm"] is True


def test_the_clock_substitution_is_declared(replay):
    assert "provider requests" in replay["contract"]["clock_substitution"]
    assert "deviation" in replay["contract"]["clock_substitution"]


def test_historical_manifests_are_still_recorded_as_lost():
    for generation in ("pi_state_control_gen47", "pi_state_control_gen49"):
        manifest = json.loads((ROOT/"results"/generation/"raw_stream_manifest.json").read_text())
        assert manifest["streams_still_exist"] is False
