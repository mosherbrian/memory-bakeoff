# Delivery c85 — Laya local data preparation: inventory, private artifacts, aggregate manifest

**cairn (local gufo) · 26 September 2026 · delivery mode (support mode withdrawn; no general
reading).** Boundaries honored here: no installation, no training, no remote teacher/API, no
hosted transcript egress, no external upload, no c67 re-run, no keyword labels called gold, no
standing Brian labeling duty. Raw/private data lives **outside tracked outputs** in a
permission-restricted directory; only this aggregate note is published.

## 1. Source inventory (what actually exists locally)

- **Pi session transcripts** — `~/.pi/agent/sessions`, 1,158 JSONL files (~64 MB); fleet seats
  (cairn/kiln/corvid via ACP) and local sessions land here.
- **Claude Code transcripts** — `~/.claude/projects`, 1,604 JSONL files; `isMeta`/`isSidechain`
  entries excluded.
- **Total scanned this pass: 2,762 files → 7,308 qualifying user messages across 1,400
  conversations** (20–2,000 chars, text blocks only).
- Fleet logs (agent-deck) are wake/dispatch records, not correction-bearing dialogue; not used.

## 2. Frontier labels: present or absent

**No authorized local frontier teacher exists, and no existing frontier labels cover this task.**
- The c67 46-label fixture is surface-derived and per lead correction **neither prices nor
  supplies** the pair-task label budget — not reused, not re-run.
- The R7 "teacher vs gold" artifacts belong to a different task (oracle feasibility), not
  correction/supersession pairs.
- **gufo (this seat) is local but not frontier; Claude is frontier but hosted — routing transcript
  excerpts through it is hosted labeling, i.e. the egress this commission forbids.**
- **Named dependency: frontier-teacher labeling of candidate pairs (local, authorized) is absent.
  Everything below is therefore candidates + schema with `label: null` — no keyword label is
  presented as gold.**

## 3. Candidate-pair construction (schema + rules)

Nomination is **rule-based shortlisting only** (`correction_cue`, `directive_cue` regexes);
`status` is `candidate`/`unresolved`, `label` is **null everywhere**. Per record: message/pair id,
conversation id, sequence, timestamp, scope (cwd), source-file sha256 (16-hex prefix), split
group, nomination rule, text. Supersession pairs = earlier directive message + first later
correction-cue message in the same conversation, `relation_hypothesis:
possible_supersession`, **ambiguous by construction — unresolved, never laundered to negative**
(c83 contract). Caps: 1,500 messages / 600 pairs (not reached).

## 4. Splits and leakage control

Conversation-level deterministic split (sha256(conv) mod 10: 0–6 train, 7–8 calibration, 9
heldout) — **all messages and pairs of one conversation share one split**; related-record
leakage across pairs is prevented by the same conversation key. **Honest caveat: the split is
leakage-safe but imbalanced** (candidate-bearing conversations hash unevenly): heldout currently
holds 28 messages / 5 pairs. Bucket boundaries are provisional and should be re-cut at labeling
time, keeping conversation-level grouping.

## 5. Artifacts, counts, named dependency

**Private (mode 700 dir, 600 files, outside tracked outputs):**
`/tmp/tern-laya-data-c85/`
— `candidates_messages.jsonl`, `candidates_pairs.jsonl`, `aggregate.json`, `prepare.py`.

**Aggregate counts (published):** 2,762 files · 7,308 user messages · 1,400 conversations ·
**954 message candidates** (train 904 / cal 22 / heldout 28) · **197 supersession pairs**
(192 / 0 / 5) · **labels present: 0**.

**Next step belongs to the dependency, not to me:** an authorized local frontier teacher (or a
Brian-approved local labeling path) labels shortlisted candidates; hand-labeled frozen test set
stays separate per the fair-comparison contract. No standing Brian labeling duty created.

— cairn (local gufo). Commission: delivery/c85-commission.md, QUEUE.md D4.

**Lead handling correction:** original private directory was inside the repo and not ignored. Tern moved it outside the repo to the path above (directory0700/files0600), without publishing raw text. No local frontier teacher means none established in this bounded inventory, not a global availability proof. Conversation grouping alone does not rule out duplicated/cross-conversation leakage; further local preparation is queued.
