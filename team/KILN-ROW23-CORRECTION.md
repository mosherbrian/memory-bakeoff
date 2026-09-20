# S4-2 correction — row 23's declared artifact EXISTS; the transcribed premise measured the wrong root

**Author:** kiln-flash (S4-2) · **Date:** 2026-09-16 · **Cost:** $0, local reads only
**Disposition chosen:** **correct the row** — I did not produce a new artifact,
because the declared artifact already exists, sha-verified, in the tree row 23
declared. No canonical writes were made.

## Measured facts (2026-09-16)

1. **The diff exists.** `implementer/repo-glm-dsh3/scripts/fix-habitus-adapter.diff`
   — sha256 `956352f6ca7730be8cb143b6b58233c09c555b7a39a54513002dc526a305e352`,
   matching row 23's recorded prefix `956352f6…` exactly.
2. **A second, byte-identical copy exists** at
   `team/row-habitus-classfix-check/fix-habitus-adapter.diff` (`cmp` clean),
   pinned at 2010 bytes by that directory's `MANIFEST.md` — Alice's
   second-driver check of 2026-09-12, which is also row 23's recorded
   verification evidence (`ALICE-HABITUS-CLASSFIX-CHECK.md`).
3. **Diff targets match row 23's description:**
   `src/memory_bakeoff/providers/external.py` + `tests/test_preflight_hardening.py`.
4. **Application state per tree** (habitus block in `external.py`):
   - `repo-glm-dsh3` (the done-in tree): **fix applied** — `product_ingest=False`
     + the "No product-mode ingestion path exists" note; classes `controlled_core`.
   - canonical `implementer/repo` and `repo-glm-dsh2`: **pre-fix**
     (`product_ingest=True`, no class change at the habitus block).
     This is precisely row 23's own recorded state: *"Canonical tree untouched;
     hand to implementer-of-record."*

## Correction

S4-2's premise — *"Row 23 is marked done but its declared artifact
`scripts/fix-habitus-adapter.diff` DOES NOT EXIST on disk"* — is **false for the
tree row 23 declared**. Row 23's status says "done-in-tree", and the tree it was
done in (`repo-glm-dsh3`) has the file at the recorded sha. The measurement
behind S4-2 evidently checked the canonical root, where the file is indeed
absent — but canonical absence is row 23's documented, intended state, not a
missing artifact. **Row 23 requires no correction on this point.**

## The real open gap (named so it is not lost)

The implementer-of-record handoff is still open: the verified diff has never
been applied to canonical (`implementer/repo`) or synced to `repo-glm-dsh2`.
That is a *forward* action on Brian's/PO's route, not a missing artifact — and
per the S3-7 precedent, writing new files into canonical goes through an
explicit ruling + `REPO-CANONICAL.txt` declaration rather than a side door.
Recommended routing: PO rules, then kiln applies the diff to canonical
(byte-identical, sha above) and syncs dsh2, or records the deferral.

— kiln-flash, 2026-09-16
