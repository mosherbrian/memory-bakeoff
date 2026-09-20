# Cross-tree census: `extensions/` — the trigger and the A2 vault fix are canonical-only

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, read-only (find + sha256)
**Extends:** `CORVID-CROSSTREE-FILE-CENSUS.md` (which covered `src/` + `tests/`).
Ran the same census over `extensions/`, which neither that note nor the
`REPO-CANONICAL.txt` declaration covers.

## Result

Canonical `implementer/repo/extensions`: **42 files**; both forks
`repo-glm-dsh2`/`repo-glm-dsh3`: **37** (identical shortfall).

**Missing in BOTH forks:**

| path | what it is |
|---|---|
| `extensions/pi-change-trigger/index.ts` | **the trigger under test** in the invocation benchmark (the extension my guard 18 and Cairn's matrix read) |
| `extensions/pi-change-trigger/package.json` | its manifest |
| `extensions/pi-change-trigger/README.md` | its docs |
| `extensions/pi-change-trigger/test/trigger.test.ts` | its test |
| `extensions/pi-perseus-recall/test/watchdog.test.ts` | A1 watchdog test |

**Differing in BOTH forks (present but stale):**

| path | canonical | forks | reading |
|---|---|---|---|
| `extensions/pi-perseus-recall/index.ts` | `24296ad6d4f9…` | `1fd3a16adba1…` | canonical carries the A2 fix; forks are pre-A2 |
| `extensions/pi-perseus-recall/vault.ts` | `50aefb3f2a51…` | `97deaffac87f…` | canonical `50aefb3f` is the A2 v3 (framing fix); forks pre-fix |

## Why it matters

- The **invocation benchmark's trigger lives only in canonical**. A lane that ran
  the trigger from a fork would find the extension absent; the smoke succeeded
  because Cairn ran from `~/acp-pi` and my guard points its `--extension` default
  at canonical — both by necessity, not by a declared rule.
- The **A2 vault framing fix is canonical-only** in the repo copies; a fork-run
  perseus arm would use the pre-A2 client (the chunk-boundary reply bug A2 v3
  fixed). The live trial dir (`~/acp-pi`, `fbd3149`) was updated separately, so
  this concerns the **repo forks**, not necessarily the pilot.
- This is the `extensions/` face of the same fork-lag as the P2 chain and the
  instrument fixes — and it is currently invisible to `check_cross_copy_drift`
  because `extensions/` is not in the declaration.

## Recommendation (owner: GiLMore/Kiln)

1. **Sync** `extensions/` to the forks (or the relevant subset) so the trigger and
   A2 fix are available where lanes run.
2. **Declare** the extension paths in `REPO-CANONICAL.txt` — `shared:` for
   `pi-perseus-recall/index.ts`/`vault.ts` (drift visible until synced) and either
   `shared:` or guard 15's new `canonical-only:` for the `pi-change-trigger` files
   if the trigger is intentionally canonical-only. Either way the gap becomes a
   standing, owned finding instead of silent.

## Limits

Hash/presence census only; does not run either extension, and does not judge
whether the forks are *meant* to carry the trigger (that is the declaration
question). `~/acp-pi` (the live trial) is a separate tree and was not audited here.

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
