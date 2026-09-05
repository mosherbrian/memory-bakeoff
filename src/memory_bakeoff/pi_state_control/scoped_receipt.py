"""`scoped-validation-receipt-v1`: what a passing check actually establishes.

Metadata only. Nothing here gates anything, and nothing here is allowed to say a
task is correct.

The programme has now measured the same confusion twice. In Gen49 an agent
edited a stale visible test, made it pass, earned a receipt and reached
control-valid done while still failing the hidden requirement. In Gen55 the stop
controller ended two runs on trees that a passing visible check had blessed and
the hidden verifier rejected. In both cases the receipt was true and the
inference drawn from it was too broad.

So a receipt says exactly one thing: *this command exited zero on this tree under
this configuration*. The scope class below records how much of the project that
command actually touched, using only what is visible in the command and the
repository - never the hidden verifier, never the reference fix.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

CONTRACT_VERSION = "scoped-validation-receipt-v1"

# Syntactic scope, from the command text alone.
SCOPE_CLASSES = ("project_wide_visible", "explicit_subset", "single_test_or_selector", "unknown_scope")

_SELECTOR = re.compile(r"(::|(?<!\w)-k(?=[\s=]))")
_PYTEST = re.compile(r"\bpytest\b")
_PATHISH = re.compile(r"(?<![\w/])((?:[\w.\-]+/)*[\w.\-]+\.py|(?:[\w.\-]+/)+)")


def classify_scope(command: str, project_wide_command: str) -> dict[str, Any]:
    """Where does this command sit between 'one test' and 'everything visible'?

    Deliberately syntactic. A command that names a single test, or filters with
    `-k`, is narrower than one that names a directory, which is narrower than the
    project-wide entrypoint. Anything unrecognised is `unknown_scope`, never a
    guess.
    """
    if not command:
        return {"scope_class": "unknown_scope", "targets": [], "reason": "no command recorded"}
    # Classify the pytest invocation itself. A `cd /some/path && ...` prefix is
    # navigation, and letting its directories count as targets makes a
    # project-wide run look like a subset.
    segments = [s.strip() for s in re.split(r"&&|\|\||;|\n|\|", command)]
    invocation = next((s for s in segments if _PYTEST.search(s)), None) or command
    normalized = " ".join(invocation.split())
    if _SELECTOR.search(normalized):
        targets = [t for t in _PATHISH.findall(normalized)]
        return {"scope_class": "single_test_or_selector", "targets": targets,
                "reason": "names an individual test or filters with -k"}
    if project_wide_command and project_wide_command.split("&&")[-1].strip() in normalized:
        return {"scope_class": "project_wide_visible", "targets": ["tests/"],
                "reason": "matches the frozen broadest shipped visible validation"}
    if _PYTEST.search(normalized):
        targets = [t for t in _PATHISH.findall(normalized) if t not in (".", "./")]
        # Naming the test directory runs every visible test, whatever the flags.
        # Requiring an exact string match against the frozen command would call
        # `pytest tests/ -v` a subset, which it plainly is not.
        directories = {t for t in targets if t.endswith("/")}
        if directories and directories <= {"tests/"} and not any(
                t.endswith(".py") for t in targets):
            return {"scope_class": "project_wide_visible", "targets": sorted(directories),
                    "reason": "runs the whole shipped tests directory, the broadest visible check"}
        if targets:
            return {"scope_class": "explicit_subset", "targets": targets,
                    "reason": "runs pytest against named paths rather than the project entrypoint"}
        return {"scope_class": "project_wide_visible", "targets": ["<default collection>"],
                "reason": "pytest with no path argument collects the whole project"}
    return {"scope_class": "unknown_scope", "targets": [],
            "reason": "not a recognised pytest invocation"}


def receipt(*, tree_digest: str, command: str, cwd: str, exit_status: int | None,
            event_index: Any, provenance: str, project_wide_command: str,
            changed_paths: list[str] | None = None) -> dict[str, Any]:
    """Describe one receipt. The authority statement is the only claim made."""
    scope = classify_scope(command, project_wide_command)
    return {
        "contract_version": CONTRACT_VERSION,
        "tracked_tree_digest": tree_digest,
        "validation_command": command,
        "cwd": cwd,
        "exit_status": exit_status,
        "event_index": event_index,
        "provenance": provenance,
        "scope_class": scope["scope_class"],
        "scope_reason": scope["reason"],
        "targets": scope["targets"],
        "changed_project_paths_on_this_tree": sorted(changed_paths or []),
        "broadest_visible_validation_for_this_task": project_wide_command,
        # The whole point. Nothing stronger may be written here.
        "authority": (f"command {command!r} exited {exit_status} on tracked tree "
                      f"{tree_digest} under the recorded configuration"),
        "establishes_task_correctness": False,
    }


def contract() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "purpose": "metadata describing what a passing visible check establishes, and no more",
        "scope_classes": list(SCOPE_CLASSES),
        "authority_form": "command X exited N on tracked tree Y under configuration Z",
        "forbidden_claims": ["task correct", "requirements satisfied", "implementation complete"],
        "hidden_verifier_is_never_an_input": True,
        "changes_no_control_behaviour": True,
        "contract_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
