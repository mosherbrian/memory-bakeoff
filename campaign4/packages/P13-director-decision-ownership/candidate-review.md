# P13-director-decision-ownership — candidate review (independent)

- **Action:** `P13-review-1`, start `05:07:16Z`, deadline `05:32:16Z`.
- **Claim:** `completion-claim.json` sha `9f490c0f…` — author status **INCOMPLETE**.
- **Pinned release:** source `bfb3851db565` (head `5b524d1`, test-only), binary
  `7040c0e32f3640daba2a1cb65083695721dec6f48d7e01c1c4b22d2562e9bc1f`; frozen
  `internal/core`, `internal/py`, `conformance/cases` (empty diff). 31/31 claim
  hashes match; release binary matches.
- **Verdict: INCOMPLETE governs — no acceptance, no live, no promotion.** The
  mechanism is built and witnessed against the real pinned scripts, but the
  bounded defects below are **requirement gaps**, not just missing live tests.

## What is verified (pinned release, not HEAD)

- `conformance` 125/125 rc 0 on the release binary; host parity 316/321 + 5.
- Witness-2 (real separate processes, real systemd calendar timers, `daemon-reload`
  + run restart, actual `notify-claude`/`escalations`/`escalation-watch` copied
  byte-for-byte, stub pager): configured ladder fired director/duty/Claude once,
  decision resolved + ledger acked; Q2 ack, forged `mallory` rc 1, renewal rc 1,
  ack expiry re-raised the **same** key (E-3 as E-2), no duplicate DECISION OVERDUE
  wakes across reload/restart; cleanup 0 units.
- Code: deadline + incident id persisted on entry; timer re-arms at the **original**
  instant; stale callback harmless; `decide` resolution skips later rungs and runs
  resolve commands; ack is explicitly not a decision; second ack refused.

## Bounded defects (requirement gaps)

1. **Missing required default ladder (req 2).** The built-in default is
   `[{0,Director},{300,Duty}]` (`decision.go:91-95`) — it **omits the +600 s Claude
   rung**. Req 2 requires the default ladder to notify Claude at +600 s via the
   escalation ledger + `notify-claude`. The Claude rung exists only as **proposed
   campaign config** (`campaign4_policy_proposed`), not applied or validated against
   the exact prospective config. **Smallest repair:** make the required three-rung
   ladder the default (or validate and pin the exact campaign config in the
   package), with a test that the default reaches Claude.
2. **Unbounded exec-rung retry (req 5).** A rung whose delivery fails is persisted
   `"failed …"`, which does **not** start with `"sent"`, so `decisionLadder`
   re-fires it on **every** check with no count. Req 5 requires bounded retry.
   **Smallest repair:** a per-rung attempt counter with a bounded cap then owned
   `unresolved`.
3. **Ambiguous crash repeat not bounded for exec rungs (req 5).** A crash between
   `"intended"` and delivery re-fires the rung, writing a **second ledger record
   with the same key** (witness-2 E-3/E-2). Req 5 allows **at most one labelled
   repeat** per ambiguous stage then owned unresolved; the seat-rung path has the
   one-repeat label, the exec path does not. **Smallest repair:** apply the
   labelled-repeat/unresolved ceiling to exec rungs too.
4. **Responder authentication is name-only (req 3).** `DecisionAck` accepts any
   `--by` that equals a literal `Cfg.DecisionResponders` string
   (`decision.go:342-348`); there is **no registry/incarnation/session binding**, and
   the CLI does not authenticate its caller. A **forged literal `claude`** is
   accepted; only a non-listed name (witness `mallory`) is refused. Req 3 requires
   forged/stale/wrong-principal responses refused. **Smallest repair:** bind the
   responder to a registry identity/incarnation (or document and get an explicit
   contract amendment that name-only is intended).
5. **Resolution-before-page conflicts with the pinned watcher (req 3).** The pinned
   `escalation-watch` lists a recurring record as recurred **even when it was
   acked**, so a record re-raised before the decision **still pages**. Req 3 says a
   timely actual decision resolves and **prevents a later page**. The author records
   this as a pinned-script limit; per the steering this is **not waived by source
   parity** — the requirement is unmet with the unchanged watcher. **Smallest
   repair:** either a resolve action that removes/acks the recurred record in the
   watcher's view, or an explicit contract amendment accepting the residual page.
6. **Mutation survivors / invalid mutants on required behaviours (req 5/tests).**
   `a reopen moves the decision deadline` **SURVIVED** and `a second acknowledgement
   is not refused cleanly` **SURVIVED**; `a rung fires again on every check` and
   `any principal may acknowledge` **BUILD FAILED** (invalid); `timeout-ack shares
   the callbacks' places` and `a migrated decision deadline starts from now` **NOT
   APPLIED** (text not unique). Invalid/unapplied mutants are **not caught**.
   **Smallest repair:** fix the mutants/tests so the reopen-deadline, second-ack and
   per-check-rung behaviours are guarded.

## Not defects (expected, live/prep held)

- Stopped-run path is **unit-tested only**; the live 20 min run and the promotion
  are **outside this round** and need Tern's signatures. Signal latency is
  `escalation-watch`'s (grace 45 min + 15 min interval + transport); no 10 min
  claim. Release/routing general registration is an explicit deferred scope limit.

## Effect

**INCOMPLETE preserved; no acceptance, no live, no promotion, no repair released.**
Bounded defect list (1–6) with the smallest repair scope above; any further work
returns Tern for disposition. No edits/resend/live effects by corvid.
