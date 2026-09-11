# EXPERIMENT-20260910B — case contract (reviewer-authored cases)

One directory per case under `scripts/experiment_20260910b/cases/<case-id>/`:

| File | Required content |
|---|---|
| `case.json` | `{"case": "<case-id>", "kind": "history" \| "control-current" \| "control-stale", "prompt": "<runner-visible task prompt>"}` |
| `seed_transcript.json` | `seed_store.ts` format: `{"conversations": [{"id": "seed-<case>-…", "session_id": "…", "created_at": ISO, "updated_at": ISO, "messages": [{"role": "user"\|"assistant", "content_text": "…", "timestamp": <epoch ms>}], "summaries": [{"depth", "text", "token_estimate", "created_at"}]}]}` — every seeded conversation gets a stable `seed-…` id |
| `repo/` | the initial worktree the model works in (plain files; the harness copies and inits git itself) |
| `verifier.py` | run with `cwd=<worktree>`; must print `VERIFIER OK` on a line by itself iff the required behavior is present |

## Case-mix rules (dispatch spec)

- 2 `history` cases: the seeded prior-session history contains a
  decision/constraint REQUIRED to satisfy a hidden requirement; the verifier
  fails without recovering it.
- 1 `control-current`: solvable entirely from information in `repo/` (tests
  unnecessary recall / noise).
- 1 `control-stale`: an older seeded decision that the CURRENT instruction
  (in `repo/` or the prompt) explicitly supersedes; taking the stale action
  must FAIL the verifier (stale-harm probe).

## Hard rules

- Hidden requirements live ONLY in the seeded history and the verifier —
  never in the runner-visible prompt (`case.json` "prompt" field).
- Verifiers assess required BEHAVIOR (outcomes in the worktree), not a
  particular implementation.
- The prompt is the complete user message for the task invocation; the
  harness delivers it identically to all three arms. Do not include recall
  instructions in it (that is arm C's treatment, delivered by the nudge
  extension through a genuine session resume).
- Cases are FROZEN by the implementer's commit before the first evaluation
  run; any post-freeze change = stop and report.
