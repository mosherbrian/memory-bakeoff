#!/usr/bin/env python3
"""Render the Gen43 prototype report and its deterministic digest."""
from __future__ import annotations

import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.pi_state_control import contract as C  # noqa: E402

BASE = ROOT / "results" / "pi_state_control_gen43"
VOLATILE = {"wall_seconds", "generated_at", "timestamp", "install_path", "host"}


def strip(obj):
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in sorted(obj.items()) if k not in VOLATILE}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def main() -> int:
    identity = json.loads((BASE / "identity.json").read_text())
    metrics = json.loads((BASE / "trace_metrics.json").read_text())
    recovery = json.loads((BASE / "restart_recovery.json").read_text())
    corruption = json.loads((BASE / "corruption_tests.json").read_text())
    fixture = json.loads((BASE / "synthetic_trace.json").read_text())
    contract = json.loads((BASE / "contract.json").read_text())

    series = metrics["metrics"]
    first, last = series[0], series[-1]
    peak_ctx = max(m["composed_context_bytes"] for m in series)
    peak_state = max(m["state_bytes"] for m in series)
    hook = identity["extension_load_test"]["context_hook"]
    restart = recovery["restarts"][0]

    rows = "\n".join(
        f"| {m['step']} | {m['history_events']} | {m['history_bytes']:,} | {m['state_bytes']:,} | "
        f"{m['composed_context_bytes']:,} | {m['tool_output_bytes_history_only']:,} |"
        for m in (series[0], series[9], series[19], series[29], series[39], series[-1])
    )
    corr = "\n".join(
        f"| {name.replace('_', ' ')} | {'closed' if row['failed_closed'] else 'OPEN'} | {row['detail'][:88]} |"
        for name, row in sorted(corruption.items()) if name != "all_failed_closed"
    )

    digest_payload = {"identity": identity, "metrics": metrics, "recovery": recovery,
                      "corruption": corruption, "fixture": fixture, "contract": contract}
    scientific_digest = hashlib.sha256(
        C.canonical(strip(digest_payload)).encode()).hexdigest()

    doc = f"""# The first Pi state/control prototype

**Evidence class:** `architecture_prototype_no_score`. This generation establishes that the
separations in `ARCHITECTURE.md` are implementable on the installed Pi and behave as designed on
a fixed synthetic trace. It makes **no** claim about coding-task success, reasoning quality,
token savings under a live model, or tool-churn reduction. Those remain unmeasured.

No model ran. No network, no API, no GPU, no reader, no benchmark corpus.

## Pi identity, and where it actually lives

{identity['note']}

| field | value |
| --- | --- |
| package | `{identity['package']['name']}` |
| version | {identity['package']['version']} (CLI reports {identity['cli_reported_version']}) |
| runtime | {identity['package']['runtime']} |
| extension events exposed | {len(identity['extension_api_events'])} |

The hooks that matter for this architecture, read from the installed package's own type
definitions rather than from documentation or recollection:

| responsibility | hook |
| --- | --- |
| session start / resume | `{identity['hooks_of_interest']['session_start_resume']}` |
| user prompt submission | `{identity['hooks_of_interest']['user_prompt_submission']}` |
| **context transformation** | `{identity['hooks_of_interest']['context_transformation']}` |
| provider payload | `{identity['hooks_of_interest']['provider_payload']}` |
| system prompt | `{identity['hooks_of_interest']['system_prompt']}` |
| compaction | `{identity['hooks_of_interest']['compaction']}` |
| tool pre / post | `{identity['hooks_of_interest']['tool_pre_post']}` |
| stop / completion | `{identity['hooks_of_interest']['stop_completion']}` |
| persistence | `{identity['hooks_of_interest']['persistence']}` |
| token accounting | `{identity['hooks_of_interest']['token_accounting']}` |

What is **not** available, stated so a later generation does not assume it:

{chr(10).join(f"- {line}" for line in identity['unsupported_or_absent'])}

## H1: a Pi-native extension, with no core patch

The prototype extension was loaded into the installed Pi by Pi's own loader and its handlers were
driven with synthetic events. Nothing was forked, patched or copied out of the package.

| observation | value |
| --- | --- |
| extension loaded | {identity['extension_load_test']['extension_loaded']} |
| load errors | {len(identity['extension_load_test']['load_errors'])} |
| handlers registered | {', '.join(identity['extension_load_test']['registered_handlers'])} |
| Pi core patched | {identity['extension_load_test']['core_patched']} |

The decisive one is the `context` hook. Handed a synthetic transcript of
{hook['incoming_messages']} messages and {hook['incoming_bytes']:,} bytes, the extension returned
{hook['replacement_messages']} composed message of {hook['replacement_bytes']:,} bytes. The
transcript was not replayed. That is the mechanism the whole architecture depends on, and it is a
public extension hook rather than something that needs Pi to change.

Compaction was also cancellable from the extension, which matters: history here is externalized,
not destructively compacted. Deleting the past is not how the context stays small.

## The frozen contract

`{contract['contract_version']}`, state schema {contract['state_schema_version']}, contract sha256
`{contract['contract_sha256']}`, frozen before the trace was measured.

Transitions: {json.dumps(contract['transitions'])}. Entering `done` requires a
`{contract['gated_phases']['done']}`. State is bounded at {contract['max_state_bytes']:,} bytes with
per-field list bounds; overflow is archived to history with a reference rather than dropped.

Patches are transactions: `{{base_revision, ops}}` with `set` / `append` / `remove` on schema
fields. A phase change is deliberately **not** a patch — control owns that.

## The synthetic trace

{fixture['step_count']} steps, digest `{fixture['fixture_digest'][:16]}`, invented and unrelated to
every corpus in this repository. It contains repository inspection, a plan revision, two
implementation attempts, a failed validation followed by a fix, a large irrelevant tool output, an
early decision that becomes relevant again after it has been archived out of active state, a check
result superseded by a newer one, an intentionally illegal transition, a stale patch, a malformed
patch, and a restart boundary.

Executing it produced {metrics['history_events']} history events and ended in phase
**{metrics['final_phase']}** — reached only after a passing receipt existed.

## H2: bounded context, lossless history

| step | history events | history bytes | state bytes | composed context bytes | tool output kept only in history |
| --- | --- | --- | --- | --- | --- |
{rows}

History grew from {first['history_bytes']:,} to {last['history_bytes']:,} bytes, a factor of
{last['history_bytes'] / first['history_bytes']:.0f}. The composed live context went from
{first['composed_context_bytes']:,} to {last['composed_context_bytes']:,} bytes and peaked at
{peak_ctx:,}. Active state peaked at {peak_state:,} bytes against a
{contract['max_state_bytes']:,}-byte guard. At the end the live context is
{last['composed_context_bytes'] / last['history_bytes']:.1%} of the history it can still reach.

The peak is worth naming rather than smoothing: context tracks the size of the *latest
observation*, so a single large kept tool result moves it. What it does not track is the length of
the run. That is the property being tested.

{last['tool_output_bytes_history_only']:,} bytes of tool output never entered the live context at
all and remain retrievable by event id.

Patches accepted {last['patches_accepted']}, rejected {last['patches_rejected']}. Transitions
accepted {last['transitions_accepted']}, rejected {last['transitions_rejected']}. Rejections are
events in the log, not silent no-ops.

## H3: restart recovers from persisted evidence only

At the declared boundary the prototype object was destroyed and rebuilt from `state.json` and
`history.ndjson` alone.

| quantity | before | after |
| --- | --- | --- |
| phase | {restart['before']['phase']} | {restart['after']['phase']} |
| state digest | `{restart['before']['state_digest'][:16]}` | `{restart['after']['state_digest'][:16]}` |
| history head | `{restart['before']['history_head'][:16]}` | `{restart['after']['history_head'][:16]}` |
| history events | {restart['before']['history_events']} | {restart['after']['history_events']} |
| identical | | **{restart['identical']}** |

And the part that makes it more than a serialization test: an early decision that had been
archived out of active state by the list bound was still recoverable from history
({recovery['archived_decision_recoverable']}), was recalled on demand, and did **not** silently
reinstall itself into active state afterwards
({recovery['archived_decision_still_in_active_state']} for "still in active state"). Retrievable
is not the same as always present.

## H4 and H5: fail-closed behaviour

| case | outcome | detail |
| --- | --- | --- |
{corr}

All {sum(1 for k in corruption if k != 'all_failed_closed')} cases failed closed. Nothing was
silently repaired. The artifact case is H5: after `done` was legitimately earned, the receipt's
file was edited, and both the artifact status and the completion gate immediately rejected it.
State said the checkpoint was valid; the artifact disagreed; the artifact won.

## What this does not establish

Everything about a real agent. No model produced any of these tokens; the trace is a fixture. The
context numbers are bytes of composed context under this prototype's composer, not tokens under a
pinned model, and there is no comparison against Pi's ordinary context assembly under load — that
needs a live session and is deliberately out of scope here.

H6 stands unmeasured by design: whether this design improves coding-task success, reduces tool
churn or saves tokens is a paired experiment, not a prototype.

Scientific digest `{scientific_digest}`, rebuilt with wall-clock, host and install paths excluded.
Contract `src/memory_bakeoff/pi_state_control/contract.py`, sha256 `{C.contract_sha256()}`.
"""
    out = ROOT / "research" / "PI_STATE_CONTROL_GEN43_PROTOTYPE.md"
    out.write_text(doc)
    (BASE / "scientific_digest.txt").write_text(scientific_digest + "\n")
    print("wrote", out.relative_to(ROOT), "digest", scientific_digest[:16])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
