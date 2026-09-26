# S11-3 design — pi-lcm NATIVE supersession on broader histories

Row S11-3 (sprint 11, BACKLOG-NEXT rank 15). Author: kiln-flash, 2026-09-19.
Built after gate S11-3G VERIFIED PASS (corvid-dsh 08:44 PDT, receipt
`team/CORVID-S11-3G-VERIFY.md`, gate sha `38ab1696…f53d27` — unchanged). The
binding declaration is `declaration.json`, written before any receipt and
sha-bound into all 138 of them; trials and generator are sha-pinned inside it.
`gen_trials.py` is deterministic and left runnable in place: re-running it
rewrites `trials.jsonl` byte-identically (verified twice). $0, local, no LLM,
no score import. NATIVE arm only — no layer code, no layer arm, per the row.

## Prior measurement (standing re-measurement rule)

`team/S7-STATELAYER/verdict.json` (VERIFIED PASS S7-3G): native pi-lcm **0/32
false supersessions, 12/12 updates superseded** — controlled corpus only: one
distractor shape (same template, different whole-token scope), streams of 2
writes. Protected comparison point: agentmemory 418/450 (92.9%) false
supersessions, `research/AGENTMEMORY_FINDINGS.md`.

## What was declared before the run (the breadth)

3 distractor families × 11 = **33 distractors** (> prior's 32) and **13
updates** (≥ prior's 12), every stream **4 writes** (> prior's 2), fixed
increasing write clocks. The families are three near-neighbor relations the
prior corpus never exercised, generated mechanically from the S7-3 template
machinery (declared in `declaration.json` verbatim):

- `mailbox-rename` — near-neighbor writes name a renamed mail target of the
  same service: subject token `s` → `s-mailbox` (the original's scope token
  embedded as a SUBSTRING).
- `ledger-amend` — near-neighbor writes are the service's companion ledger
  line: object swapped (redis→postgres, canary→blue-green, synthetic→load-test,
  import→export); whole-token difference only.
- `roster-drift` — near-neighbor writes name a joint roster of two services:
  subject token `s` → `s-sB` (scope token embedded as a SUBSTRING).

Ground truth declared with the families: near-neighbor writes are different
facts, never successors of the original, so distractor displacement is false
supersession; update streams are genuinely newer states of the same fact
(value ladder, later clocks), so the original must be displaced.

Pre-registered expectation (in `declaration.json`): whether the exact-AND gate
matches SUBSTRINGS or whole tokens decides if the rename/roster families
compete at all; low rate expected if whole-token, a high rate would be a
genuine native failure on broader histories. Either number decides.

## Protocol

Supersession is retrieval displacement generalized to streams: per trial a
fresh pinned store (`pi_lcm_store_reader_toollevel`, the S4-14/S6-2 pin)
ingests the trial's whole stream in order, the ORIGINAL's own query is
re-issued with every write present, and `superseded` = the top hit is any
write other than the original. Sanity BEFORE declaration: each original alone
answers its own query as top-1 — all 46 held (a failure would have stopped
the run before anything was frozen). Controls ran first:
`never-supersede` supersedes nothing, `always-supersede` everything.

## Result (the row's deliverable)

**native-failure.** The prior's 0/32 null does NOT generalize to broader
histories:

| arm | false supersessions | missed updates |
|---|---|---|
| pi-lcm-native (S11-3, broader) | **22/33 (66.7%)** | 0/13 |
| pi-lcm-native (S7-3 prior, controlled) | 0/32 | 0/12 |

Per family: mailbox-rename **11/11**, roster-drift **11/11**, ledger-amend
**0/11**. The mechanism is the pre-registered one: the store's exact-AND gate
matches the original's scope token inside a compound subject (`delta` inside
`delta-mailbox`, inside `delta-fjord`), so a renamed target or a joint-roster
line displaces the original; the whole-token object swap (postgres line) does
not compete. Updates all superseded (top-1 moves to a newer write), so the
failure is specifically FALSE supersession — the agentmemory disease shape
(false positives on near-neighbors), not blindness to updates.

`changes_state_layer_answer: true` — the state-layer answer's own limitation
said broader histories were untested, and the answer page required
native-failure evidence before any layer talk. This is that evidence: any
state-layer claim must now be evaluated against a native arm that fails at
66.7% on declared broader corpora, not against the controlled 0/32.

## Reproduction (for verification)

```
cd team/S10-PI-LCM-HIST
python3 gen_trials.py                       # rewrites trials.jsonl, byte-identical
PYTHONPATH=/var/home/bmosher/.local/lib/python3.14/site-packages \
  python3 run_hist.py                       # sanity → declaration → arms → verdict
python3 check.py                            # the gate: clean, rc 0
```

Environment note: this seat's sandboxed python3 does not see the host user
site-packages; the runner needs the host numpy (2.4.4) via the PYTHONPATH
above, or `/var/home/bmosher/convvenv/bin/python` (numpy 2.5.2). The S7-3 run
used the same host user site. A full re-run rewrites `declaration.json`
(new clock) and therefore invalidates the receipt sha-binding — re-verify
against the CURRENT artifact bytes; re-run only if a defect is found.
