# P9-go-supervised-preview — verification completion

- **Reviewer:** corvid-dsh
- **Action:** `P9-verify-1` (continuation; original `06:42:00Z` deadline, no reset,
  no new allocation)
- **Brief:** `verification-continuation.json` (`required-remaining`), bound archive
  `e559ad17…`, binary `221bb3aa…`, source `c124d82`, manifest `d9c55765…`.
- **Initial retained:** `verification-initial.md` sha256 `6e16f658…` (initial
  bounded PASS, unchanged bytes; also still at `verification.md`).

## Verdict

**PASS (bounded) — all six admitted checks now independently exercised.** The
mandatory-exercise gaps named by the continuation are closed: check 5 rehearsal was
executed on the exact claimed archive with injected stubs only, check 3 overhead
was mutated independently, and the WAL/concurrency focus was probed. Residuals are
named; no adoption/publication.

## Check 5 — exact-archive rehearsal (independently executed)

`evidence/rehearse.sh agent-loop-c124d82cd26a.tar.gz` → **rc0**, fresh private
`/tmp/p9-rehearsal-*`, stubs only, no real seats/services:
- archive sha `e559ad17…`; `sha256sum -c MANIFEST.sha256` → **14/14 match**; debris
  scan → **none**.
- rebuild from shipped source: deps/settings identical (differs only by vcs stamp);
  `go test` ok incl. `internal/expose`; shipped binary conformance **125/125, 1751
  steps**.
- unfilled `project.template.json` → **refused** ("missing seats.<duty seat name…");
  filled config passes `check`.
- `dispatch A` + `dispatch B --after A` (held); claim/run → `A` verifier PASS;
  `expose` read-only (ledger file hash `24356f42…` unchanged; listing
  `c4eaeabb…` unchanged across **4 renders incl. missing and malformed inventory**);
  pending `A/decision` with owner/next/blocks/source; `decide` → `pending []`,
  `resolved ['A/decision']`, `B` released; label `SUPERVISED PREVIEW / NOT
  QUALIFIED FOR UNATTENDED USE`.
- `stop` → `run` while stopped **rc64**; `start`; restore rehearsal swaps the
  previous binary/ledger copy; **main HEAD unchanged: yes; installed
  `~/.local/bin/agent-loop` unchanged: yes**; only stub systemd calls.
- Full log: `/tmp/p9rehearse.log`.

## Check 3 — unshared overhead mutations (independent)

On a private copy of the real P8 live-1 ledger (shipped binary):
- baseline → `worker_dispatches 1, verifier_dispatches 1, repairs 0, timeouts 0,
  director_decisions 0, currently_blocked 0`; steps `worker 4 s`, `verify 13 s`,
  `decision seconds:null` (never its grant). Matches recorded events.
- **missing/empty history** → `overhead: null`, `freshness: UNKNOWN: ledger
  unreadable`, `problems: [UNKNOWN … no such table]` — no invented zeros.
- **+`interrupt` reason `deadline-expired`** → `timeouts 1` only; **+`publish`
  without a `verify` flight** → `verifier_dispatches` stays 1 (not counted).
- **duplicate receipt row** (same `event_id`) → rejected by the ledger's
  **UNIQUE(event_id)** constraint, so duplicate receipt rows cannot double-count.
  No name-suffix heuristic; durations from recorded event times.

## WAL / concurrency focus (independent)

- **WAL-only committed data retained:** a `loop-pkg` row committed without
  checkpoint (WAL only), copied `db`+`-wal` as the view does → the view shows it.
  `Options.ledger` copies both `db` and `-wal` to a private temp snapshot and opens
  the snapshot read-only (`expose.go:277-292`); a copy that fails to open/read →
  `UNKNOWN`.
- **Changed input** (source bytes changed) → `CONFLICT: … no longer matches its
  pinned hash`; stale data never presented as current.
- **Residual (cannot be certified):** a copy taken across a concurrent
  checkpoint/write can be torn; a torn copy that still opens cleanly could present a
  slightly older snapshot, and "successfully opened" is not proof of concurrent
  accuracy. Not tested against a live concurrent writer within this bound —
  recorded, not inferred harmless. `as-of`/freshness stay `UNKNOWN` when no pass is
  recorded.

## Remaining residuals (adopted)

Author-reported parity `316/321+5` and `mutate_go.py 81/81` were not rerun here;
the reproduced subset above is exact. P8 NOT READY and the three liveness blockers
remain labelled in `known_limits`. Private release only.

## Effect

**PASS (bounded), completion**: checks 1–6 independently exercised on the bound
archive/source/binary, with the concurrency residual named. Initial verdict bytes
preserved (`verification-initial.md` `6e16f658…`). Returned to Tern for acceptance.
