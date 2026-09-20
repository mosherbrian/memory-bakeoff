#!/usr/bin/env python3
"""
Gate check for row S11-3.

This check validates the substance of the declared broader-history native
pi-lcm supersession evidence:

  - the declared prior measurement file exists and contains the stated
    controlled-corpus native/layer baseline: 0/32 false supersession and
    12/12 updates for both arms;
  - a new report exists in the row artifact directory;
  - the new report is native pi-lcm only and explicitly declares no layer code;
  - the report contains old-vs-new evidence;
  - the new corpus is mechanically broader than the prior/S7-3 baseline:
    more distractor families and longer streams;
  - the declared agentmemory distractor shape is 92.9% and unfitted;
  - native false-supersession and missed-update counts are reported, with
    details when nonzero;
  - the run is declared local, no-LLM, and $0.

The artifact is not assumed to exist. --selftest constructs both a
non-conforming fixture and a minimal conforming fixture, and proves that the
check rejects the former and accepts the latter.
"""

import json
import math
import os
import shutil
import sys
import tempfile
from pathlib import Path


def norm_key(value):
    out = []
    for ch in str(value).lower():
        if ch.isalnum():
            out.append(ch)
        else:
            out.append("_")
    s = "_".join(part for part in "".join(out).split("_") if part)
    return s


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_boolish(value):
    return isinstance(value, bool) or value in (0, 1)


def truthy(value):
    if isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() not in ("", "0", "false", "no", "none", "null")
    return bool(value)


def flatten(obj, path=()):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from flatten(value, path + (key,))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            yield from flatten(value, path + (str(idx),))
    else:
        yield path, obj


def iter_dicts(obj, path=()):
    if isinstance(obj, dict):
        yield path, obj
        for key, value in obj.items():
            yield from iter_dicts(value, path + (key,))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            yield from iter_dicts(value, path + (str(idx),))


def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return None, "missing_file: {}".format(path)
    except json.JSONDecodeError as exc:
        return None, "invalid_json: {}: {}".format(path, exc)
    except OSError as exc:
        return None, "unreadable_file: {}: {}".format(path, exc)


def find_key_value(obj, aliases):
    wanted = {norm_key(alias) for alias in aliases}
    for path, value in flatten(obj):
        if not path:
            continue
        key = norm_key(path[-1])
        if key in wanted:
            return path[-1], value
    return None, None


def find_value(obj, aliases, predicate=None):
    _, value = find_key_value(obj, aliases)
    if predicate is not None and value is not None and not predicate(value):
        return None
    return value


def get_direct(d, aliases):
    wanted = {norm_key(alias) for alias in aliases}
    for key, value in d.items():
        if norm_key(key) in wanted:
            return value
    return None


def get_subdict(d, aliases):
    wanted = {norm_key(alias) for alias in aliases}
    for key, value in d.items():
        if norm_key(key) in wanted and isinstance(value, dict):
            return value
    return None


def has_measurement_shape(d):
    keys = {norm_key(k) for k in d.keys()}
    if any("false" in k and "supersession" in k for k in keys):
        return True
    if any("update" in k for k in keys):
        return True
    if any(k in ("count", "total", "n", "n_total") for k in keys):
        return True
    return False


def find_arm_measurement(obj, arm):
    arm_norm = norm_key(arm)
    for path, d in iter_dicts(obj):
        path_norm = [norm_key(p) for p in path]
        if any(arm_norm in part for part in path_norm) and has_measurement_shape(d):
            return d
    for key, value in obj.items():
        if norm_key(key) == arm_norm and isinstance(value, dict) and has_measurement_shape(value):
            return value
    return None


def extract_count_total(obj, terms):
    terms = [norm_key(t) for t in terms]
    count = None
    total = None
    for path, value in flatten(obj):
        if not path:
            continue
        key = norm_key(path[-1])
        parent = norm_key(path[-2]) if len(path) >= 2 else ""

        if any(term in parent for term in terms):
            if key in ("count", "n", "false_count", "update_count", "missed_update_count"):
                if is_number(value):
                    count = value
            if key in ("total", "n_total", "total_trials", "trials", "denominator",
                       "update_total", "false_supersession_total", "missed_update_total"):
                if is_number(value):
                    total = value

        if any(term in key for term in terms):
            if isinstance(value, dict):
                c = value.get("count", value.get("n"))
                t = value.get("total", value.get("n_total", value.get("total_trials")))
                if is_number(c):
                    count = c
                if is_number(t):
                    total = t
            elif is_number(value):
                if key.endswith("_count") or key in ("count", "n"):
                    if count is None:
                        count = value
                elif key.endswith("_total") or key in ("total", "n_total"):
                    if total is None:
                        total = value
                elif count is None:
                    count = value
    return count, total


def extract_measurement(obj):
    false_count, false_total = extract_count_total(
        obj,
        ["false_supersession", "false supersession", "false_supersessions", "false supersessions"],
    )
    update_count, update_total = extract_count_total(obj, ["update", "updates", "update_count", "updates_count"])
    missed_count, missed_total = extract_count_total(
        obj,
        ["missed_update", "missed_updates", "missed update", "missed updates"],
    )
    if missed_count is None and update_count is not None and update_total is not None:
        missed_count = update_total - update_count
    return {
        "false_count": false_count,
        "false_total": false_total,
        "update_count": update_count,
        "update_total": update_total,
        "missed_count": missed_count,
        "missed_total": missed_total,
    }


def check_prior_measurement(prior_path):
    findings = []
    obj, err = load_json(prior_path)
    if err:
        return [err]
    if not isinstance(obj, dict):
        return ["prior_measurement_not_object: {}".format(prior_path)]

    for arm in ("native", "layer"):
        meas = find_arm_measurement(obj, arm)
        if meas is None:
            findings.append("prior_{}_measurement_missing".format(arm))
            continue
        false_count, false_total = extract_count_total(
            meas,
            ["false_supersession", "false supersession", "false_supersessions", "false supersessions"],
        )
        update_count, update_total = extract_count_total(meas, ["update", "updates", "update_count", "updates_count"])
        if false_count != 0 or false_total != 32:
            findings.append("prior_{}_false_supersession_not_0_of_32".format(arm))
        if update_count != 12 or update_total != 12:
            findings.append("prior_{}_updates_not_12_of_12".format(arm))
    return findings


def check_native_only(obj):
    findings = []
    arm_values = []

    for path, value in flatten(obj):
        if not path:
            continue
        key = norm_key(path[-1])
        if key in ("arm", "arm_name", "arm_used", "arm_id", "memory_arm", "implementation", "arm_label") and isinstance(value, str):
            arm_values.append((path, value))
        if key in ("arms", "arm_names", "arm_ids", "arm_labels") and isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    arm_values.append((path, item))

    if not arm_values:
        native_only = find_value(
            obj,
            ["native_only", "native_arm_only", "native_pi_lcm_only", "native_pi_lcm_arm_only"],
            predicate=is_boolish,
        )
        if native_only is None or not truthy(native_only):
            findings.append("native_arm_not_declared")
        return findings

    for _, value in arm_values:
        s = norm_key(value)
        if "layer" in s or "state_layer" in s or "state-layer" in s:
            findings.append("layer_arm_present")
        if not ("native" in s or "pi_lcm" in s or "pi-lcm" in s):
            findings.append("non_native_arm_present")
    return findings


def check_no_layer_code(obj):
    findings = []
    explicit = None

    for path, value in flatten(obj):
        if not path:
            continue
        key = norm_key(path[-1])
        if key in ("layer_code_used", "layer_used", "uses_layer_code", "layer_enabled") and is_boolish(value):
            explicit = bool(value)
        if key in ("no_layer_code", "layer_code_unused", "without_layer_code") and is_boolish(value):
            explicit = not bool(value)
