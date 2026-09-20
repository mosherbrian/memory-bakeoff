# Assay — outcome-protocol §5.2 leak-gate prototype (validated)

**Author:** Assay (`worker-glm-dsh2`), R&D pulse · **Date:** 2026-09-13 · **Cost:** $0, offline, synthetic only
**Serves:** `team/SPEC-OUTCOME-PROTOCOL.md` §5 (row 25) — the de-identified
correction-event interface to Kiln's transcript-mining pipeline.
**HARD RULE honored:** synthetic events and synthetic "raw" reference text only;
no transcript corpus or raw session content was read or emitted.

## What this is

The row-25 spec says a de-identified correction-event bundle must pass a
**fail-closed leak gate** (§5.2) before it can cross into the outcome-measurement
lane. This is a small prototype of that gate plus its power check: *does it pass
a clean bundle and reject each leak class it exists for?* It is a prototype, not
yet wired into `scripts/experiment_20260912_transcript_mining/`.

## Gate rules implemented (all structural, no model in the loop)

| # | Rule | Leak class it blocks |
|---|---|---|
| 1 | exactly the §5.1 key set; unexpected keys are findings | an extra `raw_text`/`excerpt` field being added |
| 2 | no `\n`/`\r`, no value longer than 120 chars | free-text/excerpt smuggled into a nominally-structural field |
| 3 | no raw-transcript sentinel substrings (`"type":"user"`, `"role":"user"`, `tool_result`, `<task-notification>`, `human:`/`Assistant:`) | structure bled through from the JSONL pipeline |
| 4 | `event_id` and `normalized_prefix_hash` must be 64-hex sha256 | a raw prefix/plain id substituted for the salted hash |
| 5 | `class` / `subtype` / `env_fact_kind` restricted to the frozen vocabularies | raw sentence used as a class label |
| 6 | bounded n-gram check against a **local-only** raw reference (24/32/48-char n-grams) | an excerpt copied into any exported value |
| 7 | class-count reconciliation against the aggregate card | a doctored/partial bundle whose counts don't match the published card |

Rule 6 and the reconciliation in rule 7 need inputs kept in the local export
step: the raw reference text never leaves the machine, and only the boolean
finding does; the aggregate card is the same one in
`team/TRANSCRIPT-MINING-PILOT.md`'s scale run.

## Power check — 9/9 controls correct

`outcome_leak_gate_power_check.py` builds a 3-event clean bundle and one
leak/edge per rule:

| control | result |
|---|---|
| clean bundle | **no findings** (pass) |
| extra key `raw_text` | flagged `unexpected key(s)` |
| raw n-gram copied into `project_pseudonym` | flagged `raw n-gram(>=24) leak` |
| newline in `source_session_pseudonym` | flagged `newline` |
| 200-char `detector_version` | flagged `field too long` |
| `{"type":"user",...}` in `extraction_run` | flagged `raw-transcript sentinel` |
| `event_id="not-a-hash"` | flagged `event_id is not a salted sha256 hex` |
| `class="not_a_class"` | flagged `bad class` |
| class counts vs aggregate card mismatch | flagged `counts do not reconcile` |

A clean bundle must yield an empty finding list — the negative control confirms
the gate is not one that always fails. Gate returns findings and the CLI can map
non-empty → nonzero exit; the prototype's driver is the power check itself.

## How it consumes Kiln's events later (aggregates only)

At scale-up export time on the local machine: build the event list per §5.1
(hashes, enums, buckets — no text), pass it with the aggregate card and the
local raw reference to `gate(...)`; emit only `findings` (booleans/keys) plus the
bundle if clean. Nothing in the exported bundle or the finding list contains raw
content; the raw reference is used and discarded locally.

## Limits

- **Prototype**, not integrated: it is not imported by the mining pipeline and
  has no CLI/exit-code wrapper yet.
- The sentinel list is illustrative; it should be pinned from the actual
  pipeline's known JSONL structure before a real export.
- Rule 6 is only as strong as the raw reference handed to it; passing no
  reference disables that rule (documented, not silent).
- Reconciliation trusts the aggregate card; a wrong card yields a wrong pass/fail.
- Synthetic only, so it bounds the gate's predicate sensitivity, not Kiln's
  corpus or detector precision.

## Receipts

- Prototype + power check: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-outcome-leakgate/outcome_leak_gate_power_check.py`
  sha256 `202479298f835dfd049f70ab4a10a3381e6f0a81057302e591e9fed5738354e7`
- Result: `.../result.json` sha256 `195e4b16f04e66c6bcc9d55046430cb548e6540fbd991e21f089c6556773da32`
- Re-run: `python3 outcome_leak_gate_power_check.py` (rc 0 = all controls correct)
- Spec: `team/SPEC-OUTCOME-PROTOCOL.md` §5.1–§5.2

— **Assay** (`worker-glm-dsh2`). No tree modified; no raw transcript content.
