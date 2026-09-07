#!/usr/bin/env python3
"""The controlled reader run against the v6 protocol. STABLE PATH, no generation in the name.

Renamed from run_gen119_reader.py in Gen120. The old name carried GENERATION=119
and a SOURCE_COMMIT from the Gen116 line as module constants, so authorising a
run in any later generation meant editing a file the contract binds - which
invalidates the freeze that binds it. Bookkeeping cannot require a scientific
refreeze. Execution generation, source commit and authorisation are runtime
inputs now, each checked fail-closed before the first call.

Tracked and bound into the v6 contract BEFORE the freeze, because Gen118 hashed
only five files and omitted every run-bearing surface - the runner, the request
projection, the capture and seal path, the retry policy and the marker logic.
A contract that does not bind the thing that will run is not a freeze.

NOT AUTHORISED TO RUN. --fire refuses without control-plane authorisation.

60 frozen cases from the canonical gen118 attempt, resolved through
results/gen118/CANONICAL_ATTEMPT.md and never named here, executed once each. The
protocol is CONSUMED, never touched. Preflight fails closed with zero calls. Exact response bytes are appended to reader_journal.jsonl and FSYNCED as each
answer arrives, before any decode or parse. An interruption after case N leaves
N durable captures; the run is then over, and refuses to resume, because those
cases have already been exposed and the schedule is only valid once.

This paragraph has been wrong twice. It first promised bytes "sealed as it
arrives" while the code batched them after all 60 calls. It was then corrected to
describe the batch honestly - which made the docstring true and left the defect
in place. Sol ruled at Gen121 that the ordering itself was the problem, not the
description of it.

Phases, in order, and the order is the point:
    preflight   every gate; any failure means zero model calls
    freeze      the execution contract, hashed BEFORE exposure
    execute     60 calls; each answer journalled and fsynced as it arrives
    grade       once, with the FROZEN Gen116 grader, never a reimplementation
    marker      RUN_EVIDENCE or NON_EVIDENCE, derived by the frozen gate

60 cells across 12 independent cores. NOT 60 observations.
"""
from __future__ import annotations

import argparse, base64, hashlib, json, os, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff import evidence as EV                       # noqa: E402
from memory_bakeoff import reader_interference_v6 as V6         # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
import importlib.util as _ilu                                   # noqa: E402
_spec = _ilu.spec_from_file_location("grade_gen118_v6", ROOT / "scripts/grade_gen118_v6.py")
G116 = _ilu.module_from_spec(_spec); _spec.loader.exec_module(G116)   # noqa: E402

def _canonical() -> "Path":
    """Read the canonical attempt rather than naming it.

    Hardcoding the path means pointing at a new freeze edits this file, which
    invalidates the freeze that was just made - the same circularity as pinning
    the contract hash in a file the contract hashes. The pointer is the single
    source of truth; the manifest guards the contents.
    """
    marker = ROOT / "results/gen118/CANONICAL_ATTEMPT.md"
    # Match the declaration, not "whatever the first backtick holds". The old
    # parse took the first backtick-quoted token in a prose document, so any
    # edit introducing an earlier backtick silently retargeted the run or broke
    # preflight - failing closed by accident rather than by design. Found by
    # glm-5.3 at Gen120 round 4.
    import re as _re
    found = _re.search(r"\*\*`(attempt\d+)` is canonical\*\*", marker.read_text())
    if not found:
        raise SystemExit(f"REFUSING: {marker} carries no '**`attemptN` is canonical**' "
                         "declaration; the canonical attempt is not resolvable")
    return ROOT / "results/gen118" / found.group(1)


CANONICAL = _canonical()
# NOT a hardcoded constant. The runner is itself bound into the contract, so a
# literal hash here means the runner and the contract can never both be updated -
# each invalidates the other. Integrity of the contract FILE comes from the
# sealed attempt's manifest, which EV.verify checks below, so reading the
# expected value from it is safe and breaks the cycle.
def _expected_contract() -> str:
    import json as _j
    return _j.loads((CANONICAL / "reader_interference_v6_contract.json")
                    .read_text())["contract_sha256"]
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
def preflight(source_commit: str) -> dict:
    """Every gate. Any failure means zero model calls and a NON_EVIDENCE attempt."""
    problems: list[str] = []

    head = git("rev-parse", "HEAD")
    # The old runner RECORDED source_commit_expected and never compared it to
    # anything - provenance theatre. HEAD must be exactly the commit the
    # authorising instruction named, or the evidence is filed against code that
    # was not the code under authorisation.
    if head != source_commit:
        problems.append(f"HEAD {head[:12]} is not the authorised source commit "
                        f"{source_commit[:12]}")
    # Untracked files COUNT. Filtering '??' is how Gen114 shipped a runner that
    # did not exist at its own pinned commit, and how a drill later fired a live
    # doorbell. The tree is clean or it is not.
    dirt = git("status", "--porcelain")
    if dirt:
        problems.append(f"worktree not clean: {dirt.splitlines()[:3]}")

    # Check the pointer this runner actually consumes, not the vestigial gen116
    # one. Reading a stale pointer to decide a live run is how a gate ends up
    # guarding something nobody uses. Found by glm-5.3 at Gen120.
    if not (CANONICAL / "reader_interference_v6_contract.json").exists():
        problems.append(f"canonical pointer resolves to {CANONICAL.name}, which "
                        "holds no v6 contract")

    ev = EV.verify(CANONICAL)
    if not ev["verified"]:
        problems.append(f"canonical attempt manifest failed: {ev}")

    contract = json.loads((CANONICAL / "reader_interference_v6_contract.json").read_text())
    # RECOMPUTE the sealed hash from the sealed payload and source pins, exactly
    # as the freeze computed it, and compare.
    #
    # This used to compare contract["contract_sha256"] against a helper that read
    # THE SAME FIELD FROM THE SAME FILE, and its comment claimed it verified a
    # recomputation. It could never fail. Nothing in the run path recomputed the
    # sealed hash at all - it was protected only transitively, by the manifest
    # binding the file's bytes. Found by glm-5.3-flash at Gen120: "a check that
    # cannot fail reads exactly like a check that passes", in the file that
    # anatomises that pattern.
    payload = json.loads((CANONICAL / "reader_interference_v6_contract_payload.json").read_text())
    recomputed = hashlib.sha256(json.dumps({**payload, "source_sha256": contract["source_sha256"]},
                                           sort_keys=True, default=str).encode()).hexdigest()
    if recomputed != contract["contract_sha256"]:
        problems.append(f"SEALED CONTRACT HASH DOES NOT RECOMPUTE: declared "
                        f"{contract['contract_sha256'][:16]}, recomputed "
                        f"{recomputed[:16]}. The payload or its source pins changed.")

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
        problems.append("the canonical attempt's NON_EVIDENCE marker is modified "
                        "or reports prior calls")

    schedule = json.loads((CANONICAL / "reader_interference_v6_schedule.json").read_text())
    cases = schedule["cases"]
    hashes = json.loads((CANONICAL / "reader_interference_v6_prompt_hashes.json").read_text())
    if len(cases) != 60 or len({c["case_id"] for c in cases}) != 60:
        problems.append(f"schedule is not 60 unique cases: {len(cases)}")
    if len({c["core"] for c in cases}) != 12:
        problems.append("schedule does not carry 12 cores")
    if len(set(hashes.values())) != 60:
        problems.append(f"prompt hashes are not 60 unique: {len(set(hashes.values()))}")

    # The prompts we are about to send must still hash to the frozen values, and
    # the success predicate must be the frozen one, not a live redefinition.
    drift = [c["case_id"] for c in cases
             if sha(V6.project_prompt(c)) != hashes.get(c["case_id"])]
    if drift:
        problems.append(f"prompt drift against the frozen hashes: {drift[:3]}")
    if len(V6.ONTOLOGY) != 9:
        problems.append(f"ontology is {len(V6.ONTOLOGY)} classes, not the ruled nine")
    frozen_success = {k: list(v) for k, v in V6.SUCCESS.items()}
    if frozen_success != contract_success(contract):
        problems.append("success predicate differs from attempt4")

    lineage = subprocess.run(
        [sys.executable, "-m", "pytest", "-q",
         "tests/test_gen109_reader_interference.py", "tests/test_gen110_reader_execution.py",
         "tests/test_gen111_reader_v2.py", "tests/test_gen112_reader_v3.py",
         "tests/test_gen113_reader_v4.py", "tests/test_gen115_adjudication.py",
         "tests/test_gen116_reader_v5.py"],
        cwd=ROOT, capture_output=True, text=True,
        # Inherit the real environment. A hardcoded PATH=/usr/bin:/bin is
        # host-brittle: it fails in the SAFE direction (a spurious "lineage not
        # green" blocks an authorised run rather than corrupting one), but a gate
        # that fails for the wrong reason teaches people to ignore it.
        env={**os.environ, "PYTHONPATH": "src"})
    if lineage.returncode != 0:
        problems.append("reader-interference lineage is not green")

    ledger = ROOT / "reviews/LEDGER.md"
    if ledger.exists() and "| OPEN |" in ledger.read_text():
        problems.append("an open review finding remains in reviews/LEDGER.md")

    return {"head": head, "source_commit_expected": source_commit,
            "worktree_clean": not dirt, "canonical_attempt": str(CANONICAL.relative_to(ROOT)),
            "canonical_verified": ev["verified"],
            "contract_sha256": contract["contract_sha256"],
            "cases": len(cases), "cores": len({c["core"] for c in cases}),
            "unique_prompt_hashes": len(set(hashes.values())),
            "lineage_green": lineage.returncode == 0,
            "problems": problems, "passed": not problems}


def contract_success(contract: dict) -> dict:
    payload = json.loads((CANONICAL / "reader_interference_v6_contract_payload.json").read_text())
    return {k: list(v) for k, v in payload["success_states"].items()}


# ------------------------------------------------------------------ request body
def request_body(case: dict) -> dict:
    """The exact serialized projection. Bound into the fingerprint before exposure."""
    return {"model": READER,
            "messages": [{"role": "user", "content": V6.project_prompt(case)}],
            "temperature": TEMPERATURE, "seed": SEED,
            "max_tokens": MAX_TOKENS, "stream": False}


def freeze_contract(cases: list[dict], generation: int, source_commit: str,
                    authorised_by: str) -> dict:
    bodies = {c["case_id"]: json.dumps(request_body(c), sort_keys=True) for c in cases}
    return {
        "generation": generation, "evidence_class": EVIDENCE_CLASS,
        # Two separate facts, named separately. Calling the single value
        # "authorised_by_generation" conflated the generation that AUTHORISED the
        # run with the one EXECUTING it; they are required to match, which is the
        # typo gate, but the record must not imply they are the same thing.
        "authorisation": {"authorisation_generation": authorised_by,
                          "execution_generation": generation,
                          "required_to_match": True,
                          "source_commit": source_commit,
                          "supplied_at_runtime_not_hardcoded": True},
        "consumes": {"canonical_attempt": str(CANONICAL.relative_to(ROOT)),
                     "v6_contract_sha256": _expected_contract(),
                     "source_commit": source_commit},
        "reader": {"model": READER, "endpoint": ENDPOINT, "temperature": TEMPERATURE,
                   "seed_requested": SEED,
                   "seed_accepted": "NOT REPORTED - to be read from server evidence, never authored",
                   "thinking": "absent", "max_tokens": MAX_TOKENS,
                   "timeout_s": TIMEOUT_S, "transport_retries": TRANSPORT_RETRIES,
                   "scientific_response_may_never_be_replaced": True},
        "request_body_sha256": {k: sha(v) for k, v in bodies.items()},
        "request_bodies_sha256_all": sha("".join(bodies[k] for k in sorted(bodies))),
        "capture": {
            "raw_path": JOURNAL,
            "raw_is": "exact response bytes, base64, one append-only record per call",
            "written": "per call, flushed and fsynced BEFORE any decode or parse",
            "parsed_view": "reader_records.jsonl - re-serialised objects, NOT raw bytes",
            "seal": "sha256 over the journal, bound into the manifest",
            "transport_try_contains_only": "reading the response bytes",
            "after_bytes_exist_no_failure_may_retry": True,
            "undecodable_is_terminal": "TERMINAL_UNDECODABLE_RESPONSE",
            "malformed_json_is_terminal": "TERMINAL_MALFORMED_RESPONSE",
            "interrupted_run_is_not_resumable": True,
        },
        "runner_sha256": sha(Path(__file__).read_text()),
        "grader_sha256": sha((ROOT / "scripts/grade_gen118_v6.py").read_text()),
        "v6_module_sha256": sha((ROOT / "src/memory_bakeoff/reader_interference_v6.py").read_text()),
        "independent_unit": "core",
        "cells_are_not_observations": True,
    }


# ---------------------------------------------------------------------- execution
JOURNAL = "reader_journal.jsonl"


def call_once(case: dict, journal: Path) -> dict:
    """One case, once. Exact bytes on disk before anything interprets them.

    The ordering IS the science here, and it used to be wrong in two ways that
    the docstring cheerfully denied. Sol found both at Gen121:

    - `r.read().decode()` sat inside the transport `try`, so an HTTP 200 whose
      body was not valid UTF-8 raised inside the retry handler, its bytes were
      discarded, and the same case was asked again. That is retrying a scientific
      outcome - sampling until an answer parses.
    - nothing was written to disk until all sixty calls had returned, so a crash
      at call 59 destroyed fifty-nine answers that had already been given.

    The rule now: **the transport `try` contains exactly one thing, reading the
    bytes.** The moment bytes exist they are journalled and fsynced. Only then may
    anything decode, parse, inspect or classify them, and from that point no
    failure of any kind may cause a retry.
    """
    body = request_body(case)
    payload = json.dumps(body, sort_keys=True)
    attempts: list[dict] = []
    for attempt in range(TRANSPORT_RETRIES + 1):
        started = time.time()
        req = urllib.request.Request(ENDPOINT, data=payload.encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            # TRANSPORT ONLY. Nothing but obtaining the bytes belongs in here -
            # every line added to this block becomes retryable, and a retryable
            # scientific outcome is a repeatable experiment run until it agrees.
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                raw_bytes = r.read()
                status = r.status
        except Exception as exc:
            attempts.append({"attempt": attempt, "error": f"{type(exc).__name__}: {exc}",
                             "seconds": round(time.time() - started, 3)})
            continue

        # The server ANSWERED. Persist the exact bytes before anything reads them.
        seconds = round(time.time() - started, 3)
        EV.journal_append(journal, {
            "case_id": case["case_id"], "core": case["core"],
            "condition": case["condition"], "attempt": attempt,
            "request_sha256": sha(payload),
            "request_body_b64": base64.b64encode(payload.encode()).decode(),
            "http_status": status,
            "response_bytes_b64": base64.b64encode(raw_bytes).decode(),
            "response_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "response_len": len(raw_bytes),
            "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "seconds": seconds, "retry_history": attempts,
            "captured_before_any_decode": True,
        })

        common = {"case_id": case["case_id"], "core": case["core"],
                  "condition": case["condition"], "request_sha256": sha(payload),
                  "request_body": body, "http_status": status,
                  "response_sha256": hashlib.sha256(raw_bytes).hexdigest(),
                  "response_len": len(raw_bytes),
                  "seconds": seconds, "retry_history": attempts}

        try:
            raw = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            # Bytes arrived and are journalled. Undecodable is a RESULT.
            return {**common, "raw_response": None, "text": None,
                    "served_model": None, "finish_reason": None,
                    "decode_error": f"{type(exc).__name__}: {exc}",
                    "terminal_disposition": "TERMINAL_UNDECODABLE_RESPONSE"}
        try:
            obj = json.loads(raw)
            return {**common, "raw_response": raw,
                    "text": obj["choices"][0]["message"]["content"],
                    "served_model": obj.get("model"),
                    "finish_reason": obj["choices"][0].get("finish_reason"),
                    "terminal_disposition": "COMPLETED"}
        except Exception as exc:
            return {**common, "raw_response": raw, "text": None,
                    "served_model": None, "finish_reason": None,
                    "parse_error": f"{type(exc).__name__}: {exc}",
                    "terminal_disposition": "TERMINAL_MALFORMED_RESPONSE"}

    return {"case_id": case["case_id"], "core": case["core"],
            "condition": case["condition"], "request_sha256": sha(payload),
            "request_body": body, "http_status": None, "raw_response": None,
            "text": None, "served_model": None, "finish_reason": None,
            "retry_history": attempts,
            "terminal_disposition": "TERMINAL_TRANSPORT_FAILURE"}


def refuse_to_resume_an_exposed_run(out: Path) -> None:
    """An interrupted exposed run is finished, not paused.

    If a journal already exists in this attempt directory, cases have already
    been put in front of the reader. Continuing would silently re-expose them,
    and the schedule is only valid once. The run is over; whether a FRESH
    experiment happens is a control-plane decision, not a recovery step.
    """
    journal = Path(out) / JOURNAL
    if journal.exists():
        seen = sum(1 for line in journal.read_text().splitlines() if line.strip())
        raise SystemExit(
            f"REFUSING: {journal} already holds {seen} captured response(s). This "
            "attempt was interrupted after exposure. Those cases have been seen by "
            "the reader and may not be replayed. The attempt is NON_EVIDENCE; a "
            "fresh run requires a new control-plane authorisation, not a resume.")


def seal_agrees(out: Path) -> bool:
    """Do the seal, the manifest and the bytes on disk all say the same thing?

    Three sources that must agree. Comparing only two of them is how a hash in a
    seal came to be mistaken for manifest-binding.
    """
    seal = json.loads((out / "raw_seal.json").read_text())
    entry = json.loads((out / EV.MANIFEST).read_text())["artifacts"].get(seal["file"])
    if not entry:
        return False
    return seal["sha256"] == entry["sha256"] == EV.digest((out / seal["file"]).read_text())


# The exact inventory a run must have produced before its marker is derived. The
# marker itself is deliberately absent: it is written last, from the observation
# that this set is closed.
REQUIRED_PRE_MARKER = ("preflight.json", "execution_contract.json",
                       JOURNAL, "reader_records.jsonl", "raw_seal.json",
                       "graded_rows.json", "control_gates.json", "estimands.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fire", action="store_true",
                    help="actually call the reader; without it nothing is sent")
    ap.add_argument("--generation", type=int, required=True,
                    help="the generation that will WRITE this run's evidence")
    ap.add_argument("--source-commit", default="",
                    help="the commit the authorising instruction named, verbatim")
    ap.add_argument("--authorised-by", default="",
                    help="the control-plane generation authorising this run")
    args = ap.parse_args()

    # Authorisation is checked before anything else happens, and a non-empty
    # string is not authorisation. The generation is stated twice, from two
    # different places in the instruction, and both must agree - that is what
    # makes a typo or a stale copy-paste fail instead of running under the wrong
    # provenance. Zero calls, no attempt directory, on any disagreement.
    if args.fire:
        if not args.authorised_by:
            ap.error("REFUSING: --fire will not run without explicit control-plane "
                     "authorisation. Pass --authorised-by <generation> only when "
                     "an instruction actually says so.")
        if args.authorised_by.strip() != str(args.generation):
            ap.error(f"authorisation is for generation {args.authorised_by!r} but "
                     f"this run would write generation {args.generation}. Refusing "
                     "with zero calls; a stale or mistyped generation files "
                     "evidence under the wrong provenance.")
        if not args.source_commit:
            ap.error("--fire requires --source-commit, supplied verbatim from the "
                     "authorising instruction. Provenance is not inferred.")

    source_commit = args.source_commit or git("rev-parse", "HEAD")
    pf = preflight(source_commit)
    schedule = json.loads((CANONICAL / "reader_interference_v6_schedule.json").read_text())
    cases = schedule["cases"]
    contract = freeze_contract(cases, args.generation, source_commit, args.authorised_by)

    print(f"preflight: {'PASS' if pf['passed'] else 'FAIL'}")
    print(f"  generation            {args.generation}")
    print(f"  authorised_by         {args.authorised_by or '(none - dry run)'}")
    for k in ("head", "worktree_clean", "canonical_verified", "cases", "cores",
              "unique_prompt_hashes", "lineage_green"):
        print(f"  {k:<22}{pf[k]}")
    for problem in pf["problems"]:
        print(f"  PROBLEM: {problem}")

    if not pf["passed"]:
        if not args.fire:
            # A dry run must not litter the evidence tree. The failure is real
            # and reported; it becomes an attempt only when a run was intended.
            print("\nDRY RUN - preflight failed. No attempt written, no calls made.")
            return 1
        out = EV.next_attempt(ROOT, args.generation)
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

    out = EV.next_attempt(ROOT, args.generation)
    refuse_to_resume_an_exposed_run(out)
    journal = out / JOURNAL
    EV.write_evidence(out, "preflight.json", pf)
    EV.write_evidence(out, "execution_contract.json", contract)   # BEFORE exposure

    started = time.time()
    # Each call journals its own bytes and fsyncs before the next begins, so an
    # interruption after case N leaves exactly N durable captures.
    responses = [call_once(c, journal) for c in cases]
    elapsed = round(time.time() - started, 1)

    # The JOURNAL is the raw evidence - exact response bytes, base64, written and
    # fsynced as each answer arrived. It is bound into the manifest here because
    # it can only be sealed once the run is over, not because it was written now.
    #
    # `reader_records.jsonl` is the PARSED view. It used to be called
    # reader_raw.jsonl, which was false: it is re-serialised Python objects, and
    # calling that "raw bytes" is what let a decode failure look survivable.
    EV.manifest_existing(out, JOURNAL)
    raw_sha = EV.digest(journal.read_text())
    records = "\n".join(json.dumps(r, sort_keys=True) for r in responses) + "\n"
    EV.write_raw(out, "reader_records.jsonl", records)
    EV.write_evidence(out, "raw_seal.json",
                      {"file": JOURNAL, "sha256": raw_sha,
                       "captured_before_any_decode": True,
                       "written_per_call_and_fsynced": True,
                       "parsed_view_is_separate": "reader_records.jsonl",
                       "responses": len(responses),
                       "journal_lines": sum(1 for l in journal.read_text().splitlines() if l.strip()),
                       "elapsed_seconds": elapsed})

    by_case = {c["case_id"]: c for c in cases}
    completed = [r for r in responses if r["terminal_disposition"] == "COMPLETED"]
    rows = G116.grade_all(completed, by_case)
    gates = G116.control_gate(rows)
    estim = G116.estimands(rows, gates, unique_prompts=60,
                           # From the frozen schedule, so a core that vanished
                           # entirely is counted as absent rather than unseen.
                           expected_cores=sorted({c["core"] for c in cases}))
    linkage_ok = (len(responses) == 60
                  and sum(1 for r in responses
                          if r["terminal_disposition"] == "COMPLETED") == 60
                  and len({r["case_id"] for r in responses}) == 60
                  and all(r["request_sha256"] == contract["request_body_sha256"][r["case_id"]]
                          for r in responses))

    EV.write_evidence(out, "graded_rows.json", rows)
    EV.write_evidence(out, "control_gates.json", gates)
    EV.write_evidence(out, "estimands.json", estim)

    # The pre-marker evidence set is now complete and closed. VERIFY it, and let
    # that observation decide the marker. The previous runner passed
    # manifest_ok as a literal true, which made the strongest claim in the whole
    # apparatus - "the evidence is intact" - an assertion by its author rather
    # than a measurement. The marker is written last, so it is never verifying
    # itself.
    closure = EV.verify_closed(out, REQUIRED_PRE_MARKER)
    seal_ok = seal_agrees(out)
    marker = G116.run_marker(gates, estim, linkage_ok=linkage_ok,
                             seal_ok=seal_ok, manifest_ok=closure["closed"])

    EV.write_evidence(out, f"{marker['marker']}.json",
                      {**marker, "elapsed_seconds": elapsed,
                       "evidence_closure": closure,
                       "seal_agrees_manifest_and_disk": seal_ok,
                       "served_models": sorted({r["served_model"] for r in responses}),
                       "dispositions": {d: sum(1 for r in responses
                                               if r["terminal_disposition"] == d)
                                        for d in {r["terminal_disposition"] for r in responses}}})
    final = EV.verify(out)
    print(f"\nWROTE {out}  ({elapsed}s)")
    print(f"  marker              : {marker['marker']}")
    print(f"  pre-marker closure  : {closure['closed']}")
    print(f"  seal three-way      : {seal_ok}")
    print(f"  interpretable cores : {estim['cores_interpretable']}/12")
    print(f"  Q1 both orders      : {estim['Q1_cores_selecting_current_in_both_orders']}")
    print(f"  verify              : {final}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
