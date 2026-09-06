#!/usr/bin/env python3
"""Gen117: the first controlled reader run against the decidable v5 protocol.

60 frozen cases from the canonical Gen116 attempt4, executed once each. The
protocol is CONSUMED, never touched. Preflight fails closed with zero calls. Raw
request and response bytes are sealed and hashed before anything is parsed.

Phases, in order, and the order is the point:
    preflight   every gate; any failure means zero model calls
    freeze      the execution contract, hashed BEFORE exposure
    execute     60 calls, raw evidence sealed as it arrives
    grade       once, with the FROZEN Gen116 grader, never a reimplementation
    marker      RUN_EVIDENCE or NON_EVIDENCE, derived by the frozen gate

60 cells across 12 independent cores. NOT 60 observations.
"""
from __future__ import annotations

import argparse, hashlib, json, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV                       # noqa: E402
from memory_bakeoff import reader_interference_v5 as V5         # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
import importlib.util as _ilu                                   # noqa: E402
_spec = _ilu.spec_from_file_location("grade_gen116_v5", ROOT / "scripts/grade_gen116_v5.py")
G116 = _ilu.module_from_spec(_spec); _spec.loader.exec_module(G116)   # noqa: E402

GENERATION = 117
CANONICAL = ROOT / "results/gen116/attempt4"
EXPECT_CONTRACT = "bf1bb84ece274758fd2286e858e13bd18fe2f1329c021837a87fb725059f09a8"
SOURCE_COMMIT = "1c36483e835732364145d551d25a8144ce44bd09"
EVIDENCE_CLASS = "controlled_reader_interference"

READER = "qwen3.6-35b-vulkan-nothink"
ENDPOINT = "http://strix-halo.local:8080/v1/chat/completions"
TEMPERATURE = 0.0
SEED = 0
MAX_TOKENS = 512
TIMEOUT_S = 180
# A transport failure may be retried. A SCIENTIFIC response may never be
# replaced - no sampling until a favourable answer appears.
TRANSPORT_RETRIES = 2


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


# --------------------------------------------------------------------- preflight
def preflight() -> dict:
    """Every gate. Any failure means zero model calls and a NON_EVIDENCE attempt."""
    problems: list[str] = []

    head = git("rev-parse", "HEAD")
    # Untracked files COUNT. Filtering '??' is how Gen114 shipped a runner that
    # did not exist at its own pinned commit, and how a drill later fired a live
    # doorbell. The tree is clean or it is not.
    dirt = git("status", "--porcelain")
    if dirt:
        problems.append(f"worktree not clean: {dirt.splitlines()[:3]}")

    canon = (ROOT / "results/gen116/CANONICAL_ATTEMPT.md").read_text()
    if "`attempt4` is canonical" not in canon:
        problems.append("CANONICAL_ATTEMPT.md does not resolve to attempt4")

    ev = EV.verify(CANONICAL)
    if not ev["verified"]:
        problems.append(f"attempt4 manifest failed: {ev}")

    contract = json.loads((CANONICAL / "reader_interference_v5_contract.json").read_text())
    if contract["contract_sha256"] != EXPECT_CONTRACT:
        problems.append(f"contract hash {contract['contract_sha256'][:16]} != expected")

    # Every file the frozen contract pins must still be byte-identical. Without
    # this the "no repair after exposure" rule is a sentence in an instruction,
    # not a property: edit the value matcher, re-run, and every other gate stays
    # green. Found by the Fable determinism review, 2026-09-06.
    for rel, frozen in contract.get("source_sha256", {}).items():
        f = ROOT / rel
        if not f.exists():
            problems.append(f"frozen source missing: {rel}")
        elif sha(f.read_text()) != frozen:
            problems.append(f"FROZEN SOURCE CHANGED since the contract: {rel}. "
                            "A run-bearing semantic may not be repaired after "
                            "exposure; this needs a new freeze, not a re-run.")

    marker = json.loads((CANONICAL / "NON_EVIDENCE.json").read_text())
    if marker.get("marker") != "NON_EVIDENCE" or marker.get("reader_calls") != 0:
        problems.append("Gen116 NON_EVIDENCE marker is modified or reports prior calls")

    schedule = json.loads((CANONICAL / "reader_interference_v5_schedule.json").read_text())
    cases = schedule["cases"]
    hashes = json.loads((CANONICAL / "reader_interference_v5_prompt_hashes.json").read_text())
    if len(cases) != 60 or len({c["case_id"] for c in cases}) != 60:
        problems.append(f"schedule is not 60 unique cases: {len(cases)}")
    if len({c["core"] for c in cases}) != 12:
        problems.append("schedule does not carry 12 cores")
    if len(set(hashes.values())) != 60:
        problems.append(f"prompt hashes are not 60 unique: {len(set(hashes.values()))}")

    # The prompts we are about to send must still hash to the frozen values, and
    # the success predicate must be the frozen one, not a live redefinition.
    drift = [c["case_id"] for c in cases
             if sha(V5.project_prompt(c)) != hashes.get(c["case_id"])]
    if drift:
        problems.append(f"prompt drift against the frozen hashes: {drift[:3]}")
    if len(V5.ONTOLOGY) != 9:
        problems.append(f"ontology is {len(V5.ONTOLOGY)} classes, not the ruled nine")
    frozen_success = {k: list(v) for k, v in V5.SUCCESS.items()}
    if frozen_success != contract_success(contract):
        problems.append("success predicate differs from attempt4")

    lineage = subprocess.run(
        [sys.executable, "-m", "pytest", "-q",
         "tests/test_gen109_reader_interference.py", "tests/test_gen110_reader_execution.py",
         "tests/test_gen111_reader_v2.py", "tests/test_gen112_reader_v3.py",
         "tests/test_gen113_reader_v4.py", "tests/test_gen115_adjudication.py",
         "tests/test_gen116_reader_v5.py"],
        cwd=ROOT, capture_output=True, text=True,
        env={"PYTHONPATH": "src", "PATH": "/usr/bin:/bin"})
    if lineage.returncode != 0:
        problems.append("reader-interference lineage is not green")

    ledger = ROOT / "reviews/LEDGER.md"
    if ledger.exists() and "| OPEN |" in ledger.read_text():
        problems.append("an open review finding remains in reviews/LEDGER.md")

    return {"head": head, "source_commit_expected": SOURCE_COMMIT,
            "worktree_clean": not dirt, "attempt4_verified": ev["verified"],
            "contract_sha256": contract["contract_sha256"],
            "cases": len(cases), "cores": len({c["core"] for c in cases}),
            "unique_prompt_hashes": len(set(hashes.values())),
            "lineage_green": lineage.returncode == 0,
            "problems": problems, "passed": not problems}


def contract_success(contract: dict) -> dict:
    payload = json.loads((CANONICAL / "reader_interference_v5_contract_payload.json").read_text())
    return {k: list(v) for k, v in payload["success_states"].items()}


# ------------------------------------------------------------------ request body
def request_body(case: dict) -> dict:
    """The exact serialized projection. Bound into the fingerprint before exposure."""
    return {"model": READER,
            "messages": [{"role": "user", "content": V5.project_prompt(case)}],
            "temperature": TEMPERATURE, "seed": SEED,
            "max_tokens": MAX_TOKENS, "stream": False}


def freeze_contract(cases: list[dict]) -> dict:
    bodies = {c["case_id"]: json.dumps(request_body(c), sort_keys=True) for c in cases}
    return {
        "generation": GENERATION, "evidence_class": EVIDENCE_CLASS,
        "consumes": {"canonical_attempt": str(CANONICAL.relative_to(ROOT)),
                     "v5_contract_sha256": EXPECT_CONTRACT,
                     "source_commit": SOURCE_COMMIT},
        "reader": {"model": READER, "endpoint": ENDPOINT, "temperature": TEMPERATURE,
                   "seed_requested": SEED,
                   "seed_accepted": "NOT REPORTED - to be read from server evidence, never authored",
                   "thinking": "absent", "max_tokens": MAX_TOKENS,
                   "timeout_s": TIMEOUT_S, "transport_retries": TRANSPORT_RETRIES,
                   "scientific_response_may_never_be_replaced": True},
        "request_body_sha256": {k: sha(v) for k, v in bodies.items()},
        "request_bodies_sha256_all": sha("".join(bodies[k] for k in sorted(bodies))),
        "capture": {"raw_path": "reader_raw.jsonl",
                    "sealed_before_parse": True,
                    "seal": "sha256 over the raw jsonl, written into the manifest"},
        "runner_sha256": sha(Path(__file__).read_text()),
        "grader_sha256": sha((ROOT / "scripts/grade_gen116_v5.py").read_text()),
        "v5_module_sha256": sha((ROOT / "src/memory_bakeoff/reader_interference_v5.py").read_text()),
        "independent_unit": "core",
        "cells_are_not_observations": True,
    }


# ---------------------------------------------------------------------- execution
def call_once(case: dict) -> dict:
    body = request_body(case)
    payload = json.dumps(body, sort_keys=True)
    attempts = []
    for attempt in range(TRANSPORT_RETRIES + 1):
        started = time.time()
        req = urllib.request.Request(ENDPOINT, data=payload.encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                raw = r.read().decode()
                obj = json.loads(raw)
            return {"case_id": case["case_id"], "core": case["core"],
                    "condition": case["condition"],
                    "request_sha256": sha(payload), "request_body": body,
                    "http_status": 200, "raw_response": raw,
                    "text": obj["choices"][0]["message"]["content"],
                    "served_model": obj.get("model"),
                    "finish_reason": obj["choices"][0].get("finish_reason"),
                    "seconds": round(time.time() - started, 3),
                    "retry_history": attempts,
                    "terminal_disposition": "COMPLETED"}
        except Exception as exc:                       # transport only
            attempts.append({"attempt": attempt, "error": f"{type(exc).__name__}: {exc}",
                             "seconds": round(time.time() - started, 3)})
    return {"case_id": case["case_id"], "core": case["core"],
            "condition": case["condition"], "request_sha256": sha(payload),
            "request_body": body, "http_status": None, "raw_response": None,
            "text": None, "served_model": None, "finish_reason": None,
            "retry_history": attempts,
            "terminal_disposition": "TERMINAL_TRANSPORT_FAILURE"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fire", action="store_true",
                    help="actually call the reader; without it nothing is sent")
    args = ap.parse_args()

    pf = preflight()
    schedule = json.loads((CANONICAL / "reader_interference_v5_schedule.json").read_text())
    cases = schedule["cases"]
    contract = freeze_contract(cases)

    print(f"preflight: {'PASS' if pf['passed'] else 'FAIL'}")
    for k in ("head", "worktree_clean", "attempt4_verified", "cases", "cores",
              "unique_prompt_hashes", "lineage_green"):
        print(f"  {k:<22}{pf[k]}")
    for p in pf["problems"]:
        print(f"  PROBLEM: {p}")

    if not pf["passed"]:
        if not args.fire:
            # A dry run must not litter the evidence tree. The failure is real
            # and reported; it becomes an attempt only when a run was intended.
            print("\nDRY RUN - preflight failed. No attempt written, no calls made.")
            return 1
        out = EV.next_attempt(ROOT, GENERATION)
        EV.write_evidence(out, "preflight.json", pf)
        EV.write_evidence(out, "NON_EVIDENCE.json",
                          {"marker": "NON_EVIDENCE", "reader_calls": 0,
                           "reason": "preflight failed; no model call was made",
                           "problems": pf["problems"],
                           "may_not_be_backfilled": True})
        print(f"FAILED CLOSED with zero calls -> {out}")
        return 1

    if not args.fire:
        print("\nDRY RUN - preflight passed, contract computed, zero calls made.")
        print(f"  request bodies sha256 : {contract['request_bodies_sha256_all'][:32]}")
        print(f"  runner sha256         : {contract['runner_sha256'][:32]}")
        print("Re-run with --fire to execute the 60 cases once each.")
        return 0

    out = EV.next_attempt(ROOT, GENERATION)
    EV.write_evidence(out, "preflight.json", pf)
    EV.write_evidence(out, "execution_contract.json", contract)   # BEFORE exposure

    started = time.time()
    responses = [call_once(c) for c in cases]
    elapsed = round(time.time() - started, 1)

    # Seal raw BEFORE any parse.
    raw_path = out / "reader_raw.jsonl"
    raw_path.write_text("\n".join(json.dumps(r, sort_keys=True) for r in responses) + "\n")
    raw_sha = sha(raw_path.read_text())
    EV.write_evidence(out, "raw_seal.json",
                      {"file": "reader_raw.jsonl", "sha256": raw_sha,
                       "sealed_before_parse": True, "responses": len(responses),
                       "elapsed_seconds": elapsed})

    by_case = {c["case_id"]: c for c in cases}
    completed = [r for r in responses if r["terminal_disposition"] == "COMPLETED"]
    rows = G116.grade_all(completed, by_case)
    gates = G116.control_gate(rows)
    estim = G116.estimands(rows, gates, unique_prompts=60)
    linkage_ok = (len(responses) == 60
                  and len({r["case_id"] for r in responses}) == 60
                  and all(r["request_sha256"] == contract["request_body_sha256"][r["case_id"]]
                          for r in responses))
    marker = G116.run_marker(gates, estim, linkage_ok=linkage_ok,
                             seal_ok=bool(raw_sha), manifest_ok=True)

    EV.write_evidence(out, "graded_rows.json", rows)
    EV.write_evidence(out, "control_gates.json", gates)
    EV.write_evidence(out, "estimands.json", estim)
    EV.write_evidence(out, f"{marker['marker']}.json",
                      {**marker, "elapsed_seconds": elapsed,
                       "served_models": sorted({r["served_model"] for r in responses}),
                       "dispositions": {d: sum(1 for r in responses
                                               if r["terminal_disposition"] == d)
                                        for d in {r["terminal_disposition"] for r in responses}}})
    print(f"\nWROTE {out}  ({elapsed}s)")
    print(f"  marker              : {marker['marker']}")
    print(f"  interpretable cores : {estim['cores_interpretable']}/12")
    print(f"  Q1 both orders      : {estim['Q1_cores_selecting_current_in_both_orders']}")
    print(f"  verify              : {EV.verify(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
