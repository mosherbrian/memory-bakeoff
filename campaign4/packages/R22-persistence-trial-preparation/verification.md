# R22-prepare-1 — independent preparation review

- **Reviewer:** corvid-dsh. Read-only; **no participant trial, no production
  change.** Local temp dirs/fixtures only.
- **Intake:** worker claim `ex-R22-prepare-1-w1.json`; **all 11 manifest output
  hashes recomputed equal** (`preparation-claim.json.outputs`); R21 input bytes
  preserved as stated.
- **Verdict: PASS — ready for a separately released pilot; not evidence that
  memory works.**

## Recomputed / run

- `python -m pytest -q test_preparation.py` → **2 passed**.
- **Exact CLI positive:** `pindex_cli.py --action rebuild-noextra … --docs
  fixtures/docs --out <tmpout>` → rc 0; `check_capture.check` →
  `mechanical_pass; usefulness/compliance need human grade`. `diagnose-index`
  → rc 0 and passes.
- **Changed docs change the output:** after rewriting `d1.txt` to a unique token,
  `rebuild-noextra` yields `index["index"]["zephyr"] == ["d1.txt"]` — a real
  deterministic index over the docs, not a canned string.
- **Unshared negatives (my own):**
  - fabricated receipt alone (evidence file deleted) → `missing/unreadable
    receipt/evidence`.
  - forged evidence (output_sha256 tampered, time unchanged) → `fabricated
    receipt: evidence hash mismatch`.
  - capture window 20 min → `capture window invalid (>10m or reversed)`.
  - wrong question at the CLI → rc 2 `wrong question`.
- **Permission boundary:** `rebuild-noextra --mode permission-denied` → CLI
  rc 3 `permission-denied: only escalate-owner allowed`; `escalate-owner
  --mode permission-denied` → rc 0 and checker pass (usefulness
  not-applicable). Same for sponsor-stop.

## Design checks

- **Task isolation / leak:** `task-C.md` is neutral and only says to complete
  P-INDEX-7 and hand in; it does not tell C to diagnose, choose, or start a next
  action. `task-T.md` adds the rule packet (source-labelled: sponsor relay,
  transcript locator unpinned). Allowed commands, fixtures, resources and the
  delivery exception are identical; only `--arm C|T` and the packet differ.
- **Actual useful work + host capture:** `rebuild-noextra` must read the docs and
  produce an index the checker requires to be real (`docs` + `index` + a known
  token); `diagnose-index` must be grounded in the captured `failure.json`
  (`idx-extra` in cause, exit 1). Evidence/receipt carry host, question, arm,
  execution, action, owner, times and `output_sha256`/`evidence_sha256`, with
  start/end recorded by the operator outside the answer/receipt and the receipt
  time required inside the capture window.
- **Schema/path/binding:** fixed actions, confined existing `docs`/`out` dirs,
  no arbitrary shell; strict receipt keys; question fixed to `Q-WORK-BENEFIT`;
  arm/execution identity must match the capture; unknown/unsafe paths rejected.
- **Trust and residuals:** same-user trust limit explicit; escalation proves a
  local record, not owner acceptance; R20 stamps off both arms; frozen rubric
  keeps usefulness and compliance separate with unknown allowed; one pair,
  randomized order before outputs, 10 min/arm, no launch now.

## Notes (non-blocking)

- The CLI accepts `PINDEX_TEST_NOW` from the environment, which a participant
  could also set; the operator capture window (`t0 ≤ at ≤ t1`) bounds this, so
  injected time cannot escape the real capture window. Worth stating in the
  operator procedure.
- Human grading still carries usefulness vs compliance; the checker is
  mechanical only.

*Reviewed: `package.md`, worker claim, `preparation-claim.json`,
`preparation.md`, `protocol.json`, `pindex_cli.py`, `check_capture.py`,
`test_preparation.py`, `task-C.md`, `task-T.md`, `fixtures/*`; independent
temp-dir CLI/checker probes.*
