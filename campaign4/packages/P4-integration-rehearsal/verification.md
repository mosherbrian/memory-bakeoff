# P4-integration-rehearsal — independent verification

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; verifier budget 2400 s (`infra-recovery-decision.json`)
- **Baseline:** contract `c0f31dd0…` @ `53c901bb`; accepted P3-r3 core
  `d27d5be7b4086556260974bca9aef2ec6f8b1db8`.

## Verdict

**FAIL** — one bounded defect: the required **removed-timer** fault is not
handled. A timer that was explicitly removed still produces a stop and a wake
through `on_deadline`, so a cancelled/stale deadline can still stop the worker
and wake Tern. Every other required end-to-end case and fault-matrix case
passes, the 59 accepted core tests pass, and no live effect is possible.

## Commands and actual results

```bash
PYTHONPATH=src python3 -m pytest tests/test_rehearsal.py -q   # 14 passed in 0.03s
cd campaign4/packages/P3-r3-authoritative-claims
python3 -m pytest tests/ -q                                   # 59 passed
```
Plus the independent fault matrix below (fresh `/tmp` DB per case, fake clock /
adapters only, no sleeps).

## Artifact hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/driver.py` | `181f5b994387a37c8eb6566b0cd068cdb7adc2e2af78e4afa762ff45aa41914b` |
| `src/fake.py` | `fe7d4ef74e7862bc91ad1bdeccbea930fefa539a496bff53eb81f4a756b6e0da` |
| `src/lifecycle.py` | `7ebaf466dd47e760b401fa0b1d8c2c2d8a1fd26549b0b91a0bfdbb47f498c03f` |
| `src/store.py` | `dafaeb333acc255a5c59de782e6f8be4c71a77322ac59247d232138639178242` |
| `src/validator.py` | `dcecfc1d95a75c30a9ecca9a80df6418f930e03d4525fc2b5f38ab31997666c5` |
| `src/supervisor.py` | `a71b10db5a0b3cd91369f7e9f5e76cdf3fd947c86c53c56162aee72c3fdd4526` |
| `src/status.py` | `c894ae41408250361f4bc2c3b3093818052780fdae7389343931e26c51fe23b2` |
| `tests/test_rehearsal.py` | `ae8179b55d920e687ebf98aeb3cd14c0293fc134e1796ee189a373b0f33018f9` |
| `fixtures/fixture.json` | `5df02e257518f5a83b037a7b675022583ebfb4d6edec9f6e89e05009240fe4ef` |
| `rehearsal-report.md` / `interface.md` | `5dd328aa…` / `3b82e895…` (as supplied) |

The supplied group sums are not reproducible by per-file manifest (they are
described as non-authoritative); per-file hashes above are authoritative.

## Fault matrix — expected/observed

| Case | Expected | Observed |
|---|---|---|
| crash-before-delivery | hold-for-reconciliation | hold (attempt stays 1) |
| ambiguous delivery | hold, no blind redispatch | hold; `launches==1` |
| crash-after-ack | settled-acknowledged | settled |
| repeated completion | rejected | `TransitionError` |
| repeated deadline | one-shot, single stop/wake | second call `already-handled`, 1 stop/1 wake |
| repeated trigger | deduped | `dedupe_action_due` second → ACTIVE |
| **removed timer** | **no stop/wake** | **stop=1, wake=1 → DEFECT** |
| stale snapshot | owned INVALID | INVALID (`cairn`) |
| legitimate rest | REST, no auto-authorize | REST; `(Q,2)` absent |
| missing disposition | E_MISSING_DISPOSITION | E_MISSING_DISPOSITION |
| blocked verifier resume | CHECKING, same attempt, no worker rerun | CHECKING, attempt 1, launches unchanged |
| stale worker timer | ACTIVE on verifier deadline | ACTIVE at 13:30Z |
| no live effects | none possible | scan clean |

## The defect (bounded)

`FakeTimer` records removals in `self.removed` (`src/driver.py:86,94`) and
`due()` correctly omits removed timers (they are popped from `armed`), but
`Driver.on_deadline` (`src/driver.py:190–203`) only checks `self.timer.fired`.
It never consults `removed` or `armed`, so calling it for a deadline that was
removed still fires the one-shot, appends an interrupt, calls
`ext.stop(...)` and `ext.wake("tern", ...)`:

```
d.start_dispatch(Q,"a1",DL)
d.timer.remove("deadline:a1")          # deadline cancelled
d.on_deadline("a1", Q)                 # observed: stops=1 wakes=1, ('interrupted', False)
```

Contract §4/§6 require rehearsing a **removed timer** with "finite owned
handling … no duplicate stop/wake"; a removed timer must not trigger a stop or
wake. Expected `already-handled`/no-op (or an explicit owned outcome), observed
`interrupted`. The worker's 14 tests do not exercise `remove()` at all, which is
why the gap was not caught.

**Required correction:** `on_deadline` must verify the deadline is still
armed/valid (e.g., absent from `removed`) and return without stop/wake for a
removed or never-armed timer, while preserving the one-shot behavior for a
genuine due deadline.

## Retained checks

- **59 accepted core tests pass** at the pinned P3-r3 baseline; the accepted
  `lifecycle.py` and `validator.py` copies are byte-identical to `d27d5be`.
- **No live effects:** `src/` contains no `subprocess`/`socket`/`signal`/
  `os.kill`/`os.system`/`popen`/`requests`/`urllib`/`time.sleep`/`while True`;
  imports are `hashlib`, `json`, `os`, `sqlite3`, `datetime`, `re`, `sys` plus
  local modules. `FakeStopWakeAdapter.notify` refuses Brian and only fake-queues.
- Status report is `simulated: true`, names duty `cairn` / escalation `tern`,
  and emits terminal pause only as fake output; zero notifications.

## Non-blocking provenance note

The copied core differs from accepted `d27d5be` in exactly one line:
`src/store.py` uses `from lifecycle import …` (flat layout) where the accepted
source uses `from .lifecycle import …`. Semantics are otherwise byte-identical;
this is a local-layout adaptation not disclosed in the report, and it is why the
group hash differs. It is not the FAIL cause, but the adaptation should be
documented for the immutable-core claim.

## Readiness conclusion

The rehearsal is **not ready** for a separately authorized live fixture. Beyond
the report's listed gaps (no live adapter reviewed/enabled; no real
campaign-history validation; no live director authorization), the removed-timer
fault shows the fake supervision path can still stop/wake on a cancelled
deadline, which must be fixed and re-verified before any live-adjacent step.
Simulated evidence cannot certify live behavior.

---

# POST-REPAIR VERIFICATION (authorized repair) — SUPERSEDES the verdict above

- **Verifier:** corvid; **same pass**, repaired tree; governing deadline
  2026-09-21T22:12:00Z (20 min per pass; 2400 s total initial+postrepair).
- **Verdict for the present tree:** **PASS**, subject to the provenance caveat
  below. The initial FAIL above stands as the record of the tree first reported.

## Recorded authorized change/version history (within this pass)

1. **Initial worker completion report** — kiln session
   `~/.config/agent-deck/acp-history/a79067ca-1790000758.jsonl` line 1800,
   `2026-09-21T21:03:19Z`, reported `src/driver.py 181f5b99…` and
   `tests/test_rehearsal.py ae8179b5…` (14 tests).
2. **Corvid verification FAIL** — `verification.md 2f0bbfb6…` (removed timer
   still stop+wake).
3. **Director authorized the one eligible repair** — same session line 1801,
   `~2026-09-21T21:58:41Z`: repair per `infra-recovery-decision.json`, pinned to
   that FAIL, scope `driver.py` + tests only, add removed/never-armed no-op
   tests, keep 14 rehearsal + 59 core passing, **do not touch `store.py` import
   drift** (director decision).
4. **Repair applied** — `driver.py` mtime `2026-09-21T21:58:50Z`,
   `tests/test_rehearsal.py` mtime `2026-09-21T21:58:55Z`.
5. **Repair completion report** — session line 1826, `~2026-09-21T21:59:19Z`,
   `driver.py 4726a583…`, `tests/test_rehearsal.py 3838b03a…`.

## Tree I verified (pinned present bytes)

| Artifact | sha256 |
|---|---|
| `src/driver.py` | `4726a583dc0a3405a271a656d61f3ebc59d1cfbde84a78f24e5ff101d55413c6` |
| `tests/test_rehearsal.py` | `3838b03a9ab066a9b12a8b2173cd0dd6685f7d62d3610518d9e6acd2b4936522` |
| `src/store.py` | `dafaeb333acc255a5c59de782e6f8be4c71a77322ac59247d232138639178242` (import-line drift, untouched per director) |
| other `src/*` | unchanged from the initial verification table |
| tree manifest (src, tests, fixtures, README, rehearsal-report, interface) | `cb46955304ed045d125fb7472350c3c56577d048a4ef6495414146111e95c6d5` |

**Provenance caveat (do not certify away):** the present output is **not** the
tree first reported at timely completion. The initial reported `driver.py`
(`181f5b99…`) and `tests/test_rehearsal.py` (`ae8179b5…`) differ from the present
`4726a583…`/`3838b03a…`. I verified the **present** tree only. I do not certify
that the initial timely tree equals the present output.

## Present-tree results

- `Driver.on_deadline` now checks `tid not in self.timer.armed` and returns
  `("no-op-not-armed", True)`; reproduced: `removed -> stops=0 wakes=0`, and
  `never-armed -> stops=0 wakes=0`. One-shot behavior for a genuine due deadline
  is unchanged (1 stop / 1 wake, second call `already-handled`).
- `PYTHONPATH=src python3 -m pytest tests/ -q` → **16 passed** (14 + removed-noop
  + never-armed-noop), `0.03s`.
- Pinned P3-r3 core suite → **59 passed**.
- All prior fault-matrix cases remain as in the table above (crash-before/
  ambiguous/after-ack, repeated completion/deadline/trigger, stale snapshot,
  legitimate rest + no auto-authorize, missing disposition
  `E_MISSING_DISPOSITION`, blocked verifier resume same attempt/no rerun, stale
  worker timer cannot expire verifier → `ACTIVE`).
- No live effects in `driver.py` (no subprocess/socket/signal/os.kill/
  os.system/popen/requests/urllib/time.sleep/while True); stdlib only.
- **Timeliness is not certified:** the reported worker completion 21:47Z is after
  the authorized 21:42:44Z; that is Tern's separate reconciliation.

Readiness remains **NOT ready** for a live fixture (no live adapter reviewed;
simulated evidence only; director live authorization absent).

---

## RETRACTION — CORRID version reconciliation (non-binding)

The "POST-REPAIR VERIFICATION … PASS" section above is **WITHDRAWN as
non-binding**: the current tree is **P4-repair-1 IN PROGRESS**, not a completed
repair. No kiln completion wake with per-file hashes had arrived, and CORRID
confirms no verification binding attaches to the in-progress tree until then;
a fresh pass binds bytes on completion.

**Verdict stands against the REPORTED pre-repair tree:** FAIL, bound to
`src/driver.py 181f5b99…`, `tests/test_rehearsal.py ae8179b5…`
(`verification.md 2f0bbfb6…` at the time of that pass). Both spans preserved:
session-history line 1801 and this record. No version overwritten; no repair or
relaunch from the verifier.
