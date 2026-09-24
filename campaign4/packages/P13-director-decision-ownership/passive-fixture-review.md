# P13-passive-fixture-1 — independent review (corvid)

- **Action:** `P13-passive-review-1`, owner corvid, `19:34:40Z`–`19:49:40Z`.
- **Claim:** `passive-fixture-claim.json` (`7a6978ba…`) — author status
  **INCOMPLETE retained**. Intake **174/174 claim hashes** and **14/14 canonical
  manifest** pass.
- **Verdict: current readiness PASS** on the passive-fixture evidence, with the
  proof boundary stated below. No source/live edits.

## Admitted proof boundary (explicit)

- Director/duty are **receiver doubles** — the pinned real
  `/var/home/bmosher/.config/agent-deck/acp-worker` running
  `plans/passive-acp-engine.py` — behind the **real** ACP runtime / wake /
  registry / socket. They are **not** evidence of human or model compliance.
- **No tools / no exec by construction:** the engine imports only
  `json, os, sys, time`; advertises **no tools and no capabilities**; never sends a
  tool call or permission request; has no process-spawning/shell code; the lane
  `unset ACP_AUTO_APPROVE ACP_MODE` (no auto-approve). Absolute-path commands in a
  prompt are inert — the engine only records the prompt and ends the turn.
- **Worker/verifier stay real model lanes**; the **driver alone** acknowledges
  (capability) and decides. Induction requires the pinned lane+engine bytes, a
  fresh-nonce probe through the **real** wake to director/duty (rc 0/3), and the
  nonce in each receiver's own record within 60 s — else `INDUCTION INVALID`,
  exit 4, no dispatch. Missing receiver fails before dispatch.

## Frozen harness (git show, not tree search)

- `git show 6e60ce5d:…/evidence/live-composition/inject-test.sh` = **`1a18fc1f…`**
  — matches the cited frozen hash (bound; commit `6e60ce5d`).
- `diff frozen(1a18fc1f) → current` is **one line** (1 removal + 1 addition), in the
  **negative early-decide helper** subshell: it now skips `*.db.*` config files
  (`grep -v '\.db\.'`) and tolerates whitespace (`'"step": ?"decision"'`) — the two
  disclosed harness-only bugs. That line runs **only** for the `neg-early-decide`
  mode, so the **positive (29/0) and no-receiver paths are unchanged**; the later
  negative rerun (4/0) is sufficient. Driver/evaluator/lane/engine/prep/inputs are
  unchanged after the freeze; manifest refreshed **14/14** (`sha256sum -c` rc 0).

## Runtime pin for signature

`plans/acp-passive-lane` = `8516171d…`, `plans/passive-acp-engine.py` = `9d987847…`,
`plans/live-p13-driver.sh` = `e5f8c54d…`, `plans/prep-p13.sh` = `8de8d306…`,
`plans/live-p13-inputs.template.env` = `47700c17…` (all in the 14-file manifest).
Prep uses the correct lanes (`prep-p13.sh` launches director/duty with
`-cmd plans/acp-passive-lane`); cleanup removes exact IDs. Product/adapters frozen
(`47f69dfd…`/`df51a1f4…`/`fdf49d0b…`).

## Consolidation

- Author **INCOMPLETE retained** (generator-labelled because a frozen file changed
  after freeze); independent current readiness: **PASS** — the change is proven to
  be the negative-helper assertion only, the positive/no-receiver paths are intact,
  and the passive boundary is explicit (no human/model obedience claimed).
- Remaining: injected runs are **not live proof**; the ladder/ack/recurrence under
  the passive fixtures is exercised offline with the real runtime/wake and injected
  OS. Live remains separately held. No edits/live.

Returned to Tern via receipt path; no source/live effect by corvid.
