"""Run only the predeclared 46-request LAN probe after documented panel review."""
import hashlib
import json
import math
from pathlib import Path
import socket
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    review = ROOT / "PANEL-REVIEW.md"
    if not review.exists() or "READY_TO_RUN" not in review.read_text():
        raise SystemExit("Panel review has not released this probe.")
    manifest = json.loads((ROOT / "manifest.json").read_text())
    data = (ROOT / "cases.jsonl").read_bytes()
    if hashlib.sha256(data).hexdigest() != manifest["cases_sha256"]:
        raise SystemExit("Case bytes differ from the predeclared manifest.")
    source = ROOT.parents[2] / manifest["source_path"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != manifest["source_sha256"]:
        raise SystemExit("Historical fixture bytes changed; stopping.")
    rows = [json.loads(line) for line in data.splitlines()]
    if len(rows) != 46 or manifest["max_requests"] != 46:
        raise SystemExit("Unexpected request count.")
    results_path = ROOT / "responses.jsonl"
    if results_path.exists():
        raise SystemExit("Results already exist; this script does not rerun or append a new trial.")
    run = {
        "started_at": utc(), "endpoint": manifest["endpoint"],
        "cases_sha256": manifest["cases_sha256"], "max_requests": 46,
        "attempted": 0, "completed": 0, "status": "running",
        "served_model_identity": "unknown; preserve any reply metadata",
    }
    start = time.monotonic()
    deadline = start + manifest["wall_time_cap_seconds"]
    try:
        with results_path.open("x") as output:
            remaining = deadline - time.monotonic()
            with socket.create_connection(
                ("Brians-MacBook-Air.local", 8799),
                timeout=min(manifest["socket_timeout_seconds"], remaining),
            ) as connection:
                reader = connection.makefile("rb")
                with reader:
                    for row in rows:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise TimeoutError("Overall time cap reached")
                        connection.settimeout(min(manifest["socket_timeout_seconds"], remaining))
                        sent_at = utc()
                        call_start = time.monotonic()
                        run["attempted"] += 1
                        connection.sendall((json.dumps(row["request"]) + "\n").encode())
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise TimeoutError("Overall time cap reached after send")
                        connection.settimeout(min(manifest["socket_timeout_seconds"], remaining))
                        wire = reader.readline(1_048_577)
                        elapsed = time.monotonic() - call_start
                        if not wire or not wire.endswith(b"\n") or len(wire) > 1_048_576:
                            raise ValueError("Missing, oversized or unterminated reply")
                        reply = json.loads(wire)
                        record = {"id": row["id"], "sent_at": sent_at,
                                  "elapsed_seconds": elapsed, "reply": reply}
                        output.write(json.dumps(record, sort_keys=True) + "\n")
                        output.flush()
                        if reply.get("ok") is not True:
                            raise ValueError("Service returned ok != true; reply retained")
                        p = reply["answers"]["superseded"]["noul"]
                        if isinstance(p, bool) or not isinstance(p, (int, float)):
                            raise ValueError("Noul is not a numeric probability")
                        if not math.isfinite(p) or not 0 <= p <= 1:
                            raise ValueError("Noul outside finite [0,1]")
                        run["completed"] += 1
        run["status"] = "complete"
    except Exception as error:
        run["status"] = "stopped"
        run["error"] = f"{type(error).__name__}: {error}"
    finally:
        run["finished_at"] = utc()
        run["elapsed_seconds"] = time.monotonic() - start
        (ROOT / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(json.dumps(run, indent=2))
    if run["status"] != "complete":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
