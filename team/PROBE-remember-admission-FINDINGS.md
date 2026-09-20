# PROBE-20260912-REMEMBER-ADMISSION — findings

**Probe seat:** Aletheia (Alice), `worker-glm-dsh`
**Claim under test:** *a record written through the native `remember` path + admission
chain becomes SERVEABLE in recall (unlike capture's permanently-proposed output);
our confirmed records could migrate from CLI write to the native admission flow.*
**Verdict: NOT CONFIRMED — and the migration direction is harmful as shipped.**
**Method:** read-only over `/var/home/bmosher/perseus-build/src`; writes confined to
fresh scratch vaults under this worktree. Binary pinned `perseus-vault 2.23.2 (9c82920)`.
**Receipts:** `conductor-chat-glm-dsh/probe-20260912-remember-admission/receipts/`,
harness `probe.py`, `enum_attestation.py`.

---

## Answer in one line

The admission chain does **not** confer serveability on native `remember` records.
Worse: using it in the direction proposed **destroys** a serveable record.

## What was actually observed

### 1. Bare `remember` is non-serveable — same class as capture (CONFIRMS Assay)

    disposition: pending_approval   proposed: true   requires_review: true
    serveable: false
    provenance.reason: "missing_admission_envelope"
    db: status='proposed', source='agent'

Receipt: `04-armA-remember-no-admission.json`. This alone means the claim's stated
contrast ("unlike capture's permanently-proposed output") does not hold: the default
native `remember` output is *exactly* the permanently-proposed class.

### 2. Supplying an admission envelope does NOT make it serveable

With `source_trust: "authoritative"` and an admission envelope attached, the write is
still `proposed`:

    admission.authoritative: false
    admission.outcome: "proposed"   outcome_class: "pending_approval"
    admission.reason_codes: ["source_validation_required"]

Receipt: `07-armB-remember-with-admission.json`. The envelope is evaluated and then
**downgraded** to proposed because the `source_event_id` is not bound to a real journal
`admission_source` row.

### 3. `admission_decide` cannot rescue a bare proposal — Assay's error reproduced

Approving ARM A's proposal as an operator with an enforce-mode
`memory.admission.review` authority fails:

    "admission_decide candidate has no admission evidence"

Receipt: `04b-armC-admission_decide-approve.json`. This is **the same error string
Assay's native-capture probe hit** (`scripts/experiment_20260912_native_capture`). The
public `remember` path without admission produces candidates that the public admission
tool **cannot admit**. The tool is a dead end for its own output.

### 4. THE DECISIVE RESULT — native `remember` demotes an active record

The exact migration scenario the claim proposes, run against an active CLI-written
record and reproduced in two independent arms (`scratch-repro-*`):

| step | status | source |
|---|---|---|
| 1. CLI `write` (operator seed) | `active` | `cli-write` |
| 2. recall "how do we deploy" | **served** ("Docker Compose") | — |
| 3. native `remember`, same category+key | `active` -> **`proposed`** | `agent` |
| 4. recall again | **abstains** (`no_match`) | — |

Reproduced with **and without** an admission envelope — identical `active -> proposed`
demotion both times. Note `action: "updated"` in the response: it reports a successful
update while silently dropping the record out of the serveable set.

**This inverts the claim's premise.** The native admission flow is not an upgrade path
from CLI write; as shipped it is a *downgrade* path. Migrating confirmed records to it
would take every serveable record and make it invisible, with an `ok: true, action:
"updated"` receipt.

## Why the positive arm could not be completed (method limit, stated plainly)

The one route that should reach `remember_admitted_with_write_options` needs a journal
`admission_source` row attested with `PERSEUS_VAULT_ADMISSION_SOURCE_HMAC_KEY`. I set
that operator key on a scratch server and computed the HMAC-SHA256 over the payload the
source documents (`tools.rs:admission_source_attestation_payload`, key order and
`", "`/`": "` separators matched). The server rejected it:

    "admission_source source_attestation is invalid"

I verified (a) my HMAC is a correct RFC-4231 implementation, (b) the server *does* load
the key (absent key yields a different error: "…key is not configured"), and (c) 15
plausible canonicalizations x 2 keys all fail (`receipts/attestation-enum.json`). I did
not recover the exact byte form. **So the strongest positive statement I can defend is
mechanism-level, not empirical:** `tools.rs:1657` shows verified admission routing to
`db.remember_admitted_with_write_options` rather than `remember_with_options`. I did not
observe a record become `active` through this path, and I am not claiming it works.

## Sibling finding: capability vocabulary is a trap

A manifest naming `memory.write.propose` / `memory.write.commit` **denies every write**:

    "write denied: agent probe-operator lacks required capability memory.propose
     (manifest allows: memory.admission.review, memory.admission.source,
     memory.write.propose, memory.write.commit)"

The real nouns are `memory.propose`, `memory.commit`, `memory.read`. The error echoes the
manifest's own wrong noun back, so the mistake looks like a permissions problem rather
than a vocabulary problem. `authority_set` additionally fails with a bare
`EOF while parsing a value at line 1 column 0` if `capability_constraints_json` is
omitted, because it defaults to `""` and is fed to `serde_json::from_str`. Its `mode`
also defaults to `shadow`, which silently does *not* satisfy admission requirements.
Three separate footguns in one call, each with an unhelpful error.

## Recommendation (for the migration decision)

1. **Do not migrate confirmed records to native `remember`.** It demotes them.
2. **Keep CLI `write` as the activation path.** Verified directly: CLI write lands
   `status='active', source='cli-write'` and is served by recall (`scratch-migrate`).
   It needs no admission envelope at all.
3. If the team wants native admission, the precondition is a reachable, verified
   `admission_source` binding. Until a record can be observed going `proposed ->
   active` **through the public tools**, treat the native admission chain as inert —
   the same verdict as capture, one layer up.
4. Cheap follow-up with real value: confirm the admitted path via the crate's own unit
   tests, which do construct valid evidence. That closes the mechanism claim without
   the HMAC reproduction. Not done here (no `cargo`/`rustc` on this host).

## Honest failure-mode ledger

| Failure mode | Observed? |
|---|---|
| native remember non-serveable without admission | **yes** (ARM A) |
| admission envelope alone insufficient | **yes** (ARM B, `source_validation_required`) |
| admission_decide cannot admit bare proposal | **yes** (ARM C, Assay's error) |
| native remember demotes an active record out of recall | **yes**, reproduced x2 |
| recall silently abstains while reporting `active_memories: 1` | **yes** (diagnostic disagrees with `entities.status`) |
| attested journal path reachable | **not demonstrated** (method limit; 15 formats rejected) |
| record observed `proposed -> active` via public tools | **never observed** |

## Reproduction

    cd /var/home/bmosher/conductor-chat-glm-dsh/probe-20260912-remember-admission
    python3 probe.py                 # ARMs A/B/C + read surfaces -> receipts/
    python3 enum_attestation.py      # 15 canonicalizations x 2 keys vs attestation gate

Scratch vaults are disposable; delete `scratch-*` to re-run clean.
