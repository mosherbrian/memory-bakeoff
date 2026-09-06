#!/usr/bin/env python3
"""Gen114: the first fresh measurement against the authoritative v4 ruler.

60 stateless calls - 20 frozen cases x 3 repetitions. The ruler is consumed, not
touched. Preflight fails closed with zero scored calls. Raw evidence is sealed
and hashed before anything is parsed or graded.
"""
from __future__ import annotations

import argparse, hashlib, json, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV                          # noqa: E402
from memory_bakeoff import reader_interference_v3 as V3            # noqa: E402
from memory_bakeoff import reader_interference_v4 as V4            # noqa: E402

GENERATION = 114
AUTHORITATIVE = ROOT / "results/gen113/attempt2/reader_interference_v4.json"
EXPECT_CONTRACT = "2bc281b9dea248ce09b3b75392ffa91bb36a1a489468afed7dbda3fb43ff809d"
EXPECT_FILE = "0d63bb82e18595d8ea47b93e8d9f1b0ae62b9bc885021a6614da407c635eaa24"
SOURCE_COMMIT = "b286c2182b236de28f6148cf56e84d7cb0692cf6"
EVIDENCE_CLASS = "controlled_reader_interference"
CARDINALITY = {"fixture_identity": 20, "prompt_sha256": 20, "parser_table": 13,
               "classifier_table": 20, "citation_table": 72, "truth_matrix": 360}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def preflight() -> dict:
    """Every gate. Any failure means zero scored calls."""
    problems: list[str] = []
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    origin = subprocess.run(["git", "rev-parse", "origin/main"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                           capture_output=True, text=True).stdout.splitlines()
    tracked = [l for l in dirty if not l.startswith("??")]
    if head != SOURCE_COMMIT or origin != SOURCE_COMMIT:
        problems.append(f"commit mismatch: head={head} origin={origin}")
    if tracked:
        problems.append(f"worktree not clean: {tracked}")

    raw = AUTHORITATIVE.read_bytes()
    doc = json.loads(raw)
    if hashlib.sha256(raw).hexdigest() != EXPECT_FILE:
        problems.append("authoritative artifact file digest differs")
    if doc["contract_sha256"] != EXPECT_CONTRACT:
        problems.append("v4 contract digest differs")
    reconstruction = V4.verify_contract(doc)
    if not reconstruction["verified"]:
        problems.append(f"independent reconstruction failed: {reconstruction['problems']}")
    manifest = EV.verify(AUTHORITATIVE.parent)
    if not manifest["verified"]:
        problems.append(f"attempt2 manifest failed: {manifest}")

    payload = doc["contract_payload"]
    for field, want in CARDINALITY.items():
        if len(payload[field]) != want:
            problems.append(f"{field}: {len(payload[field])} != {want}")
    if payload["repetitions"] != 3:
        problems.append("repetitions != 3")
    if set(payload["control_passing_forms"]) != set(V4.CONTROL_CONDITIONS):
        problems.append("control forms incomplete")

    # frozen parser + projection, checked against the payload before any endpoint access
    for row in payload["parser_table"]:
        fixtures = {f["name"]: f for f in V4.VALID_FIXTURES + V4.INVALID_FIXTURES}
        parsed = V4.parse_response(fixtures[row["name"]]["text"])
        if parsed["parse_status"] != row["parse_status"] or parsed["parsed"] != row["parsed"]:
            problems.append(f"parser drift on {row['name']!r}")
    for case in V4.build_fixture()["cases"]:
        if sha(V4.project_prompt(case)) != payload["prompt_sha256"][case["id"]]:
            problems.append(f"prompt hash drift on {case['id']}")
        V4.assert_prompt_is_blind(case)
    try:
        V4.assert_behaviour_identical_to_v3()
    except ValueError as exc:
        problems.append(str(exc))

    # non-benchmark identity probe: no record text, no case id, no canonical value
    identity = {}
    try:
        body = json.dumps({"model": V4.READER_SETTINGS["requested_model"],
                           "messages": [{"role": "user", "content": "Reply with the single word: ready"}],
                           "temperature": 0.0, "seed": 0, "max_tokens": 16}).encode()
        request = urllib.request.Request(
            f"{V4.READER_SETTINGS['endpoint']}/chat/completions", data=body,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=120) as response:
            probe = json.loads(response.read())
        choice = probe["choices"][0]
        identity = {"served_model": probe.get("model"),
                    "reasoning_present": bool(choice["message"].get("reasoning_content")),
                    "finish_reason": choice.get("finish_reason"),
                    "seed_accepted": True}
        if identity["served_model"] != V4.READER_SETTINGS["requested_model"]:
            problems.append(f"served model is {identity['served_model']}")
        if identity["reasoning_present"]:
            problems.append("thinking is not disabled")
    except Exception as exc:
        problems.append(f"endpoint preflight failed: {type(exc).__name__}: {exc}")

    return {"passed": not problems, "problems": problems,
            "identity": identity, "reconstruction": reconstruction,
            "manifest": manifest}


def call(prompt: str) -> dict:
    settings = V4.READER_SETTINGS
    body = json.dumps({"model": settings["requested_model"],
                       "messages": [{"role": "user", "content": prompt}],
                       "temperature": settings["temperature"],
                       "seed": settings["seed"],
                       "max_tokens": settings["max_tokens"]}).encode()
    request = urllib.request.Request(
        f"{settings['endpoint']}/chat/completions", data=body,
        headers={"Content-Type": "application/json"})
    started = time.time()
    with urllib.request.urlopen(request, timeout=300) as response:
        raw = response.read().decode()
        status = response.status
    payload = json.loads(raw)
    choice = payload["choices"][0]
    return {"http_status": status, "raw_body": raw,
            "text": choice["message"]["content"],
            "finish_reason": choice.get("finish_reason"),
            "served_model": payload.get("model"),
            "usage": payload.get("usage"),
            "elapsed_s": round(time.time() - started, 2)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", type=int, default=None)
    args = parser.parse_args()

    checks = preflight()
    if not checks["passed"]:
        out = EV.next_attempt(ROOT, GENERATION)
        EV.write_evidence(out, "BLOCKED.json", {
            "status": "BLOCKED / NON_EVIDENCE", "scored_calls": 0,
            "problems": checks["problems"], "evidence_class": EVIDENCE_CLASS})
        print(f"BLOCKED, zero scored calls: {checks['problems']}")
        return 1
    print("preflight passed; identity:", checks["identity"])

    cases = sorted(V4.build_fixture()["cases"], key=lambda c: c["id"])
    schedule = [{"call_index": i, "repetition": rep, "case_id": c["id"],
                 "core": c["core"], "condition": c["condition"],
                 "prompt_sha256": sha(V4.project_prompt(c))}
                for i, (rep, c) in enumerate(
                    ((r, c) for r in (1, 2, 3) for c in cases), 1)]
    assert len(schedule) == 60 and len({(s["case_id"], s["repetition"])
                                        for s in schedule}) == 60

    out = (EV.attempt_dir(ROOT, GENERATION, args.attempt) if args.attempt
           else EV.next_attempt(ROOT, GENERATION))
    addendum = {
        "generation": GENERATION, "evidence_class": EVIDENCE_CLASS,
        "source_commit": SOURCE_COMMIT,
        "consumes": {"path": str(AUTHORITATIVE.relative_to(ROOT)),
                     "contract_sha256": EXPECT_CONTRACT, "file_sha256": EXPECT_FILE},
        "reader_settings": V4.READER_SETTINGS,
        "identity_preflight": checks["identity"],
        "planned_calls": 60, "stateless": True, "no_silent_retry": True,
        "ordering_rule": "case_id ascending within repetition 1, then 2, then 3; "
                         "frozen before any output and never reordered",
        "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "scope_note": "This CONTROLS which benchmark-owned records the reader "
                      "sees. It does not establish that any memory product "
                      "supplies this context or this order.",
    }
    addendum["addendum_sha256"] = sha(json.dumps(addendum, sort_keys=True))
    EV.write_evidence(out, "execution_addendum.json", addendum)
    EV.write_evidence(out, "call_schedule.json",
                      {"schedule_sha256": sha(json.dumps(schedule, sort_keys=True)),
                       "calls": schedule})
    print(f"froze addendum and 60-call schedule at {out}")

    requests_path, responses_path = out / "reader_requests.jsonl", out / "reader_responses.jsonl"
    by_id = {c["id"]: c for c in cases}
    with requests_path.open("w") as rq, responses_path.open("w") as rs:
        for entry in schedule:
            case = by_id[entry["case_id"]]
            prompt = V4.project_prompt(case)
            fingerprint = sha(f"{entry['call_index']}|{prompt}")
            rq.write(json.dumps({**entry, "prompt": prompt,
                                 "request_fingerprint": fingerprint,
                                 "settings": V4.READER_SETTINGS,
                                 "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")}) + "\n")
            try:
                result = call(prompt)
                terminal = "COMPLETED"
            except Exception as exc:
                result = {"http_status": None, "raw_body": "", "text": "",
                          "finish_reason": None, "served_model": None,
                          "usage": None, "elapsed_s": None,
                          "error": f"{type(exc).__name__}: {exc}"}
                terminal = "FAILED"
            rs.write(json.dumps({**entry, **result,
                                 "request_fingerprint": fingerprint,
                                 "response_sha256": sha(result["raw_body"] or result.get("error", "")),
                                 "terminal_disposition": terminal,
                                 "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")}) + "\n")
            print(f"  [{entry['call_index']:>2}/60] {entry['case_id']:<46} {terminal}")

    # Seal the raw evidence BEFORE anything is parsed.
    for name in ("reader_requests.jsonl", "reader_responses.jsonl"):
        EV.record(out, name, (out / name).read_text())
    print("\nraw evidence sealed and hashed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
