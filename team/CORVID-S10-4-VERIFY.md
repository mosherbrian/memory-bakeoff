# CORVID-S10-4-VERIFY — build verification of row S10-4

corvid-dsh, 2026-09-18 15:45 PDT. Verdict: **VERIFIED PASS** (one deployment
hazard restated for cairn, §6). Row S10-4 ("Planner integrity — fix
sprint-next's duplicate detector so it keys on candidate identity, not rank
number"), owner kiln-flash, artifact `team/S9-SELECT-FIX/` (sprint-next =
the fix, sprint-next.before = the live tool verbatim as of 15:2x, proof.py,
manifest.json). Gate S10-4G was verified by this seat 13:50 PDT
(`team/CORVID-S10-4G-VERIFY.md`); the gate is unchanged.

## 1. Gate

- `check.py` sha256 `eb049906eba0644c67bebced314091a3de09e7c813178112245196339b136540`
  — identical to my 13:50 gate verification and to kiln's 15:24 close value.
- Mandatory `--selftest`: rc 0, PASS — 2 conforming builds accepted;
  receipts-only directory and 16 mutants each rejected by exactly their own
  markers. Two of those mutants matter to this row's honesty claims: "a proof
  that cannot fail" and "one that writes to the live board" — the gate already
  rejects both failure modes.

## 2. Declared check — both directions, on the patched tool and on the bug

- `python3 team/S9-SELECT-FIX/proof.py` rc 0: all four directions hold on the
  patched copy — same artifact re-declared under a NEW rank refused (→ S8-1);
  same artifact under the SAME rank refused (→ S8-1); fresh artifact over
  burned rank 2 admitted (None); fresh artifact at rank 1 admitted (None).
- `python3 team/S9-SELECT-FIX/proof.py --tool team/S9-SELECT-FIX/sprint-next.before`
  rc 1 with exactly one failing direction: "a fresh artifact over burned rank 2
  is admitted … = 'S8-1', must be None" — the pre-fix copy reproduces the
  false refusal on the record (the 11:04 re-plan lost ranks 2–4 this way; the
  12:27 proposal lost rank 5).

## 3. The fix — diff scope verified independently

`diff sprint-next.before sprint-next` shows exactly two hunks: one comment
block rewritten (documenting the repair and the two dead proposals), and the
single logic change `if m:` → `if m and art in m.group(0):` inside
already_admitted's rank fallback. Nothing else in the 36 KB tool changed —
the path test above it is untouched, as the row's "scoped to already_admitted
and nowhere else" claims.

## 4. Scratch-board discipline — verified by construction, not by trust

proof.py wires the tool through SN_TEAM / SN_QUEUE / SN_DIR onto a temp
directory holding one synthetic row; it never reads team/QUEUE.md. Those env
settings are real tool inputs (`sprint-next` lines 44–48), so the scratch
wiring is genuine, and the tool module is loaded and called on the real
`already_admitted` path. Live-board mtime before/after my proof runs shows
only my own queue-claim edits. My additional edge probe (beyond the four proof
directions): same burned rank with a re-pointed artifact path → admitted
(None), and same path same rank → refused (S8-1) — exactly the gate's stated
note, "the rule the row defines".

## 5. Deployment honesty

`deployed: false` verified: the live tool `/home/bmosher/conductor-chat/workers/sprint-next`
still contains the old `if m:` fallback, so the fix is not live. The row's
caution was warranted: the live tool's mtime moved from 12:45 to **15:38**
(size 46948 vs the before-copy's 36796) — its operator is mid-repair today,
so `sprint-next.before` is a faithful snapshot of 15:2x but is no longer
byte-identical to the live file.

## 6. Deployment hazard restated for cairn (the handoff this row declares)

The fixed copy is proven here, but it is a patch against the 15:2x live file.
The live file has since moved (15:38). Deploying by overwrite with
`team/S9-SELECT-FIX/sprint-next` would clobber the operator's newer work —
the exact hazard `deployed: false` anticipates. The one-line fix (`if m:` →
`if m and art in m.group(0):` plus its comment) should be re-applied onto the
operator's current live version at their next checkpoint, then proof.py
re-pointed at the deployed file (`--tool`) to re-run all four directions in
place. That re-application is cairn/operator work, not this row's.

## 7. Verdict

VERIFIED PASS. The detector now keys on candidate identity: a true re-admission
is refused by path regardless of the rank cited, and a fresh candidate over a
burned rank number is admitted — proven in both directions on scratch copies,
with the bug demonstrated on the preserved pre-fix copy and the live board
untouched throughout.
