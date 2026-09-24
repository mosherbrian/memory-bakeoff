# P13-binding-4 — independent binding review (corvid)

- **Action:** `P13-binding-4`, owner corvid, `19:55:46Z`–`20:04:51Z`; prep
  `PASS no tasks` (`prep-binding-release-4.json`). Read-only; no launch/wake/cleanup.
- **Verdict: PASS.** The full prep composition is explicit and binds correctly:
  returned IDs → registry wrapper → wrapper sha/argv (absolute RECORD + distinct KEY)
  → prep-result fields; W/V real lanes; runtime pinned; sockets fresh; citation
  reconciled.

## Prep hashes (15/15 match `binding-receipt-4.json`)

`fixture-ids.txt` `3eb41f3e…`, `registry-before.json` `48a9cc20…`, `cleanup.sh`
`cae62130…`, `prep-result.env` `b5362812…`, `worker.json` `6f220a35…`,
`verifier.json` `2b7d5dc1…`, `lane-director` `ae826af4…`, `director.json`
`ffd78765…`, `lane-duty` `ffb895ad…`, `duty.json` `9c324e75…`,
`registry-after.json` `ed002f63…`; all `.stderr` empty.

## Composition: returned ID → wrapper → argv/hash → prep-result

- **Registry (returned IDs):** W `42eee9c4-1790279701` → real `acp-go`;
  V `7935b4fc-1790279702` → real `acp-go-deepseek`; D `6f0fa7a4-1790279702` →
  `command=/home/bmosher/p13-prep-p13l4/lane-director`; U `3c98816d-1790279702` →
  `command=/home/bmosher/p13-prep-p13l4/lane-duty`; profile `campaign4`; **no main
  seats**.
- **Wrapper argv (absolute RECORD + distinct KEY, no HOME inference):**
  `lane-director` = `exec plans/acp-passive-lane /home/bmosher/p13-prep-p13l4/passive-director.jsonl p13l4-director`
  (`sha256 ae826af4…` = `D_LANE_WRAPPER_SHA`);
  `lane-duty` = `…/passive-duty.jsonl p13l4-duty` (`sha256 ffb895ad…` =
  `U_LANE_WRAPPER_SHA`).
- **prep-result fields:** `D_RECORD=/home/bmosher/p13-prep-p13l4/passive-director.jsonl`,
  `D_KEY=p13l4-director`, `D_LANE_WRAPPER_SHA=ae826af4…`, `D_ID=6f0fa7a4…`;
  `U_RECORD=…/passive-duty.jsonl`, `U_KEY=p13l4-duty`, `U_LANE_WRAPPER_SHA=ffb895ad…`,
  `U_ID=3c98816d…` — **distinct paths and keys**, absolute, no HOME/runtime-ID
  assumption.
- Wrapper shas equal `prep-result` fields and the receipt file hashes.

## Runtime / sockets / cleanup

- Real runtime `/home/bmosher/.config/agent-deck/acp-worker` = `6871ceb1…`, matching
  `prep-binding-release-4.json`.
- Live sockets: distinct inodes `24114403` (D), `24114411` (U), fresh mtimes
  (`2026-09-24 12:…` PDT) — distinct incarnations.
- `p13prep-cleanup-p13l4.timer` active, `OnCalendar=2026-09-24 20:45:00 UTC`
  (`next_elapse` 13:45 PDT), exactly the receipt.

## Citation reconciliation

`prep-binding-release-4.json` cites **`ddea0cf7`** (the receiver-binding freeze
commit) — the earlier stale `6e60ce5d` citation is reconciled; the canonical
manifest pins the final bytes.

**PASS** with the hashes/argv/socket facts above; returned to Tern for the live
signature. No launch/wake/cleanup/edit by corvid.
