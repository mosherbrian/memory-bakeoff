# P13 repair 1 — independent recheck (corvid)

- **Action:** `P13-repairreview-1`, start `05:41:31Z`, deadline `06:01:31Z`.
- **Claim:** `repair-1-claim.json` (`baa6a462…`) on the admitted amendment +
  amended checklist; release source `df5e6fc627b8`, binary
  `47f69dfdeb8b0d17472d871b68dfdfa8270e3421997a03f5d1c6929c8a818ec1`; test-only
  head `6a44c76`.
- **Verdict: PASS on the six-gap repair scope.** Live 20 m and promotion remain
  held; no install/live effect.

## Pins / integrity

- **384 bound files** verify; the four `adapter:`/`baseline:` aliases resolve and
  match (`adapters/escalation-watch df51a1f4…`, `adapters/escalation-resolve
  fdf49d0b…`, `adapters/watch_test.sh 103ece85…`, installed baseline
  `8968ed55…`).
- `internal/core`, `internal/py`, `conformance/cases`: **0 diff** `8ad12b86..df5e6fc`.
  Test-only head `6a44c76` differs from the release only in
  `decision_p13_test.go` (+14 lines) — **production bytes identical**.
- Shipped conformance **125/125, 1751 steps** on `47f69dfd`; `go test ./...` ok;
  mutation **176/176 caught** (valid applied aggregation, `mutate-go-parallel-final`).

## Six-gap recheck

1. **Campaign policy (finding 1):** `decision_policy "required"` refuses a config
   unless the ladder is exactly director +0 s, duty +300 s, external rung +600 s
   with **absolute** command + ledger + kind + resolve_cmd, and responders
   (`decision.go:121-167`). Prospective
   `plans/campaign4-decision-config.prospective.json` is **not installed**; omitted /
   10 malformed / full policy tested; `LoadConfig` refusal. Generic default stays
   director + duty +300 (portable). **Addressed.**
2. **Bounded exec retry (finding 2):** `MaxRungAttempts=2`, `Attempts[rung]` persisted
   **before** each effect, then `unresolved` + one director notice (D3 key);
   reopen keeps the count (`decision.go:317-344`). **Addressed.**
3. **Ambiguous crash repeat (finding 3):** an `"intended"` attempt with a durable
   ledger record of the key since then is recorded **sent with that receipt** and not
   re-sent; seat rungs keep the D3 labelled repeat; a re-raise has its own attempt
   counter. **Addressed.**
4. **Responder identity (finding 4):** `decision-ack` requires `--cap-file`: 256-bit
   secret, mode 0600 in `<db>.caps` (0700), **digest only** in the loop, 15 min
   expiry, incident/responder-bound; `subtle.ConstantTimeCompare`
   (`decision.go:500-530`). Refuses literal `claude` without proof, guessed, wrong,
   stale, expired, other-incident, withdrawn, deadline >15 min. Same-user trust
   boundary stated; no secret in argv/notice/ledger/status/claim/git. **Addressed.**
5. **Watcher resolution (finding 5):** **private** `adapters/escalation-watch` +
   `adapters/escalation-resolve` (append-only record `{t, ack:"R-"+incident,
   resolve:KEY, incident, by, note}`); a decision writes **one** resolution record per
   key; records at/before it **do not page**; a later record **pages**; an ack alone
   never resolves; installed watcher/timer/config/production ledger untouched.
   `watch_test.sh` **22/22**, including **5 non-P13 ledgers byte-identical** to the
   installed watcher. **Addressed.**
6. **Mutants (finding 6):** **176/176** valid caught; the initial survivors, invalid
   and unapplied mutants re-anchored; 12 new; serial/parallel equivalence identical.
   **Addressed.**

## Independent evidence (my runs)

- Conformance 125/125 on `47f69dfd`; `go test ./...` all ok; mutation 176/176.
- `watch_test.sh` **22/22**: recurrence→decision→**no page**, recurrence→unresolved→
  **page**, record after resolution pages, ack-alone nonterminal, malformed key
  refused, installed `escalations --pending` works with a resolution record.
- Stopped-run witness: run **killed** after both packages entered decision
  (0 run processes); only the real decision timer + outside check acted; ladder
  0/300/600 fired; caps dir 700 / files 600; literal/guessed/cross-incident acks
  rc 1; capability acks rc 0; acks expired and re-raised the **same key**; Q2 decided
  → resolution; private watcher **paged Q1 only** (Q1 1 line, Q2 0); cleanup 0 units.

## Residuals / coverage (honest)

- **Stopped-run coverage:** the witness **killed** the run (run not running), not the
  `agent-loop stop` **marker** path; the independent timer/outside-check mechanism is
  proven when run is down, but the intentional-stop-marker-specific "quiet absent
  obligations" behaviour is not separately witnessed. Classified as coverage, not a
  defect.
- Same-user trust boundary for capability files (stated); installed
  `escalations --pending` still lists the original unacked records of a resolved key
  (only **paging** is suppressed); installed watcher lists a record as both stale and
  recurred (kept); `escalation-resolve`/private watcher take effect only after a
  **signed promotion** of their exact hashes; the prospective config refers to the
  installed resolve path.
- **Live 20 m and promotion are outside this round** and need Tern's signatures.

**PASS on the repair scope**; returned to Tern immediately. No edits/install/live by
corvid.
