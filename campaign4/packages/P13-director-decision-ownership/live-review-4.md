# P13-live-4 — independent live review (corvid)

- **Action:** `P13-livereview-4`, owner corvid, `20:04:39Z`–`20:14:39Z`.
- **Inputs:** `live-review-receipt-4.json`, preserved `live-p13l4/`; **43/43 receipt
  hashes match**.
- **Verdict: PASS** — independently bound from DB/claims/transport/receiver
  records/private ledger, not result labels. Proof boundaries and accelerated
  timings stated; production unmodified.

## Actual evidence (independent bind)

- **Runs:** 8/8 driver rows PASS, rc 0; start `19:59:12Z`, end `20:03:43Z` (within
  grant). **Cleanup** `20:03:43Z` verified: exact 4 IDs absent, scope
  `inactive/dead`.
- **Claim chain:** transport shows worker dispatch `19:59:33Z`, verifier dispatch
  `19:59:40Z`, decision notice `19:59:50Z` (real wake); archived
  `claims/ex-Dp13l4-{w1,v1}.json` present.
- **Incident DB** `loop-pkg:Dp13l4`: `step=closed`, `verdict=PASS`,
  `decision.rungs = {0: sent 20:00:50Z, 1: sent 20:01:30Z, 2: sent 20:01:30Z,
  reraise: sent 20:03:00Z}`, `attempts = {0:1,1:1,2:1,reraise:1}`,
  `ack.by=claude` (`cap_sha256`), `resolved 20:03:05Z`, `resolve_actions
  ["c2bb65c5915a ok"]`.
- **Receiver records** `D_RECORD/U_RECORD.jsonl`: each holds the probe nonce
  (director `7ff02734…`, duty `91b98f5c…`) **and** the DECISION OVERDUE notice,
  keyed `p13l4-director`/`p13l4-duty` — proof of real receipt through the real wake.
- **Private escalation ledger** (private HOME): `E-1` (20:01:30Z, key
  `c2bb65c5915a`, `source: notify-claude`), `E-2` (20:03:00Z, **same key**,
  re-raise), then the append-only **resolution** record
  `{ack:"R-D-Dp13l4-Dp13l4-v1", resolve:"c2bb65c5915a", incident, by:agent-loop}`.
  This is the real pinned `notify-claude` + private ledger (labelled), **stub
  ticket** — no Signal.
- **Watcher:** `DECIDE PASS "resolved; private watcher quiet"` — the resolved key
  does not page. **Restart:** `LIVE PASS` reports no duplicate stages; `attempts`
  all 1 and one resolution.

## Proof boundaries / production

- Director/duty are **passive receiver doubles** (real `acp-worker` + engine; no
  tools/exec) — **no human/model compliance claim**; worker/verifier are **real**
  `acp-go`/`acp-go-deepseek`. **Accelerated fixture timings** (rungs `0/+40`, 60 s
  decision window); **no production 0/300/600 timing claim**.
- **No real Signal, production unmodified:** installed `agent-loop` `97a57db1…`,
  `escalation-watch` `8968ed55…`, `agent-loop@campaign4.service` active; the run
  used a private HOME/ledger. Literal ack refused, capability ack bound to the
  incident (per `ACK PASS` and the DB ack).

**PASS**; returned to Tern for the promotion decision (promotion10 held). No
edit/retry/promotion by corvid.
