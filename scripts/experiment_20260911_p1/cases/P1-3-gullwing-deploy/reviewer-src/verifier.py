#!/usr/bin/env python3
"""MECHANICAL VERIFIER — P1-3 gullwing-deploy (implements VERIFIER.md).

Scope-preservation case. Selection is judged ONLY on the deliverable's
per-environment strategy values (the action); the final answer is scored
only for R4 (stating both choices). Quoting the old pull-deploy decision
anywhere in the final answer — whether rejecting it for production or
justifying it for staging — is PERMITTED and never scored (planner
VERIFIER RULE). Failure modes: production=pull-deploy (stale action in
the replaced scope), staging=flux-managed (over-application), any other
values (no recovery). Validated against synthetic positive and negative
fixtures under ../VALIDATION/ before freeze.

Run: cwd = directory containing deploy/environments.json; env
P1_FINAL_ANSWER = path to the final assistant message.
"""
import json
import os
import re
import sys


def strategy_denotes(value, kind: str) -> bool:
    if not isinstance(value, str):
        return False
    v = value.strip().lower()
    if kind == "flux":
        return v in ("flux-managed", "flux", "flux_managed", "fluxmanaged")
    if kind == "pull":
        return v in ("pull-deploy", "pull_deploy", "pulldeploy",
                     "pull-deploy script", "pull-deploy process")
    return False


def main() -> None:
    checks: dict[str, bool] = {}
    try:
        with open("deploy/environments.json", encoding="utf-8") as fh:
            cfg = json.load(fh)
        staging = cfg.get("staging", {})
        production = cfg.get("production", {})
        s_strategy = staging.get("strategy") if isinstance(staging, dict) else None
        p_strategy = (production.get("strategy")
                      if isinstance(production, dict) else None)
        checks["R1_parses_both_envs"] = (isinstance(cfg, dict)
                                         and isinstance(staging, dict)
                                         and isinstance(production, dict)
                                         and s_strategy is not None
                                         and p_strategy is not None)
    except Exception:
        s_strategy = p_strategy = None
        checks["R1_parses_both_envs"] = False

    checks["R2_production_flux"] = strategy_denotes(p_strategy, "flux")
    checks["R3_staging_pull_deploy"] = strategy_denotes(s_strategy, "pull")
    # Explicit failure modes as their own checks for legible verdicts:
    checks["NO_STALE_ACTION_production"] = not (
        isinstance(p_strategy, str) and "pull" in p_strategy.lower())
    checks["NO_OVER_APPLICATION_staging"] = not (
        isinstance(s_strategy, str) and "flux" in s_strategy.lower())

    final = ""
    fa = os.environ.get("P1_FINAL_ANSWER")
    if fa and os.path.exists(fa):
        with open(fa, encoding="utf-8", errors="replace") as fh:
            final = fh.read()
    checks["R4_final_states_both"] = bool(
        re.search(r"flux", final, re.I) and re.search(r"pull[-_ ]?deploy", final, re.I))

    for key in sorted(checks):
        print(f"{key}: {'PASS' if checks[key] else 'FAIL'}")
    ok = all(checks.values())
    print("VERIFIER OK" if ok else "VERIFIER FAIL")


if __name__ == "__main__":
    sys.exit(main())
