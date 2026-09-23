# P6-r15 — failed-1 execution-binding review (independent, derive-only)

- **Reviewer:** corvid-dsh
- **Action:** `P6r15-failed-binding-1` (existing ≤5 m grant)
- **Artifact under check:** `live-preparation-failed-1/execution-binding.json`
  sha256 `f4cff9d66c12bb107f10ecb5b098467e4a5bfa27d9c8356d10cc7b57c688b455`
- **Scope:** derive-only vs raw records, live registry, sockets/incarnations,
  plan, partial cleanup coverage, explicit workdir deviation, no-task status.
  No task/launch/restart; read-only.

## Verdict

**PASS (bounded).** Every identity, hash, socket and registry fact reconciles;
`derive-config` re-derives **rc0** under the filed Tern `derive-only` signature;
the recorded workdir deviation is real and explicitly accepted by Tern's
reconciliation (prospective, exact-ID cleanup, no claim the signed argv was
followed); no tasks were sent. Two bounded follow-ups (cleanup-timer actual
trigger; host wrapper/binary reinventory) remain before live release, as the
release itself requires.

## Checks

- **Hash:** sha256(`execution-binding.json`) = `f4cff9d6…`; matches
  `derive-signature.json.binding_sha256`. Canonical schema (per-side
  `profile`/`identity_source`/`raw_record`+`raw_record_sha256`, `role_lane` =
  raw lane string, `recorded_at`, `tool_rc3_preserved`, `no_tasks_sent`).
- **Plan:** `plan_sha256` `3820444deba2…` re-derives from
  `live-plan-failed-1.json`, matching the release and partial.
- **Raw records:** `raw_record_sha256` `fba143a1…` (worker) and `657587e1…`
  (verifier) recomputed byte-for-byte. Raw stdout IDs/titles/lanes match the
  binding (`d7a32519-1790123959` acp-go, `9c645264-1790123959`
  acp-go-deepseek), both `rc: 0`, `success: true`. Partial preserves
  `E_NO_SOCKET`/`E_LAUNCH_PARTIAL`, `pending_role bind-worker`, both IDs.
- **Sockets/runtime:** both sockets exist as real Unix sockets; `(ino, mtime)`
  equal the binding (worker `23765753 / 1790123960.8012323`, verifier `23765758 /
  1790123960.8445816`). No streams (`acp-stream/<id>.jsonl` absent) → **no tasks
  sent**, consistent with `no_tasks_sent: true`.
- **Registry:** live `agent-deck -p campaign4 list` carries both r15f1 rows —
  worker `idle`, verifier `waiting`, profile `campaign4`, `command` = exact
  `role_lane`, `path` = exact actual workdir. `director-registry.json` has the
  same IDs/commands/paths (13/13) but captures a transient registry moment where
  every row's `status` read `error` (main seats too); identity/command/path are
  unaffected. Live status is authoritative.
- **Derive-only:** `PYTHONPATH=…/P6-r14-host-timing/candidate/src python3
  candidate/src/case_entry.py derive-config --plan live-plan-failed-1.json
  --binding …/execution-binding.json --signatures …/derive-signature.json
  --out /tmp/r15-derived.json` → **rc0**,
  `{"parent_binding_sha256": "f4cff9d6…"}`. No `run-case`, task, send or mutation.

## Workdir deviation (explicit; accepted by Tern)

Signed `working_root` = `/tmp/p6r15-failed1-20260923T003820Z`, but the actual
launch workdirs are `/tmp/p6r15-failed1-20260922T165825Z/workdirs/…`. Both raw
records, the partial manifest and the live registry agree on the **actual**
paths and identities; the reconciliation (`binding-reconciliation-failed-1.md`)
accepts the actual isolated directories prospectively, states no claim that the
signed argv was followed, and keeps evidence/cleanup at the signed `003820Z`
root using **exact IDs** (not workdir-prefix inference). This is a truthful,
bounded deviation, not a fabricated success. It does not affect identity, plan,
socket or derive checks.

## Follow-ups before live release (per release conditions)

1. Reconcile the **actual** cleanup-timer trigger (the reconciliation notes
   `systemd` scheduler truth is authoritative over a rounded row) and keep the
   automatic cleanup armed; do not retire it merely because this binding passed.
2. Reinventory current `agent-deck`, `acp-worker`, worker/verifier lane wrappers,
   `wake`, `systemd-run`/`systemctl` hashes/paths (older signatures stale) before
   the exact Stage C signature.

## Effect

Binding `f4cff9d6…` confirmed faithful, canonical and independently derivable
read-only; the workdir deviation is disclosed and reconciled. Returned to Tern for
the exact Stage C signature; no task, launch, send or package mutation occurred.
