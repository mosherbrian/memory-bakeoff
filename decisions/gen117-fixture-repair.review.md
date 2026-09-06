VERDICT: SUPPORTED

Evidence checked (all in this repo, at `main` = `c73dc4a`):

**Run artifacts — `results/gen117/attempt1`**
- Manifest verifies: recomputed sha256 for all 7 artifacts, all match `MANIFEST.json`.
- `NON_EVIDENCE.json`: marker `NON_EVIDENCE`, dispositions `{COMPLETED: 60}`, one served model. `raw_seal.json` sha256 matches the actual `reader_raw.jsonl` bytes. All 60 rows: http 200, `finish_reason: stop`, empty `retry_history` — "no transport failures" holds.
- `estimands.json`: `cores_interpretable: 0`, `cores_total: 12`. "0/12 interpretable" holds.

**Measured numbers — recomputed independently from `reader_raw.jsonl` through the frozen parser**
- 48 selections total: 6 exactly canonical, 36 equal to the distinguishing token alone (head noun dropped), 6 other. Exactly the claimed 48/6/36/6.
- Cross-tab: all 36 head-dropped scored `UNSUPPORTED_VALUE` (total UNSUPPORTED_VALUE = 42 = 36 + 6 other).
- Mechanism confirmed: canonical values are `sector marlow` / `sector fenwick` (schedule `core01`); the reader returned `"selected_value": "fenwick"`; `classify_answer` (src/memory_bakeoff/reader_interference_v5.py:266-269) requires exact `_norm()` equality, so the token-only answer fails. Loosening is indeed a one-line-scale change, and a simulated token-accepting match turns 9/12 cores interpretable — consistent with the hedged "very likely... a usable run" (not 12/12; the 6 whole-sentence selections still fail).

**The enforcement claim — commit `7b54fff`**
- Exists, dated 2026-09-06 11:39 (before the 11:46 decision). Diff adds exactly the loop over `contract["source_sha256"]` refusing with `FROZEN SOURCE CHANGED`.
- The frozen contract (`results/gen116/attempt4/reader_interference_v5_contract.json`) pins exactly 5 files — "all five" holds.
- Pre-`7b54fff` version of the runner checked only the contract's own hash, never the pinned source files — so "before that commit I could have edited the matcher, re-run, and produced a green attempt2" is accurate about the code.
- Live test: I mutated the v5 module and ran the preflight; it failed with exactly `FROZEN SOURCE CHANGED since the contract: src/memory_bakeoff/reader_interference_v5.py...` (restored afterwards). `tests/test_gen117_execution.py`: 25 passed.

**Documents**
- `research/PI_READER_INTERFERENCE_RUN_GEN117.md`: three options, explicitly "stated without preference" — matches.
- Gen114 retraction: commit `7142581` (2026-09-06 01:18, same morning) "the Gen114 headline retracted"; `STATUS_AND_FINDINGS.md` confirms "Gen114's headline is RETRACTED at Gen115".
- Decision timestamp 11:46:02 vs commit `c73dc4a` at 11:46:16 — consistent.

**Could not verify from the repo**
- Sol's instruction, "Do not repair a run-bearing semantic after exposure" — the primary brief is external. The quote appears in `research/PI_READER_INTERFERENCE_RUN_GEN117.md`, `handoff/CODEX_TO_CHATGPT.md`, and the `7b54fff` commit message (which cites an external Fable review of the same rule). Internally consistent, but no independent source in the repo.
- "Sent to the control plane for ruling; not yet answered" — the control plane is an external GitHub PR/ChatGPT channel. The repo shows commit `e42d0da` "ruling requested" and the handoff text, but delivery and non-answer are not verifiable here.

Neither unverifiable item bears the decision's substance; every repo-checkable claim is exact.
