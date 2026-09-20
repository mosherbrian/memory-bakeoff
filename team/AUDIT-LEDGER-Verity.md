# AUDIT-LEDGER — Verity (worker-glm-3)

Append-only audit ledger for this seat. Filing rule (self-adopted 2026-09-12,
after the S5-notes gap): entries land here **same turn**, signed, with
receipts this seat actually checked — artifact-level where load-bearing,
hash-pinned where reported. Entries record corrections and their consequences
for the record; they do not edit frozen documents. Annotation policy for
frozen docs belongs to the conductor.

---

## Entry 001 — recorded finding CORRECTED: admission chain is not inert (2026-09-12 13:32)

**Source:** GiLMore dispatch (audit-ledger item, no unblinding); receipt
`team/PROBE-row6-admission-unit-tests.md` (Aletheia/Alice, QUEUE row 6,
closed 13:28).

**The correction.** The record has said, in several places, that the native
admission chain was treated as inert and the attested-journal route was
"unreached / not demonstrated (15 formats rejected)," with `proposed →
active` never observed through public tools. Alice's row-6 run shows the
unreachability was **probe-harness bugs, not the system**:

1. Attestation HMAC computed over pretty-printed JSON (`(", ", ": ")`
   separators) while the vault builds the payload compact (serde_json
   `CompactFormatter`);
2. Payload key order unmodeled — serde_json's map here is a `BTreeMap`
   (no `preserve_order`), so keys serialize alphabetically;
3. HMAC computed with the wrong requester identity (`op-alpha`/`op-beta`)
   while the transport stamps `requesting_agent_id` from
   `clientInfo.name` (`"probe-operator"`);
4. Body digest hashed over pretty JSON; the vault re-serializes compact
   before hashing.

With the harness corrected: **public-tool run observed journal acceptance →
`remember` admission (`outcome:"admitted"`, `authoritative:true`,
`disposition:"save"`, `serveable:true`, `proposed:false`) → stored entity
`status:"active"`, `epistemic_state:"verified"` → recall delivers the
record.** Exactly the observation the earlier probe logged as "never
observed."

**What this seat verified, and how:**

- Raw unit-test log sha256 `858bde15eb9716db80ad345999d9e5e5d3217ad0d7598f480db9765142d6cd69`
  — matches the receipt's stated hash (log itself hash-pinned, not re-run;
  the 37/0 PASS is Alice's receipt).
- `receipts/11-public-admitted-path.json` **read at artifact level this
  seat**: the full chain above is in the artifact, internally consistent
  (record digest `09a1926f…` identical across body/provenance/admission;
  payload compact, alphabetically ordered, requester = transport stamp —
  i.e., precisely the three corrected bug classes). The load-bearing claim
  of the correction is artifact-verified, not summary-trusted.
- Probe-scoped workspace (`ws-probe-admitted`); no live-arm or trial-vault
  contact; no S6 implications; S4 materials untouched (no unblinding).

**What STANDS (per receipt §5, checked):** bare `remember` without
admission stays `proposed`/non-serveable; a trusted envelope alone stays
`proposed`; `admission_decide` remains fail-closed on missing evidence; the
`active → proposed` demotion reproduces. **Assay's non-delivery /
status-withholding finding is unaffected** — the correction shows the gated
path works when valid evidence is constructed; it does not soften the
default-path withholding. The two findings compose.

**Consequences for the record (flagged; decisions belong to conductor/Brian):**

1. **CAMPAIGN-1 guardrail 2's premise is corrected mid-window.** Its own
   wording was conditional — "treated as inert UNTIL a record is OBSERVED
   going proposed→active through public tools." That condition is now met.
   The frozen campaign-1 instruments do not move: guardrail 1 (CLI write
   remains the live arm's activation path) binds exactly as frozen for this
   window; nothing un-freezes mid-window.
2. **Citation hygiene:** any future citation of "never observed," "15
   formats rejected," or "chain is dead" carries this entry as its
   correction pointer. `PROBE-remember-admission-FINDINGS.md`, ROLES.md,
   and CAMPAIGN-1's guardrail text are historical records; whether to
   annotate them in place is the conductor's call.
3. **Campaign-2 input, one line, not direction-setting:** the un-gating
   premise behind campaign-C (upstream repair) now has an observed
   mechanism behind it. That changes the cost/benefit Brian was asked to
   weigh; worth re-presenting at window end with this receipt attached.

**Process note, on the record:** the original probe stated its method limit
honestly, and the record held — the correction came from running the very
tests the record said were blocked, once the toolchain landed. This is the
second campaign finding corrected by constructing a missing positive
control (the row-6 answer_id gap was the first). Standing lesson for this
seat's own instruments: a stated limit should name its own falsifier; a
negative result is a deliverable, an un-falsified negative is half of one.

— **Verity** (worker-glm-3), entry 001. Receipts, or it didn't happen.

---

## Entry 002 — Sprint 2 reviewer pulse (2026-09-14)

Three small reviewer deliverables, all $0 read-only, all blind-safe (no
packet/fire-log content opened, no tallies quoted):

1. **S4 B6 encounter log** (`team/VERITY-S4-B6-ENCOUNTER-LOG.md`, QUEUE row
   37, verifier fsync): EXPOSED — read BOARD.md:412 + :557 during the Sprint
   2 origination sweep. Recused from blind rulings over the exposed span;
   consequence logged: no unexposed rater remains on the metered lane
   (Corvid recused, Assay row-1-exposed). Available for post-unblinding
   audit, A1 review, citation-rule check.
2. **A1 watchdog design review** (`team/VERITY-A1-DESIGN-REVIEW.md`): PASS as
   amendment. Mechanism (timeout→suspect→respawn, no blind mutation retry,
   recall preserved) is sound defense-in-depth; diagnosis superseded (the
   "serve deadlock" was the client chunk bug, fixed by A2 v3 fbd3149).
   Residuals: no respawn backoff/cap; WINDOW-OPENING A1 receipt uncommitted.
3. **Citation-rule Rev 2 rule check** (`team/VERITY-CITATION-RULE-CHECK.md`):
   PASS with two editorial tightenings (T1: grade line names author+date;
   T2: trigger vocabulary of three shapes + `other:`). Gate operational and
   testable; no conflict with Corners 7b/8 or charter. Ready for GiLMore nod.

Standing position unchanged: freeze-checks, audit ledger, post-unblinding
audit — no blind ratings over exposed spans.

— **Verity** (worker-glm-3), entry 002. Receipts, or it didn't happen.
