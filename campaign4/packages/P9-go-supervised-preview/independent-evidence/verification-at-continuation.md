# P9-go-supervised-preview — verification (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P9-verify-1` (existing ≤20 m grant)
- **Brief:** `dispatch-receipt.json` (`P9-initial-1`, release `7736d38`);
  contract `63053fe3…`, admission `eb5629d3…`.
- **Bound bytes:** branch `p9-preview` commit
  `c124d82cd26ae4966f3e6a935cb24d971347ec8c`, private release archive
  `…/agent-loop-c124d82cd26a.tar.gz` sha256 `e559ad17…`, binary `bin/agent-loop`
  sha256 `221bb3aa…`.
- **Scope:** read-only verification; no source/live/publication.

## Verdict

**PASS (bounded).** The six admitted checks hold on the bound source/binary/
archive as far as reproduced here: frozen control verified, suite/conformance
green on the shipped binary, the read-only Expose view renders required facts and
`NOT READY`/`UNKNOWN` without touching the ledger, pending resolution is
verified-or-unknown, and the archive/manifest/BUILD are clean and host-portable.
P8 blockers remain declared known. No adoption/publication.

## Checks

- **Pins:** worktree `p9-preview` HEAD `c124d82…` clean; `git diff 71318c4 HEAD
  -- internal/core internal/host internal/py internal/loop` **empty**; `cmd/agent-loop`
  changes are additions only (`loop.go +34/-0`, `main.go +3/-0`). Archive sha
  `e559ad17…`, binary `221bb3aa…`, `MANIFEST.sha256 d9c55765…` recomputed equal.
- **1 — status/pending:** real view over the preserved P8 live-1 ledger renders
  `pending` with owner/question/dependents/next/source (CUTOVER owner `tern`;
  `P8-positive-1/decision` owner `UNKNOWN` + no-command note). Independent
  mutation: adding a valid `resolved_by` to CUTOVER → **resolved `[CUTOVER]`,
  pending drops it**; pointing `resolved_by` at a missing file keeps it pending
  with `UNKNOWN: … claimed resolution not verified`. No conversational memory used.
- **2 — UNKNOWN/conflict/read-only:** label `SUPERVISED PREVIEW / NOT QUALIFIED
  FOR UNATTENDED USE`; `freshness: UNKNOWN`; a **malformed inventory** yields
  `problems: UNKNOWN … unreadable` with the real ledger pending still shown (never
  healthy, no crash). Read-only reproduced: ledger files + directory listing
  sha256 **unchanged** before/after (`afd16421…`, `26b74633…`). P8 `NOT_READY`
  appears in `known_limits` verbatim and is not rendered green.
- **3 — overhead:** counts derive from real ledger events (worker/verifier
  dispatches 1/1, repairs 0, decisions 0, `currently_blocked` shown as a state
  count with "block events not recorded as ledger events"); the decision step is
  `seconds: null` (never its grant); step times are recorded receipt times;
  `costs` outside the binary. (Full `TestOverheadMatchesTheSequence` author test
  is reported; I did not rerun every author test.)
- **4 — frozen control + regressions:** control diff empty (above);
  `go test ./...` on the worktree → **ok** all packages incl. `internal/expose`;
  shipped binary `conformance conformance/cases` → **125/125, 1751 steps**.
  Host parity `316/321 + 5 adjudicated` and `mutate_go.py 81/81` are author/reported
  (not rerun here).
- **5 — archive rehearsal:** extracted the tarball to a fresh `/tmp` dir; manifest
  **14/14 OK, 0 failures**; `BUILD.json` contains **no host paths**; the shipped
  binary runs. (Full install/stop/restore rehearsal is `evidence/rehearse.sh` /
  `rehearsal-final.txt`, author-reported.)
- **6 — manifest/docs:** release manifest and `source_manifest_sha256` (197
  entries) match bytes; no cache/credential/debris in the archive listing; README
  and `docs/SUPERVISED-PREVIEW.md` carry the preview label and limitations;
  `known_limits` names the three P8 liveness blockers; `research` explicitly "not
  advanced by this machinery". Nothing published/merged/installed.

## Residuals (adopted, honest)

- All P8 liveness blockers stand (damaged `<db>.liveness.json` exits 1 with no
  notification; future pass → false REST; no incarnation binding). The view
  labels them; the checker defect is not fixed (frozen scope).
- A ledger copy taken during a live writer can be torn; an opens-clean torn copy
  could show slightly older state (not tested against a concurrent writer).
- Overhead counts only recorded ledger events; blocks/recoveries/escalations are
  state/notes, not events; durations are receipt times, not remote occurrence times.
- Inventory status strings are copied verbatim (hash-checked, not meaning-checked);
  packages without recorded principals show `UNKNOWN` owner.
- Author-reported results (parity, mutation, full rehearsal) were not all rerun
  here; the reproduced subset above is exact.

## Effect

One bounded verdict: **PASS (bounded)** — six checks verified on the bound
source/binary/archive as reproduced; P8 blockers and residuals named; private
release only, no adoption. Returned to Tern.

---

## Steering addendum (`director-intake.json` focus; bound 197 files, unchanged)

Bound re-checked: source `c124d82`, archive `e559ad17…`, binary `221bb3aa…`,
manifest `d9c55765…` (unchanged). All six checks above stand. Focus reproduced on
the shipped binary with private fixtures.

### WAL-only committed data (retained) — VERIFIED

`Options.ledger` copies the ledger **and its `-wal`** to a private temp snapshot
(`internal/expose/expose.go:277-292`) and opens the snapshot read-only. Reproduced:
a WAL-mode ledger with a `loop-pkg:WALPKG` row and an `events` row committed
**without checkpoint**, copied `db`+`-wal` as the view does → the view shows
`WALPKG` (step `worker`, owner `UNKNOWN`, next action), so committed-but-not-
checkpointed data is not lost. A copy that fails to open/read yields `UNKNOWN`.

### Changed inputs → truthful UNKNOWN/CONFLICT — VERIFIED

Corrupting one inventory item's pinned hash (source bytes changed) →
`problems: ["P8: CONFLICT: packages/P8-go-unattended-qualification/
terminal-disposition.json no longer matches its pinned hash", …]`. The item is not
presented as current/authoritative on a stale hash. Missing `resolved_by` source →
pending remains with `UNKNOWN … claimed resolution not verified` (previous
addendum). Hash validates bytes, not semantic status.

### Private DB+WAL scope + concurrency residual — VERIFIED / RESIDUAL

The view never opens the live ledger (only a private snapshot), and the real-view
run left ledger files and directory listing byte-identical (previous addendum).
Residual (concrete): a copy taken across a concurrent checkpoint/write can be torn;
a torn copy fails to open/read → `UNKNOWN`, but a copy that still opens cleanly
could show a slightly older state. Not tested against a live concurrent writer —
recorded, not inferred harmless.

### Remaining focus

Missing history → `UNKNOWN` (freshness line) and event counts/durations are from
recorded receipt times (no name-suffix heuristic, no grant-as-duration) — verified
above; P8 NOT READY and the three liveness blockers remain visible in
`known_limits`. No new task; no live/implementation.
