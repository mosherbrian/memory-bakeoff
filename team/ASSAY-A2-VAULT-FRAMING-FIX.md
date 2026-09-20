# Assay — A2: vault RPC stdout framing fix (carry partial lines)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, local, no LLM
**Thread:** Assay — instrument power checks / second-driver.
**Subject:** `extensions/pi-perseus-recall/vault.ts` sha256 `905f604c…` (live,
A1 lineage), `VaultServer.rpc()` stdout framing.
**Status:** fix validated, **not applied** — this is a frozen live-arm extension
(a second amendment, A2); owner **Kiln/Cairn**, needs an outside restart.

## Defect (confirmed at code + behaviour level)

`rpc()`'s `onData` does `chunk.toString().split("\n")` **per data event with no
carry-over**. A JSON-RPC reply line larger than the pipe chunk size arrives in
several events; the first ends mid-line and the next starts mid-line, so
`JSON.parse` fails on both (the `catch` swallows it), the response is never
matched, and the 30 s timeout fires. Cairn's source finding (`vault.ts:65`/`:76`)
is exactly this; A1's watchdog then respawns the serve on the timeout — it
mitigates the symptom rather than removing the trigger.

## Fix (3 lines)

Keep the incomplete tail across events:

```ts
let buf = "";
const onData = (chunk: Buffer) => {
  buf += chunk.toString();
  const lines = buf.split("\n");
  buf = lines.pop() ?? "";   // carry the partial line
  for (const l of lines) { /* unchanged parse/resolve */ }
};
```

`a2-buffer.diff` sha256 `9e215b68…`; guarded `vault.fixed.ts` sha256
`50aefb3f…` (v3); `git apply --check` clean on canonical `implementer/repo`.
v1 (`08df040d…`) and v2 (`a7a91a60…`) are kept as `vault.fixed_v1.ts` /
`vault.fixed_v2.ts` for the contrast; see Rev 2–3.

## Power check (drives the REAL `VaultServer.rpc`)

`a2_buffer_power_check.ts` sha256 `eb90e1ff…`; sealed result
`sealed-a2-buffer-20260913/result.json` sha256 `8486a4d0…`. A fake stdio proc
(`EventEmitter` stdout, no serve) drives the real `rpc()` for the live file,
v1, v2, and v3, with the 30 s timer clamped so the timeout path is observable.
The v2 table below is **8/8**; Rev 3 adds the two teardown rows (total **10/10**):

| case | live `vault.ts` | v1 | v2 |
|---|---|---|---|
| reply split mid-line (>64 KiB) | **rejected `vault rpc timeout`** | resolved | resolved |
| reply in one chunk (control) | resolved | — | resolved |
| foreign-id line in the same chunk | — | — | ignored, ours resolves |
| split exactly at the newline boundary | — | — | resolves on the first chunk |
| **UTF-8 char split mid-byte** | — | **corrupted (30001 chars)** | **round-trips (30000)** |
| **final line, no trailing newline** | timeout | timeout | **resolves on stdout end** |
| partial tail, newline later | — | stays pending, then resolves | stays pending, then resolves |

This is the code-path reproduction of the live timeout, not a re-run of the
pinned binary (Cairn's/Alice's evidence covers the real serve).

## Relationship to A1

- A1 (watchdog): on timeout, mark suspect and respawn a fresh serve — mitigation,
  landed (`2e247bb`).
- A2 (this): carry partial lines so a >64 KiB reply is parsed at all — removes
  the trigger. Independent of A1; a clean A2 makes the timeout path far rarer
  (A1 stays useful for genuine hangs).

Both are amendments to the `060d842` frozen lineage and each needs its own
provenance receipt; the `WINDOW-OPENING.md` lineage block is already stale after
A1 (`ASSAY-A1-PROVENANCE-SECONDDRIVER.md`).

## Limits

Fake stdio, not the pinned binary; the fix is to the client framing only. No
serve, vault, or network touched; no tree modified (diff parked).

— **Assay** (`worker-glm-dsh2`).

---

## Rev 2 — folds Alice's two framing residuals (land A2 once, complete)

Alice's second seat (`ALICE-A2-FRAMING-SECONDCHECK.md`) PASSed the target and
found two holes in v1:

1. **UTF-8 boundary (moderate):** `buf += chunk.toString()` decodes each chunk
   independently, so a multibyte char split at the boundary is silently
   corrupted. Fixed with `StringDecoder("utf8")`, which holds partial byte
   sequences across `write()` calls.
2. **No trailing newline (low, latent):** a final line without `\n` sat in `buf`
   forever → timeout. Fixed by listening for stdout `end` and flushing the
   remainder.

v2 diff `d78ef21d…`, guarded `a7a91a60…` (v1 `08df040d…` kept as
`vault.fixed_v1.ts`); `git apply --check` clean on the live `905f604c…`. Power
check `90d040bf…` now **8/8**: v1 corrupts the UTF-8 split (30001 chars) while
v2 round-trips exactly (30000), and v2 resolves the no-newline case on stdout
`end` (v1 and the live file time out). Everything v1 did still holds.

fsync's ask ("land A2 once, complete") is satisfied by v2; the diff is parked
for Kiln's apply + an outside `cairn-pi` restart.

— **Assay** (`worker-glm-dsh2`).

---

## Rev 3 — folds Alice's settle-path teardown residual (A2, complete)

Alice's `ALICE-A2-V2-CHECK.md` PASSed v2 and found: `finish()` detaches the
listeners only on the **response** path; the **timeout** and **stdin-write-error**
paths reject with `onData`/`onEnd` still attached. On the long-lived serve's
shared stdout every timeout accrued a stale pair (v1 leaked one listener; v2's
`end` listener made it two), each still running `consume()` on later chunks, and
past 10 Node warns `MaxListenersExceededWarning`.

v3 centralizes teardown:

```ts
let settled = false;
let timer: any;
const teardown = () => {
  this.proc!.stdout!.off("data", onData);
  this.proc!.stdout!.off("end", onEnd);
  clearTimeout(timer);
};
const finish = (resp) => { if (settled) return; settled = true; teardown(); /* resolve|reject */ };
const fail   = (err)  => { if (settled) return; settled = true; teardown(); reject(err); };
timer = setTimeout(() => { this.suspect = true; fail(new Error("vault rpc timeout")); }, 30_000);
...
this.proc.stdin.write(line, (err) => { if (err) fail(err); });
```

Diff `9e215b68…`, guarded `50aefb3f…` (v1 `08df040d…`, v2 `a7a91a60…` kept);
`git apply --check` clean on live `905f604c…`. Power check `eb90e1ff…` now
**10/10**; the teardown probe on a call that never gets a reply:

| build | `stdout` listeners left after timeout (`data` / `end`) |
|---|---|
| v1 | 1 / 0 |
| v2 | 1 / 1 |
| **v3** | **0 / 0** |

and v3 also leaves 0/0 on the response path and on a `stdin`-write error
(rejected `stdin boom`). All v2 framing results still hold (UTF-8 round-trip,
no-newline flush, split/control/boundary/foreign-id).

fsync's "land A2 once, complete" is now satisfied by v3; parked for Kiln's apply
+ an outside `cairn-pi` restart.

— **Assay** (`worker-glm-dsh2`).
