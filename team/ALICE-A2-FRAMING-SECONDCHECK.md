# Second-seat — A2 vault RPC framing fix (`a2-buffer.diff`): target PASS, two residual framing holes

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 23:4x UTC · **Cost:** $0, independent bun harness, one turn.
**Trigger:** `ASSAY-A2-VAULT-FRAMING-FIX.md` — the fix for the live-arm
chunk-boundary timeout, "validated, not applied". No tree modified.
Harness: `row-a2-framing-check/alice_a2_check.ts` (`c82b3233…`), result
`result.json` (`4fb7862c…`). Drives the **real** `VaultServer.rpc()` on the live
`vault.ts` (`905f604c…`) and Assay's `vault.fixed.ts` (`08df040d…`) with fake stdio.

## Verdict

**PASS on the defect and the fix's target.** Diff `a2-buffer.diff` (`415c85b6…`)
matches the note, `git apply --check` is clean on canonical `implementer/repo`,
and the harness reproduces both directions:

| case | live `vault.ts` | fixed |
|---|---|---|
| reply split mid-line (>64 KiB) | **rejected `vault rpc timeout`** | **resolved** |
| foreign-id line then ours, one chunk | — | resolved (ours; foreign ignored) |
| split exactly at the newline | — | resolved |

So the carry-over buffer removes the production trigger, and the fix is strictly
better than the live file.

## Residual 1 (moderate) — per-chunk `toString()` corrupts UTF-8 at a boundary

The fix appends **decoded strings** (`buf += chunk.toString()`), so a multi-byte
UTF-8 character split across a chunk boundary is decoded twice: each half becomes
U+FFFD. The reply still resolves, but the text is **silently corrupted**.
Harness case `utf8_split` (a reply containing `café ☃ …`, boundary 1 byte into
the `é`): fixed resolves, but the round-trip is **not equal** (got length 70008
vs 70007) — one character became two replacement characters.

This matters here: the vault carries operator text, which is exactly where
non-ASCII lives. **Fix:** decode with `new StringDecoder("utf8")`, or accumulate
`Buffer`s and split on byte `0x0A`, decoding each complete line once. (The live
file is worse — it drops the reply entirely — so this is not a regression, but
it is a hole in the new code path.)

## Residual 2 (low, latent) — a final line with no trailing newline never resolves

`buf` is only consumed on later `data`; nothing flushes it at EOF. A reply whose
last line lacks `\n` stays pending and times out (harness: `rejected vault rpc
timeout`). If the serve always writes `\n`-terminated lines this is latent; still
the same class as the bug being fixed (a complete reply silently dropped).
**Fix:** flush `buf` on the stdout `"end"`/`"close"` event, or state the
newline-termination contract explicitly.

## Scope and limits

- Fake stdio, not the pinned serve; I did not re-run Assay's 6/6 power check —
  I wrote an independent harness with two adversarial cases it does not cover.
- Both residuals are in the **client framing**; the fix is still the right A2
  unblock. If applied as-is, note the UTF-8 caveat in the amendment receipt, or
  land the `StringDecoder` variant instead.
