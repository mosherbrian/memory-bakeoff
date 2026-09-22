# C4 reviewed-regressions — ten-row evidence matrix

- **Action:** `C4-review-regressions-1` (corvid, diagnostic ≤40 m), start
  `2026-09-22T20:27Z`, deadline `21:07Z`.
- **Authorization:** `CODE-REVIEW-DISPOSITION-20260922.md` @ `abb0f90`;
  input `CODE-REVIEW-20260922.md` @ `c464709`.
- **Frozen pins:** P5-r2 `80092f9` (`store.py` `dafaeb33…`, `ingress.py`
  `c9327f85…`, `lifecycle.py` `7ebaf466…`); P6-r9 `f1d7c86`
  (`r3harness/harness.py` `d7b4e517…`, `case_entry.py` `9a1bb23c…`).
- **R11 candidate comparison:** `store.py`/`lifecycle.py`/`ingress.py`
  (`dafaeb33`/`7ebaf466`/`4d12429f` copy) and `harness.py` (`d7b4e517`) bytes
  present; `case_entry.py` is `701a383e…` (differs), but the cited `wait_s:8`
  and `datetime.now` sites remain. All ten defects are present in the current
  R11 local copy.
- **Probes:** `campaign4/code-review-regressions/probes/` (private temp DBs,
  fake clock, no real timer/socket/service). No source edited.
- **Priority order:** 2,5,6,7,10 then 1,3,8,9,4.

| # | finding | status | runtime evidence |
|---|---|---|---|
| 2 | rolled-back `record_terminal` leaves verdict in `seen_events` | **REPRODUCED** | probe_core.py |
| 5 | atomic decide/hold dropped with a non-terminal-maker event | **UNTESTED** | attempted; see below |
| 6 | second DECIDE overwrites first disposition | **REPRODUCED** | probe_core.py |
| 7 | `decide`+`grant_ref` accepted, grant silently dropped | **REPRODUCED** | probe_core.py |
| 10 | deadlines compared as text | **REPRODUCED** | probe_core.py |
| 1 | host timer callback checks wrong qid (`P6F` vs `P6C`) | **REPRODUCED** | c4_probe1.py |
| 3 | verifier wait measured from worker dispatch; `verify_window_s` unread | **REPRODUCED (source)** | grep/line pins |
| 8 | first worker wait keeps the short 8 s slice (harness run-fixture alone) | **REPRODUCED (source + r9 baseline runtime)** | r9 FV-W baseline |
| 9 | reattach decision uses host clock, ignores `live_stop_utc` | **REPRODUCED (source)** | line pins |
| 4 | one slow normal turn = synthetic failure row + success row | **REPRODUCED** | c4_probe4.py |

## Row detail

### #2 REPRODUCED
Command: `python3 probes/probe_core.py` (P5-r2 `Store.record_terminal`).
Assertion: after a duplicate decide event forces rollback, the verdict id is in
`seen_events`, the verdict row is absent, and a retry with a *fresh* decide
still raises `E_DUP_EVENT`. Actual: `first=E_DUP_EVENT
seen_after_rollback=True persisted=0 retry_with_fresh_decide=raised
E_DUP_EVENT`. Same-store retry cannot persist the verdict until reopen.

### #5 UNTESTED
Attempted the two described public forms against a CHECKING package:
`append({type:"accept"}, atomic={"decide":…})` → `E_PHASE_MISMATCH` (accept does
not land terminal); `append({type:"accept"}, atomic={"hold":…})` →
`E_FORGED_ATTRIBUTION`. I could not construct a public event type that lands a
terminal phase while being absent from `TERMINAL_MAKERS`, which the store
condition (`store.py:95-99`) requires for the silent drop. Exact unresolved:
which concrete public event/type reaches the drop (the review's `accept`-on-
COMPLETE path is blocked earlier by `apply()`'s `E_TERMINAL`). Reported honestly
rather than guessed.

### #6 REPRODUCED
`lifecycle.apply` DECIDE twice on a COMPLETE state (no `disposition is not None`
guard, unlike `DECISION_TASK` at `lifecycle.py:370`): disposition reason
`'first' -> 'second'`. First director decision overwritten; replay reproduces.

### #7 REPRODUCED
`ingress.append(verify_pass, atomic={"decide":sub,"grant_ref":"g-forged"}, …)`
accepted; disposition committed and `grant_ref` silently stripped
(`ingress.py` strips it before `_ATOMIC_FORMS`). Actual: `decide+grant_ref
accepted; disposition set=True`.

### #10 REPRODUCED
`lifecycle.apply` PUBLISH with `deadline="2026-09-22T22:00:00+02:00"`
(=20:00Z) and `now="2026-09-22T20:30:00Z"`: accepted (phase CHECKING) although
the instant is 30 min past the deadline — text comparison `now > deadline`
(lexicographic) says not expired.

### #1 REPRODUCED
`_arm_host_timer` callback argv contains `--db`, `timer-callback`, `--timer`,
`--action` and **no** `--qid-cb` (`harness.py:340-342`); `timer_callback`
defaults `qid="P6F"` (`:95`) while the case runs as `P6C` (`case_entry.py:999`).
Actual with a live P6C flight: default-qid callback →
`{"decision":"no-op-no-current-action"}` (P6C **not** interrupted);
`qid="P6C"` → `{"decision":"interrupted"}`.

### #3 REPRODUCED (source)
`esc_deadline = t0 + escalation_window_s` where `t0` is the **worker** dispatch
(`harness.py:530-534`), used as the verifier bound (`:750`); `verify_window_s`
is only written into the manifest (`:255`) and the config (`case_entry.py:474`)
and never read in the wait logic (grep: no read site). Runtime not re-run in
bound; source path is unambiguous.

### #8 REPRODUCED (source + runtime)
`harness.run_fixture` uses `until_utc=None` unless `resume` (`harness.py:695-702`),
so the first wait is the 8 s slice (`case_entry.py:476 wait_s:8`); only the
`case_entry` wrapper reattaches. Runtime corroboration: the r9 baseline
`failed-verification` (no reattach) with an 18 s worker returns rc3
`E_NO_ONSET` — the harness slice misses a valid slow turn.

### #9 REPRODUCED (source)
`case_entry._grant_remaining_s` uses `datetime.datetime.now(timezone.utc)`
(`case_entry.py:1169`, r11 copy) and the reattach path does not consult
`live_stop_utc`; only reason text differs when live stop has passed. Source
path present; runtime not re-run.

### #4 REPRODUCED
`c4_probe4.py` runs the r9 positive-handoff with an 18 s worker. `latency.jsonl`
has **3** rows: `p6c-h1w no-end-failure`, `p6c-h1w transition-committed`,
`p6c-h1v terminal-rest`. A single normal delayed completion contributes a
synthetic failure row to the same file/denominator.

## Effect

Ten findings reviewed: **9 REPRODUCED** — runtime evidence (#1,#2,#4,#6,#7,#10)
or source with corroboration (#3,#8,#9) — and **1 UNTESTED (#5)**. No source fix,
no live effect, no fixture setup failure conflated with a defect. Failing
regressions supplied for a separately admitted repair contract. Returned to
Tern.
