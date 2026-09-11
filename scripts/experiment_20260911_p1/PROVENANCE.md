# STUDY-20260911-P1 — Perseus binary provenance record (committed per conductor instruction; the build handoff left it uncommitted)

## Study binary (used by ALL arms A/B/C of this study, on THIS host)

- Path: `/var/home/bmosher/perseus-build/src/target/release/perseus-vault`
- sha256: `c8a222ec7077d713212c2414d440586f564338aaa153eeb13b08ebf14854a172`
- Self-reports: `perseus-vault 2.23.2 (9c82920)` (conductor-verified 2026-09-11;
  re-verified by the harness at every phase-0 run: sha asserted before any
  vault operation)
- Build method: `build.sh` with `GIT_HASH=9c82920`, rust 1.97.1, bookworm
  (Debian), **DEFAULT features**. The Dockerfile lean build is FORBIDDEN —
  it is keyword-only wearing the version string (no inspect surfaces).

## Relationship to the Gen21-measured artifact

- Gen21 pinned artifact: official `perseus-vault-aarch64-apple-darwin.tar.gz`,
  sha256 `e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb`,
  source commit `9c829207a4b44a8e679ba912b4c1c5608c8f1e36` (annotated tag
  `4f405f53f4c9b6a403df0d42cf0d59bf80c64da4`), MIT.
- The study binary and the Gen21 artifact are **source-identical, NOT
  byte-identical** (same source commit, different target: linux-x86_64 vs
  darwin-aarch64).

## Validity statement (conductor design decision, 2026-09-11)

Within-study contrasts (A vs B vs C) all run on this host with this same
binary, so they are internally valid. Gen21/Round-3 numbers
(`ROUND3_SUPERSESSION_RESULT.md`: EXPLICIT_LINEAGE stale co-return removed
48/48, current lost 0) are **labeled prior evidence from a different
(measured, arm64) build**, not replication claims for this build.

## Supersede direction (standing trap)

`perseus_vault_supersede` parameter descriptions are AUTHORITATIVE:
`from_key`/`from_category` = the OLD entity being superseded;
`to_key`/`to_category` = the NEW one that supersedes. The tool's summary
text disagrees ("relates a new fact to an old one") — measured behavior
agrees with the parameters; the inverted Gen102 run is retained as
evidence (`perseus-on-INVERTED-SUPERSEDED.json`).

This provenance block MUST be carried in every run record, the results
doc, and the freeze commit of this study.
