# R2H pack integrity re-check (spark pulse, post-REV-3)

**Seat:** worker-glm-2 · **Date:** 2026-09-14 · **Cost:** $0, local, read-only

## Checks (all green)

1. **Stamp matches bytes:** `PACK-SHA256.txt` records `005211d4…4377c`;
   recomputed sha256 of the committed `r2h_deploy.py` is identical.
2. **FREEZE.md byte-frozen:** tracked, last touched by the freeze commit
   `b0b761a`; working tree clean; current sha `6dcd356e…` — REV-3 added no
   edits to it.
3. **Freeze/stamp relationship is as designed:** `FREEZE.md:51` pins the
   pre-REV-3 script hash `74e7ae86…`; the live script is REV-3 `005211d4…`.
   The freeze describes the frozen proposal/method; the stamp file
   (`PACK-SHA256.txt`, commit `822be32`) carries the deploy-script lineage.
   Brian checking staleness should compare against the stamp, not the freeze
   row — the receipt (`team/R2H-REV3-RECEIPT.md`) already says this.

No action needed; recorded so the next seat doesn't re-derive it.
