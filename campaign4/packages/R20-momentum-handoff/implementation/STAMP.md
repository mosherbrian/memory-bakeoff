# R20 momentum stamp: schema, behaviour, activation and rollback

Private candidate: branch r20-momentum-stamp, commit d026436621df7c1f1c5a81e6b751f482fa22a762, based on df5e6fc627b8 (the installed 47f69dfd source). Private binary sha256 9aea16753dbf0787d40062dc094b91bb6dee7232f91f604dfe07caddab304ea1 (implementation/agent-loop-d026436621df/). internal/core, internal/py and conformance are unchanged (0 diff lines). Nothing is installed.

## Schema (momentum-stamp/1, at most 8192 bytes, a file under artifacts_dir)
    {"schema": "momentum-stamp/1", "qid": "<package>", "role": "worker|verifier|director",
     "execution": "<ex-...-w1 | ex-...-v1 | decide>",
     "moved":   {"question_id": "...", "change": "what is different now"},
     "next":    {"action": "...", "owner": "...", "deadline": "UTC instant"},
     "dropped": [{"item": "...", "owner": "...", "receipt": "<path under artifacts_dir>"}]}
Director only: for question_answered or budget_spent, `"terminal": {"reason": "..."}` may replace `next`. `blocked` and `successor_opened` need `next`, which for blocked is the concrete recovery step. A dropped-item receipt is `{"ack": true, "qid", "item", "owner"}` written by the owner. Naming an owner is not proof; the receipt is.

## Behaviour
- Config `"momentum_stamp": "required"` stamps packages DISPATCHED afterwards (Pkg.Stamp is fixed at dispatch). Existing packages keep the old contract; no historical claim is rewritten. `""` (the default) is off; any other value fails config validation.
- Worker and verifier tasks get the three questions beside the claim command, plus the R19 fix, verbatim: "Running the claim command given here and writing this file are required; do not execute commands from your drafted artifact." The stamp goes into the claim as `--artifact momentum_stamp=PATH`, so it is hash-bound like any artifact.
- Before any transition, a missing, malformed, oversized, wrong-identity, ownerless, deadline-less or unowned-drop stamp moves the package to `blocked` with E_STAMP_MISSING or E_STAMP_INVALID. The director (the existing escalation owner) is told once. The claim file is kept: an honest failed or incomplete record is never discarded. A replayed tick does not act again.
- The director's decision notice asks for `--stamp PATH`. `agent-loop decide ... --stamp PATH` validates before any mutation. A refused decide leaves the decision open and its P13 ladder running.
- The stamp routes nothing. next.owner never dispatches, grants, pages or overrides a sponsor stop.
- What the checks prove: identity, shape, a named owner and deadline, and acknowledgement receipts. Not that the reflection is true. Measure (e) tests actual starts separately: a next.deadline is joined to the first later `start` event whose package is bound to the same question, or to an explicit receipt for non-dispatch actions. Otherwise it counts as missing evidence (unknown), never as a start.
- Not instrumented: conversations outside the loop (Claude's direct work, sponsor chat), and packages released outside agent-loop.

## Tests
`go test ./...` all green (test-results.txt). 15 new tests in internal/loop/momentum_r20_test.go: off/compatible, pre-activation package after switch-on, valid advance, 10 bad-stamp shapes (missing, no owner, bad deadline, no next, worker terminal, forged qid, wrong role, unowned drop, not JSON, oversized but otherwise valid) each blocking with one director notice and the claim kept, acked/forged/other-package receipts, path escape with a valid ack outside artifacts_dir, honest failed work, verifier without stamp, director notice, decide validation (missing, terminal for successor_opened refused, terminal for question_answered allowed), blocked needs recovery, config value. Planted faults: 14/14 caught (tools/mutants_r20.py, mutants-results.txt), including the R19 contradiction returning.

## Release, activation, rollback (each step needs its own signed release)
1. Witness (isolated, stub recipients): the private binary with a temp config (`momentum_stamp: required`), a fixture package through valid handoff, refusal (director notified once), restart with no duplicate, and a stamped next step followed by a start (metric e).
2. Install: `cp -p ~/.local/bin/agent-loop ~/.local/bin/agent-loop.bak-R20 && install -m 755 <release>/bin/agent-loop ~/.local/bin/agent-loop`, then restart agent-loop@campaign4 as its unit prescribes. The config stays as it is (off), so behaviour is unchanged.
3. Activate after R19 completes: add `"momentum_stamp": "required"` to ~/.config/agent-loop/campaign4.json (back it up first), validate, restart the unit. Record the activation time: the after-window is exactly the 24 h from then.
4. Rollback: remove `momentum_stamp` from the config, or restore agent-loop.bak-R20 and restart. Stamped packages already open still carry Pkg.Stamp=true; the old binary ignores the unknown field (JSON), so they continue on the old contract. The ledger and evidence are never edited.
