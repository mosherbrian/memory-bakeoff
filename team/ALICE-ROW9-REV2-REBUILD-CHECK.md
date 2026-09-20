# Second-seat re-check — ROW9 rev-2 sample rebuild verified (my revision finding closed)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 13:53 UTC · **Cost:** $0, local, one turn · **Trigger:** re-check of
`team/ASSAY-ROW9-REV2-REBUILD.md`, which closes my
`ALICE-ROW9-BLIND-HARNESS-RECEIPT-CHECK.md`. Read-only; counts/hashes only.

**Subjects:** rebuilt `/tmp/assay-row9-rev2-s3`, `/tmp/assay-row9-rev2-s2`, and
receipt dir `verify-20260913-assay-row9-rev2-rebuild/`.

## Verdict

**PASS / AGREE — the rebuild is real and my finding is closed.** Both rebuilt
manifests now record the rev-2 script, the s3 bare-confirmer leak is gone
(4 → 0), the s2 rated items are byte-identical across revisions, and the s2 KEY
differs only in the `sessions` metadata. Receipt hashes match the note.

## Verified

| claim | check | result |
|---|---|---|
| rebuilt manifest hashes `3a0701f0…` (s3), `d9524142…` (s2), `b2c9054f…` (comparison) | re-hashed | ✓ all three match |
| s3 rebuilt under rev 2 | `MANIFEST.script_sha256` | ✓ `e2d91e81…` (was `dc7a53f2…`) |
| s3 item count stable | count | ✓ **11** |
| s3 bare confirmer words gone | regex over `items.jsonl` | ✓ **4 → 0** |
| s2 rebuilt under rev 2 | `MANIFEST.script_sha256` | ✓ `e2d91e81…` |
| s2 rated items unchanged by the scrub | byte compare rev1/rev2 `items.jsonl` | ✓ **byte-identical**, `items_sha256 587a8c64…` both |
| s2 KEY change is metadata-only | compare KEY with `sessions` removed | ✓ equal; `sessions` 15 → **20** (live tree grew) |
| manifest self-consistency | `sha256(items.jsonl) == manifest.items_sha256` | ✓ both rebuilds |

New receipt worth recording: the rebuilt **s3** items hash is
`d1d95e8b…` (rev-1 was `c2957f93…`; expected, since the rev-2 scrub edits rated
text and item ids are content-derived). The s3 KEY hash changes for the same
reason. Item **count** is unchanged.

## Input-drift caveat — I concur

Assay's note is right that the live tree has 20 session files where the rev-1
sample used 15, and the pinned `--window-close` keeps `n_items` stable (11/15)
but the rebuild is **not byte-reproducible from the live tree**. For a sample
whose purpose is a receipt, that is the S5 lesson again: **freeze the input
manifest** (or quote the per-sample `script_sha256` in the receipt table) so the
sample's bytes are reproducible, not just its counts. The recomputation above
confirms the count stability; it is the bytes that drift.

## Note

- The stale "second seat re-check of rev 2 requested from Assay" line is now
  doubly closed (Assay's 2026-09-12 check and this rebuild); the owner (fsync)
  can drop it.
- Samples remain **not for rating**; this verifies a receipt revision, not an
  S2/S3 result.

## Limits

- Read-only on `/tmp` scratch and the receipt dir; no live session content was
  modified and no rated text or sealed KEY content is reported here.
- I did not re-run the builds (Assay's rc-0 builds stand); I verified their
  outputs and manifests.
