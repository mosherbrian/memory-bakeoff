#!/usr/bin/env python3
"""S12-1G: check S12-1 from its row text, without an artifact-specific schema.

Usage:
    check.py [--root REPOSITORY] [--artifact DIRECTORY]
    check.py --selftest

Exit contract: 0 clean; 1 with FINDING[NAME]; no traceback.

Evidence interface
------------------
The artifact directory must contain declaration.json, receipts.jsonl, and
verdict.json. These are this check's explicit evidence interface, not filenames
inferred from a builder's output.

The repository must contain the frozen corpus, existing thin layer, both prior
verdicts, and the two-role policy at the paths named in S12-1.

declaration.json contains:
  declared_at: timezone-qualified ISO timestamp
  corpus_sha256, layer_sha256, generator_sha256, harness_sha256: full hashes
  generator, harness: repository-relative paths to existing Python scripts
  generator_args, harness_args: arrays of strings; substitutions supported:
    {root}, {corpus}, {layer}, {declaration}, {python}
  limits:
    m, k: finite numbers in [0, 1]
    reduction_metric: "relative_false_supersession_reduction"
    missed_update_metric: "missed_updates_per_update"
    registration: "fresh" or "explicit_redeclaration"
  prediction:
    false_supersession: integer in [0, 33]
    missed_updates: integer in [0, 13]
    distractor_key_relation: "same_as_original"
    rationale: nonempty string
  sensitivity:
    m, k: distinct numeric axis values in [0, 1]; each axis contains at least
          two values and includes its preregistered limit
  execution:
    local: true
    llm_calls: 0
    cost_usd: 0
  trial_fields:
    id, kind, original, candidate: JSON pointers into frozen trial records
  kind_values:
    distractor, update: distinct JSON scalar labels
  prior_fields:
    native_controlled, layer_controlled, native_broader:
      false_supersession, distractors, missed_updates, updates:
        JSON pointers into the corresponding prior verdict

The generator must emit the corpus bytes on stdout. The harness must emit
receipts JSONL on stdout. Replay runs the declared scripts again, rather than
accepting assertions that replay occurred. Generator bytes must match exactly.
Harness evidence must match apart from timestamps and record order. The replay
also observes calls to decide in the named existing thin_layer.py.

Each receipt contains:
  phase: "before", "main", or "after"
  arm: "native" or "layer"
  id: nonempty string
  kind: "distractor" or "update"
  original, candidate: objects containing scope and fact_type
  superseded: boolean
  at: timezone-qualified ISO timestamp
  declaration_sha256: hash of the exact declaration bytes

Main receipts cover every frozen trial once per arm. Both endpoint controls
contain the same 32 distractors and 12 updates per arm, with identical inputs
across arms and endpoints. All layer decisions must equal equality of
(scope, fact_type). Both arms use the same outcome-counting function.

verdict.json contains:
  corpus_sha256, layer_sha256, declaration_sha256, receipts_sha256
  old:
    native_controlled, layer_controlled, native_broader: count objects
  new:
    native_broader, layer_broader: count objects
  reduction, missed_update_rate: measured numbers
  protection, safe: booleans
  outcome: "reopen_state_layer_question" or "close_trivial_layer_class"
  sensitivity: complete Cartesian grid of objects containing:
    m, k, reduction, missed_update_rate, protection, safe, outcome
  reporting:
    measured_role: "pi-lcm bake-off MEMORY contestant"
    compaction_role: "Brian's stack compaction layer"
    compaction_measured: false
    compaction_conclusion_changed: false

Count objects contain false_supersession, distractors, missed_updates, updates.
Protection requires relative false-supersession reduction >= m. Safety requires
missed_updates / updates <= k. Reopening requires BOTH conditions.

Only the hash prefix and suffix supplied in the row are independently pinned;
the full corpus digest must also agree with the preregistration and verdict.
Recorded chronology and declaration hashes establish evidence consistency,
not authenticated historical publication time. Script hashes and observed
replay establish consistency with the local declared implementations, not their
historical identity. Python audit checks are not an adversarial OS sandbox.

--selftest builds its own synthetic corpus and implementations. A private
in-process hash parameter admits that synthetic corpus; the CLI exposes no
override of the production corpus pin. Every negative fixture must fail with
its individually expected finding, and a conforming fixture must pass.
"""

import argparse
import contextlib
import copy
import hashlib
import io
import itertools
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


CORPUS = "team/S10-PI-LCM-HIST/trials.jsonl"
LAYER = "team/S7-STATELAYER/thin_layer.py"
PRIOR_CONTROL = "team/S7-STATELAYER/verdict.json"
PRIOR_BROAD = "team/S10-PI-LCM-HIST/verdict.json"
ROLE_POLICY = "team/OPS-PI-LCM-TWO-ROLES-20260918.md"
ARTIFACT = "team/S11-LAYER-HIST"
FROZEN_PIN = ("52289107", "367b1d")
FIELDS = ("false_supersession", "distractors", "missed_updates", "updates")
CONTROL = dict(zip(FIELDS, (0, 32, 0, 12)))
BROAD = dict(zip(FIELDS, (22, 33, 0, 13)))
PHASES = ("before", "main", "after")
ARMS = ("native", "layer")
REPLAY_TIMEOUT = 30


class Finding(Exception):
    def __init__(self, name, detail):
        self.name = name
        self.detail = str(detail)
        super().__init__(self.detail)


def require(condition, name, detail):
    if not condition:
        raise Finding(name, detail)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    )


def json_bytes(value):
    return (canonical(value) + "\n").encode("utf-8")


def lines_bytes(rows):
    return b"".join(json_bytes(row) for row in rows)


def read_bytes(path):
    require(path.is_file(), "MISSING_FILE", str(path))
    try:
        return path.read_bytes()
    except OSError as exc:
        raise Finding("READ_ERROR", f"{path}: {exc}") from None


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_JSON_KEY", repr(key))
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f"non-finite JSON constant {value}")


def parse_json(data, label):
    try:
        return json.loads(
            data, object_pairs_hook=unique_object,
            parse_constant=invalid_constant,
        )
    except Finding:
        raise
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        raise Finding("INVALID_JSON", f"{label}: {exc}") from None


def read_json(path):
    return parse_json(read_bytes(path), str(path))


def json_lines(data, label):
    require(bool(data.strip()), "EMPTY_EVIDENCE", label)
    result = []
    for index, line in enumerate(data.splitlines(), 1):
        require(bool(line.strip()), "INVALID_JSONL", f"{label}:{index}: blank line")
        row = parse_json(line, f"{label}:{index}")
        require(isinstance(row, dict), "SCHEMA", f"{label}:{index}: expected object")
        result.append(row)
    return result


def member(obj, key, name="SCHEMA"):
    require(isinstance(obj, dict) and key in obj, name, f"missing {key}")
    return obj[key]


def number(value, name, lower=None, upper=None):
    require(type(value) in (int, float), name, "expected a number")
    try:
        finite = math.isfinite(value)
    except (ValueError, OverflowError):
        finite = False
    require(finite, name, "expected a finite number")
    require(lower is None or value >= lower, name, "number below allowed range")
    require(upper is None or value <= upper, name, "number above allowed range")
    return value


def integer(value, name, lower=0, upper=None):
    require(type(value) is int, name, "expected an integer")
    return number(value, name, lower, upper)


def close(actual, expected, name):
    number(actual, name)
    require(
        math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-12),
        name, f"expected {expected!r}, got {actual!r}",
    )


def timestamp(value, name="CHRONOLOGY"):
    require(isinstance(value, str), name, "timestamp must be a string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(result.tzinfo is not None and result.utcoffset() is not None,
                name, "timestamp must include a timezone")
        return result.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise Finding(name, f"invalid timestamp {value!r}") from None


def full_hash(value, name):
    require(
        isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
        name, "expected a full lowercase SHA-256 digest",
    )
    return value


def local_path(root, relative):
    require(isinstance(relative, str) and bool(relative), "PATH", "empty path")
    require(not Path(relative).is_absolute(), "PATH", "expected repository-relative path")
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise Finding("PATH", f"path escapes repository: {relative}") from None
    return path


def pointer(obj, path, name="SCHEMA"):
    require(isinstance(path, str), name, "JSON pointer must be a string")
    if path == "":
        return obj
    require(path.startswith("/"), name, f"invalid JSON pointer {path!r}")
    try:
        for token in path[1:].split("/"):
            require(not re.search(r"~(?![01])", token), name, "invalid pointer escape")
            token = token.replace("~1", "/").replace("~0", "~")
            if isinstance(obj, list):
                require(re.fullmatch(r"0|[1-9][0-9]*", token) is not None,
                        name, "invalid array index")
                obj = obj[int(token)]
            else:
                obj = obj[token]
        return obj
    except (KeyError, IndexError, TypeError, ValueError):
        raise Finding(name, f"unresolved JSON pointer {path!r}") from None


def key_of(write):
    require(isinstance(write, dict), "WRITE_KEY", "write must be an object")
    require("scope" in write and "fact_type" in write,
            "WRITE_KEY", "each write needs both scope and fact_type")
    return write["scope"], write["fact_type"]


def count_rows(rows):
    distractors = [r for r in rows if r["kind"] == "distractor"]
    updates = [r for r in rows if r["kind"] == "update"]
    return dict(zip(FIELDS, (
        sum(r["superseded"] for r in distractors),
        len(distractors),
        sum(not r["superseded"] for r in updates),
        len(updates),
    )))


def count_object(obj, expected, name):
    require(isinstance(obj, dict), name, "expected count object")
    for field in FIELDS:
        value = member(obj, field, name)
        integer(value, name)
        require(value == expected[field], name,
                f"{field}: expected {expected[field]}, got {value}")


def decision(reduction, missed_rate, m, k):
    protection = reduction >= m
    safe = missed_rate <= k
    return {
        "protection": protection,
        "safe": safe,
        "outcome": (
            "reopen_state_layer_question" if protection and safe
            else "close_trivial_layer_class"
        ),
    }


def check_decision(obj, expected, prefix=""):
    names = {
        "protection": prefix or "PROTECTION_DECISION",
        "safe": prefix or "SAFETY_DECISION",
        "outcome": prefix or "OUTCOME",
    }
    for field in ("protection", "safe"):
        value = member(obj, field, names[field])
        require(type(value) is bool and value == expected[field],
                names[field], f"incorrect {field}")
    require(member(obj, "outcome", names["outcome"]) == expected["outcome"],
            names["outcome"], "incorrect outcome")


def input_signature(row):
    return canonical({key: row[key] for key in ("kind", "original", "candidate")})


def validate_declaration(decl):
    require(isinstance(decl, dict), "SCHEMA", "declaration must be an object")
    declared_at = timestamp(member(decl, "declared_at"), "PREREGISTRATION_TIME")
    limits = member(decl, "limits")
    m = number(member(limits, "m", "PROTECTION_LIMIT"), "PROTECTION_LIMIT", 0, 1)
    k = number(member(limits, "k", "SAFETY_LIMIT"), "SAFETY_LIMIT", 0, 1)
    require(
        member(limits, "registration", "LIMIT_REGISTRATION")
        in ("fresh", "explicit_redeclaration"),
        "LIMIT_REGISTRATION", "both limits must be explicitly preregistered",
    )
    require(
        member(limits, "reduction_metric", "REDUCTION_METRIC")
        == "relative_false_supersession_reduction",
        "REDUCTION_METRIC", "declare the reduction metric",
    )
    require(
        member(limits, "missed_update_metric", "MISSED_UPDATE_METRIC")
        == "missed_updates_per_update",
        "MISSED_UPDATE_METRIC", "declare the missed-update denominator",
    )
    prediction = member(decl, "prediction", "PREDICTION")
    integer(member(prediction, "false_supersession", "PREDICTION"), "PREDICTION", 0, 33)
    integer(member(prediction, "missed_updates", "PREDICTION"), "PREDICTION", 0, 13)
    require(
        member(prediction, "distractor_key_relation", "PREDICTION")
        == "same_as_original",
        "PREDICTION", "prediction must acknowledge the original-key distractors",
    )
    rationale = member(prediction, "rationale", "PREDICTION")
    require(isinstance(rationale, str) and bool(rationale.strip()),
            "PREDICTION", "prediction needs a rationale")

    sensitivity = member(decl, "sensitivity", "SENSITIVITY_PLAN")
    axes = {}
    for axis, limit in (("m", m), ("k", k)):
        values = member(sensitivity, axis, "SENSITIVITY_PLAN")
        require(isinstance(values, list) and len(values) >= 2,
                "SENSITIVITY_PLAN", f"{axis} needs at least two values")
        for value in values:
            number(value, "SENSITIVITY_PLAN", 0, 1)
        require(len(set(values)) == len(values), "SENSITIVITY_PLAN", "duplicate axis value")
        require(limit in values, "SENSITIVITY_PLAN", "grid omits a registered limit")
        axes[axis] = values

    execution = member(decl, "execution")
    require(member(execution, "local", "LOCAL_ONLY") is True,
            "LOCAL_ONLY", "execution must be local")
    integer(member(execution, "llm_calls", "NO_LLM"), "NO_LLM")
    require(execution["llm_calls"] == 0, "NO_LLM", "LLM calls are forbidden")
    number(member(execution, "cost_usd", "ZERO_COST"), "ZERO_COST", 0)
    require(execution["cost_usd"] == 0, "ZERO_COST", "cost must be zero")
    return declared_at, m, k, axes


def load_trials(data, decl):
    fields = member(decl, "trial_fields", "CORPUS_SCHEMA")
    labels = member(decl, "kind_values", "CORPUS_SCHEMA")
    label_keys = {}
    for kind in ("distractor", "update"):
        value = member(labels, kind, "CORPUS_SCHEMA")
        require(value is None or type(value) in (str, bool, int, float),
                "CORPUS_SCHEMA", "kind labels must be JSON scalars")
        label_keys[kind] = canonical(value)
    require(label_keys["distractor"] != label_keys["update"],
            "CORPUS_SCHEMA", "kind labels must differ")

    trials = {}
    for raw in json_lines(data, CORPUS):
        row = {
            field: pointer(
                raw, member(fields, field, "CORPUS_SCHEMA"), "CORPUS_SCHEMA"
            )
            for field in ("id", "kind", "original", "candidate")
        }
        trial_id = row["id"]
        require(isinstance(trial_id, str) and bool(trial_id),
                "TRIAL_IDS", "trial ids must be nonempty strings")
        require(trial_id not in trials, "TRIAL_IDS", f"duplicate trial {trial_id}")
        encoded_kind = canonical(row["kind"])
        matches = [kind for kind, label in label_keys.items() if label == encoded_kind]
        require(len(matches) == 1, "TRIAL_CLASSIFICATION", f"unknown kind for {trial_id}")
        row["kind"] = matches[0]
        original_key = key_of(row["original"])
        candidate_key = key_of(row["candidate"])
        if row["kind"] == "distractor":
            require(original_key == candidate_key, "DISTRACTOR_KEY",
                    f"{trial_id}: frozen distractor must carry the original's key")
        trials[trial_id] = row
    require(
        sum(r["kind"] == "distractor" for r in trials.values()) == 33
        and sum(r["kind"] == "update" for r in trials.values()) == 13,
        "CORPUS_CARDINALITY", "frozen corpus must contain 33 distractors and 13 updates",
    )
    return trials


def check_priors(root, decl):
    sources = {
        "native_controlled": read_json(root / PRIOR_CONTROL),
        "layer_controlled": read_json(root / PRIOR_CONTROL),
        "native_broader": read_json(root / PRIOR_BROAD),
    }
    mappings = member(decl, "prior_fields")
    for label, expected, name in (
        ("native_controlled", CONTROL, "PRIOR_NATIVE_CONTROLLED"),
        ("layer_controlled", CONTROL, "PRIOR_LAYER_CONTROLLED"),
        ("native_broader", BROAD, "PRIOR_NATIVE_BROADER"),
    ):
        mapping = member(mappings, label, name)
        extracted = {
            field: pointer(sources[label], member(mapping, field, name), name)
            for field in FIELDS
        }
        count_object(extracted, expected, name)


def validate_receipts(rows, trials, declared_at, declaration_hash):
    groups = {(phase, arm): {} for phase in PHASES for arm in ARMS}
    times = {phase: [] for phase in PHASES}
    for row in rows:
        phase = member(row, "phase", "RECEIPT_SCHEMA")
        arm = member(row, "arm", "RECEIPT_SCHEMA")
        trial_id = member(row, "id", "RECEIPT_SCHEMA")
        kind = member(row, "kind", "RECEIPT_SCHEMA")
        require(isinstance(phase, str) and phase in PHASES,
                "RECEIPT_SCHEMA", "invalid phase")
        require(isinstance(arm, str) and arm in ARMS,
                "RECEIPT_SCHEMA", "invalid arm")
        require(isinstance(trial_id, str) and bool(trial_id),
                "RECEIPT_SCHEMA", "invalid trial id")
        require(isinstance(kind, str) and kind in ("distractor", "update"),
                "RECEIPT_SCHEMA", "invalid trial kind")
        require(type(member(row, "superseded", "RECEIPT_SCHEMA")) is bool,
                "RECEIPT_SCHEMA", "superseded must be boolean")
        key_of(member(row, "original", "RECEIPT_SCHEMA"))
        key_of(member(row, "candidate", "RECEIPT_SCHEMA"))
        require(
            member(row, "declaration_sha256", "DECLARATION_BINDING") == declaration_hash,
            "DECLARATION_BINDING", "receipt is not bound to the exact declaration",
        )
        at = timestamp(member(row, "at", "RECEIPT_SCHEMA"))
        require(declared_at < at, "PREREGISTRATION_TIME",
                "declaration must precede every receipt, including initial controls")
        require(trial_id not in groups[(phase, arm)], "RECEIPT_DUPLICATE",
                f"duplicate receipt for {phase}/{arm}/{trial_id}")
        groups[(phase, arm)][trial_id] = row
        times[phase].append(at)

    for (phase, arm), group in groups.items():
        expected_size = 46 if phase == "main" else 44
        require(len(group) == expected_size, "ARM_COVERAGE",
                f"{phase}/{arm}: expected {expected_size} unique trials")
        if phase == "main":
            require(set(group) == set(trials), "ARM_COVERAGE",
                    f"{arm}: main trial ids must equal the frozen corpus")
            for trial_id, row in group.items():
                require(input_signature(row) == input_signature(trials[trial_id]),
                        "CORPUS_BINDING", f"{arm}/{trial_id}: altered trial input or label")
        else:
            observed = count_rows(list(group.values()))
            require(observed["distractors"] == 32 and observed["updates"] == 12,
                    "CONTROL_CARDINALITY", f"{phase}/{arm}: wrong control composition")

    for phase in ("before", "after"):
        native = groups[(phase, "native")]
        layer = groups[(phase, "layer")]
        require(set(native) == set(layer), "CONTROL_PAIRING",
                f"{phase}: control ids differ across arms")
        for trial_id in native:
            require(input_signature(native[trial_id]) == input_signature(layer[trial_id]),
                    "CONTROL_PAIRING", f"{phase}/{trial_id}: control inputs differ")

    first = groups[("before", "native")]
    last = groups[("after", "native")]
    require(set(first) == set(last), "CONTROL_STABILITY",
            "endpoint control ids differ")
    for trial_id in first:
        require(input_signature(first[trial_id]) == input_signature(last[trial_id]),
                "CONTROL_STABILITY", f"{trial_id}: endpoint control inputs differ")

    require(
        max(times["before"]) < min(times["main"])
        and max(times["main"]) < min(times["after"]),
        "PHASE_ORDER", "controls must bracket both arms' main measurements",
    )

    for row in rows:
        if row["arm"] == "layer":
            expected = key_of(row["original"]) == key_of(row["candidate"])
            require(row["superseded"] is expected, "LAYER_RULE",
                    f"{row['phase']}/{row['id']}: decision violates key equality")

    for phase in ("before", "after"):
        count_object(count_rows(list(groups[(phase, "native")].values())),
                     CONTROL, "NATIVE_CONTROL")
        count_object(count_rows(list(groups[(phase, "layer")].values())),
                     CONTROL, "LAYER_CONTROL")

    native = count_rows(list(groups[("main", "native")].values()))
    layer = count_rows(list(groups[("main", "layer")].values()))
    count_object(native, BROAD, "NATIVE_BROAD")
    return native, layer


def validate_verdict(verdict, hashes, native, layer, m, k, axes):
    require(isinstance(verdict, dict), "SCHEMA", "verdict must be an object")
    for field, expected in hashes.items():
        require(member(verdict, field, "VERDICT_BINDING") == expected,
                "VERDICT_BINDING", f"verdict has the wrong {field}")

    old = member(verdict, "old", "OLD_COMPARISON")
    new = member(verdict, "new", "NEW_COMPARISON")
    for obj, label, expected, name in (
        (old, "native_controlled", CONTROL, "OLD_NATIVE_CONTROLLED"),
        (old, "layer_controlled", CONTROL, "OLD_LAYER_CONTROLLED"),
        (old, "native_broader", BROAD, "OLD_NATIVE_BROADER"),
        (new, "native_broader", native, "NEW_NATIVE_BROADER"),
        (new, "layer_broader", layer, "NEW_LAYER_BROADER"),
    ):
        count_object(member(obj, label, name), expected, name)

    native_rate = native["false_supersession"] / native["distractors"]
    layer_rate = layer["false_supersession"] / layer["distractors"]
    reduction = (native_rate - layer_rate) / native_rate
    missed_rate = layer["missed_updates"] / layer["updates"]
    close(member(verdict, "reduction", "REDUCTION"), reduction, "REDUCTION")
    close(member(verdict, "missed_update_rate", "MISSED_UPDATE_RATE"),
          missed_rate, "MISSED_UPDATE_RATE")
    check_decision(verdict, decision(reduction, missed_rate, m, k))

    grid = member(verdict, "sensitivity", "SENSITIVITY_GRID")
    expected_cells = set(itertools.product(axes["m"], axes["k"]))
    require(isinstance(grid, list) and len(grid) == len(expected_cells),
            "SENSITIVITY_GRID", "report every preregistered grid cell as data")
    seen = set()
    for cell in grid:
        cm = number(member(cell, "m", "SENSITIVITY_AXIS"), "SENSITIVITY_AXIS", 0, 1)
        ck = number(member(cell, "k", "SENSITIVITY_AXIS"), "SENSITIVITY_AXIS", 0, 1)
        pair = (cm, ck)
        require(pair in expected_cells, "SENSITIVITY_AXIS", "undeclared grid cell")
        require(pair not in seen, "SENSITIVITY_DUPLICATE", "duplicate grid cell")
        seen.add(pair)
        close(member(cell, "reduction", "SENSITIVITY_VALUES"),
              reduction, "SENSITIVITY_VALUES")
        close(member(cell, "missed_update_rate", "SENSITIVITY_VALUES"),
              missed_rate, "SENSITIVITY_VALUES")
        check_decision(cell, decision(reduction, missed_rate, cm, ck), "SENSITIVITY_VALUES")
    require(seen == expected_cells, "SENSITIVITY_GRID", "incomplete grid")

    reporting = member(verdict, "reporting", "MEMORY_ROLE")
    require(
        member(reporting, "measured_role", "MEMORY_ROLE")
        == "pi-lcm bake-off MEMORY contestant",
        "MEMORY_ROLE", "identify the measured bake-off MEMORY role",
    )
    require(
        member(reporting, "compaction_role", "COMPACTION_ROLE")
        == "Brian's stack compaction layer",
        "COMPACTION_ROLE", "identify the separate stack compaction role",
    )
    require(member(reporting, "compaction_measured", "COMPACTION_NOT_MEASURED") is False,
            "COMPACTION_NOT_MEASURED", "these measurements do not measure compaction")
    require(
        member(reporting, "compaction_conclusion_changed", "COMPACTION_UNCHANGED") is False,
        "COMPACTION_UNCHANGED", "do not extend this conclusion to the compaction role",
    )


REPLAY_DRIVER = r"""
import json
import os
import runpy
import sys

script, layer, trace_path = sys.argv[1:4]
arguments = sys.argv[4:]
layer = os.path.realpath(layer)
trace = {"decide_calls": 0, "policy_violation": False, "error": None}

def audit(event, args):
    if event.startswith("socket."):
        trace["policy_violation"] = True
        raise RuntimeError("network activity is outside the local-only declaration")

def profile(frame, event, arg):
    if (event == "call" and frame.f_code.co_name == "decide"
            and os.path.realpath(frame.f_code.co_filename) == layer):
        trace["decide_calls"] += 1

sys.addaudithook(audit)
sys.argv = [script] + arguments
sys.path.insert(0, os.path.dirname(script))
sys.setprofile(profile)
status = 0
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as exc:
    if exc.code is not None and exc.code != 0:
        status = 1
        trace["error"] = "script exited unsuccessfully"
except BaseException as exc:
    status = 1
    trace["error"] = type(exc).__name__ + ": " + str(exc).replace("\n", " ")[:300]
finally:
    sys.setprofile(None)
    with open(trace_path, "w", encoding="utf-8") as stream:
        json.dump(trace, stream)
sys.exit(status)
"""


def execute(root, declaration_path, decl, which):
    script = local_path(root, member(decl, which))
    require(script.suffix == ".py", "EXECUTION_SCHEMA", "replay script must be Python")
    args = member(decl, which + "_args", "EXECUTION_SCHEMA")
    require(isinstance(args, list) and all(isinstance(arg, str) for arg in args),
            "EXECUTION_SCHEMA", f"{which}_args must be an array of strings")
    replacements = {
        "{root}": str(root),
        "{corpus}": str(root / CORPUS),
        "{layer}": str(root / LAYER),
        "{declaration}": str(declaration_path),
        "{python}": sys.executable,
    }
    expanded = []
    for arg in args:
        for token, value in replacements.items():
            arg = arg.replace(token, value)
        expanded.append(arg)
    with tempfile.TemporaryDirectory(prefix="s12-1g-replay-") as temporary:
        trace_path = Path(temporary) / "trace.json"
        command = [
            sys.executable, "-B", "-c", REPLAY_DRIVER,
            str(script), str(root / LAYER), str(trace_path), *expanded,
        ]
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONHASHSEED"] = "0"
        try:
            completed = subprocess.run(
                command, cwd=temporary, env=environment, capture_output=True,
                timeout=REPLAY_TIMEOUT, check=False,
            )
        except subprocess.TimeoutExpired:
            raise Finding("EXECUTION_TIMEOUT", f"{which} exceeded {REPLAY_TIMEOUT}s") from None
        except OSError as exc:
            raise Finding("EXECUTION_FAILURE", f"{which}: {exc}") from None
        require(trace_path.is_file(), "EXECUTION_FAILURE",
                f"{which} terminated without replay evidence")
        trace = read_json(trace_path)
        require(not trace.get("policy_violation"), "LOCAL_EXECUTION",
                f"{which} attempted network activity")
        require(completed.returncode == 0 and trace.get("error") is None,
                "EXECUTION_FAILURE",
                f"{which}: {trace.get('error') or 'unsuccessful process exit'}")
        return completed.stdout, trace


def replay_signature(rows):
    signatures = []
    for row in rows:
        require(isinstance(row, dict), "HARNESS_REPLAY", "replay receipt must be an object")
        timestamp(member(row, "at", "HARNESS_REPLAY"), "HARNESS_REPLAY")
        signatures.append(canonical({key: value for key, value in row.items() if key != "at"}))
    return sorted(signatures)


def _validate(root, artifact, frozen_pin=FROZEN_PIN):
    root = Path(root).resolve()
    artifact = Path(artifact).resolve()
    declaration_path = artifact / "declaration.json"
    declaration_data = read_bytes(declaration_path)
    receipt_data = read_bytes(artifact / "receipts.jsonl")
    verdict_data = read_bytes(artifact / "verdict.json")
    corpus_data = read_bytes(root / CORPUS)
    layer_data = read_bytes(root / LAYER)
    read_bytes(root / PRIOR_CONTROL)
    read_bytes(root / PRIOR_BROAD)
    require(bool(read_bytes(root / ROLE_POLICY).strip()),
            "EMPTY_EVIDENCE", "two-role policy file is empty")

    decl = parse_json(declaration_data, str(declaration_path))
    declared_at, m, k, axes = validate_declaration(decl)
    trials = load_trials(corpus_data, decl)

    corpus_hash = digest(corpus_data)
    require(full_hash(member(decl, "corpus_sha256"), "CORPUS_DIGEST") == corpus_hash,
            "CORPUS_DIGEST", "declared corpus digest disagrees with its bytes")
    if isinstance(frozen_pin, tuple):
        pinned = corpus_hash.startswith(frozen_pin[0]) and corpus_hash.endswith(frozen_pin[1])
    else:
        pinned = corpus_hash == frozen_pin
    require(pinned, "FROZEN_CORPUS", "corpus does not match the row's frozen hash pin")

    watched = {
        declaration_path: declaration_data,
        artifact / "receipts.jsonl": receipt_data,
        artifact / "verdict.json": verdict_data,
        root / CORPUS: corpus_data,
        root / LAYER: layer_data,
    }
    layer_hash = digest(layer_data)
    require(full_hash(member(decl, "layer_sha256"), "LAYER_DIGEST") == layer_hash,
            "LAYER_DIGEST", "existing thin layer differs from preregistered bytes")
    for which in ("generator", "harness"):
        script = local_path(root, member(decl, which))
        data = read_bytes(script)
        name = which.upper() + "_DIGEST"
        require(full_hash(member(decl, which + "_sha256"), name) == digest(data),
                name, f"{which} differs from preregistered bytes")
        watched[script] = data
    for relative in (PRIOR_CONTROL, PRIOR_BROAD, ROLE_POLICY):
        watched[root / relative] = read_bytes(root / relative)

    check_priors(root, decl)
    declaration_hash = digest(declaration_data)
    rows = json_lines(receipt_data, "receipts.jsonl")
    native, layer = validate_receipts(rows, trials, declared_at, declaration_hash)
    hashes = {
        "corpus_sha256": corpus_hash,
        "layer_sha256": layer_hash,
        "declaration_sha256": declaration_hash,
        "receipts_sha256": digest(receipt_data),
    }
    verdict = parse_json(verdict_data, "verdict.json")
    validate_verdict(verdict, hashes, native, layer, m, k, axes)

    generated, _ = execute(root, declaration_path, decl, "generator")
    require(generated == corpus_data, "GENERATOR_REPLAY",
            "generator did not reproduce the frozen corpus byte-identically")
    replay_data, trace = execute(root, declaration_path, decl, "harness")
    required_calls = sum(row["arm"] == "layer" for row in rows)
    require(type(trace.get("decide_calls")) is int
            and trace["decide_calls"] >= required_calls,
            "LAYER_EXECUTION", "replay did not execute the existing layer for every layer receipt")
    try:
        replay_rows = json_lines(replay_data, "harness stdout")
        same = replay_signature(replay_rows) == replay_signature(rows)
    except Finding as exc:
        raise Finding("HARNESS_REPLAY", f"invalid replay evidence: {exc.name}") from None
    require(same, "HARNESS_REPLAY", "harness replay changed measured inputs or outcomes")

    for path, before in watched.items():
        require(read_bytes(path) == before, "REPLAY_MUTATION",
                f"replay modified evidence or implementation: {path}")
    return verdict


def write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path, value):
    write_bytes(path, json_bytes(value))


def fixture(root):
    """Construct independent synthetic evidence, never inspect real artifacts."""
    root = Path(root)
    artifact = root / ARTIFACT
    trials = []
    for kind, amount in (("distractor", 33), ("update", 13)):
        for index in range(amount):
            trial_id = ("D" if kind == "distractor" else "U") + f"{index:03d}"
            original = {"scope": trial_id, "fact_type": "preference", "value": "old"}
            candidate = {
                "scope": trial_id, "fact_type": "preference",
                "value": "distractor" if kind == "distractor" else "new",
            }
            trials.append({
                "id": trial_id, "kind": kind,
                "original": original, "candidate": candidate,
            })
    corpus_data = lines_bytes(trials)
    write_bytes(root / CORPUS, corpus_data)
    layer_source = (
        "def key(write):\n"
        "    return (write['scope'], write['fact_type'])\n\n"
        "def decide(original, candidate):\n"
        "    return key(original) == key(candidate)\n"
    )
    write_bytes(root / LAYER, layer_source.encode())
    write_json(root / PRIOR_CONTROL, {"native": CONTROL, "layer": CONTROL})
    write_json(root / PRIOR_BROAD, {"native": BROAD})
    write_bytes(root / ROLE_POLICY, (
        "pi-lcm is the bake-off MEMORY contestant. Its separate role as Brian's "
        "stack compaction layer is not measured by retrieval or supersession.\n"
    ).encode())

    controls = []
    for kind, amount in (("distractor", 32), ("update", 12)):
        for index in range(amount):
            trial_id = "C-" + ("D" if kind == "distractor" else "U") + f"{index:03d}"
            original = {"scope": trial_id, "fact_type": "preference", "value": "old"}
            candidate = {
                "scope": trial_id + ("-other" if kind == "distractor" else ""),
                "fact_type": "preference", "value": "new",
            }
            controls.append({
                "id": trial_id, "kind": kind,
                "original": original, "candidate": candidate,
            })

    rows = []
    phase_times = {
        "before": "2026-01-02T00:00:00Z",
        "main": "2026-01-03T00:00:00Z",
        "after": "2026-01-04T00:00:00Z",
    }
    for phase in PHASES:
        selected = trials if phase == "main" else controls
        for arm in ARMS:
            for source in selected:
                row = copy.deepcopy(source)
                if arm == "layer":
                    superseded = key_of(row["original"]) == key_of(row["candidate"])
                elif phase == "main" and row["kind"] == "distractor":
                    superseded = int(row["id"][1:]) < 22
                else:
                    superseded = row["kind"] == "update"
                row.update(
                    phase=phase, arm=arm, superseded=superseded,
                    at=phase_times[phase],
                )
                rows.append(row)

    generator = "team/S10-PI-LCM-HIST/generate.py"
    harness = "team/S7-STATELAYER/harness.py"
    write_bytes(root / generator, (
        "import sys\nsys.stdout.buffer.write(" + repr(corpus_data) + ")\n"
    ).encode())
    harness_source = (
        "import hashlib\nimport json\nimport pathlib\nimport runpy\nimport sys\n"
        "layer = runpy.run_path(sys.argv[1])\n"
        "declaration_hash = hashlib.sha256(pathlib.Path(sys.argv[2]).read_bytes()).hexdigest()\n"
        "rows = json.loads(" + repr(canonical(rows)) + ")\n"
        "for row in rows:\n"
        "    row['declaration_sha256'] = declaration_hash\n"
        "    if row['arm'] == 'layer':\n"
        "        row['superseded'] = layer['decide'](row['original'], row['candidate'])\n"
        "    print(json.dumps(row, sort_keys=True, separators=(',', ':')))\n"
    )
    write_bytes(root / harness, harness_source.encode())
    decl = {
        "declared_at": "2026-01-01T00:00:00Z",
        "corpus_sha256": digest(corpus_data),
        "layer_sha256": digest(read_bytes(root / LAYER)),
        "generator": generator,
        "generator_sha256": digest(read_bytes(root / generator)),
        "generator_args": [],
        "harness": harness,
        "harness_sha256": digest(read_bytes(root / harness)),
        "harness_args": ["{layer}", "{declaration}"],
        "limits": {
            "m": 0.5, "k": 0.1,
            "reduction_metric": "relative_false_supersession_reduction",
            "missed_update_metric": "missed_updates_per_update",
            "registration": "explicit_redeclaration",
        },
        "prediction": {
            "false_supersession": 33,
            "missed_updates": 0,
            "distractor_key_relation": "same_as_original",
            "rationale": "The distractors carry the original key, so equality accepts them.",
        },
        "sensitivity": {"m": [0, 0.5], "k": [0, 0.1]},
        "execution": {"local": True, "llm_calls": 0, "cost_usd": 0},
        "trial_fields": {name: "/" + name for name in ("id", "kind", "original", "candidate")},
        "kind_values": {"distractor": "distractor", "update": "update"},
        "prior_fields": {
            label: {field: "/" + arm + "/" + field for field in FIELDS}
            for label, arm in (
                ("native_controlled", "native"),
                ("layer_controlled", "layer"),
                ("native_broader", "native"),
            )
        },
    }
    write_json(artifact / "declaration.json", decl)
    declaration_hash = digest(read_bytes(artifact / "declaration.json"))
    for row in rows:
        row["declaration_sha256"] = declaration_hash
    write_bytes(artifact / "receipts.jsonl", lines_bytes(rows))
    layer_counts = dict(zip(FIELDS, (33, 33, 0, 13)))
    reduction = (22 / 33 - 33 / 33) / (22 / 33)
    missed_rate = 0.0
    verdict = {
        "corpus_sha256": digest(corpus_data),
        "layer_sha256": decl["layer_sha256"],
        "declaration_sha256": declaration_hash,
        "receipts_sha256": digest(read_bytes(artifact / "receipts.jsonl")),
        "old": {
            "native_controlled": copy.deepcopy(CONTROL),
            "layer_controlled": copy.deepcopy(CONTROL),
            "native_broader": copy.deepcopy(BROAD),
        },
        "new": {"native_broader": copy.deepcopy(BROAD), "layer_broader": layer_counts},
        "reduction": reduction,
        "missed_update_rate": missed_rate,
        **decision(reduction, missed_rate, 0.5, 0.1),
        "sensitivity": [
            {
                "m": m, "k": k, "reduction": reduction,
                "missed_update_rate": missed_rate,
                **decision(reduction, missed_rate, m, k),
            }
            for m, k in itertools.product(decl["sensitivity"]["m"], decl["sensitivity"]["k"])
        ],
        "reporting": {
            "measured_role": "pi-lcm bake-off MEMORY contestant",
            "compaction_role": "Brian's stack compaction layer",
            "compaction_measured": False,
            "compaction_conclusion_changed": False,
        },
    }
    write_json(artifact / "verdict.json", verdict)
    return digest(corpus_data)


def mutate_json(path, mutate):
    value = read_json(path)
    mutate(value)
    write_json(path, value)


def rebind_declaration(root):
    artifact = root / ARTIFACT
    declaration_hash = digest(read_bytes(artifact / "declaration.json"))
    rows = json_lines(read_bytes(artifact / "receipts.jsonl"), "fixture receipts")
    for row in rows:
        row["declaration_sha256"] = declaration_hash
    write_bytes(artifact / "receipts.jsonl", lines_bytes(rows))
    mutate_json(
        artifact / "verdict.json",
        lambda v: v.update(
            declaration_sha256=declaration_hash,
            receipts_sha256=digest(read_bytes(artifact / "receipts.jsonl")),
        ),
    )


def edit_decl(root, mutate):
    mutate_json(root / ARTIFACT / "declaration.json", mutate)
    rebind_declaration(root)


def edit_receipts(root, mutate):
    artifact = root / ARTIFACT
    rows = json_lines(read_bytes(artifact / "receipts.jsonl"), "fixture receipts")
    mutate(rows)
    write_bytes(artifact / "receipts.jsonl", lines_bytes(rows))
    mutate_json(
        artifact / "verdict.json",
        lambda v: v.update(receipts_sha256=digest(read_bytes(artifact / "receipts.jsonl"))),
    )


def edit_corpus(root, mutate, update_digest=False):
    rows = json_lines(read_bytes(root / CORPUS), "fixture corpus")
    mutate(rows)
    write_bytes(root / CORPUS, lines_bytes(rows))
    if update_digest:
        edit_decl(root, lambda d: d.update(corpus_sha256=digest(read_bytes(root / CORPUS))))


def edit_script(root, which, transform, update_digest=True):
    decl = read_json(root / ARTIFACT / "declaration.json")
    path = root / decl[which]
    write_bytes(path, transform(read_bytes(path).decode()).encode())
    if update_digest:
        edit_decl(root, lambda d: d.update({which + "_sha256": digest(read_bytes(path))}))


def first_receipt(rows, phase, arm, kind="distractor"):
    return next(
        row for row in rows
        if row["phase"] == phase and row["arm"] == arm and row["kind"] == kind
    )


def selftest():
    failures = []
    tests = []

    def case(name, mutation):
        tests.append((name, mutation))

    def declaration_case(name, mutation):
        case(name, lambda root: edit_decl(root, mutation))

    def receipt_case(name, mutation):
        case(name, lambda root: edit_receipts(root, mutation))

    def verdict_case(name, mutation):
        case(name, lambda root: mutate_json(root / ARTIFACT / "verdict.json", mutation))

    def corpus_case(name, mutation):
        case(name, lambda root: edit_corpus(root, mutation))

    case("MISSING_FILE", lambda root: (root / ARTIFACT / "verdict.json").unlink())
    case("INVALID_JSON", lambda root: write_bytes(root / ARTIFACT / "verdict.json", b"{\n"))
    case("DUPLICATE_JSON_KEY", lambda root: write_bytes(
        root / ARTIFACT / "verdict.json", b'{"old":{},"old":{}}\n'
    ))
    case("EMPTY_EVIDENCE", lambda root: write_bytes(root / ROLE_POLICY, b""))
    declaration_case("PROTECTION_LIMIT", lambda d: d["limits"].pop("m"))
    declaration_case("SAFETY_LIMIT", lambda d: d["limits"].pop("k"))
    declaration_case("LIMIT_REGISTRATION", lambda d: d["limits"].update(registration="implicit"))
    declaration_case("REDUCTION_METRIC", lambda d: d["limits"].update(reduction_metric="raw_count"))
    declaration_case("MISSED_UPDATE_METRIC", lambda d: d["limits"].update(
        missed_update_metric="misses_per_all_writes"
    ))
    declaration_case("PREDICTION", lambda d: d["prediction"].update(
        distractor_key_relation="cross_key"
    ))
    declaration_case("SENSITIVITY_PLAN", lambda d: d["sensitivity"].update(k=[0.1]))
    declaration_case("LOCAL_ONLY", lambda d: d["execution"].update(local=False))
    declaration_case("NO_LLM", lambda d: d["execution"].update(llm_calls=1))
    declaration_case("ZERO_COST", lambda d: d["execution"].update(cost_usd=0.01))
    declaration_case("PREREGISTRATION_TIME", lambda d: d.update(
        declared_at="2026-01-02T00:00:00Z"
    ))
    declaration_case("CORPUS_SCHEMA", lambda d: d["trial_fields"].update(kind="/unavailable"))
    declaration_case("CORPUS_DIGEST", lambda d: d.update(corpus_sha256="0" * 64))
    declaration_case("PATH", lambda d: d.update(generator="../outside.py"))
    declaration_case("EXECUTION_SCHEMA", lambda d: d.update(generator_args="not-an-array"))

    corpus_case("TRIAL_IDS", lambda rows: rows[1].update(id=rows[0]["id"]))
    corpus_case("TRIAL_CLASSIFICATION", lambda rows: rows[0].update(kind="unlabelled"))
    corpus_case("WRITE_KEY", lambda rows: rows[0]["candidate"].pop("fact_type"))
    corpus_case("DISTRACTOR_KEY", lambda rows: rows[0]["candidate"].update(scope="different"))
    corpus_case("CORPUS_CARDINALITY", lambda rows: rows.pop())
    case("FROZEN_CORPUS", lambda root: edit_corpus(
        root, lambda rows: rows[0]["original"].update(value="rewritten"), True
    ))
    case("LAYER_DIGEST", lambda root: write_bytes(
        root / LAYER, read_bytes(root / LAYER) + b"\n# changed after declaration\n"
    ))
    case("GENERATOR_DIGEST", lambda root: edit_script(
        root, "generator", lambda source: source + "\n# changed\n", False
    ))
    case("HARNESS_DIGEST", lambda root: edit_script(
        root, "harness", lambda source: source + "\n# changed\n", False
    ))

    for label, relative, arm, field in (
        ("PRIOR_NATIVE_CONTROLLED", PRIOR_CONTROL, "native", "false_supersession"),
        ("PRIOR_LAYER_CONTROLLED", PRIOR_CONTROL, "layer", "missed_updates"),
        ("PRIOR_NATIVE_BROADER", PRIOR_BROAD, "native", "false_supersession"),
    ):
        case(label, lambda root, p=relative, a=arm, f=field: mutate_json(
            root / p, lambda value: value[a].update({f: value[a][f] + 1})
        ))

    receipt_case("RECEIPT_SCHEMA", lambda rows: rows[0].update(superseded=1))
    receipt_case("DECLARATION_BINDING", lambda rows: rows[0].update(
        declaration_sha256="0" * 64
    ))
    receipt_case("CHRONOLOGY", lambda rows: rows[0].update(at="2026-01-02T00:00:00"))
    receipt_case("RECEIPT_DUPLICATE", lambda rows: rows.append(copy.deepcopy(rows[0])))
    receipt_case("ARM_COVERAGE", lambda rows: rows.pop())
    receipt_case("CONTROL_CARDINALITY", lambda rows: rows[0].update(kind="update"))
    receipt_case("CORPUS_BINDING", lambda rows: first_receipt(
        rows, "main", "native"
    )["candidate"].update(value="substituted"))
    receipt_case("CONTROL_PAIRING", lambda rows: first_receipt(
        rows, "before", "native"
    )["candidate"].update(value="one-arm-only"))

    def unstable_controls(rows):
        for arm in ARMS:
            first_receipt(rows, "after", arm)["candidate"]["value"] = "changed-at-end"

    receipt_case("CONTROL_STABILITY", unstable_controls)
    receipt_case("PHASE_ORDER", lambda rows: first_receipt(
        rows, "after", "native"
    ).update(at="2026-01-02T12:00:00Z"))
    receipt_case("LAYER_RULE", lambda rows: first_receipt(
        rows, "main", "layer"
    ).update(superseded=False))
    receipt_case("NATIVE_CONTROL", lambda rows: first_receipt(
        rows, "before", "native"
    ).update(superseded=True))

    def failing_layer_control(rows):
        for phase in ("before", "after"):
            for arm in ARMS:
                row = first_receipt(rows, phase, arm)
                row["candidate"]["scope"] = row["original"]["scope"]
                if arm == "layer":
                    row["superseded"] = True

    receipt_case("LAYER_CONTROL", failing_layer_control)
    receipt_case("NATIVE_BROAD", lambda rows: first_receipt(
        rows, "main", "native"
    ).update(superseded=False))

    verdict_case("VERDICT_BINDING", lambda v: v.update(receipts_sha256="0" * 64))
    verdict_case("OLD_COMPARISON", lambda v: v.pop("old"))
    verdict_case("NEW_COMPARISON", lambda v: v.pop("new"))
    for marker, section, label in (
        ("OLD_NATIVE_CONTROLLED", "old", "native_controlled"),
        ("OLD_LAYER_CONTROLLED", "old", "layer_controlled"),
        ("OLD_NATIVE_BROADER", "old", "native_broader"),
        ("NEW_NATIVE_BROADER", "new", "native_broader"),
        ("NEW_LAYER_BROADER", "new", "layer_broader"),
    ):
        verdict_case(marker, lambda v, s=section, label=label: v[s][label].update(
            false_supersession=v[s][label]["false_supersession"] + 1
        ))
    verdict_case("REDUCTION", lambda v: v.update(reduction=0.5))
    verdict_case("MISSED_UPDATE_RATE", lambda v: v.update(missed_update_rate=1.0))
    verdict_case("PROTECTION_DECISION", lambda v: v.update(protection=True))
    verdict_case("SAFETY_DECISION", lambda v: v.update(safe=False))
    verdict_case("OUTCOME", lambda v: v.update(outcome="reopen_state_layer_question"))
    verdict_case("SENSITIVITY_GRID", lambda v: v["sensitivity"].pop())
    verdict_case("SENSITIVITY_AXIS", lambda v: v["sensitivity"][0].update(m=0.25))
    verdict_case("SENSITIVITY_DUPLICATE", lambda v: v["sensitivity"].__setitem__(
        1, copy.deepcopy(v["sensitivity"][0])
    ))
    verdict_case("SENSITIVITY_VALUES", lambda v: v["sensitivity"][0].update(reduction=1.0))
    verdict_case("MEMORY_ROLE", lambda v: v["reporting"].update(
        measured_role="general pi-lcm effectiveness"
    ))
    verdict_case("COMPACTION_ROLE", lambda v: v["reporting"].pop("compaction_role"))
    verdict_case("COMPACTION_NOT_MEASURED", lambda v: v["reporting"].update(
        compaction_measured=True
    ))
    verdict_case("COMPACTION_UNCHANGED", lambda v: v["reporting"].update(
        compaction_conclusion_changed=True
    ))

    case("GENERATOR_REPLAY", lambda root: edit_script(
        root, "generator", lambda source: source + "\nprint(' ')\n"
    ))
    case("HARNESS_REPLAY", lambda root: edit_script(
        root, "harness", lambda source: source.replace(
            "    row['declaration_sha256'] = declaration_hash\n",
            "    row['declaration_sha256'] = declaration_hash\n"
            "    if row['phase'] == 'main' and row['arm'] == 'native':\n"
            "        row['superseded'] = not row['superseded']\n",
        )
    ))
    case("LAYER_EXECUTION", lambda root: edit_script(
        root, "harness", lambda source: source.replace(
            "row['superseded'] = layer['decide'](row['original'], row['candidate'])",
            "row['superseded'] = row['superseded']",
        )
    ))
    case("EXECUTION_FAILURE", lambda root: edit_script(
        root, "generator", lambda source: "raise RuntimeError('deliberate failure')\n"
    ))
    case("LOCAL_EXECUTION", lambda root: edit_script(
        root, "generator", lambda source: "import socket\nsocket.socket()\n" + source
    ))
    case("REPLAY_MUTATION", lambda root: edit_script(
        root, "harness", lambda source: source + (
            "\nwith open(sys.argv[1], 'a', encoding='utf-8') as changed:\n"
            "    changed.write('\\n# changed during verification\\n')\n"
        )
    ))

    require(len({name for name, _ in tests}) == len(tests),
            "SELFTEST_FAILURE", "negative fixtures must have distinct named findings")

    with tempfile.TemporaryDirectory(prefix="s12-1g-selftest-") as temporary:
        workspace = Path(temporary)
        base = workspace / "conforming"
        frozen_hash = fixture(base)
        try:
            result = _validate(base, base / ARTIFACT, frozen_hash)
            require(result["outcome"] == "close_trivial_layer_class",
                    "SELFTEST_FAILURE", "a measured failure must be accepted as evidence")
        except Exception as exc:
            failures.append(f"conforming fixture rejected: {type(exc).__name__}: {exc}")

        for index, (expected, mutation) in enumerate(tests):
            root = workspace / f"negative-{index:03d}"
            shutil.copytree(base, root)
            try:
                mutation(root)
                _validate(root, root / ARTIFACT, frozen_hash)
            except Finding as exc:
                if exc.name != expected:
                    failures.append(f"{expected}: got FINDING[{exc.name}] instead")
            except Exception as exc:
                failures.append(f"{expected}: unexpected {type(exc).__name__}: {exc}")
            else:
                failures.append(f"{expected}: deliberately wrong fixture was accepted")

        # Exercise the production pin rather than merely testing the private
        # synthetic-corpus entry point.
        try:
            _validate(base, base / ARTIFACT)
        except Finding as exc:
            if exc.name != "FROZEN_CORPUS":
                failures.append(f"production pin: got FINDING[{exc.name}]")
        else:
            failures.append("production pin admitted the synthetic corpus")

        # These cases independently exercise both limits, including a result
        # that protects but is unsafe, and inclusive threshold boundaries.
        decision_cases = (
            ((0.5, 0.1, 0.5, 0.1), (True, True, "reopen_state_layer_question")),
            ((0.49, 0.0, 0.5, 0.1), (False, True, "close_trivial_layer_class")),
            ((0.8, 0.11, 0.5, 0.1), (True, False, "close_trivial_layer_class")),
            ((0.49, 0.11, 0.5, 0.1), (False, False, "close_trivial_layer_class")),
            ((-0.5, 0.0, 0.0, 0.1), (False, True, "close_trivial_layer_class")),
            ((1.0, 0.0, 1.0, 0.0), (True, True, "reopen_state_layer_question")),
        )
        for args, expected in decision_cases:
            actual = decision(*args)
            observed = tuple(actual[field] for field in ("protection", "safe", "outcome"))
            if observed != expected:
                failures.append(f"threshold logic failed for {args!r}")

        # Test the public exit boundary for malformed arguments and a missing
        # artifact, including the absence of a traceback.
        for arguments, marker in (
            (["--unknown-option"], "ARGUMENTS"),
            (["--root", str(base), "--artifact", str(workspace / "absent")], "MISSING_FILE"),
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                status = main(arguments)
            rendered = output.getvalue()
            if status != 1 or f"FINDING[{marker}]" not in rendered or "Traceback" in rendered:
                failures.append(f"public exit contract failed for {marker}")

    require(not failures, "SELFTEST_FAILURE", "; ".join(failures))
    print(
        f"SELFTEST_OK: conforming fixture accepted; {len(tests)} distinct named "
        "rejections verified; production pin, both-limit decisions, and exit contract verified"
    )


class GateArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Finding("ARGUMENTS", message)


def default_root():
    here = Path(__file__).resolve()
    for parent in here.parents:
        if parent.name == "team":
            return parent.parent
    return Path.cwd()


def print_finding(name, detail):
    compact = " ".join(str(detail).split())
    print(f"FINDING[{name}]: {compact}")


def main(argv=None):
    try:
        parser = GateArgumentParser(description="S12-1 state-layer evidence gate")
        parser.add_argument("--root", type=Path, default=None)
        parser.add_argument("--artifact", type=Path, default=None)
        parser.add_argument("--selftest", action="store_true")
        args = parser.parse_args(argv)
        if args.selftest:
            selftest()
            return 0
        root = (args.root if args.root is not None else default_root()).resolve()
        artifact = args.artifact
        if artifact is None:
            artifact = root / ARTIFACT
        elif not artifact.is_absolute():
            artifact = root / artifact
        _validate(root, artifact)
        print("CLEAN: S12-1 evidence, comparison, decision, and replay verified")
        return 0
    except Finding as exc:
        print_finding(exc.name, exc.detail)
        return 1
    except SystemExit as exc:
        if exc.code in (None, 0):
            return 0
        print_finding("ARGUMENTS", "argument processing failed")
        return 1
    except KeyboardInterrupt:
        print_finding("INTERRUPTED", "verification interrupted")
        return 1
    except Exception as exc:
        print_finding("INTERNAL_ERROR", f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
