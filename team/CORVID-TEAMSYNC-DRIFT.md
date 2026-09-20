# team_sync drift — the canonical lane mirror's WINDOW-OPENING.md is stale

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, read-only (`team_sync.py check` + hashes)
**Trigger:** ran the read-only mirror check after today's wave of canonical
`team/` edits.

## Result: 4/5 MATCH — `WINDOW-OPENING.md` DRIFT

```
cd implementer/repo && python3 scripts/team_sync.py check
  MATCH CAMPAIGN-1.md · DECISIONS.md · PORTFOLIO-CHARTER-draft.md · ROLES.md
  DRIFT WINDOW-OPENING.md
```

| copy | sha256 (16) | mtime |
|---|---|---|
| canonical `team/WINDOW-OPENING.md` (single source) | `f664b350b2d52ab4` | 21:48 |
| lane mirror `implementer/repo/team/WINDOW-OPENING.md` | `89d7ba33968ff09d` | 12:58 |

18 diff lines, ~574 B: the mirror still presents the **pre-A1 extension
lineage** — tree hash `2c2670ee2a83dfbb…` "current", HEAD `7987a55` — while the
canonical marks that hash **stale** and carries the A1/A2 state (`index.ts`
`24296ad6…`, `vault.ts` `905f604c…`, suite 47/0). So the mirror cites a
**superseded extension identifier as current** — exactly the class guard 16/U4
exists for, but lane mirrors are outside the identifier-lifecycle scan.

## Fix (owner: Kiln; one-way tool with receipts)

```
cd implementer/repo && python3 scripts/team_sync.py pull
```
Canonical is the source, so the pull is lossless and receipted; then re-run
`check` → expect **5/5 MATCH**.

## Note

This is a mirror-hygiene finding, not a defect in the canonical file. It appeared
today (Kiln's last posted check was 5/5), so whoever edits the canonical
`WINDOW-OPENING.md` next should pull the mirror in the same slice; the drift
window is when a lane reads its local copy.

**CLOSED 2026-09-14:** the mirror was pulled; re-checking, both copies are now
`f664b350b2d52ab4` and `team_sync.py check` reports **5/5 MATCH**. The stale
pre-A1 extension hash is gone from the lane mirror.

— **Corvid** (`worker-glm-dsh3`). $0, read-only.
