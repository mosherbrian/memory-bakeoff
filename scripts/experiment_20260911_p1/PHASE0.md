# STUDY-20260911-P1 — Phase 0 integration checkpoint record

Dispatch §Phase 0, executed 2026-09-11. Binary provenance: PROVENANCE.md
(this directory) — study build sha `c8a222ec…a172` (self-reports 2.23.2
(9c82920)), source-identical, NOT byte-identical to the Gen21-measured
arm64 tarball (`e9b0912c…0dcb`); from_key = OLD authoritative.

## The three checkpoint items — all PASS

1. **Perseus adapter runs as a Pi recall path** — new extension
   `extensions/pi-perseus-recall/` (separate adapter path;
   pi-project-recall/ and pi-recall-nudge/ untouched) registers the
   `project_recall` tool (same name + description text, so the untouched
   nudge companion's active-tool guard works unchanged), spawns
   `perseus-vault serve` and speaks newline-delimited JSON-RPC. Through the
   REAL B/C-round machinery (prime `--print` + RPC `switch_session`
   genuine-resume task): both extensions registered, pi-lcm ACTIVE (store
   written), nudge fired via `onResume` on the genuine resume
   (`reason='resume'`, inject line captured), `project_recall` invoked once
   through the real path.
2. **Supersession toggles cleanly between otherwise-identical configs** —
   seed-time `binding_on` (Gen102 pattern): two vaults with byte-identical
   records; ON adds only the `perseus_vault_supersede` link
   (from_key=record-old → to_key=record-new). Recall "staging deploy
   process": OFF → `['record-old', 'record-new']`; ON → `['record-new']`.
   Receipt: `phase0_toggle.txt` in the private evidence dir.
3. **Agent retrieves the known replacement through the real path** — with
   the supersede-ON vault, the resumed+nudged agent's
   `project_recall` result and final answer carry the CURRENT record
   (P1-NEW-9, helm on kite-k8s) and the superseded record (P1-OLD-1,
   ansible) never surfaces anywhere in the stream.

Receipt: `PHASE0_RECEIPT.txt` (private evidence dir
`~/.local/share/memory-bakeoff/experiment-20260911-p1/phase0-smoke/`),
verdict **PHASE 0 SMOKE RECEIPT: PASS**. Reproducible via
`scripts/experiment_20260911_p1/phase0_smoke.py` (asserts the binary sha
before any vault operation; records the provenance block in the receipt).

## Notes for case preparation (next phase, AFTER the conductor gate)

- Arm config pattern proven: packages [pi-lcm, pi-perseus-recall,
  pi-recall-nudge], settings carry `recallNudge` (orig F2 nudge — arms get
  the IDENTICAL nudge; supersession is the only variable, applied at seed
  time via vault lineage state) + `perseusRecall` vault pointer.
- pi-lcm writes the run's conversation (store rows written: 1) while the
  vault is read-only to the agent — the isolation/verification scheme maps
  cleanly: per-slot vault content snapshot (records + lineage) + pi-lcm
  store confinement as in B/C rounds.
- The extension is byte-identical across arms B/C; arm A omits it.
- Prime runs can be slow on a cold model (~92 s in this smoke; task 2.9 s
  warm) — schedule machine time accordingly for the 24-slot walk.
