#!/usr/bin/env python3
"""Independent, row-derived gate for S13-1.

This checker does not execute transfer code or consult a builder's implementation.
Its evidence interface is specified here because the row does not specify an
output serialization.

Required transfer outputs:
  declaration.json: preregistered rule, grid, criterion, admission, and provenance
  run.json: local execution receipt, frozen harness identity, and invocation
  results.jsonl: exhaustive item x implementation x threshold replay
  verdict.json: separate rejection/loss measurements, controls, and family scores

The S11 declaration must expose rule={score: expression, reject: expression} and
threshold_grid. Expressions are literals, lists, {"path":"item.some.field"},
{"var":"score"}, {"var":"threshold"}, or {"op":name,"args":[expressions]}.
Unsupported translations fail closed rather than silently inventing a coverage
rule. Original item and S10 baseline objects are the expression context.

Items expose id and family. Baselines expose item_id, implementation, abstained,
and useful_retrieval, with boolean outcomes. The gate recomputes the replay and
scores; it never trusts a claimed pass or an aggregate alone.

Git source, preregistration, and run commits establish recorded ordering and
unchanged inputs. They cannot establish that no private, unrecorded experiment
occurred. Local execution, cost, and LLM/network use remain receipt attestations.
These limitations must also appear as machine-readable limits in the verdict.

Run with --root REPOSITORY [--artifact REPOSITORY_RELATIVE_DIRECTORY].
Without --root, the repository is located relative to this checker.
--selftest builds only synthetic temporary repositories.
"""

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile


ARTIFACT = "team/S13-KD-COVERAGE-TRANSFER"
S11 = "team/S11-ABSTAIN3"
S7 = "team/S7-KD-WORLDS"
S10 = "team/S10-KD-CROSS"
S6 = "team/S6-SELECTIVITY"
UPSTREAM = S7 + "/upstream"
SOURCES = (
    S11 + "/declaration.json",
    S11 + "/design.md",
    S11 + "/verdict.json",
    S7 + "/items.jsonl",
    S7 + "/verdict.json",
    S10 + "/results.jsonl",
    S10 + "/verdict.json",
    S6 + "/results.jsonl",
)
OUTPUTS = ("declaration.json", "run.json", "results.jsonl", "verdict.json")
SCHEMA = "S13-1-transfer/v1"
COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")

PRIOR_FACTS = {
    "coverage_rule_previously_admitted_to_external_sample": False,
    "S11": {
        "threshold": 0.5,
        "declaration_rejected": 5,
        "declaration_total": 5,
        "holdout_rejected": 3,
        "holdout_total": 5,
        "declaration_useful_lost": 0,
        "holdout_useful_lost": 0,
        "registered_bar_met_at": [0.25, 0.5],
    },
    "external_baselines": {
        "implementations": 5,
        "items": 40,
        "abstentions_per_implementation": 0,
        "useful_retrieval_range": [11, 21],
    },
}


class Finding(Exception):
    def __init__(self, name, detail):
        super().__init__(str(detail))
        self.name = name
        self.detail = str(detail)


class MissingFeature(Exception):
    pass


def need(condition, name, detail):
    if not condition:
        raise Finding(name, detail)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def same(a, b):
    return canonical(a) == canonical(b)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def numeric(value):
    return type(value) in (int, float) and math.isfinite(value)


def ratio(value):
    return numeric(value) and 0 <= value <= 1


def relative(value):
    need(isinstance(value, str) and bool(value), "E_PATH", "missing relative path")
    p = PurePosixPath(value)
    need(not p.is_absolute() and ".." not in p.parts and "\\" not in value
         and "\x00" not in value and p.as_posix() == value,
         "E_PATH", "unsafe/noncanonical relative path: " + repr(value))
    return value


def file(root, name):
    name = relative(name)
    p = root
    for part in PurePosixPath(name).parts:
        p = p / part
        need(not p.is_symlink(), "E_PATH", "symlink input: " + name)
    need(p.is_file(), "E_REQUIRED_FILE", "missing file: " + name)
    return p


def raw(root, name):
    return file(root, name).read_bytes()


def pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate object key: " + key)
        result[key] = value
    return result


def bad_constant(value):
    raise ValueError("nonfinite JSON constant: " + value)


def parse(data, label):
    try:
        return json.loads(data, object_pairs_hook=pairs_unique,
                          parse_constant=bad_constant)
    except (ValueError, UnicodeError) as exc:
        raise Finding("E_JSON", label + ": " + str(exc))


def obj(root, name):
    value = parse(raw(root, name), name)
    need(isinstance(value, dict), "E_JSON", name + ": expected object")
    return value


def lines(root, name, allow_empty=False):
    data = raw(root, name)
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise Finding("E_JSON", name + ": " + str(exc))
    result = []
    for n, line in enumerate(text.splitlines(), 1):
        need(bool(line.strip()), "E_JSON", "%s:%d: blank record" % (name, n))
        row = parse(line, "%s:%d" % (name, n))
        need(isinstance(row, dict), "E_JSON", name + ": expected object records")
        result.append(row)
    need(allow_empty or bool(result), "E_EMPTY_INPUT", name + ": empty data")
    return result


def git(root, *args, optional=False):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0",
               GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    try:
        proc = subprocess.run(["git", "-C", str(root), *args],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=30, env=env, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Finding("E_GIT", str(exc))
    need(optional or proc.returncode == 0, "E_GIT",
         proc.stderr.decode("utf-8", "replace").strip() or "git command failed")
    return proc


def blob(root, commit, path, marker):
    p = git(root, "show", commit + ":" + relative(path), optional=True)
    need(p.returncode == 0, marker, "missing committed blob: " + path)
    return p.stdout


def commit_valid(root, commit):
    need(isinstance(commit, str) and COMMIT_RE.fullmatch(commit),
         "E_PREREG_ORDER", "a full source/preregistration/run commit is required")
    proc = git(root, "cat-file", "-t", commit, optional=True)
    need(proc.returncode == 0 and proc.stdout.strip() == b"commit",
         "E_PREREG_ORDER", "invalid commit object")


def ancestor(root, a, b):
    return a != b and git(root, "merge-base", "--is-ancestor", a, b,
                         optional=True).returncode == 0


def tree_names(root, commit, path):
    proc = git(root, "ls-tree", "-r", "--name-only", "-z", commit, "--", path)
    return {x.decode("utf-8") for x in proc.stdout.split(b"\0") if x}


def upstream_files(root):
    base = root / UPSTREAM
    need(base.is_dir() and not base.is_symlink(), "E_REQUIRED_FILE",
         "missing frozen upstream directory")
    names = set()
    for p in base.rglob("*"):
        need(not p.is_symlink(), "E_PATH", "symlink in upstream")
        if p.is_file():
            names.add(p.relative_to(root).as_posix())
    need(bool(names), "E_REQUIRED_FILE", "empty upstream")
    need(any("/worlds/v2/" in "/" + x for x in names),
         "E_SAMPLE_IDENTITY", "upstream has no worlds/v2 files")
    return names


def evaluate(expr, context, variables, depth=0):
    need(depth <= 60, "E_RULE_UNSUPPORTED", "rule nesting exceeds 60")
    if expr is None or type(expr) in (str, bool, int, float):
        need(type(expr) is not float or math.isfinite(expr),
             "E_RULE_UNSUPPORTED", "nonfinite literal")
        return expr
    if isinstance(expr, list):
        return [evaluate(x, context, variables, depth + 1) for x in expr]
    need(isinstance(expr, dict), "E_RULE_UNSUPPORTED", "invalid expression")
    if set(expr) == {"path"}:
        path = expr["path"]
        need(isinstance(path, str) and path.split(".")[0] in ("item", "baseline"),
             "E_RULE_UNSUPPORTED", "path must address original item or baseline")
        value = context
        for part in path.split("."):
            if isinstance(value, dict) and part in value:
                value = value[part]
            elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                value = value[int(part)]
            else:
                raise MissingFeature(path)
        return value
    if set(expr) == {"var"}:
        need(isinstance(expr["var"], str) and expr["var"] in variables,
             "E_RULE_UNSUPPORTED", "unknown variable")
        return variables[expr["var"]]
    need(set(expr) == {"op", "args"} and isinstance(expr["args"], list),
         "E_RULE_UNSUPPORTED", "expected operation and argument list")
    op, args = expr["op"], expr["args"]
    supported = {
        "add", "sub", "mul", "div", "min", "max", "len", "intersection",
        "union", "unique", "lower", "split", "lt", "le", "gt", "ge",
        "eq", "ne", "and", "or", "not", "contains", "if",
    }
    need(isinstance(op, str) and op in supported, "E_RULE_UNSUPPORTED",
         "unsupported operation: " + repr(op))
    if op == "if":
        need(len(args) == 3, "E_RULE_UNSUPPORTED", "if arity")
        condition = evaluate(args[0], context, variables, depth + 1)
        need(type(condition) is bool, "E_RULE_UNSUPPORTED", "nonboolean condition")
        return evaluate(args[1 if condition else 2], context, variables, depth + 1)
    values = [evaluate(x, context, variables, depth + 1) for x in args]
    try:
        if op in {"add", "sub", "mul", "div", "min", "max"}:
            need(values and all(numeric(x) for x in values),
                 "E_RULE_UNSUPPORTED", "nonnumeric arithmetic")
            if op in {"sub", "div"}:
                need(len(values) == 2, "E_RULE_UNSUPPORTED", "binary arity")
            if op == "add":
                result = sum(values)
            elif op == "sub":
                result = values[0] - values[1]
            elif op == "mul":
                result = math.prod(values)
            elif op == "div":
                need(values[1] != 0, "E_RULE_UNSUPPORTED",
                     "undefined coverage: no invented zero-denominator convention")
                result = values[0] / values[1]
            elif op == "min":
                result = min(values)
            else:
                result = max(values)
            need(numeric(result), "E_RULE_UNSUPPORTED", "nonfinite result")
            return result
        if op in {"lt", "le", "gt", "ge", "eq", "ne", "contains"}:
            need(len(values) == 2, "E_RULE_UNSUPPORTED", "comparison arity")
            a, b = values
            if op == "eq":
                return same(a, b)
            if op == "ne":
                return not same(a, b)
            if op == "contains":
                return b in a
            need(numeric(a) and numeric(b), "E_RULE_UNSUPPORTED",
                 "ordered comparisons require numbers")
            return {"lt": a < b, "le": a <= b, "gt": a > b, "ge": a >= b}[op]
        if op in {"and", "or", "not"}:
            need(values and all(type(x) is bool for x in values),
                 "E_RULE_UNSUPPORTED", "logical operands must be booleans")
            if op == "not":
                need(len(values) == 1, "E_RULE_UNSUPPORTED", "not arity")
                return not values[0]
            return all(values) if op == "and" else any(values)
        if op in {"intersection", "union"}:
            need(len(values) == 2 and all(isinstance(x, list) for x in values),
                 "E_RULE_UNSUPPORTED", "set operation operands")
            left = {canonical(x): x for x in values[0]}
            right = {canonical(x): x for x in values[1]}
            keys = set(left) & set(right) if op == "intersection" else set(left) | set(right)
            both = dict(left, **right)
            return [both[k] for k in sorted(keys)]
        need(len(values) == 1, "E_RULE_UNSUPPORTED", "unary arity")
        value = values[0]
        if op == "len":
            need(isinstance(value, (str, list, dict)), "E_RULE_UNSUPPORTED", "len type")
            return len(value)
        if op == "unique":
            need(isinstance(value, list), "E_RULE_UNSUPPORTED", "unique type")
            indexed = {canonical(x): x for x in value}
            return [indexed[k] for k in sorted(indexed)]
        need(isinstance(value, str), "E_RULE_UNSUPPORTED", "string operation type")
        return value.lower() if op == "lower" else value.split()
    except Finding:
        raise
    except (TypeError, ValueError, OverflowError, ZeroDivisionError) as exc:
        raise Finding("E_RULE_UNSUPPORTED", str(exc))


def frozen_data(root):
    for path in SOURCES:
        raw(root, path)
    frozen = obj(root, S11 + "/declaration.json")
    need(bool(raw(root, S11 + "/design.md").strip()),
         "E_SOURCE_DESIGN", "empty frozen design")
    for path in (S11 + "/verdict.json", S7 + "/verdict.json", S10 + "/verdict.json"):
        obj(root, path)
    lines(root, S6 + "/results.jsonl")
    rule = frozen.get("rule")
    grid = frozen.get("threshold_grid")
    need(isinstance(rule, dict) and set(rule) == {"score", "reject"},
         "E_RULE_UNSUPPORTED", "S11 must expose its exact score and reject expressions")
    need(isinstance(grid, list) and bool(grid) and all(ratio(t) for t in grid)
         and len(set(grid)) == len(grid),
         "E_SOURCE_GRID", "invalid frozen threshold grid")
    items = lines(root, S7 + "/items.jsonl")
    baselines = lines(root, S10 + "/results.jsonl")
    ids = {}
    for item in items:
        ident, family = item.get("id"), item.get("family")
        need(isinstance(ident, str) and bool(ident) and ident not in ids,
             "E_ITEM_IDENTITY", "missing or duplicate item ID")
        need(isinstance(family, str) and bool(family),
             "E_FAMILY_IDENTITY", "missing source family")
        ids[ident] = item
    need(len(ids) == 40, "E_SAMPLE_SIZE", "frozen external sample must have 40 items")
    need(len({x["family"] for x in items}) >= 2,
         "E_FAMILY_IDENTITY", "external families must remain distinct")
    indexed = {}
    implementations = set()
    for row in baselines:
        ident, impl = row.get("item_id"), row.get("implementation")
        need(ident in ids and isinstance(impl, str) and bool(impl),
             "E_BASELINE_MATRIX", "unmatched baseline ID or implementation")
        key = (ident, impl)
        need(key not in indexed, "E_BASELINE_MATRIX", "duplicate baseline record")
        need(type(row.get("abstained")) is bool
             and type(row.get("useful_retrieval")) is bool,
             "E_BASELINE_OUTCOMES", "baseline outcomes must be booleans")
        need(not (row["abstained"] and row["useful_retrieval"]),
             "E_BASELINE_OUTCOMES", "abstaining baseline cannot retrieve usefully")
        indexed[key] = row
        implementations.add(impl)
    need(len(implementations) == 5 and
         set(indexed) == {(i, m) for i in ids for m in implementations},
         "E_BASELINE_MATRIX", "five complete unchanged baseline implementations required")
    totals = [sum(indexed[i, m]["useful_retrieval"] for i in ids)
              for m in sorted(implementations)]
    need(not any(x["abstained"] for x in baselines)
         and min(totals) == 11 and max(totals) == 21
         and all(11 <= x <= 21 for x in totals),
         "E_BASELINE_PRIOR", "baseline outcomes contradict the row's frozen prior measurement")
    return rule, grid, ids, indexed, sorted(implementations)


def audit_replay(rule, grid, items, baselines):
    expected, missing = [], []
    for (ident, impl), baseline in sorted(baselines.items()):
        context = {"item": items[ident], "baseline": baseline}
        try:
            score = evaluate(rule["score"], context, {})
            need(ratio(score), "E_COVERAGE_SCORE", "coverage score must lie in [0,1]")
            local = []
            for threshold in grid:
                rejected = evaluate(rule["reject"], context,
                                    {"score": score, "threshold": threshold})
                need(type(rejected) is bool, "E_RULE_UNSUPPORTED",
                     "reject expression must return a boolean")
                useful = baseline["useful_retrieval"]
                local.append({
                    "item_id": ident, "implementation": impl,
                    "family": items[ident]["family"], "threshold": threshold,
                    "score": score, "rejected": rejected,
                    "baseline_abstained": baseline["abstained"],
                    "baseline_useful_retrieval": useful,
                    "useful_retrieval_lost": useful and rejected,
                    "useful_retrieval_retained": useful and not rejected,
                })
            expected.extend(local)
        except MissingFeature as exc:
            missing.append({"item_id": ident, "implementation": impl,
                            "missing_path": str(exc)})
    # Partial scoring is not a faithful admission of the unchanged sample.
    return ([] if missing else expected), missing


def control_scores(items, baselines):
    groups = {}
    for (ident, impl), row in baselines.items():
        key = (impl, items[ident]["family"])
        cell = groups.setdefault(key, {
            "implementation": impl, "family": key[1], "items": 0,
            "abstentions": 0, "useful_retrievals": 0,
        })
        cell["items"] += 1
        cell["abstentions"] += int(row["abstained"])
        cell["useful_retrievals"] += int(row["useful_retrieval"])
    return [groups[k] for k in sorted(groups)]


def family_scores(replay):
    groups = {}
    for row in replay:
        key = (row["implementation"], row["family"], row["threshold"])
        cell = groups.setdefault(key, {
            "implementation": key[0], "family": key[1], "threshold": key[2],
            "items": 0, "rejected": 0, "baseline_useful": 0,
            "useful_lost": 0, "useful_retained": 0, "baseline_abstentions": 0,
        })
        cell["items"] += 1
        cell["rejected"] += int(row["rejected"])
        cell["baseline_useful"] += int(row["baseline_useful_retrieval"])
        cell["useful_lost"] += int(row["useful_retrieval_lost"])
        cell["useful_retained"] += int(row["useful_retrieval_retained"])
        cell["baseline_abstentions"] += int(row["baseline_abstained"])
    for cell in groups.values():
        cell["rejection_rate"] = cell["rejected"] / cell["items"]
        cell["useful_loss_rate"] = (
            cell["useful_lost"] / cell["baseline_useful"]
            if cell["baseline_useful"] else None
        )
    return [groups[k] for k in sorted(groups)]


def sensitivity(scores, grid, criterion):
    result = []
    for threshold in grid:
        cells = [x for x in scores if x["threshold"] == threshold]
        meets = bool(cells) and all(
            x["rejection_rate"] >= criterion["min_rejection_rate"]
            and (x["useful_loss_rate"] is None
                 or x["useful_loss_rate"] <= criterion["max_useful_loss_rate"])
            for x in cells
        )
        result.append({"threshold": threshold, "meets_criterion": meets})
    return result


def indexed_rows(rows, keys, marker):
    need(isinstance(rows, list), marker, "expected list of records")
    result = {}
    for row in rows:
        need(isinstance(row, dict) and all(k in row for k in keys),
             marker, "missing record identity")
        values = [row[k] for k in keys]
        need(all(type(x) in (str, int, float) for x in values),
             marker, "invalid identity value")
        key = canonical(values)
        need(key not in result, marker, "duplicate record identity")
        result[key] = row
    return result


def check_provenance(root, artifact, declaration, run, verdict, upstream):
    source = declaration.get("source_commit")
    prereg = verdict.get("preregistration_commit")
    ran = verdict.get("run_commit")
    for commit in (source, prereg, ran):
        commit_valid(root, commit)
    need(ancestor(root, source, prereg) and ancestor(root, prereg, ran),
         "E_PREREG_ORDER", "source < preregistration < run ancestry is required")
    need(run.get("preregistration_commit") == prereg,
         "E_PREREG_RECEIPT", "run does not identify its preregistration")
    decl_path = artifact + "/declaration.json"
    for commit in (prereg, ran):
        need(blob(root, commit, decl_path, "E_PREREG_DECLARATION")
             == raw(root, decl_path),
             "E_PREREG_DECLARATION", "declaration differs from committed preregistration")
    for name in ("run.json", "results.jsonl", "verdict.json"):
        proc = git(root, "cat-file", "-e", prereg + ":" + artifact + "/" + name,
                   optional=True)
        need(proc.returncode != 0, "E_PREREG_CONTAMINATION",
             "preregistration already contains " + name)
    for name in ("run.json", "results.jsonl"):
        path = artifact + "/" + name
        need(blob(root, ran, path, "E_RUN_BINDING") == raw(root, path),
             "E_RUN_BINDING", "current run evidence differs from recorded run")
    harness = declaration["harness"]
    names = set(SOURCES) | upstream | {harness}
    manifest = declaration.get("input_sha256")
    need(isinstance(manifest, dict) and set(manifest) == names,
         "E_INPUT_MANIFEST", "manifest must cover all and only frozen inputs and harness")
    for path in sorted(names):
        data = raw(root, path)
        need(manifest[path] == digest(data), "E_INPUT_DIGEST", "digest mismatch: " + path)
        for commit in (source, prereg, ran):
            need(blob(root, commit, path, "E_FROZEN_INPUT") == data,
                 "E_FROZEN_INPUT", "changed frozen input: " + path)
    for commit in (source, prereg, ran):
        need(tree_names(root, commit, UPSTREAM) == upstream,
             "E_UPSTREAM_MEMBERSHIP", "upstream file set changed")
    need(run.get("input_sha256") == manifest, "E_RUN_INPUTS",
         "run did not use the preregistered frozen input manifest")
    need(run.get("declaration_sha256") == digest(raw(root, decl_path)),
         "E_RUN_DECLARATION", "run is not bound to the exact declaration")


def check(root, artifact=ARTIFACT):
    root = Path(root).resolve()
    artifact = relative(artifact)
    for name in OUTPUTS:
        raw(root, artifact + "/" + name)
    declaration = obj(root, artifact + "/declaration.json")
    run = obj(root, artifact + "/run.json")
    verdict = obj(root, artifact + "/verdict.json")
    for value in (declaration, run, verdict):
        need(value.get("schema") == SCHEMA, "E_SCHEMA", "unsupported evidence interface")
    rule, grid, items, baselines, implementations = frozen_data(root)
    upstream = upstream_files(root)

    need(same(declaration.get("rule"), rule), "E_RULE_RETUNED",
         "transfer must use the exact frozen S11 rule")
    need(same(declaration.get("threshold_grid"), grid), "E_GRID",
         "transfer must use the entire frozen threshold grid, without additions")
    need(same(declaration.get("sensitivity_grid"), grid), "E_SENSITIVITY_PLAN",
         "sensitivity grid must be declared as data before running")
    need(declaration.get("sample") == {
        "evidence_class": "external", "version": "worlds/v2",
        "items": S7 + "/items.jsonl", "upstream": UPSTREAM,
        "baselines": S10 + "/results.jsonl", "unchanged": True,
    }, "E_SAMPLE_IDENTITY", "must identify the unchanged external worlds/v2 sample")
    criterion = declaration.get("transfer_criterion")
    need(isinstance(criterion, dict)
         and set(criterion) == {
             "unit", "decision", "min_rejection_rate", "max_useful_loss_rate",
             "zero_useful_denominator",
         }
         and criterion["unit"] == "implementation_family"
         and criterion["decision"] == "all_cells_at_registered_threshold"
         and ratio(criterion["min_rejection_rate"])
         and ratio(criterion["max_useful_loss_rate"])
         and criterion["zero_useful_denominator"] == "null_rate_zero_count",
         "E_TRANSFER_CRITERION", "explicit pre-run, separate rejection/loss bar required")
    primary = declaration.get("primary_threshold")
    need(numeric(primary) and primary in grid
         and declaration.get("threshold_selection") == "preregistered"
         and run.get("primary_threshold") == primary
         and verdict.get("primary_threshold") == primary,
         "E_THRESHOLD_SELECTION", "post-result threshold selection is disqualifying")
    need(declaration.get("baseline_policy") == "all_five_unchanged_per_family",
         "E_CONTROL_PLAN", "all prior baseline controls must be preserved")
    harness = declaration.get("harness")
    need(isinstance(harness, str) and harness.startswith(S7 + "/")
         and harness.endswith(".py") and not harness.startswith(UPSTREAM + "/"),
         "E_HARNESS", "must reuse a frozen S7 local declare-then-run harness")
    relative(harness)
    need(run.get("harness") == harness
         and run.get("harness_sha256") == digest(raw(root, harness)),
         "E_HARNESS", "run harness differs from declared frozen S7 harness")
    need(run.get("mode") == "local", "E_LOCAL", "execution must be local")
    need(type(run.get("cost_usd")) in (int, float) and run["cost_usd"] == 0,
         "E_COST", "execution must cost $0")
    need(type(run.get("llm_calls")) is int and run["llm_calls"] == 0,
         "E_LLM", "no LLM calls permitted")
    need(type(run.get("network_calls")) is int and run["network_calls"] == 0,
         "E_NETWORK", "frozen local replay must not fetch or modify external data")
    argv = run.get("argv")
    need(isinstance(argv, list) and all(isinstance(x, str) for x in argv)
         and len(argv) >= 4 and argv[1] == harness
         and "--declaration" in argv
         and argv.index("--declaration") + 1 < len(argv)
         and argv[argv.index("--declaration") + 1] == artifact + "/declaration.json",
         "E_INVOCATION", "receipt must record a declaration-bound harness invocation")
    need(run.get("invocation") == "G3", "E_G3", "G3 invocation evidence missing")
    check_provenance(root, artifact, declaration, run, verdict, upstream)

    expected, missing = audit_replay(rule, grid, items, baselines)
    faithful = not missing
    admission = declaration.get("admission")
    need(isinstance(admission, dict)
         and admission.get("status") == ("faithful" if faithful else "inadmissible")
         and same(admission.get("missing_features"), missing)
         and admission.get("feature_policy") == "original_fields_only",
         "E_ADMISSION", "faithful admission must be established on original fields")
    need(verdict.get("admission") == admission, "E_ADMISSION_REPORT",
         "verdict must preserve the admission result and limitations")
    need(run.get("status") == ("replayed" if faithful else "blocked_before_replay"),
         "E_ADMISSION_RUN", "an inadmissible rule cannot be reported as replayed")
    actual = lines(root, artifact + "/results.jsonl", allow_empty=not faithful)
    if not faithful:
        need(not actual, "E_BLOCKED_REPLAY",
             "inadmissible sample must not be partially scored or patched")
    keys = ("item_id", "implementation", "threshold")
    got = indexed_rows(actual, keys, "E_REPLAY_MATRIX")
    wanted = indexed_rows(expected, keys, "E_REPLAY_MATRIX")
    need(set(got) == set(wanted), "E_REPLAY_MATRIX",
         "missing, duplicate, or extra replay cells")
    for key, target in wanted.items():
        row = got[key]
        need(row.get("family") == target["family"], "E_REPLAY_FAMILY",
             "item family changed in replay")
        need(same(row.get("score"), target["score"]), "E_REPLAY_SCORE",
             "coverage score is not a replay of the frozen rule")
        need(type(row.get("rejected")) is bool
             and row["rejected"] == target["rejected"], "E_REPLAY_REJECTION",
             "rejection decision differs from exact frozen rule")
        for field in ("baseline_abstained", "baseline_useful_retrieval"):
            need(type(row.get(field)) is bool and row[field] == target[field],
                 "E_REPLAY_CONTROL", "baseline outcome changed in replay")
        for field in ("useful_retrieval_lost", "useful_retrieval_retained"):
            need(type(row.get(field)) is bool and row[field] == target[field],
                 "E_REPLAY_LOSS", "useful retrieval loss/retention is incorrect")

    controls = control_scores(items, baselines)
    actual_controls = indexed_rows(verdict.get("baseline_controls"),
                                   ("implementation", "family"), "E_CONTROLS")
    expected_controls = indexed_rows(controls, ("implementation", "family"), "E_CONTROLS")
    need(same(actual_controls, expected_controls), "E_CONTROLS",
         "prior baseline controls must be unchanged and separately scored by family")
    scores = family_scores(expected)
    actual_scores = indexed_rows(verdict.get("family_scores"),
                                ("implementation", "family", "threshold"), "E_FAMILY_SCORES")
    expected_scores = indexed_rows(scores, ("implementation", "family", "threshold"),
                                  "E_FAMILY_SCORES")
    need(set(actual_scores) == set(expected_scores), "E_FAMILY_SCORES",
         "all implementation/family/threshold scores must be preserved")
    for key, target in expected_scores.items():
        row = actual_scores[key]
        need(all(field in row for field in (
            "rejected", "rejection_rate", "useful_lost", "useful_loss_rate")),
            "E_SEPARATE_METRICS", "rejection and useful loss require separate numbers")
        need(same(row["rejected"], target["rejected"])
             and same(row["rejection_rate"], target["rejection_rate"]),
             "E_REJECTION_SCORE", "incorrect rejection count or denominator")
        need(same(row["useful_lost"], target["useful_lost"])
             and same(row["useful_loss_rate"], target["useful_loss_rate"]),
             "E_LOSS_SCORE", "incorrect useful-retrieval loss count or denominator")
        need(all(same(row.get(field), target[field]) for field in (
            "items", "baseline_useful", "useful_retained", "baseline_abstentions")),
            "E_SCORE_DENOMINATORS", "incorrect counts or baseline denominators")
    expected_sensitivity = sensitivity(scores, grid, criterion) if faithful else []
    need(same(verdict.get("sensitivity"), expected_sensitivity), "E_SENSITIVITY_RESULTS",
         "report every frozen threshold against the registered criterion")
    passed = (next(x["meets_criterion"] for x in expected_sensitivity
                   if x["threshold"] == primary) if faithful else None)
    need(same(verdict.get("transfer_pass"), passed), "E_TRANSFER_DECISION",
         "transfer decision must follow the registered threshold and criterion")
    limits = verdict.get("limits")
    need(isinstance(limits, dict)
         and limits.get("sample") == "frozen_external_worlds/v2"
         and limits.get("items") == len(items)
         and limits.get("implementations") == len(implementations)
         and limits.get("rule_retuned") is False
         and limits.get("loss_denominator") == "baseline_useful_retrievals"
         and limits.get("zero_useful_denominator") == "null_rate_zero_count"
         and isinstance(limits.get("cannot_establish"), list)
         and {"generalization", "causality", "no_unrecorded_runs",
              "independent_execution_attestation"}.issubset(limits["cannot_establish"]),
         "E_LIMITS", "limits, denominator conventions, and provenance limits required as data")
    need(same(verdict.get("prior_measurement"), PRIOR_FACTS), "E_PRIOR_MEASUREMENT",
         "must preserve the prior measurement and never-before-admitted distinction")
    prior_paths = (S11 + "/verdict.json", S7 + "/verdict.json",
                   S10 + "/verdict.json", S6 + "/results.jsonl")
    need(verdict.get("prior_sources_sha256") ==
         {p: digest(raw(root, p)) for p in prior_paths},
         "E_PRIOR_REFERENCES", "prior controls and measurement sources must be bound")
    need(verdict.get("evidence_class") == "external_transfer"
         and verdict.get("roadmap_lane") == "R-PE"
         and verdict.get("pool_with_internal_evidence") is False,
         "E_EVIDENCE_CLASS", "external transfer must remain a separate evidence class")
    updates = verdict.get("answer_updates")
    need(isinstance(updates, dict) and set(updates) == {"Q2", "Q5"},
         "E_ANSWER_STEPS", "must move both Q2 and Q5 next steps")
    q2, q5 = updates["Q2"], updates["Q5"]
    need(isinstance(q2, dict) and isinstance(q5, dict)
         and q2.get("external_assessment") == ("replayed" if faithful else "blocked")
         and q2.get("separate_rejection_and_loss") is True
         and q2.get("post_result_threshold_selection") is False
         and q5.get("faithfully_admitted") is faithful
         and q5.get("preregistered") is True
         and q5.get("baseline_controls_preserved") is True
         and q5.get("separate_family_scores") is True,
         "E_ANSWER_SUBSTANCE", "Q2/Q5 updates must describe the actual transfer distinctions")


def execute(root, artifact=ARTIFACT):
    try:
        check(root, artifact)
        return 0, "CLEAN S13-1G"
    except Finding as exc:
        return 1, "FINDING %s: %s" % (exc.name, exc.detail)
    except Exception as exc:
        # Malformed input and environmental failures must not escape as tracebacks.
        return 1, "FINDING E_CHECKER_INPUT: %s: %s" % (type(exc).__name__, str(exc))


def write_json(root, path, value):
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(canonical(value) + "\n", encoding="utf-8")


def write_lines(root, path, values):
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(canonical(x) + "\n" for x in values), encoding="utf-8")


def commit_all(root, message):
    git(root, "add", "-A")
    git(root, "-c", "user.name=S13 gate selftest",
        "-c", "user.email=s13-selftest@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD").stdout.decode().strip()


def fixture(root, mutation=None, stage="verdict", blocked=False):
    """Generate evidence independently of any real artifact or builder."""
    git(root, "init", "-q")
    harness = S7 + "/declare_then_run.py"
    rule = {
        "score": {"op": "div", "args": [
            {"path": "item.sample.covered"}, {"path": "item.sample.total"}]},
        "reject": {"op": "lt", "args": [{"var": "score"}, {"var": "threshold"}]},
    }
    grid = [0.25, 0.5]
    write_json(root, S11 + "/declaration.json", {"rule": rule, "threshold_grid": grid})
    p = root / (S11 + "/design.md")
    p.write_text(
        "Frozen coverage = covered / total; reject iff coverage < threshold.\n"
        "Frozen grid: 0.25, 0.5. No external retuning.\n", encoding="utf-8")
    for path in (S11 + "/verdict.json", S7 + "/verdict.json", S10 + "/verdict.json"):
        write_json(root, path, {"synthetic_prior": True})
    write_lines(root, S6 + "/results.jsonl", [{"synthetic_selectivity_control": True}])
    write_json(root, UPSTREAM + "/worlds/v2/sample.json", {"frozen": True, "items": 40})
    hp = root / harness
    hp.write_text(
        "# Synthetic frozen S7 declare-then-run harness; never executed by gate.\n"
        "def main():\n    return 0\n", encoding="utf-8")
    items = []
    for i in range(40):
        covered = 4 if i < 22 else (i - 22) % 3
        item = {"id": "i%02d" % i, "family": "A" if i % 2 == 0 else "B",
                "sample": {"covered": covered, "total": 4}}
        if blocked and i == 39:
            del item["sample"]["covered"]
        items.append(item)
    baselines = []
    for m, count in enumerate((11, 13, 15, 18, 21)):
        for i, item in enumerate(items):
            baselines.append({
                "item_id": item["id"], "implementation": "impl%d" % m,
                "abstained": False, "useful_retrieval": i < count,
            })
    write_lines(root, S7 + "/items.jsonl", items)
    write_lines(root, S10 + "/results.jsonl", baselines)
    state = {"root": root, "harness": harness}
    if stage == "source" and mutation:
        mutation(state)
    source_commit = commit_all(root, "freeze synthetic external inputs")
    ids = {x["id"]: x for x in items}
    bases = {(x["item_id"], x["implementation"]): x for x in baselines}
    expected, missing = audit_replay(rule, grid, ids, bases)
    criterion = {
        "unit": "implementation_family",
        "decision": "all_cells_at_registered_threshold",
        "min_rejection_rate": 0.1, "max_useful_loss_rate": 0,
        "zero_useful_denominator": "null_rate_zero_count",
    }
    manifest_paths = set(SOURCES) | upstream_files(root) | {harness}
    manifest = {x: digest(raw(root, x)) for x in sorted(manifest_paths)}
    declaration = {
        "schema": SCHEMA, "source_commit": source_commit,
        "rule": copy.deepcopy(rule), "threshold_grid": grid[:],
        "sensitivity_grid": grid[:], "primary_threshold": 0.5,
        "threshold_selection": "preregistered", "transfer_criterion": criterion,
        "baseline_policy": "all_five_unchanged_per_family",
        "harness": harness, "input_sha256": manifest,
        "sample": {
            "evidence_class": "external", "version": "worlds/v2",
            "items": S7 + "/items.jsonl", "upstream": UPSTREAM,
            "baselines": S10 + "/results.jsonl", "unchanged": True,
        },
        "admission": {
            "status": "inadmissible" if missing else "faithful",
            "missing_features": missing, "feature_policy": "original_fields_only",
        },
    }
    state["d"] = declaration
    state["results"] = copy.deepcopy(expected)
    if stage == "declaration" and mutation:
        mutation(state)
    write_json(root, ARTIFACT + "/declaration.json", declaration)
    prereg = commit_all(root, "preregister synthetic transfer")
    run = {
        "schema": SCHEMA, "preregistration_commit": prereg,
        "primary_threshold": 0.5, "harness": harness,
        "harness_sha256": digest(raw(root, harness)),
        "mode": "local", "cost_usd": 0, "llm_calls": 0, "network_calls": 0,
        "argv": ["python3", harness, "--declaration", ARTIFACT + "/declaration.json"],
        "invocation": "G3", "input_sha256": copy.deepcopy(manifest),
        "declaration_sha256": digest(raw(root, ARTIFACT + "/declaration.json")),
        "status": "blocked_before_replay" if missing else "replayed",
    }
    state["run"] = run
    state["prereg"] = prereg
    if stage == "run" and mutation:
        mutation(state)
    write_json(root, ARTIFACT + "/run.json", run)
    write_lines(root, ARTIFACT + "/results.jsonl", state["results"])
    run_commit = commit_all(root, "record synthetic transfer replay")
    scores = family_scores(expected)
    sens = sensitivity(scores, grid, criterion) if not missing else []
    verdict = {
        "schema": SCHEMA, "preregistration_commit": prereg, "run_commit": run_commit,
        "primary_threshold": 0.5, "admission": copy.deepcopy(declaration["admission"]),
        "baseline_controls": control_scores(ids, bases), "family_scores": scores,
        "sensitivity": sens,
        "transfer_pass": None if missing else next(
            x["meets_criterion"] for x in sens if x["threshold"] == 0.5),
        "limits": {
            "sample": "frozen_external_worlds/v2", "items": 40, "implementations": 5,
            "rule_retuned": False, "loss_denominator": "baseline_useful_retrievals",
            "zero_useful_denominator": "null_rate_zero_count",
            "cannot_establish": [
                "generalization", "causality", "no_unrecorded_runs",
                "independent_execution_attestation",
            ],
        },
        "prior_measurement": copy.deepcopy(PRIOR_FACTS),
        "prior_sources_sha256": {
            x: digest(raw(root, x)) for x in (
                S11 + "/verdict.json", S7 + "/verdict.json",
                S10 + "/verdict.json", S6 + "/results.jsonl")},
        "evidence_class": "external_transfer", "roadmap_lane": "R-PE",
        "pool_with_internal_evidence": False,
        "answer_updates": {
            "Q2": {
                "external_assessment": "blocked" if missing else "replayed",
                "separate_rejection_and_loss": True,
                "post_result_threshold_selection": False,
            },
            "Q5": {
                "faithfully_admitted": not bool(missing), "preregistered": True,
                "baseline_controls_preserved": True, "separate_family_scores": True,
            },
        },
    }
    state["v"] = verdict
    if stage == "verdict" and mutation:
        mutation(state)
    write_json(root, ARTIFACT + "/verdict.json", verdict)
    if stage == "after" and mutation:
        mutation(state)
    return state


def change(path, value):
    def mutate(state):
        target = state
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = copy.deepcopy(value)
    return mutate


def remove(path):
    def mutate(state):
        target = state
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]
    return mutate


def selftest():
    """Every negative fixture must fail by its own specific finding, not merely fail."""
    cases = []

    def case(name, marker, stage, mutation, blocked=False):
        cases.append((name, marker, stage, mutation, blocked))

    case("missing_declared_source", "E_REQUIRED_FILE", "after",
         lambda s: (s["root"] / (S6 + "/results.jsonl")).unlink())
    case("malformed_machine_evidence", "E_JSON", "after",
         lambda s: (s["root"] / (ARTIFACT + "/verdict.json")).write_text("{"))
    case("empty_selectivity_control", "E_EMPTY_INPUT", "after",
         lambda s: (s["root"] / (S6 + "/results.jsonl")).write_text(""))
    case("unsupported_rule_translation", "E_RULE_UNSUPPORTED", "source",
         lambda s: write_json(s["root"], S11 + "/declaration.json",
                              {"rule": "coverage", "threshold_grid": [0.25, 0.5]}))
    case("empty_frozen_design", "E_SOURCE_DESIGN", "after",
         lambda s: (s["root"] / (S11 + "/design.md")).write_text(""))
    case("retuned_rule", "E_RULE_RETUNED", "declaration",
         change(("d", "rule", "reject", "op"), "le"))
    case("trimmed_threshold_grid", "E_GRID", "declaration",
         change(("d", "threshold_grid"), [0.5]))
    case("missing_sensitivity_plan", "E_SENSITIVITY_PLAN", "declaration",
         remove(("d", "sensitivity_grid")))
    case("internal_sample_substituted", "E_SAMPLE_IDENTITY", "declaration",
         change(("d", "sample", "evidence_class"), "internal"))
    case("criterion_combines_loss_and_rejection", "E_TRANSFER_CRITERION", "declaration",
         change(("d", "transfer_criterion"), {"combined_accuracy_min": 0.9}))
    case("post_result_threshold_selection", "E_THRESHOLD_SELECTION", "declaration",
         change(("d", "threshold_selection"), "best_observed"))
    case("controls_not_preserved_in_plan", "E_CONTROL_PLAN", "declaration",
         change(("d", "baseline_policy"), "best_implementation_only"))
    case("new_harness_substituted", "E_HARNESS", "run",
         change(("run", "harness"), ARTIFACT + "/new_harness.py"))
    case("remote_execution", "E_LOCAL", "run", change(("run", "mode"), "remote"))
    case("paid_execution", "E_COST", "run", change(("run", "cost_usd"), 0.01))
    case("llm_used", "E_LLM", "run", change(("run", "llm_calls"), 1))
    case("sample_refetched_during_replay", "E_NETWORK", "run",
         change(("run", "network_calls"), 1))
    case("invocation_not_bound_to_declaration", "E_INVOCATION", "run",
         change(("run", "argv"), ["python3", S7 + "/declare_then_run.py"]))
    case("G3_not_invoked", "E_G3", "run", change(("run", "invocation"), "G2"))
    case("preregistered_at_run_commit", "E_PREREG_ORDER", "verdict",
         lambda s: s["v"].update(preregistration_commit=s["v"]["run_commit"]))
    case("receipt_points_to_wrong_preregistration", "E_PREREG_RECEIPT", "run",
         lambda s: s["run"].update(preregistration_commit=s["d"]["source_commit"]))

    def edited_declaration(s):
        d = copy.deepcopy(s["d"])
        d["unregistered_note"] = "added after results"
        write_json(s["root"], ARTIFACT + "/declaration.json", d)

    case("declaration_edited_after_run", "E_PREREG_DECLARATION", "after",
         edited_declaration)
    case("results_already_present_at_preregistration", "E_PREREG_CONTAMINATION",
         "declaration",
         lambda s: write_lines(s["root"], ARTIFACT + "/results.jsonl",
                               [{"premature_result": True}]))
    case("uncommitted_run_evidence", "E_RUN_BINDING", "after",
         lambda s: (s["root"] / (ARTIFACT + "/results.jsonl")).write_text(
             raw(s["root"], ARTIFACT + "/results.jsonl").decode() + "{}\n"))
    case("manifest_omits_prior_input", "E_INPUT_MANIFEST", "declaration",
         lambda s: s["d"]["input_sha256"].pop(S6 + "/results.jsonl"))
    case("wrong_input_digest", "E_INPUT_DIGEST", "declaration",
         change(("d", "input_sha256", S11 + "/design.md"), "0" * 64))

    def changed_frozen_input(s):
        path = UPSTREAM + "/worlds/v2/sample.json"
        write_json(s["root"], path, {"frozen": False, "items": 40})
        s["d"]["input_sha256"][path] = digest(raw(s["root"], path))

    case("changed_external_world_with_updated_digest", "E_FROZEN_INPUT",
         "declaration", changed_frozen_input)

    def removed_upstream_file(s):
        path = UPSTREAM + "/worlds/v2/extra.json"
        write_json(s["root"], path, {"original_member": True})
        # This file is frozen in the source snapshot but absent from every later
        # manifest. It tests set membership, not only hashes of retained files.
        original_commit = commit_all(s["root"], "synthetic earlier upstream member")
        (s["root"] / path).unlink()
        s["d"]["source_commit"] = original_commit

    case("upstream_file_removed_from_manifest", "E_UPSTREAM_MEMBERSHIP",
         "declaration", removed_upstream_file)
    case("run_uses_different_inputs", "E_RUN_INPUTS", "run",
         change(("run", "input_sha256"), {}))
    case("run_uses_different_declaration", "E_RUN_DECLARATION", "run",
         change(("run", "declaration_sha256"), "0" * 64))
    case("invented_feature_mapping", "E_ADMISSION", "declaration",
         change(("d", "admission", "feature_policy"), "impute_missing"))
    case("admission_report_changed", "E_ADMISSION_REPORT", "verdict",
         change(("v", "admission", "status"), "inadmissible"))
    case("blocked_sample_claimed_replayed", "E_ADMISSION_RUN", "run",
         change(("run", "status"), "replayed"), blocked=True)
    case("partially_scored_inadmissible_sample", "E_BLOCKED_REPLAY", "run",
         change(("results",), [{"item_id": "i00", "implementation": "impl0",
                                "threshold": 0.5}]), blocked=True)
    case("missing_replay_cell", "E_REPLAY_MATRIX", "run",
         lambda s: s["results"].pop())
    case("family_reassigned", "E_REPLAY_FAMILY", "run",
         change(("results", 0, "family"), "pooled"))
    case("incorrect_rule_score", "E_REPLAY_SCORE", "run",
         change(("results", 0, "score"), 0.9))
    case("incorrect_rejection_decision", "E_REPLAY_REJECTION", "run",
         lambda s: s["results"][0].update(rejected=not s["results"][0]["rejected"]))
    case("baseline_outcome_changed_in_replay", "E_REPLAY_CONTROL", "run",
         change(("results", 0, "baseline_useful_retrieval"), False))
    case("incorrect_useful_retrieval_loss", "E_REPLAY_LOSS", "run",
         change(("results", 0, "useful_retrieval_lost"), True))
    case("prior_control_score_changed", "E_CONTROLS", "verdict",
         change(("v", "baseline_controls", 0, "useful_retrievals"), 999))
    case("families_pooled_in_report", "E_FAMILY_SCORES", "verdict",
         lambda s: s["v"]["family_scores"].pop())
    case("loss_hidden_in_combined_metric", "E_SEPARATE_METRICS", "verdict",
         remove(("v", "family_scores", 0, "useful_lost")))
    case("incorrect_rejection_aggregate", "E_REJECTION_SCORE", "verdict",
         change(("v", "family_scores", 0, "rejection_rate"), 0.999))
    case("incorrect_loss_denominator", "E_LOSS_SCORE", "verdict",
         change(("v", "family_scores", 0, "useful_loss_rate"), 0.999))
    case("incorrect_baseline_denominator", "E_SCORE_DENOMINATORS", "verdict",
         change(("v", "family_scores", 0, "baseline_useful"), 999))
    case("sensitivity_cherry_picked", "E_SENSITIVITY_RESULTS", "verdict",
         lambda s: s["v"]["sensitivity"].pop())
    case("unsupported_transfer_success_claim", "E_TRANSFER_DECISION", "verdict",
         lambda s: s["v"].update(transfer_pass=not s["v"]["transfer_pass"]))
    case("limits_omitted", "E_LIMITS", "verdict", remove(("v", "limits")))
    case("previous_admission_invented", "E_PRIOR_MEASUREMENT", "verdict",
         change(("v", "prior_measurement",
                 "coverage_rule_previously_admitted_to_external_sample"), True))
    case("selectivity_prior_reference_omitted", "E_PRIOR_REFERENCES", "verdict",
         remove(("v", "prior_sources_sha256", S6 + "/results.jsonl")))
    case("external_and_internal_evidence_pooled", "E_EVIDENCE_CLASS", "verdict",
         change(("v", "pool_with_internal_evidence"), True))
    case("Q5_next_step_omitted", "E_ANSWER_STEPS", "verdict",
         remove(("v", "answer_updates", "Q5")))
    case("Q2_allows_post_result_selection", "E_ANSWER_SUBSTANCE", "verdict",
         change(("v", "answer_updates", "Q2", "post_result_threshold_selection"), True))

    # The expected markers are deliberately distinct. A generic failure cannot
    # satisfy these tests, and an early accidental failure cannot mask a later one.
    markers = [x[1] for x in cases]
    need(len(markers) == len(set(markers)), "E_SELFTEST",
         "negative fixtures must have distinct expected named findings")
    passed = []
    with tempfile.TemporaryDirectory(prefix="s13-gate-selftest-") as temp:
        base = Path(temp)
        for name, blocked in (
            ("accept_minimal_conforming", False),
            ("accept_honest_inadmissibility_without_partial_replay", True),
        ):
            root = base / name
            root.mkdir()
            fixture(root, blocked=blocked)
            code, message = execute(root)
            need(code == 0, "E_SELFTEST", name + " unexpectedly failed: " + message)
            passed.append(name)
        for n, (name, marker, stage, mutation, blocked) in enumerate(cases):
            root = base / ("%02d_" % n + name)
            root.mkdir()
            fixture(root, mutation, stage, blocked)
            code, message = execute(root)
            need(code == 1 and message.startswith("FINDING " + marker + ":")
                 and "Traceback (most recent call last)" not in message,
                 "E_SELFTEST",
                 "%s expected exit 1/%s; got %s/%s" % (name, marker, code, message))
            passed.append(name + ":" + marker)

    print("SELFTEST PASS: %d acceptance/rejection assertions" % len(passed))
    for name in passed:
        print("  " + name)
    return 0


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Finding("E_ARGUMENTS", message)


def default_root():
    here = Path(__file__).resolve().parent
    for parent in (here,) + tuple(here.parents):
        if (parent / "team").is_dir():
            return parent
    return Path.cwd()


def main(argv=None):
    try:
        parser = Parser(description=__doc__)
        parser.add_argument("--selftest", action="store_true")
        parser.add_argument("--root", type=Path, default=None)
        parser.add_argument("--artifact", default=ARTIFACT)
        args = parser.parse_args(argv)
        if args.selftest:
            return selftest()
        code, message = execute(args.root if args.root is not None else default_root(),
                                args.artifact)
        print(message)
        return code
    except Finding as exc:
        print("FINDING %s: %s" % (exc.name, exc.detail))
        return 1
    except KeyboardInterrupt:
        print("FINDING E_INTERRUPTED: checker interrupted")
        return 1
    except Exception as exc:
        print("FINDING E_CHECKER_INPUT: %s: %s" % (type(exc).__name__, str(exc)))
        return 1


if __name__ == "__main__":
    sys.exit(main())