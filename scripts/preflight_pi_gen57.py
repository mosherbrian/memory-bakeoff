#!/usr/bin/env python3
"""Gen57 Part D: prove both diagnostics on tiny synthetic fixtures, before any
historical outcome is read. IP1-IP4 are not touched. No model, no network."""
from __future__ import annotations

import json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen40 import block_network            # noqa: E402
from memory_bakeoff.pi_state_control import artifact_coverage as A  # noqa: E402
from memory_bakeoff.pi_state_control import tracked_digest as T     # noqa: E402

OUT = ROOT / "results" / "pi_artifact_coverage_gen57"

# Each fixture: initial files, final files, and what the diagnostics must say.
FIXTURES = {
    "changed_line_never_executed": {
        "initial": {"pkg/__init__.py": "", "pkg/core.py": "def used():\n    return 1\n\ndef unused():\n    return 0\n",
                    "tests/test_core.py": "from pkg.core import used\ndef test_used():\n    assert used() == 1\n"},
        "final_edit": {"pkg/core.py": ("def unused():\n    return 0\n", "def unused():\n    return 99\n")},
    },
    "executed_but_never_asserted": {
        "initial": {"pkg/__init__.py": "", "pkg/core.py": "def value():\n    return 1\n",
                    "tests/test_core.py": "from pkg.core import value\ndef test_runs():\n    value()\n"},
        "final_edit": {"pkg/core.py": ("    return 1\n", "    return 2\n")},
    },
    "executed_and_asserted": {
        "initial": {"pkg/__init__.py": "", "pkg/core.py": "def value():\n    return 1\n",
                    "tests/test_core.py": "from pkg.core import value\ndef test_value():\n    assert value() == 2\n"},
        "final_edit": {"pkg/core.py": ("    return 1\n", "    return 2\n")},
        "asserted": True,
    },
    "two_hunks_one_constrained": {
        "initial": {"pkg/__init__.py": "",
                    "pkg/core.py": "def a():\n    return 1\n\n\ndef b():\n    return 1\n",
                    "tests/test_core.py": "from pkg.core import a\ndef test_a():\n    assert a() == 2\n"},
        "final_edit": {"pkg/core.py": ("def a():\n    return 1\n\n\ndef b():\n    return 1\n",
                                       "def a():\n    return 2\n\n\ndef b():\n    return 2\n")},
    },
    "new_production_file_used": {
        "initial": {"pkg/__init__.py": "", "pkg/core.py": "def value():\n    return 1\n",
                    "tests/test_core.py": "from pkg.extra import helper\ndef test_helper():\n    assert helper() == 7\n"},
        "final_add": {"pkg/extra.py": "def helper():\n    return 7\n"},
    },
    "new_production_file_unused": {
        "initial": {"pkg/__init__.py": "", "pkg/core.py": "def value():\n    return 1\n",
                    "tests/test_core.py": "from pkg.core import value\ndef test_value():\n    assert value() == 1\n"},
        "final_add": {"pkg/orphan.py": "def never_called():\n    return 3\n"},
    },
    "test_only_change": {
        "initial": {"pkg/__init__.py": "", "pkg/core.py": "def value():\n    return 1\n",
                    "tests/test_core.py": "from pkg.core import value\ndef test_value():\n    assert value() == 1\n"},
        "final_edit": {"tests/test_core.py": ("def test_value():", "def test_value_renamed():")},
    },
}


def _hidden_verifier_absent_from_logic() -> bool:
    """Inspect code, not prose. The module's own docstring says the words."""
    import ast as _ast
    source = (ROOT / "src/memory_bakeoff/pi_state_control/artifact_coverage.py").read_text()
    tree = _ast.parse(source)
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Expr) and isinstance(node.value, _ast.Constant):
            continue          # a docstring
        for name in ("verifier", "reference_fix"):
            if isinstance(node, _ast.Name) and name in node.id:
                return False
            if isinstance(node, _ast.Attribute) and name in node.attr:
                return False
    return True


def build(spec: dict) -> tuple[Path, Path]:
    initial = Path(tempfile.mkdtemp(prefix="gen57-init-"))
    for name, text in spec["initial"].items():
        target = initial / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    final = Path(tempfile.mkdtemp(prefix="gen57-final-"))
    shutil.copytree(initial, final, dirs_exist_ok=True)
    for name, (old, new) in spec.get("final_edit", {}).items():
        target = final / name
        target.write_text(target.read_text().replace(old, new, 1))
    for name, text in spec.get("final_add", {}).items():
        target = final / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    return initial, final


def line_diagnostic(initial: Path, final: Path) -> dict:
    changed, total, hit = {}, 0, 0
    targets = [p for p in A.production_paths(final) if p.suffix == ".py"]
    for path in targets:
        relative = str(path.relative_to(final))
        info = A.changed_lines(initial, final, relative)
        if info["status"] == "deleted_only":
            continue
        executable = A.executable_lines(path)
        lines = sorted(set(info["lines"]) & executable)
        if lines:
            changed[relative] = lines
            total += len(lines)
    if total == 0:
        traced = A.run_traced_broad_check(final, targets)
        return {"category": "no_production_change", "changed_line_total": 0,
                "broad_passes": traced["passed"], "seconds": traced["seconds"]}
    traced = A.run_traced_broad_check(final, targets)
    misses = []
    for relative, lines in changed.items():
        resolved = str((final / relative).resolve())
        for line in lines:
            if (resolved, line) in traced["hits"]:
                hit += 1
            else:
                misses.append(f"{relative}:{line}")
    return {"category": "measured", "changed_line_total": total, "changed_line_hit_count": hit,
            "hit_fraction": round(hit / total, 3),
            "all_changed_executable_lines_hit": hit == total, "missed": misses,
            "broad_passes": traced["passed"], "seconds": traced["seconds"]}


def reversion_diagnostic(initial: Path, final: Path) -> dict:
    hunks = A.production_hunks(initial, final)
    killed = survived = unknown = 0
    details = []
    digest_before = T.tracked_digest(final)
    for hunk in hunks:
        probe = A.reverse_probe(final, hunk["patch"])
        if not probe["applied"]:
            unknown += 1
            details.append({"hunk": hunk["index"], "outcome": "unknown",
                            "reason": probe["apply_error"]})
            shutil.rmtree(probe["work"], ignore_errors=True)
            continue
        done = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q",
                               "-p", "no:cacheprovider"], cwd=probe["tree"],
                              capture_output=True, text=True, timeout=300)
        outcome = "killed_reversion" if done.returncode != 0 else "survived_reversion"
        killed += outcome == "killed_reversion"
        survived += outcome == "survived_reversion"
        details.append({"hunk": hunk["index"], "outcome": outcome, "paths": hunk["paths"]})
        shutil.rmtree(probe["work"], ignore_errors=True)
    return {"hunks": len(hunks), "killed": killed, "survived": survived, "unknown": unknown,
            "any_survived_reversion": survived > 0, "details": details,
            "final_digest_unchanged_after_probes": T.tracked_digest(final) == digest_before}


def main() -> int:
    block_network()
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, spec in FIXTURES.items():
        initial, final = build(spec)
        results[name] = {"line": line_diagnostic(initial, final),
                         "reversion": reversion_diagnostic(initial, final),
                         "tests_changed_since_initial":
                             (initial / "tests/test_core.py").read_text()
                             != (final / "tests/test_core.py").read_text()}
        shutil.rmtree(initial, ignore_errors=True)
        shutil.rmtree(final, ignore_errors=True)

    checks = {
        "1_changed_line_never_executed_reports_uncovered":
            results["changed_line_never_executed"]["line"]["all_changed_executable_lines_hit"] is False,
        "2_executed_but_unasserted_hits_line_and_survives_reversion":
            results["executed_but_never_asserted"]["line"]["all_changed_executable_lines_hit"] is True
            and results["executed_but_never_asserted"]["reversion"]["any_survived_reversion"] is True,
        "3_executed_and_asserted_hits_line_and_kills_reversion":
            results["executed_and_asserted"]["line"]["all_changed_executable_lines_hit"] is True
            and results["executed_and_asserted"]["reversion"]["killed"] >= 1,
        "7_test_only_change_reports_no_production_change":
            results["test_only_change"]["line"]["category"] == "no_production_change"
            and results["test_only_change"]["tests_changed_since_initial"] is True,
        "8_probe_isolation_restores_the_final_tree":
            all(r["reversion"]["final_digest_unchanged_after_probes"] for r in results.values()),
        "4_two_hunks_one_constrained_are_distinguished":
            results["two_hunks_one_constrained"]["reversion"]["killed"] >= 1
            and results["two_hunks_one_constrained"]["reversion"]["survived"] >= 1,
        "5_new_production_file_used_is_killed_by_deletion_probe":
            results["new_production_file_used"]["reversion"]["killed"] >= 1,
        "6_new_production_file_unused_survives_deletion_probe":
            results["new_production_file_unused"]["reversion"]["any_survived_reversion"] is True,
        "9_hidden_verifier_absent_from_diagnostic_logic":
            _hidden_verifier_absent_from_logic(),
    }
    report = {"contract": A.contract(), "fixtures": results, "checks": checks,
              "no_network": True}
    report["passed"] = all(checks.values())
    (OUT / "artifact_coverage_contract.json").write_text(
        json.dumps(A.contract(), indent=2, sort_keys=True) + "\n")
    (OUT / "synthetic_preflight.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"checks": checks, "passed": report["passed"],
                      "line": {k: v["line"].get("category") or v["line"] for k, v in results.items()}},
                     indent=1))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
