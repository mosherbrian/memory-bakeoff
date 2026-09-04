"""Gen51 Part A: exercise the real retention helper, including failure injection."""
import json, os, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/"src"))
from memory_bakeoff.membukkit_gen40 import BlockedNetwork, block_network
from memory_bakeoff.pi_state_control import raw_evidence as R

WORK = Path(os.environ.get("GEN51_SCRATCH", "/tmp/gen51-retention")); shutil.rmtree(WORK, ignore_errors=True)
capture_dir = WORK/"ephemeral"/"run_work"; capture_dir.mkdir(parents=True)
archive = WORK/"archive"; archive.mkdir(parents=True)

fixtures = {
    "01-IP1-r1-arm_c": ("ordinary", b"a normal stream\n" * 40),
    "02-IP2-r2-arm_d": ("empty", b""),
    "03-T3-r1-arm_b": ("multi_megabyte", os.urandom(3 * 1024 * 1024)),
    "04-IP4-r3-arm_harness_state_control_task_floor_v1": ("long_run_id", b"x" * 4096),
}
captures, streams = [], []
for run_id, (_kind, blob) in fixtures.items():
    p = capture_dir/f"{run_id}.stdout.txt"; p.write_bytes(blob); captures.append(p)
    streams.append(R.archive_stream(p, archive, run_id))

manifest = R.build_manifest(streams, archive)
before = {s.run_id: (s.archive_path.stat().st_ino, s.sha256, s.bytes) for s in streams}
manifest2 = R.build_manifest(streams, archive)   # hashing twice must change nothing
after_hash = {s.run_id: (s.archive_path.stat().st_ino, R.sha256_file(s.archive_path),
                         s.archive_path.stat().st_size) for s in streams}

cleanup = R.cleanup_capture(captures, manifest, archive)
verified = R.verify_retention(json.loads(json.dumps(manifest)), archive)

# failure injection 1: delete one archived stream
tamper_dir = WORK/"archive_deleted"; shutil.copytree(archive, tamper_dir)
victim = tamper_dir/"01-IP1-r1-arm_c"/"stdout.txt"; victim.unlink()
deleted_check = R.verify_retention(json.loads(json.dumps(manifest)), tamper_dir)
try:
    R.assert_retained(json.loads(json.dumps(manifest)), tamper_dir); deleted_raises = False
except R.RetentionError: deleted_raises = True

# failure injection 2: modify one archived stream in place
tamper2 = WORK/"archive_modified"; shutil.copytree(archive, tamper2)
(tamper2/"01-IP1-r1-arm_c"/"stdout.txt").write_bytes(b"quietly different\n")
modified_check = R.verify_retention(json.loads(json.dumps(manifest)), tamper2)

block_network()
import socket
try:
    socket.create_connection(("127.0.0.2", 8080), timeout=0.2); blocked = False
except (BlockedNetwork, OSError): blocked = True

result = {
 "contract": R.contract(),
 "fixtures": {k: v[0] for k, v in fixtures.items()},
 "manifest_generation_is_read_only": {
   "inode_unchanged": all(before[k][0] == after_hash[k][0] for k in before),
   "sha256_unchanged": all(before[k][1] == after_hash[k][1] for k in before),
   "size_unchanged": all(before[k][2] == after_hash[k][2] for k in before),
   "second_manifest_identical": manifest["streams"] == manifest2["streams"],
 },
 "cleanup": cleanup,
 "survives_cleanup": {
   "retention_verified": verified["retention_verified"],
   "all_exist_after_cleanup": all(v["exists_after_cleanup"] for v in verified["per_stream_verification"].values()),
   "all_hashes_match": all(v.get("sha256_matches") for v in verified["per_stream_verification"].values()),
   "ephemeral_captures_removed": len(cleanup["removed_capture_files"]),
   "captures_kept_because_unverified": cleanup["kept_because_unverified"],
 },
 "fails_closed_when_a_stream_is_deleted": {
   "retention_verified": deleted_check["retention_verified"],
   "failures": deleted_check["failures"], "assert_raises": deleted_raises,
 },
 "fails_closed_when_a_stream_is_modified": {
   "retention_verified": modified_check["retention_verified"],
   "failures": modified_check["failures"],
 },
 "no_network": blocked,
 "historical_manifests_left_as_lost": {
   gen: json.loads((ROOT/"results"/gen/"raw_stream_manifest.json").read_text())["streams_still_exist"]
   for gen in ("pi_state_control_gen47", "pi_state_control_gen49")},
}
result["passed"] = (
  all(result["manifest_generation_is_read_only"].values())
  and result["survives_cleanup"]["retention_verified"]
  and result["survives_cleanup"]["all_exist_after_cleanup"]
  and result["fails_closed_when_a_stream_is_deleted"]["retention_verified"] is False
  and result["fails_closed_when_a_stream_is_deleted"]["assert_raises"]
  and result["fails_closed_when_a_stream_is_modified"]["retention_verified"] is False
  and result["no_network"]
  and not any(result["historical_manifests_left_as_lost"].values()))
OUT = ROOT/"results/pi_gen51"; OUT.mkdir(parents=True, exist_ok=True)
(OUT/"raw_evidence_retention_contract.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
print(json.dumps({k: result[k] for k in ("manifest_generation_is_read_only","survives_cleanup",
    "fails_closed_when_a_stream_is_deleted","fails_closed_when_a_stream_is_modified","no_network","passed")}, indent=1))
