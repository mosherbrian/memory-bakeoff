# P13-live-3 — independent live review (corvid)

- **Action:** `P13-livereview-3`, owner corvid, `19:43:35Z`–`19:53:35Z`.
- **Result:** `wait:both passive receivers recorded their probe` INCOMPLETE (60 s) →
  `INDUCTION INVALID` (rc 4); cleanup `19:42:44Z` verified. **No work dispatch.**
- **Verdict: measurement/record-path failure — not a product or receiver failure.**
  INVALID preserved; ladder unexecuted; no product FAIL/PASS.

## Bound evidence

- Real wake probe sent to both passive seats at `19:41:31Z`
  (`wake-fixture-extract.txt`: director `7f67ddd2…`, duty `1dbdc692…`, transport
  state `started` — **real delivery**). Driver `received()` then timed out.
- Receivers **did record** the probes — at
  `/home/bmosher/.local/share/p13-passive/unknown.jsonl`:
  `nonce a08a2451aa4439bac0c67622fe1070b4` (director) and
  `nonce 7a8c40d328140578696b976b7935fe58` (duty), matching the probe nonces.
- Cleanup `19:42:44Z`: all four exact IDs absent, scope `inactive/dead`; no
  worker/verifier dispatch occurred.

## Actual runtime/path vs driver expectation

- Engine `plans/passive-acp-engine.py:12`:
  `INST = os.environ.get("AGENTDECK_INSTANCE_ID", "unknown")`; the seats were
  launched at prep **without** `AGENTDECK_INSTANCE_ID`, so `INST="unknown"` and the
  record file is **`unknown.jsonl`** (not `<sid>.jsonl`).
- The prep seats run under the **real `HOME=/home/bmosher`**, so the engine wrote to
  `/home/bmosher/.local/share/p13-passive/`.
- The driver's `received()` (`live-p13-driver.sh:329`) checks
  `"$HOME/.local/share/p13-passive/$sid.jsonl"` under the driver's **private
  `ROOT/home`**. So the path, filename and HOME all differ from where the records
  actually landed — the probe was delivered and recorded, but **not where the driver
  looked**. This is a **record-instance/path mismatch**, not a receiver or product
  failure.

## Smallest concrete correction (no edit here)

Make the record location **deterministic and shared**: at prep, launch the passive
lane with a stable instance id and an agreed probe directory that the seats and the
driver both read — e.g. export `AGENTDECK_INSTANCE_ID=$sid` (or a `P13_PASSIVE_*`
env) and a pinned `P13_PASSIVE_DIR` for the lane, have the engine write
`<sid>.jsonl` there, and have `received()` read that **same** path. Alternatively
derive the instance from the ACP session/argv. This removes the "unknown" filename
and the HOME divergence; do not infer identity from filenames, and do not fabricate
records.

## Preserved

`INDUCTION INVALID` retained; the ladder (`0/+20/+40`), capability ack, same-key
recurrence, decide-suppression and restart-no-duplicates remain **unexecuted /
unproven**. No edit/live effect by corvid; live remains separately held.
