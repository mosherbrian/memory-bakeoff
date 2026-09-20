#!/usr/bin/env python3
"""Independent, standard-library gate for QUEUE row S12-2.

Written from the supplied row text. Does not execute submitted code.

Usage:
    python check.py [ROOT]
    python check.py --root ROOT
    python check.py --selftest

ROOT defaults to this script's directory.

Evidence contract
-----------------
declaration.json fixes:
  schema_version: 1
  rule:
    family: "corpus-coverage"
    decision: "supported_fraction_lt_threshold"
    min_document_frequency: positive integer
    content_stopwords: sorted, unique lowercase ASCII alphanumeric tokens
  thresholds: nonempty, strictly increasing numeric grid in [0, 1]
  retrieval: {algorithm: "bm25", k1: positive number, b: [0,1], top_k: 1}
  execution:
    local: true
    llm_calls: 0
    cost_usd: 0
    harness: "S7-1"
    protocol: "declare-then-run/sha-bound-rows"
  artifacts:
    declaration_cases: {path: relative path, sha256: SHA256}
    holdout_cases: {path: relative path, sha256: SHA256}
    generator: {path: relative path, sha256: SHA256}
    results: {path: relative path}
    report: {path: relative path}
    provenance: {path: relative path}

All referenced files are required, distinct, and contained in ROOT.
Case files are {"cases": [{id, query, documents: [{id, text}],
                          relevant_ids: [document_id, ...]}, ...]}.
The declaration set has ten cases: five useful and five irrelevant.
The holdout has both classes, separate case IDs, and no copied case bodies.

The pinned mechanical generator is a JSON specification:
  {algorithm: "coverage-cases-v1", seed: integer, count: positive even integer}
Its complete deterministic implementation is mechanical_cases() below.
The gate reconstructs the holdout and compares its complete contents.

Coverage is the fraction of distinct query content tokens supported by at least
min_document_frequency documents in the case corpus. Tokenization is lowercase
ASCII alphanumeric runs. Empty content has coverage zero. Abstain exactly when
coverage < threshold. Coverage feature selection never changes the BM25 query.
The coverage decision receives no scores or score distribution.

BM25 uses log(1 + (N - df + .5)/(df + .5)), declared k1 and b,
all query tokens including repetitions, document-ID tie breaking, and no result
if all scores are zero.

Results are JSONL, one row per case per declared threshold on each set:
  set, case_id, threshold, declaration_sha256, cases_sha256,
  query_tokens, content_tokens, document_frequencies, support_fraction,
  baseline_top1, decision, returned_top1
decision is "abstain" or "retrieve". Exact keys are required.

Report JSON is {"sets": {
  "declaration": {"grid": [entry, ...]},
  "holdout": {"grid": [entry, ...]}
}}. Every grid entry contains threshold plus every counter in METRICS.
Both grids follow declaration order. No selected threshold is permitted.
Honest refutations and honest survivals are both acceptable.

Provenance JSON is {"events": [...]} with strictly increasing timezone-aware
ISO timestamps in "at". Required singleton events:
  pin_generator: {event, at, sha256}
  freeze_holdout: {event, at, sha256, generator_sha256}
  declare: {event, at, sha256, inputs: {declaration_cases: SHA256}}
  run: {event, at, sha256}
  finish: {event, at, results_sha256, report_sha256}
Read events: {event: "read", at, actor, artifact, sha256}.
The generator is pinned before holdout freeze; freeze precedes declaration;
declaration precedes run; run precedes finish.
Before declaration, the declarer reads the declaration cases only.
Runner reads of both case sets occur between declaration and run.
All hashes are checked against actual bytes.

Evidence limits: unsigned files cannot establish absence of unlogged reads,
hidden LLM calls, earlier runs, or undeclared implementations. Nor can ten
submitted cases be authenticated as the historical original without an external
anchor. This gate verifies supplied protocol evidence and independently replays
the claimed experiment; it does not claim that hashes prove these limitations.

Exit contract: 0 clean; 1 with FINDING [NAME]: message; no traceback.
Selftest builds its own fixtures. Each independent corruption must fail with
its specifically expected finding, including rehashed substantive corruptions
that cannot be rejected merely because a checksum changed.
"""

import argparse
import copy
import hashlib
import json
import math
import re
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


MAX_BYTES = 32 * 1024 * 1024
MAX_CASES = 2000
MAX_GRID = 128
TOKEN = re.compile(r"[a-z0-9]+")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SETS = ("declaration", "holdout")
INPUTS = ("declaration_cases", "holdout_cases", "generator")
ARTIFACTS = INPUTS + ("results", "report", "provenance")
DECLARATION_KEYS = {
    "schema_version", "rule", "thresholds", "retrieval", "execution", "artifacts",
}
RULE_KEYS = {
    "family", "decision", "min_document_frequency", "content_stopwords",
}
ROW_KEYS = {
    "set", "case_id", "threshold", "declaration_sha256", "cases_sha256",
    "query_tokens", "content_tokens", "document_frequencies", "support_fraction",
    "baseline_top1", "decision", "returned_top1",
}
METRICS = (
    "irrelevant_total",
    "irrelevant_baseline_retrieved",
    "irrelevant_rejected",
    "useful_total",
    "baseline_useful_retrieved",
    "useful_retrieved",
    "useful_lost",
)
EVENT_KEYS = {
    "pin_generator": {"event", "at", "sha256"},
    "freeze_holdout": {"event", "at", "sha256", "generator_sha256"},
    "declare": {"event", "at", "sha256", "inputs"},
    "run": {"event", "at", "sha256"},
    "finish": {"event", "at", "results_sha256", "report_sha256"},
    "read": {"event", "at", "actor", "artifact", "sha256"},
}


class Finding(Exception):
    def __init__(self, marker, message):
        super().__init__(message)
        self.marker = marker
        self.message = message


def require(condition, marker, message):
    if not condition:
        raise Finding(marker, message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def encode_rows(rows):
    return b"".join(
        (json.dumps(row, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
        for row in rows
    )


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-finite JSON constant: " + value)


def parse_json(data, label):
    try:
        return json.loads(
            data,
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Finding("JSON_INVALID", label + ": " + str(exc)) from None


def number(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, ValueError):
        return False


def valid_sha(value):
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def tokens(text):
    return TOKEN.findall(text.lower())


def read_bytes(path):
    require(path.is_file(), "FILE_REQUIRED", "Required file missing: " + str(path))
    require(path.stat().st_size <= MAX_BYTES, "FILE_SIZE", str(path))
    data = path.read_bytes()
    require(len(data) <= MAX_BYTES, "FILE_SIZE", str(path))
    return data


def validate_declaration(declaration):
    require(
        isinstance(declaration, dict)
        and set(declaration) == DECLARATION_KEYS
        and type(declaration.get("schema_version")) is int
        and declaration["schema_version"] == 1,
        "DECLARATION_SCHEMA",
        "Declare the exact rule, grid, retrieval, execution, and artifact bindings.",
    )
    rule = declaration["rule"]
    require(isinstance(rule, dict), "RULE_INPUTS", "Rule must be an object.")
    require(
        rule.get("family") == "corpus-coverage",
        "FAMILY_REFUTED",
        "The third decision must use corpus coverage.",
    )
    require(
        set(rule) == RULE_KEYS,
        "RULE_INPUTS",
        "Only corpus-coverage inputs are allowed; no score distribution inputs.",
    )
    require(
        rule["decision"] == "supported_fraction_lt_threshold",
        "RULE_SEMANTICS",
        "Fix the coverage comparison and its exact boundary before running.",
    )
    require(
        type(rule["min_document_frequency"]) is int
        and rule["min_document_frequency"] >= 1,
        "RULE_DF",
        "Minimum document-frequency support must be a positive integer.",
    )
    stopwords = rule["content_stopwords"]
    require(
        isinstance(stopwords, list)
        and all(
            isinstance(word, str) and TOKEN.fullmatch(word) is not None
            for word in stopwords
        )
        and stopwords == sorted(set(stopwords)),
        "CONTENT_WORDS",
        "Declare sorted, unique coverage stopwords.",
    )
    grid = declaration["thresholds"]
    require(
        isinstance(grid, list)
        and 1 <= len(grid) <= MAX_GRID
        and all(number(value) and 0 <= value <= 1 for value in grid)
        and all(left < right for left, right in zip(grid, grid[1:])),
        "GRID_INVALID",
        "Declare a finite, strictly increasing threshold grid in [0, 1].",
    )
    retrieval = declaration["retrieval"]
    require(
        isinstance(retrieval, dict)
        and set(retrieval) == {"algorithm", "k1", "b", "top_k"}
        and retrieval["algorithm"] == "bm25"
        and number(retrieval["k1"])
        and 0 < retrieval["k1"] <= 1000000
        and number(retrieval["b"])
        and 0 <= retrieval["b"] <= 1
        and type(retrieval["top_k"]) is int
        and retrieval["top_k"] == 1,
        "RETRIEVAL_SPEC",
        "Fix a replayable BM25 baseline.",
    )
    execution = declaration["execution"]
    require(
        isinstance(execution, dict)
        and set(execution) == {
            "local", "llm_calls", "cost_usd", "harness", "protocol",
        },
        "EXECUTION_SCHEMA",
        "Declare local, zero-cost, no-LLM execution and harness protocol.",
    )
    require(execution["local"] is True, "NONLOCAL_EXECUTION", "Run locally.")
    require(
        type(execution["llm_calls"]) is int and execution["llm_calls"] == 0,
        "LLM_DEPENDENCY",
        "The experiment must use no LLM calls.",
    )
    require(
        number(execution["cost_usd"]) and execution["cost_usd"] == 0,
        "NONZERO_COST",
        "The experiment must cost zero dollars.",
    )
    require(
        execution["harness"] == "S7-1"
        and execution["protocol"] == "declare-then-run/sha-bound-rows",
        "HARNESS_PROTOCOL",
        "Reuse the S7-1 declare-then-run, SHA-bound-row protocol.",
    )


def load_artifacts(root, declaration):
    refs = declaration["artifacts"]
    require(
        isinstance(refs, dict) and set(refs) == set(ARTIFACTS),
        "ARTIFACT_MANIFEST",
        "Require both case sets, the generator, results, report, and provenance.",
    )
    used = {root / "declaration.json"}
    blobs = {}
    for name in ARTIFACTS:
        ref = refs[name]
        keys = {"path", "sha256"} if name in INPUTS else {"path"}
        require(
            isinstance(ref, dict) and set(ref) == keys,
            "ARTIFACT_MANIFEST",
            "Invalid artifact reference: " + name,
        )
        raw_path = ref["path"]
        require(
            isinstance(raw_path, str) and raw_path,
            "PATH_INVALID",
            "Artifact paths must be nonempty relative paths.",
        )
        relative = Path(raw_path)
        require(
            not relative.is_absolute()
            and ".." not in relative.parts
            and "\x00" not in raw_path,
            "PATH_INVALID",
            "Artifact path escapes ROOT: " + name,
        )
        path = (root / relative).resolve()
        require(
            path != root and root in path.parents,
            "PATH_INVALID",
            "Artifact resolves outside ROOT: " + name,
        )
        require(
            path not in used,
            "ARTIFACT_ALIAS",
            "Each artifact must have its own file: " + name,
        )
        used.add(path)
        blobs[name] = read_bytes(path)
        if name in INPUTS:
            require(
                valid_sha(ref["sha256"]) and sha(blobs[name]) == ref["sha256"],
                "ARTIFACT_HASH",
                "Declared input hash does not match bytes: " + name,
            )
    return blobs


def validate_cases(value, label):
    require(
        isinstance(value, dict)
        and set(value) == {"cases"}
        and isinstance(value["cases"], list)
        and 1 <= len(value["cases"]) <= MAX_CASES,
        "CASESET_SCHEMA",
        label + " must contain a nonempty case list.",
    )
    ids = set()
    for case in value["cases"]:
        require(
            isinstance(case, dict)
            and set(case) == {"id", "query", "documents", "relevant_ids"},
            "CASE_SCHEMA",
            label + ": each case must declare query, corpus, and relevance.",
        )
        require(
            isinstance(case["id"], str) and case["id"] and case["id"] not in ids,
            "CASE_ID",
            label + ": case IDs must be nonempty and unique.",
        )
        ids.add(case["id"])
        require(
            isinstance(case["query"], str) and bool(tokens(case["query"])),
            "CASE_QUERY",
            label + ": a tokenizable query is required.",
        )
        docs = case["documents"]
        require(
            isinstance(docs, list) and 1 <= len(docs) <= MAX_CASES,
            "CASE_CORPUS",
            label + ": a nonempty case corpus is required.",
        )
        doc_ids = set()
        for doc in docs:
            require(
                isinstance(doc, dict)
                and set(doc) == {"id", "text"}
                and isinstance(doc["id"], str)
                and doc["id"]
                and doc["id"] not in doc_ids
                and isinstance(doc["text"], str),
                "CASE_DOCUMENT",
                label + ": documents require unique IDs and text.",
            )
            doc_ids.add(doc["id"])
        relevant = case["relevant_ids"]
        require(
            isinstance(relevant, list)
            and all(isinstance(item, str) and item in doc_ids for item in relevant)
            and len(relevant) == len(set(relevant)),
            "CASE_LABELS",
            label + ": relevance labels must refer to distinct corpus documents.",
        )
    return value["cases"]


def case_body(case):
    return encode({
        "query": case["query"],
        "documents": sorted(
            ({"text": doc["text"]} for doc in case["documents"]),
            key=lambda doc: doc["text"],
        ),
    })


def validate_set_relationship(declaration_cases, holdout_cases):
    useful = sum(bool(case["relevant_ids"]) for case in declaration_cases)
    require(
        len(declaration_cases) == 10 and useful == 5,
        "DECLARATION_CASES",
        "The declaration set must contain the original ten-case shape, 5/5.",
    )
    useful_holdout = sum(bool(case["relevant_ids"]) for case in holdout_cases)
    require(
        0 < useful_holdout < len(holdout_cases),
        "HOLDOUT_CLASSES",
        "The holdout must measure both useful and irrelevant cases.",
    )
    declaration_ids = {case["id"] for case in declaration_cases}
    declaration_bodies = {case_body(case) for case in declaration_cases}
    require(
        all(
            case["id"] not in declaration_ids
            and case_body(case) not in declaration_bodies
            for case in holdout_cases
        ),
        "HOLDOUT_OVERLAP",
        "Holdout cases must be separate from the declaration cases.",
    )


def mechanical_cases(spec):
    """Fully specified local generator; no filesystem, model, or score inputs."""
    seed = spec["seed"]
    cases = []
    for index in range(spec["count"]):
        topic = "topic" + str(seed) + "x" + str(index)
        absent = "absent" + str(seed) + "x" + str(index)
        useful = index % 2 == 0
        if index % 4 == 1:
            query = absent + " unknown"
        elif index % 4 == 2:
            query = topic + " guide"
        else:
            query = topic + " " + absent
        cases.append({
            "id": "generated-" + str(seed) + "-" + str(index),
            "query": query,
            "documents": [
                {"id": "a", "text": topic + " guide " + topic},
                {"id": "b", "text": "background reference"},
            ],
            "relevant_ids": ["a"] if useful else [],
        })
    return {"cases": cases}


def validate_generator(spec, holdout):
    require(
        isinstance(spec, dict)
        and set(spec) == {"algorithm", "seed", "count"}
        and spec["algorithm"] == "coverage-cases-v1"
        and type(spec["seed"]) is int
        and 0 <= spec["seed"] <= 2**63 - 1
        and type(spec["count"]) is int
        and 2 <= spec["count"] <= MAX_CASES
        and spec["count"] % 2 == 0,
        "GENERATOR_SPEC",
        "Pin the complete supported mechanical generator, seed, and count.",
    )
    require(
        holdout == mechanical_cases(spec),
        "HOLDOUT_GENERATION",
        "The complete holdout must reproduce from its pinned generator.",
    )


def bm25_top1(case, retrieval):
    docs = [(doc["id"], Counter(tokens(doc["text"]))) for doc in case["documents"]]
    lengths = [sum(counts.values()) for _, counts in docs]
    average_length = sum(lengths) / len(docs)
    if average_length == 0:
        return None
    df = Counter()
    for _, counts in docs:
        df.update(counts.keys())
    query = tokens(case["query"])
    k1, b = retrieval["k1"], retrieval["b"]
    scores = []
    for (doc_id, counts), length in zip(docs, lengths):
        score = 0.0
        for term in query:
            frequency = counts.get(term, 0)
            if not frequency:
                continue
            idf = math.log(1 + (len(docs) - df[term] + 0.5) / (df[term] + 0.5))
            denominator = frequency + k1 * (1 - b + b * length / average_length)
            score += idf * frequency * (k1 + 1) / denominator
        scores.append((score, doc_id))
    best_score, best_id = min(scores, key=lambda item: (-item[0], item[1]))
    return best_id if best_score > 0 else None


def coverage_evidence(case, rule):
    """Deliberately accepts only query/corpus and coverage-rule inputs."""
    query_tokens = tokens(case["query"])
    content = sorted(set(query_tokens) - set(rule["content_stopwords"]))
    corpus = [set(tokens(doc["text"])) for doc in case["documents"]]
    frequencies = {
        term: sum(term in document for document in corpus)
        for term in content
    }
    supported = sum(
        frequencies[term] >= rule["min_document_frequency"]
        for term in content
    )
    fraction = supported / len(content) if content else 0.0
    return query_tokens, content, frequencies, fraction


def replay(case, declaration, threshold):
    query, content, frequencies, fraction = coverage_evidence(
        case, declaration["rule"],
    )
    abstain = fraction < threshold
    baseline = bm25_top1(case, declaration["retrieval"])
    return {
        "query_tokens": query,
        "content_tokens": content,
        "document_frequencies": frequencies,
        "support_fraction": fraction,
        "baseline_top1": baseline,
        "decision": "abstain" if abstain else "retrieve",
        "returned_top1": None if abstain else baseline,
    }


def measurements(cases, declaration, threshold):
    result = {name: 0 for name in METRICS}
    for case in cases:
        outcome = replay(case, declaration, threshold)
        baseline = outcome["baseline_top1"]
        returned = outcome["returned_top1"]
        if case["relevant_ids"]:
            result["useful_total"] += 1
            before = baseline in case["relevant_ids"]
            after = returned in case["relevant_ids"]
            result["baseline_useful_retrieved"] += int(before)
            result["useful_retrieved"] += int(after)
            result["useful_lost"] += int(before and not after)
        else:
            result["irrelevant_total"] += 1
            result["irrelevant_baseline_retrieved"] += int(baseline is not None)
            result["irrelevant_rejected"] += int(outcome["decision"] == "abstain")
    return result


def validate_provenance(value, hashes):
    require(
        isinstance(value, dict)
        and set(value) == {"events"}
        and isinstance(value["events"], list)
        and value["events"],
        "PROVENANCE_SCHEMA",
        "Require a chronological protocol event log.",
    )
    events = value["events"]
    positions = {}
    previous_time = None
    for index, event in enumerate(events):
        require(
            isinstance(event, dict)
            and isinstance(event.get("event"), str)
            and event["event"] in EVENT_KEYS
            and set(event) == EVENT_KEYS[event["event"]],
            "PROVENANCE_EVENT",
            "An event is missing required fields or contains undeclared fields.",
        )
        require(
            isinstance(event["at"], str),
            "PROVENANCE_TIME",
            "Event timestamps must be strings.",
        )
        try:
            timestamp = datetime.fromisoformat(event["at"].replace("Z", "+00:00"))
        except (ValueError, OverflowError):
            raise Finding("PROVENANCE_TIME", "Invalid event timestamp.") from None
        require(
            timestamp.tzinfo is not None and timestamp.utcoffset() is not None,
            "PROVENANCE_TIME",
            "Event timestamps must include a timezone.",
        )
        require(
            previous_time is None or previous_time < timestamp,
            "PROVENANCE_TIME",
            "Event timestamps must be strictly increasing.",
        )
        previous_time = timestamp
        if event["event"] != "read":
            require(
                event["event"] not in positions,
                "PROVENANCE_SINGLETON",
                "Protocol event repeated: " + event["event"],
            )
            positions[event["event"]] = index
    required_events = set(EVENT_KEYS) - {"read"}
    require(
        set(positions) == required_events,
        "PROVENANCE_REQUIRED",
        "Pin, freeze, declare, run, and finish must all be recorded.",
    )
    require(
        positions["pin_generator"] < positions["freeze_holdout"],
        "GENERATOR_NOT_PINNED",
        "Pin the generator before freezing holdout.",
    )
    require(
        positions["freeze_holdout"] < positions["declare"],
        "HOLDOUT_NOT_FROZEN",
        "Freeze the generated holdout before declaration.",
    )
    require(
        positions["declare"] < positions["run"],
        "RUN_BEFORE_DECLARE",
        "The exact declaration must precede any recorded run.",
    )
    require(
        positions["run"] < positions["finish"],
        "FINISH_BEFORE_RUN",
        "The bound outputs must be recorded after running.",
    )
    pin = events[positions["pin_generator"]]
    freeze = events[positions["freeze_holdout"]]
    declare = events[positions["declare"]]
    run = events[positions["run"]]
    finish = events[positions["finish"]]
    require(
        pin["sha256"] == hashes["generator"]
        and freeze["generator_sha256"] == hashes["generator"],
        "GENERATOR_BINDING",
        "Pin and freeze must bind the actual generator bytes.",
    )
    require(
        freeze["sha256"] == hashes["holdout_cases"],
        "HOLDOUT_FREEZE_BINDING",
        "Freeze must bind the actual held-out cases.",
    )
    require(
        declare["sha256"] == hashes["declaration"],
        "DECLARATION_BINDING",
        "Declaration event must bind the exact declaration file.",
    )
    require(
        isinstance(declare["inputs"], dict)
        and set(declare["inputs"]) == {"declaration_cases"}
        and declare["inputs"]["declaration_cases"] == hashes["declaration_cases"],
        "DECLARATION_INPUTS",
        "The declaration's case input must be the original set only.",
    )
    require(
        run["sha256"] == hashes["declaration"],
        "RUN_DECLARATION_BINDING",
        "Run must bind the preregistered declaration.",
    )
    require(
        finish["results_sha256"] == hashes["results"]
        and finish["report_sha256"] == hashes["report"],
        "OUTPUT_BINDING",
        "Finish must bind both result rows and the separate-set report.",
    )
    declarer_read = False
    runner_reads = set()
    for index, event in enumerate(events):
        if event["event"] != "read":
            continue
        require(
            event["actor"] in ("declarer", "runner")
            and event["artifact"] in INPUTS,
            "READ_SCHEMA",
            "Reads must identify a known actor and input artifact.",
        )
        artifact = event["artifact"]
        require(
            event["sha256"] == hashes[artifact],
            "READ_BINDING",
            "Read event does not bind the actual input bytes.",
        )
        if event["actor"] == "declarer":
            if index < positions["declare"]:
                require(
                    artifact != "holdout_cases",
                    "HOLDOUT_READ_AT_DECLARATION",
                    "The declarer must not read held-out cases before declaration.",
                )
                require(
                    artifact == "declaration_cases",
                    "DECLARATION_INPUT_LEAK",
                    "Before declaration the declarer may read only original cases.",
                )
                declarer_read = True
        else:
            require(
                positions["declare"] < index < positions["run"],
                "RUN_READ_ORDER",
                "Runner input reads must occur after declaration and before run.",
            )
            runner_reads.add(artifact)
    require(
        declarer_read,
        "DECLARATION_INPUT_UNREAD",
        "Record the declarer's original-case read before declaration.",
    )
    require(
        {"declaration_cases", "holdout_cases"} <= runner_reads,
        "RUN_INPUT_UNREAD",
        "The run must read both case sets after declaration.",
    )


def validate_rows(data, declaration, cases, hashes):
    lines = data.splitlines()
    require(
        lines and all(line.strip() for line in lines),
        "RESULTS_EMPTY",
        "Results must be nonempty JSONL without blank rows.",
    )
    by_id = {
        name: {case["id"]: case for case in cases[name]}
        for name in SETS
    }
    expected_keys = {
        (name, case["id"], threshold)
        for name in SETS
        for case in cases[name]
        for threshold in declaration["thresholds"]
    }
    seen = set()
    for line_number, line in enumerate(lines, 1):
        row = parse_json(line, "results line " + str(line_number))
        require(
            isinstance(row, dict) and set(row) == ROW_KEYS,
            "ROW_SCHEMA",
            "Every row must provide the complete declared coverage evidence.",
        )
        name = row["set"]
        require(
            isinstance(name, str) and name in SETS,
            "ROW_SET",
            "Each row must explicitly identify declaration or holdout.",
        )
        require(
            isinstance(row["case_id"], str) and row["case_id"] in by_id[name],
            "ROW_CASE",
            "Row refers to an unknown case in its named set.",
        )
        threshold = row["threshold"]
        require(
            number(threshold) and threshold in declaration["thresholds"],
            "ROW_THRESHOLD",
            "Every result threshold must have been preregistered.",
        )
        key = (name, row["case_id"], threshold)
        require(key not in seen, "ROW_DUPLICATE", "Duplicate case/threshold row.")
        seen.add(key)
        require(
            row["declaration_sha256"] == hashes["declaration"],
            "ROW_DECLARATION_BINDING",
            "Every result row must bind the exact preregistered declaration.",
        )
        require(
            row["cases_sha256"] == hashes[name + "_cases"],
            "ROW_CASESET_BINDING",
            "Every result row must bind its own case-set bytes.",
        )
        expected = replay(by_id[name][row["case_id"]], declaration, threshold)
        require(
            row["query_tokens"] == expected["query_tokens"],
            "TOKEN_FILTERING",
            "BM25 must receive the complete tokenized query without removals.",
        )
        require(
            row["content_tokens"] == expected["content_tokens"],
            "CONTENT_FEATURES",
            "Coverage content tokens must follow the preregistered definition.",
        )
        frequencies = row["document_frequencies"]
        require(
            isinstance(frequencies, dict)
            and all(type(value) is int for value in frequencies.values())
            and frequencies == expected["document_frequencies"],
            "DOCUMENT_FREQUENCY",
            "Support must use document frequency in this case's corpus.",
        )
        require(
            number(row["support_fraction"])
            and math.isclose(
                row["support_fraction"], expected["support_fraction"],
                rel_tol=0, abs_tol=1e-12,
            ),
            "COVERAGE_FRACTION",
            "Reported coverage does not match declared corpus support.",
        )
        require(
            row["baseline_top1"] == expected["baseline_top1"],
            "BM25_BASELINE",
            "Baseline retrieval must match full-query BM25 replay.",
        )
        require(
            row["decision"] == expected["decision"],
            "COVERAGE_DECISION",
            "Abstention must follow the exact declared coverage rule.",
        )
        require(
            row["returned_top1"] == expected["returned_top1"],
            "RETRIEVAL_OUTCOME",
            "The rule may abstain or retain baseline retrieval; it may not rerank.",
        )
    require(
        seen == expected_keys,
        "GRID_RESULTS_INCOMPLETE",
        "Require every case at every declared threshold on both sets.",
    )


def validate_report(report, declaration, cases):
    require(
        isinstance(report, dict) and set(report) == {"sets"},
        "REPORT_SELECTION",
        "Report the entire grid as data without a selected threshold.",
    )
    require(
        isinstance(report["sets"], dict) and set(report["sets"]) == set(SETS),
        "SETS_SEPARATE",
        "Report declaration and holdout separately; pooled results are insufficient.",
    )
    for name in SETS:
        entry = report["sets"][name]
        require(
            isinstance(entry, dict)
            and set(entry) == {"grid"}
            and isinstance(entry["grid"], list),
            "REPORT_SET_SCHEMA",
            "Each set must contain only its complete grid.",
        )
        grid = entry["grid"]
        require(
            len(grid) == len(declaration["thresholds"]),
            "REPORT_GRID",
            "Both reports must retain every preregistered threshold.",
        )
        for item, threshold in zip(grid, declaration["thresholds"]):
            require(
                isinstance(item, dict)
                and set(item) == {"threshold"} | set(METRICS),
                "REPORT_METRICS",
                "Report rejection, useful loss, and their denominators on both sets.",
            )
            require(
                number(item["threshold"]) and item["threshold"] == threshold,
                "REPORT_GRID",
                "Report the declared grid in declaration order.",
            )
            expected = measurements(cases[name], declaration, threshold)
            for metric in METRICS:
                require(
                    type(item[metric]) is int and item[metric] == expected[metric],
                    "REPORT_" + name.upper() + "_" + metric.upper(),
                    "Incorrect " + metric + " on " + name
                    + " at threshold " + str(threshold) + ".",
                )


def check(root):
    root = Path(root).resolve()
    declaration_path = root / "declaration.json"
    require(
        declaration_path.resolve() == declaration_path,
        "PATH_INVALID",
        "declaration.json must not resolve through a symlink outside its location.",
    )
    declaration_bytes = read_bytes(declaration_path)
    declaration = parse_json(declaration_bytes, "declaration.json")
    validate_declaration(declaration)
    blobs = load_artifacts(root, declaration)
    parsed = {
        name: parse_json(blobs[name], name)
        for name in ARTIFACTS if name != "results"
    }
    cases = {
        name: validate_cases(parsed[name + "_cases"], name)
        for name in SETS
    }
    validate_set_relationship(cases["declaration"], cases["holdout"])
    validate_generator(parsed["generator"], parsed["holdout_cases"])
    hashes = {name: sha(blob) for name, blob in blobs.items()}
    hashes["declaration"] = sha(declaration_bytes)
    validate_provenance(parsed["provenance"], hashes)
    validate_rows(blobs["results"], declaration, cases, hashes)
    validate_report(parsed["report"], declaration, cases)


# Fixture construction and mutation below are used only by --selftest.
# Mutated fixtures normally receive fresh, consistent hashes. Thus a false
# outcome, leaked holdout, or pooled report must fail its substantive check.


def retime(events):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for index, event in enumerate(events):
        event["at"] = (start + timedelta(seconds=index)).isoformat()


def event_named(bundle, name):
    return next(
        event for event in bundle["provenance"]["events"]
        if event["event"] == name
    )


def populate_outputs(bundle):
    declaration = bundle["declaration"]
    bundle["results"] = []
    bundle["report"] = {"sets": {}}
    for name in SETS:
        cases = bundle[name + "_cases"]["cases"]
        bundle["report"]["sets"][name] = {
            "grid": [
                dict(
                    threshold=threshold,
                    **measurements(cases, declaration, threshold),
                )
                for threshold in declaration["thresholds"]
            ],
        }
        for case in cases:
            for threshold in declaration["thresholds"]:
                bundle["results"].append({
                    "set": name,
                    "case_id": case["id"],
                    "threshold": threshold,
                    "declaration_sha256": "",
                    "cases_sha256": "",
                    **replay(case, declaration, threshold),
                })


def fixture():
    generator = {"algorithm": "coverage-cases-v1", "seed": 22, "count": 4}
    original = mechanical_cases({
        "algorithm": "coverage-cases-v1", "seed": 11, "count": 10,
    })
    # Keep the original fixture's irrelevant baseline queries retrieving.
    for index, case in enumerate(original["cases"]):
        if index % 4 == 1:
            case["query"] = "topic11x" + str(index) + " absent11x" + str(index)
    # A repeated stopword must survive in BM25 but not coverage features.
    original["cases"][0]["query"] += " the the"
    declaration = {
        "schema_version": 1,
        "rule": {
            "family": "corpus-coverage",
            "decision": "supported_fraction_lt_threshold",
            "min_document_frequency": 1,
            "content_stopwords": ["the"],
        },
        "thresholds": [0.0, 0.5, 1.0],
        "retrieval": {"algorithm": "bm25", "k1": 1.2, "b": 0.75, "top_k": 1},
        "execution": {
            "local": True,
            "llm_calls": 0,
            "cost_usd": 0,
            "harness": "S7-1",
            "protocol": "declare-then-run/sha-bound-rows",
        },
        "artifacts": {
            name: {
                "path": name + (".jsonl" if name == "results" else ".json"),
                **({"sha256": ""} if name in INPUTS else {}),
            }
            for name in ARTIFACTS
        },
    }
    events = [
        {"event": "pin_generator", "sha256": ""},
        {"event": "freeze_holdout", "sha256": "", "generator_sha256": ""},
        {
            "event": "read", "actor": "declarer",
            "artifact": "declaration_cases", "sha256": "",
        },
        {"event": "declare", "sha256": "", "inputs": {"declaration_cases": ""}},
        {
            "event": "read", "actor": "runner",
            "artifact": "declaration_cases", "sha256": "",
        },
        {
            "event": "read", "actor": "runner",
            "artifact": "holdout_cases", "sha256": "",
        },
        {"event": "run", "sha256": ""},
        {"event": "finish", "results_sha256": "", "report_sha256": ""},
    ]
    retime(events)
    bundle = {
        "declaration": declaration,
        "declaration_cases": original,
        "holdout_cases": mechanical_cases(generator),
        "generator": generator,
        "provenance": {"events": events},
    }
    populate_outputs(bundle)
    return bundle


def seal(bundle):
    """Bind actual fixture bytes without repairing substantive mutations."""
    input_blobs = {name: encode(bundle[name]) for name in INPUTS}
    hashes = {name: sha(blob) for name, blob in input_blobs.items()}
    refs = bundle["declaration"].get("artifacts", {})
    for name in INPUTS:
        if isinstance(refs.get(name), dict):
            refs[name]["sha256"] = hashes[name]
    declaration_bytes = encode(bundle["declaration"])
    hashes["declaration"] = sha(declaration_bytes)
    for row in bundle["results"]:
        row["declaration_sha256"] = hashes["declaration"]
        if row.get("set") in SETS:
            row["cases_sha256"] = hashes[row["set"] + "_cases"]
    results_bytes = encode_rows(bundle["results"])
    report_bytes = encode(bundle["report"])
    hashes["results"] = sha(results_bytes)
    hashes["report"] = sha(report_bytes)
    for event in bundle["provenance"]["events"]:
        kind = event["event"]
        if kind == "pin_generator":
            event["sha256"] = hashes["generator"]
        elif kind == "freeze_holdout":
            event["sha256"] = hashes["holdout_cases"]
            event["generator_sha256"] = hashes["generator"]
        elif kind in ("declare", "run"):
            event["sha256"] = hashes["declaration"]
            if kind == "declare":
                event["inputs"]["declaration_cases"] = hashes["declaration_cases"]
        elif kind == "finish":
            event["results_sha256"] = hashes["results"]
            event["report_sha256"] = hashes["report"]
        elif kind == "read" and event.get("artifact") in hashes:
            event["sha256"] = hashes[event["artifact"]]
    return {
        "declaration.json": declaration_bytes,
        **{name + ".json": blob for name, blob in input_blobs.items()},
        "results.jsonl": results_bytes,
        "report.json": report_bytes,
        "provenance.json": encode(bundle["provenance"]),
    }


def write_fixture(root, files):
    root.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (root / name).write_bytes(data)


def set_value(bundle, path, value):
    target = bundle
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] = copy.deepcopy(value)


def setter(path, value):
    return lambda bundle: set_value(bundle, path, value)


def delete_value(bundle, path):
    target = bundle
    for component in path[:-1]:
        target = target[component]
    del target[path[-1]]


def deleter(path):
    return lambda bundle: delete_value(bundle, path)


def mutate_row(bundle, predicate, field, value):
    row = next(row for row in bundle["results"] if predicate(row))
    row[field] = value(row[field]) if callable(value) else copy.deepcopy(value)


def row_mutator(predicate, field, value):
    return lambda bundle: mutate_row(bundle, predicate, field, value)


def move_event(bundle, moved, before):
    events = bundle["provenance"]["events"]
    event = event_named(bundle, moved)
    events.remove(event)
    destination = next(i for i, item in enumerate(events) if item["event"] == before)
    events.insert(destination, event)
    retime(events)


def add_early_read(bundle, artifact):
    events = bundle["provenance"]["events"]
    index = next(i for i, event in enumerate(events) if event["event"] == "declare")
    events.insert(index, {
        "event": "read", "actor": "declarer",
        "artifact": artifact, "sha256": "",
    })
    retime(events)


def remove_read(bundle, actor, artifact):
    events = bundle["provenance"]["events"]
    events[:] = [
        event for event in events
        if not (
            event["event"] == "read"
            and event["actor"] == actor
            and event["artifact"] == artifact
        )
    ]
    retime(events)


def early_runner_read(bundle):
    events = bundle["provenance"]["events"]
    event = next(
        item for item in events
        if item["event"] == "read" and item["actor"] == "runner"
    )
    events.remove(event)
    index = next(i for i, item in enumerate(events) if item["event"] == "declare")
    events.insert(index, event)
    retime(events)


def alter_serialized_json(files, filename, mutation):
    value = parse_json(files[filename], filename)
    mutation(value)
    files[filename] = encode(value)


def corrupt_event_hash(files, event_name, field):
    def mutate(value):
        event = next(item for item in value["events"] if item["event"] == event_name)
        event[field] = "0" * 64
    alter_serialized_json(files, "provenance.json", mutate)


def corrupt_row_hash(files, field):
    rows = [parse_json(line, "fixture row") for line in files["results.jsonl"].splitlines()]
    rows[0][field] = "0" * 64
    files["results.jsonl"] = encode_rows(rows)
    # Preserve finish binding so validation must reach the corrupted row.
    def mutate(value):
        finish = next(item for item in value["events"] if item["event"] == "finish")
        finish["results_sha256"] = sha(files["results.jsonl"])
    alter_serialized_json(files, "provenance.json", mutate)


def selftest():
    tests = []

    def add(label, expected, mutation=None, raw_mutation=None):
        tests.append((label, expected, mutation, raw_mutation))

    add(
        "a required evidence file is absent", "FILE_REQUIRED",
        raw_mutation=lambda files: files.pop("holdout_cases.json"),
    )
    add(
        "duplicate JSON keys cannot silently override the preregistration",
        "JSON_INVALID",
        raw_mutation=lambda files: files.__setitem__(
            "declaration.json", b'{"schema_version":1,"schema_version":2}\n',
        ),
    )
    add(
        "the exact rule is omitted", "DECLARATION_SCHEMA",
        deleter(("declaration", "rule")),
    )
    add(
        "the refuted margin family is reused", "FAMILY_REFUTED",
        setter(("declaration", "rule", "family"), "score-margin"),
    )
    add(
        "coverage secretly reads a score distribution", "RULE_INPUTS",
        setter(("declaration", "rule", "score_distribution"), "top-two-scores"),
    )
    add(
        "the comparison boundary is not the declared rule", "RULE_SEMANTICS",
        setter(("declaration", "rule", "decision"), "supported_fraction_le_threshold"),
    )
    add(
        "zero document frequency counts as support", "RULE_DF",
        setter(("declaration", "rule", "min_document_frequency"), 0),
    )
    add(
        "the threshold grid is not preregistered", "GRID_INVALID",
        setter(("declaration", "thresholds"), []),
    )
    add(
        "thresholds contain repeated values", "GRID_INVALID",
        setter(("declaration", "thresholds"), [0.0, 0.5, 0.5]),
    )
    add(
        "the baseline is changed to a different retriever", "RETRIEVAL_SPEC",
        setter(("declaration", "retrieval", "algorithm"), "cosine"),
    )
    add(
        "the run depends on remote execution", "NONLOCAL_EXECUTION",
        setter(("declaration", "execution", "local"), False),
    )
    add(
        "a model is called", "LLM_DEPENDENCY",
        setter(("declaration", "execution", "llm_calls"), 1),
    )
    add(
        "the experiment has a nonzero cost", "NONZERO_COST",
        setter(("declaration", "execution", "cost_usd"), 0.01),
    )
    add(
        "the declare-then-run harness is not reused", "HARNESS_PROTOCOL",
        setter(("declaration", "execution", "protocol"), "run-then-declare"),
    )
    add(
        "holdout evidence is omitted from the manifest", "ARTIFACT_MANIFEST",
        deleter(("declaration", "artifacts", "holdout_cases")),
    )
    add(
        "an input changes after its declared checksum", "ARTIFACT_HASH",
        raw_mutation=lambda files: files.__setitem__(
            "declaration_cases.json", files["declaration_cases.json"] + b" ",
        ),
    )
    add(
        "the declaration set is no longer the original ten-case shape",
        "DECLARATION_CASES",
        lambda bundle: bundle["declaration_cases"]["cases"].pop(),
    )

    def erase_useful_holdout_labels(bundle):
        for case in bundle["holdout_cases"]["cases"]:
            case["relevant_ids"] = []

    add(
        "holdout omits the useful-retrieval half of the measurement",
        "HOLDOUT_CLASSES", erase_useful_holdout_labels,
    )
    add(
        "a declaration case is recycled as held-out evidence", "HOLDOUT_OVERLAP",
        lambda bundle: bundle["holdout_cases"]["cases"].__setitem__(
            0, copy.deepcopy(bundle["declaration_cases"]["cases"][0]),
        ),
    )
    add(
        "the generator is only an unimplemented name", "GENERATOR_SPEC",
        setter(("generator", "algorithm"), "trust-the-builder"),
    )
    add(
        "the pinned generator seed cannot reproduce the holdout",
        "HOLDOUT_GENERATION", setter(("generator", "seed"), 23),
    )
    add(
        "a generated case is hand-edited despite fresh valid hashes",
        "HOLDOUT_GENERATION",
        setter(("holdout_cases", "cases", 0, "query"), "hand edited query"),
    )
    add(
        "the generator is pinned after the holdout freezes", "GENERATOR_NOT_PINNED",
        lambda bundle: move_event(bundle, "freeze_holdout", "pin_generator"),
    )
    add(
        "the holdout is frozen only after declaration", "HOLDOUT_NOT_FROZEN",
        lambda bundle: move_event(bundle, "declare", "freeze_holdout"),
    )
    add(
        "execution precedes preregistration", "RUN_BEFORE_DECLARE",
        lambda bundle: move_event(bundle, "run", "declare"),
    )
    add(
        "the declarer reads held-out cases before fixing the rule",
        "HOLDOUT_READ_AT_DECLARATION",
        lambda bundle: add_early_read(bundle, "holdout_cases"),
    )
    add(
        "the declarer reads the generator instead of original cases alone",
        "DECLARATION_INPUT_LEAK",
        lambda bundle: add_early_read(bundle, "generator"),
    )
    add(
        "holdout is admitted as an explicit declaration input",
        "DECLARATION_INPUTS",
        lambda bundle: event_named(bundle, "declare")["inputs"].__setitem__(
            "holdout_cases", "0" * 64,
        ),
    )
    add(
        "no original-case read supports the declaration",
        "DECLARATION_INPUT_UNREAD",
        lambda bundle: remove_read(bundle, "declarer", "declaration_cases"),
    )
    add(
        "the runner reads cases before declaration", "RUN_READ_ORDER",
        early_runner_read,
    )
    add(
        "the run never reads the holdout", "RUN_INPUT_UNREAD",
        lambda bundle: remove_read(bundle, "runner", "holdout_cases"),
    )
    add(
        "the freeze event binds a different held-out file",
        "HOLDOUT_FREEZE_BINDING",
        raw_mutation=lambda files: corrupt_event_hash(
            files, "freeze_holdout", "sha256",
        ),
    )
    add(
        "the declaration event binds a different declaration",
        "DECLARATION_BINDING",
        raw_mutation=lambda files: corrupt_event_hash(files, "declare", "sha256"),
    )
    add(
        "the run binds a different declaration", "RUN_DECLARATION_BINDING",
        raw_mutation=lambda files: corrupt_event_hash(files, "run", "sha256"),
    )
    add(
        "the finish event binds a different report", "OUTPUT_BINDING",
        raw_mutation=lambda files: corrupt_event_hash(
            files, "finish", "report_sha256",
        ),
    )
    add(
        "result rows are detached from the preregistration",
        "ROW_DECLARATION_BINDING",
        raw_mutation=lambda files: corrupt_row_hash(files, "declaration_sha256"),
    )
    add(
        "result rows are detached from their case set", "ROW_CASESET_BINDING",
        raw_mutation=lambda files: corrupt_row_hash(files, "cases_sha256"),
    )
    add(
        "a retrieval query silently loses its stopwords", "TOKEN_FILTERING",
        row_mutator(
            lambda row: row["set"] == "declaration" and "the" in row["query_tokens"],
            "query_tokens",
            lambda value: [token for token in value if token != "the"],
        ),
    )
    add(
        "coverage silently excludes an unsupported content token",
        "CONTENT_FEATURES",
        row_mutator(lambda row: True, "content_tokens", lambda value: value[:-1]),
    )
    add(
        "term frequency is substituted for document frequency",
        "DOCUMENT_FREQUENCY",
        row_mutator(
            lambda row: True, "document_frequencies",
            lambda value: {
                token: (frequency + 1 if frequency else frequency)
                for token, frequency in value.items()
            },
        ),
    )
    add(
        "coverage is fabricated despite correct token and df evidence",
        "COVERAGE_FRACTION",
        row_mutator(lambda row: True, "support_fraction", 0.75),
    )
    add(
        "the baseline result is fabricated", "BM25_BASELINE",
        row_mutator(lambda row: row["baseline_top1"] == "a", "baseline_top1", "b"),
    )
    add(
        "the strict comparison is changed at equality", "COVERAGE_DECISION",
        row_mutator(
            lambda row: row["threshold"] == row["support_fraction"] == 0.5,
            "decision", "abstain",
        ),
    )
    add(
        "a useful retrieval remains returned after declared abstention",
        "RETRIEVAL_OUTCOME",
        row_mutator(
            lambda row: row["decision"] == "abstain" and row["baseline_top1"] == "a",
            "returned_top1", "a",
        ),
    )
    add(
        "a post-run threshold is inserted into the results", "ROW_THRESHOLD",
        row_mutator(lambda row: True, "threshold", 0.75),
    )
    add(
        "a case/threshold measurement is duplicated", "ROW_DUPLICATE",
        lambda bundle: bundle["results"].append(copy.deepcopy(bundle["results"][0])),
    )

    def omit_holdout_threshold(bundle):
        bundle["results"] = [
            row for row in bundle["results"]
            if not (row["set"] == "holdout" and row["threshold"] == 1.0)
        ]

    add(
        "the costly holdout threshold is selectively omitted",
        "GRID_RESULTS_INCOMPLETE", omit_holdout_threshold,
    )
    add(
        "a winning threshold is selected after the run", "REPORT_SELECTION",
        setter(("report", "selected_threshold"), 0.5),
    )

    def pool_report(bundle):
        bundle["report"]["sets"] = {
            "combined": copy.deepcopy(bundle["report"]["sets"]["declaration"]),
        }

    add(
        "declaration and holdout are pooled into one measurement",
        "SETS_SEPARATE", pool_report,
    )
    add(
        "only a favorable threshold is reported on holdout", "REPORT_GRID",
        lambda bundle: bundle["report"]["sets"]["holdout"]["grid"].pop(),
    )
    add(
        "holdout useful-loss reporting is omitted", "REPORT_METRICS",
        deleter(("report", "sets", "holdout", "grid", 2, "useful_lost")),
    )
    add(
        "declaration rejection is exaggerated",
        "REPORT_DECLARATION_IRRELEVANT_REJECTED",
        setter(("report", "sets", "declaration", "grid", 0, "irrelevant_rejected"), 5),
    )
    add(
        "declaration useful loss is hidden",
        "REPORT_DECLARATION_USEFUL_LOST",
        setter(("report", "sets", "declaration", "grid", 2, "useful_lost"), 0),
    )
    add(
        "holdout rejection is exaggerated",
        "REPORT_HOLDOUT_IRRELEVANT_REJECTED",
        setter(("report", "sets", "holdout", "grid", 0, "irrelevant_rejected"), 2),
    )
    add(
        "holdout useful loss is hidden",
        "REPORT_HOLDOUT_USEFUL_LOST",
        setter(("report", "sets", "holdout", "grid", 2, "useful_lost"), 0),
    )
    add(
        "the holdout denominator is inflated",
        "REPORT_HOLDOUT_USEFUL_TOTAL",
        setter(("report", "sets", "holdout", "grid", 0, "useful_total"), 20),
    )
    add(
        "a boolean masquerades as a measurement counter",
        "REPORT_HOLDOUT_USEFUL_LOST",
        setter(("report", "sets", "holdout", "grid", 0, "useful_lost"), False),
    )

    base = fixture()
    with tempfile.TemporaryDirectory(prefix="s12-2-gate-selftest-") as temporary:
        root = Path(temporary)
        clean = root / "conforming"
        write_fixture(clean, seal(copy.deepcopy(base)))
        try:
            check(clean)
        except Exception as exc:
            raise Finding(
                "SELFTEST_CONFORMING_REJECTED",
                type(exc).__name__ + ": " + str(exc),
            ) from None
        print("SELFTEST ACCEPT: conforming full-grid experiment with honest losses")

        # Accept a minimal two-case held-out set, retaining both classes.
        minimal = copy.deepcopy(base)
        minimal["generator"]["count"] = 2
        minimal["holdout_cases"] = mechanical_cases(minimal["generator"])
        populate_outputs(minimal)
        path = root / "minimal"
        write_fixture(path, seal(minimal))
        try:
            check(path)
        except Exception as exc:
            raise Finding(
                "SELFTEST_MINIMAL_REJECTED",
                type(exc).__name__ + ": " + str(exc),
            ) from None
        print("SELFTEST ACCEPT: minimal conforming holdout with both classes")

        # Higher declared df support honestly refutes the rule more strongly.
        # The gate must accept that result, not demand a favorable experiment.
        refuted = copy.deepcopy(base)
        refuted["declaration"]["rule"]["min_document_frequency"] = 2
        populate_outputs(refuted)
        path = root / "honest-refutation"
        write_fixture(path, seal(refuted))
        try:
            check(path)
        except Exception as exc:
            raise Finding(
                "SELFTEST_REFUTATION_REJECTED",
                type(exc).__name__ + ": " + str(exc),
            ) from None
        print("SELFTEST ACCEPT: honest refutation with useful retrieval losses")

        for index, (label, expected, mutation, raw_mutation) in enumerate(tests):
            corrupted = copy.deepcopy(base)
            if mutation is not None:
                mutation(corrupted)
            files = seal(corrupted)
            if raw_mutation is not None:
                raw_mutation(files)
            path = root / ("wrong-" + str(index))
            write_fixture(path, files)
            try:
                check(path)
            except Finding as exc:
                require(
                    exc.marker == expected,
                    "SELFTEST_WRONG_FINDING",
                    label + ": expected " + expected + ", received " + exc.marker
                    + " (" + exc.message + ")",
                )
                print("SELFTEST REJECT [" + expected + "]: " + label)
            except Exception as exc:
                raise Finding(
                    "SELFTEST_UNNAMED_FAILURE",
                    label + ": " + type(exc).__name__ + ": " + str(exc),
                ) from None
            else:
                raise Finding(
                    "SELFTEST_FALSE_ACCEPT",
                    label + ": corrupted fixture was accepted.",
                )
    print(
        "SELFTEST PASS: 3 conforming fixtures accepted; "
        + str(len(tests))
        + " independent corruptions rejected by their expected named findings."
    )


class GateArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Finding("ARGUMENTS", message)


def main(argv=None):
    try:
        parser = GateArgumentParser(description=__doc__)
        parser.add_argument("root", nargs="?", help="Experiment evidence directory")
        parser.add_argument("--root", dest="root_option", help="Experiment evidence directory")
        parser.add_argument(
            "--selftest", action="store_true",
            help="Accept conforming fixtures and reject independent corruptions",
        )
        args = parser.parse_args(argv)
        require(
            not (args.root and args.root_option),
            "ARGUMENTS",
            "Supply either positional ROOT or --root ROOT.",
        )
        if args.selftest:
            require(
                not (args.root or args.root_option),
                "ARGUMENTS",
                "--selftest uses only internally generated temporary fixtures.",
            )
            selftest()
        else:
            root = args.root_option or args.root or Path(__file__).resolve().parent
            check(root)
            print("PASS: S12-2 declaration, holdout, full grid, and both outcomes verified.")
        return 0
    except Finding as exc:
        print("FINDING [" + exc.marker + "]: " + exc.message, file=sys.stderr)
        return 1
    except OSError as exc:
        print("FINDING [IO_ERROR]: " + str(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("FINDING [INTERRUPTED]: Gate interrupted.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(
            "FINDING [CHECK_ERROR]: " + type(exc).__name__ + ": " + str(exc),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
