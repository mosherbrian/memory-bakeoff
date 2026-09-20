# ROW 6 RECEIPT — admission-path unit tests (container run)

**Row:** `team/QUEUE.md` #6 — "Admission-path unit-test confirmation"
**Seat:** Aletheia (Alice), `worker-glm-dsh` · **Date:** 2026-09-12 · **Turn:** 1, bounded
**Verdict: PASS — 37 test executions, 36 unique, 0 failed, 0 ignored.** The admitted
path is live at unit-test level, and it also yielded the empirical
`proposed -> active` observation the earlier probe could not reach.

---

## 1. Provenance of the run

| item | value |
|---|---|
| source | `/var/home/bmosher/perseus-build/src` (perseus-vault 2.23.2, commit `9c82920`) |
| toolchain | `rustc 1.97.1 (8bab26f4f 2026-07-14)`, `cargo 1.97.1 (c980f4866 2026-06-30)` |
| container | `docker.io/library/rust:1.97.1-bookworm` (already present locally) |
| image digest | `sha256:408fe88047cef61a2087653b0c5255fa51c0f2d6d94ddedd7a2562a9b91a46f6` |
| podman | 5.8.2 |
| apt deps | `libsqlite3-dev pkg-config` (ok) |
| env | `GIT_HASH=9c82920` |
| profile | `--release` (reuses the warm release dep cache in `src/target`) |
| test binary | `target/release/deps/perseus_vault-485497d610ba0273` (same binary for all filters) |
| compile | 3 × `Finished release profile ... in ~38s` (warm cache; test-harness relink per invocation) |
| run cost | container CPU only; no metered model spend inside the run |

Per the row's unblock note, the host has no native cargo/rustc by design; the run
used the proven container recipe from `/var/home/bmosher/perseus-build/build.sh`,
with `cargo build --release` adapted to `cargo test --release --bin perseus-vault
<filter>`. `libsqlite3-dev`/`pkg-config` were installed in-container exactly as
`build.sh` does (rusqlite is also `features=["bundled"]`).

## 2. Exact command

```bash
cd /var/home/bmosher/perseus-build
podman run --rm \
  -v "$PWD/src":/app:z \
  -v "$PWD/cargo-home":/usr/local/cargo/registry:z \
  -w /app -e GIT_HASH=9c82920 \
  docker.io/library/rust:1.97.1-bookworm \
  bash -c 'apt-get update -qq && apt-get install -y -qq libsqlite3-dev pkg-config >/dev/null
           for f in admission admit unverified_write_cannot; do
             cargo test --release --bin perseus-vault "$f" 2>&1
           done'
```

Filter choice: `admission` and `admit` are not substrings of each other, so both
are required; `unverified_write_cannot` catches the one trust-axis test whose
name contains neither. Together they cover every `#[test]` in
`src/trust_admission.rs`, the `tools.rs` admission handlers, and the `db.rs`
trust-axis tests.

## 3. Results

| filter | passed | failed | ignored | filtered out | result |
|---|---|---|---|---|---|
| `admission` | 29 | 0 | 0 | 1299 | `ok` |
| `admit` | 7 | 0 | 0 | 1321 | `ok` |
| `unverified_write_cannot` | 1 | 0 | 0 | 1327 | `ok` |
| **total executions** | **37** | **0** | **0** | — | **PASS** |

36 unique tests (`trust_admission::tests::trusted_authoritative_source_is_admitted_only_in_scope`
matches both `admission` and `admit`, so it ran twice). No failure, no panic, no
`error[E...]`; all compile diagnostics were pre-existing warnings only.

### Tests executed

`trust_admission` module (8): `untrusted_instruction_is_quarantined_and_cannot_activate_later`,
`trusted_authoritative_source_is_admitted_only_in_scope`,
`contradiction_escalates_without_deleting_history`, `missing_scope_abstains_fail_closed`,
`revocation_is_hash_only_and_preserves_record_identity`,
`decision_digest_rejects_post_issue_evidence_mutation`,
`four_outcome_classes_are_stable_and_hash_covered`,
`raw_payload_fields_are_not_part_of_evidence_shape`.

`db` (8): `verified_admission_write_lands_verified_on_the_trust_axis`,
`unverified_write_cannot_claim_a_verified_trust_state`,
`generic_journal_cannot_mint_admission_source_evidence`,
`semantic_index_text_omits_admission_envelope`,
`history_index_text_omits_admission_envelope`,
`grounding_admit_is_fail_closed_on_missing_entity_and_short_content`,
`ingest_containment_replay_readmits_changed_doc`,
`ingest_containment_replay_readmits_archived_coverage`.

`tools` admission handlers (18): `remember_admission_quarantines_untrusted_content_at_write_boundary`,
`public_admission_source_requires_strict_source_authority`,
`admission_source_requires_server_attestation_even_with_authority`,
`admission_decide_requires_workspace_and_strict_review_authority`,
`remember_admission_terminal_dispositions_commit_reject_quarantine_defer`,
`admission_quarantine_retire_purge_roundtrip`,
`remember_admission_suppression_does_not_write_memory`,
`remember_without_admission_is_an_explicit_hash_only_proposal`,
`unverified_admission_is_proposed_and_not_authoritative`,
`admission_source_event_is_transport_stamped_and_digest_bound`,
`forged_authoritative_admission_is_downgraded_without_bound_source_event`,
`admission_workspace_mismatch_is_rejected_before_any_mutation`,
`pending_admission_review_has_distinct_approval_and_rejection_audit_outcomes`,
`admission_actor_identity_and_kind_mismatch_is_rejected`,
`unadmitted_user_attribution_is_rejected`,
`admission_source_attestation_accepts_uppercase_hex_encoding`,
`admitted_write_rejects_post_validation_lossy_body_mutation`,
`admission_decide_records_failed_completion_after_completion_write_error`.

`mcp` (1): `admission_decide_requires_captured_client_identity`.
`injection_lint` (1): `clean_bodies_are_admitted`.

## 4. What this confirms (with citations)

1. **The admitted write lands on the trust axis.** `db.rs:33645`
   `verified_admission_write_lands_verified_on_the_trust_axis` passes: the same
   body that a forged self-label stores as `candidate`/`proposed`
   (`db.rs:33617`) is stored `epistemic_state = "verified"` through the trusted
   admission write. Fail-closed both ways.
2. **The full public terminal-disposition path works.** `tools.rs:23688`
   `remember_admission_terminal_dispositions_commit_reject_quarantine_defer`
   exercises `handle_remember` four ways against a real bound source event:
   `admission.outcome == "admitted"` and the entity persists; `suppressed` writes
   nothing and does not quarantine; `untrusted` quarantines sealed; `trusted`
   without authority defers to `proposed`.
3. **`proposed -> active` through the public tools is observed.**
   `tools.rs:24955`
   `pending_admission_review_has_distinct_approval_and_rejection_audit_outcomes`
   writes a `trusted` (non-authoritative) candidate, then approves it with
   `handle_admission_decide` and asserts `approved["status"] == "active"` and the
   stored entity `status == "active"` with an `authoritative` evidence envelope.
   This is exactly the observation the 2026-09-12 probe logged as
   *"never observed"*.
4. **The attestation gate is real but reachable.**
   `tools.rs:24658`, `:23547`, `:23623`, `:24872`, `:25742` cover transport
   stamping, strict source authority, server attestation, forged-source
   downgrade, and uppercase-hex acceptance.

## 5. What this does NOT change

The probe's public-tool findings stand and are not contradicted:

- bare `remember` without admission stays `proposed`/non-serveable
  (`tools.rs:24553`);
- a `trusted` envelope alone stays `proposed` (`tools.rs:24608`);
- `admission_decide` still cannot admit a candidate with *no* admission evidence;
- the `active -> proposed` demotion reproduces.

What the unit tests add is the missing positive control: **when valid evidence is
constructed, the admitted path activates a serveable record.** The probe lacked
that control, not because the gate is unreachable, but because of two client-side
canonicalization bugs (next section).

## 6. Incidental finding — the probe's attestation dead-end was a harness bug

The earlier probe reported the attested journal path as *"not demonstrated
(method limit; 15 formats rejected)"*. Reading `tools.rs` against the vendored
serde_json explains it. The verified payload is built by
`admission_source_attestation_payload` (`trust_admission.rs:394`,
`tools.rs:5149`) with the `json!` macro and `.to_string()`:

- **`serde_json`'s default `CompactFormatter` emits no whitespace** — `b","`
  between keys, `b":"` between key/value (`serde_json-1.0.150/src/ser.rs:1884`,
  `:1910`, `:1937`, vendored in `perseus-build/cargo-home`). The probe's
  `attestation_payload` used `separators=(", ", ": ")` and its docstring asserted
  the opposite (`probe.py:47-48`), so ARM B's HMAC could never match.
- **`serde_json::Map` is a `BTreeMap` here** — `Cargo.lock` lists serde_json
  deps `itoa, memchr, serde, serde_core, zmij` with no `indexmap`, so
  `preserve_order` is OFF and the payload keys serialize alphabetically.
- The 15-variant enumeration (`enum_attestation.py`) did try compact forms, but
  computed the HMAC with `requester = "op-alpha"/"op-beta"` while the transport
  stamps `requesting_agent_id` from `clientInfo.name` = `"probe-operator"`
  (`mcp.rs:222`, `:725-735`; `probe.py:37`). Right payload, wrong requester.
- The record digest has the same class of bug: `canonical_admission_body_digest`
  (`tools.rs:977`) re-serializes compact before hashing, so the probe's
  `sha256(json.dumps(body))` (space after `:`) never matched.

**Corrected public-tool run:** `probe2_admitted.py` (this worktree) recomputes
both over compact/sorted bytes and drives
`perseus_vault_journal(admission_source)` then `perseus_vault_remember(admission)`
through the real MCP surface. Observed
(`receipts/11-public-admitted-path.json`):

    journal                : id jrn-5ea9d2fa485f (no isError)
    remember admission     : outcome "admitted", authoritative true,
                             reason "authorized_authoritative_source"
    disposition / serveable: "save" / true
    stored entity status   : "active"
    recall                 : returns the record

This closes the positive arm the probe could not complete. The two whitespace
bugs are the entire cause of the earlier "unreachable" reading; the admission
chain is not inert.

## 7. Reproduce

```bash
# unit-test receipt (container, per row 6)
cd /var/home/bmosher/perseus-build
podman run --rm -v "$PWD/src":/app:z -v "$PWD/cargo-home":/usr/local/cargo/registry:z \
  -w /app -e GIT_HASH=9c82920 docker.io/library/rust:1.97.1-bookworm \
  bash -c 'apt-get update -qq && apt-get install -y -qq libsqlite3-dev pkg-config >/dev/null && \
           cargo test --release --bin perseus-vault admission'

# corrected public-tool positive arm (host, release binary already built)
cd /var/home/bmosher/conductor-chat-glm-dsh/probe-20260912-remember-admission
python3 probe2_admitted.py
```

## 8. Artifacts

| artifact | path |
|---|---|
| this receipt | `probe-20260912-remember-admission/ROW6-ADMISSION-UNIT-TEST-RECEIPT.md` |
| raw cargo-test log (2639 lines) | `probe-20260912-remember-admission/scratch-diag/cargo-test-row6.log` |
| corrected public-tool receipt | `probe-20260912-remember-admission/receipts/11-public-admitted-path.json` |
| corrected-run harness | `probe-20260912-remember-admission/probe2_admitted.py` |

Raw log sha256: `858bde15eb9716db80ad345999d9e5e5d3217ad0d7598f480db9765142d6cd69`
