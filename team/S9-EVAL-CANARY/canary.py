#!/usr/bin/env python3
"""S10-3 pre-sweep canary (kiln-flash, 2026-09-18).

Fail-closed: the wrapped COMMAND runs only when every guard in the manifest
passes first. Any guard that exits non-zero, is missing from disk, or
exceeds the timeout is named on stdout, the command is NOT run, and the
exit is non-zero. A manifest that lists no guards is itself a failure:
checking nothing is not a clean sweep.

Usage:
  python3 canary.py --team TEAM --manifest FILE [--timeout SECONDS] [-- COMMAND ...]

Guards are [{script: path relative to TEAM, argv: [...]}]. Each runs under
the same interpreter with its argv; exit 0 is pass. The command after `--`
inherits this canary's stdout/stderr and its exit code becomes the canary's.
No LLM, no network."""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="fail-closed pre-sweep guard canary")
    ap.add_argument("--team", required=True,
                    help="team directory the guard scripts are relative to")
    ap.add_argument("--manifest", required=True,
                    help="guards.json: [{script, argv: [...]}]")
    ap.add_argument("--timeout", type=float, default=120.0,
                    help="per-guard timeout in seconds")
    ap.add_argument("cmd", nargs=argparse.REMAINDER,
                    help="the expensive command, after --")
    args = ap.parse_args()

    team = Path(args.team)
    guards = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    failures: list = []
    if not guards:
        failures.append("guards manifest lists no guards: nothing was checked")
    for g in guards:
        script = team / g["script"]
        argv = list(g.get("argv", []))
        if not script.is_file():
            failures.append(f"{g['script']}: guard missing from disk")
            continue
        try:
            p = subprocess.run([sys.executable, str(script), *argv],
                               capture_output=True, text=True,
                               timeout=args.timeout)
        except subprocess.TimeoutExpired:
            failures.append(f"{g['script']}: exceeded the "
                            f"{args.timeout:g}s canary timeout")
            continue
        except OSError as e:
            failures.append(f"{g['script']}: could not run ({e})")
            continue
        if p.returncode != 0:
            detail = (p.stdout.strip().splitlines() or
                      p.stderr.strip().splitlines() or [""])[0][:120]
            failures.append(f"{g['script']}: exit {p.returncode}"
                            + (f" :: {detail}" if detail else ""))

    if failures:
        for f in failures:
            print(f"CANARY FAIL: {f}")
        print(f"canary: {len(failures)} guard failure(s); "
              f"the wrapped command did not run")
        return 1

    cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not cmd:
        return 0
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
