# Perseus Vault Gen30 — MCP valid-time ablation, blocked

## Status

`blocked_valid_time_reset_by_admission_approval`. No longitudinal score is
published. Gen29 remains the authoritative Perseus longitudinal profile.

Gen30 asked one question: was the missing application-time axis in Gen29 caused
by the operator CLI `write` surface, or by Perseus's underlying bitemporal
model? The answer is neither. It is caused by the **admission approval step**,
which is the only documented way to make an agent-facing record serveable.

## The documented chain

Getting an agent-facing record from `remember` to serveable in v2.23.2 requires
five things, each discovered from the product's own refusals:

1. `perseus_vault_agent` — the agent must be registered, or the authority
   manifest is refused (`authority manifest agent_id must be registered`).
2. `perseus_vault_authority_set` in `enforce` mode for that agent and workspace,
   granting `memory.read`, `memory.write`, `memory.propose`, `memory.commit`,
   `memory.admission.review` and `memory.admission.source`. Without it review is
   refused; with too narrow a capability list the writes themselves are refused.
3. `PERSEUS_VAULT_ADMISSION_SOURCE_HMAC_KEY` configured on the server, or the
   approval refuses to sign its source attestation.
4. `perseus_vault_remember` carrying a full admission envelope. The envelope
   must satisfy `evaluate()`: `authorization_scope == workspace_hash`,
   `task_relevance_bps >= 5000`, not instruction-bearing, not
   contradicts-authoritative, `source_trust = authoritative`, `validated`, and a
   `source_event_id`. Its `actor_identity` must equal the writing `agent_id`.
5. `perseus_vault_admission_decide(decision="approve")` — an operator review.

Every field above is constant or derived from public coordinates. Nothing varies
with the content of the record, so this is a single uniform policy as required.
It is nevertheless a **different trust class** from Gen29: an agent-facing write
under an enforce manifest, reviewed by a registered operator principal, rather
than the operator CLI write whose authority the product grants implicitly.

## The measurement

One row, measured before and after each step in a single run:

| stage | status | `valid_from_unix_ms` | recallable |
|---|---|---|---|
| requested | — | `T − 200 days` | — |
| after `remember` | `proposed` | **`T − 200 days`** | no |
| after `admission_decide(approve)` | `active` | **approval instant** | yes |
| after a second `remember` | `proposed` | `T − 200 days` | no |

`remember` honours the retroactive application time exactly. Approval resets it
by the full 200 days. Re-ingesting restores it and simultaneously returns the
record to `proposed`, where recall cannot see it.

So the two states are mutually exclusive:

- **serveable** implies valid time collapsed onto the approval instant;
- **retroactive valid time** implies `proposed`, invisible to recall.

There is no documented path in v2.23.2 that yields both, and therefore no way to
give the ruler an independent application-time axis through this surface.

## Root cause

`models::Entity` has no `valid_from_unix_ms` or `valid_to_unix_ms` field. Those
columns exist in the schema and are written by the `remember` path, but the
struct that carries an entity through the rest of the codebase does not hold
them. `admission_decide` clones the stored entity, flips `status` to `active`,
sets `verified`, and re-persists it — and the application-time columns are
rewritten to the write default.

Any code path that reads an entity, mutates it and writes it back will lose
application time the same way. This is a product observation from one version,
reported as such: it is not scored, and no claim is made about other releases.

## Why this is a stop rather than a result

Scoring the profile in this state was possible and would have been misleading.
Every record would carry `valid_from` equal to its approval instant, the two
time axes would be collinear again, and the failure profile would land close to
Gen29's — but for an entirely different reason. Publishing that as the
"MCP valid-time ablation" would have reported a one-variable experiment whose
variable was never actually established.

Gen29 is untouched and remains the authoritative operator-write profile: three
identical repetitions, zero future leakage, exact provenance, both
historical-belief cases passing on the transaction-time axis.

## What was preserved

The unrelated synthetic preflight is reproducible with
`scripts/probe_perseus_gen30_admission`, which writes
`results/perseus_vault_gen30_mcp_valid_time/summary.json`. Focused tests lock
the frozen ruler and the Gen29 query adapter contract, assert Gen29's published
result is unchanged, assert Gen30 publishes a blocker and no invented score, and
assert the mutual exclusion above.

No `longitudinal-v1` name, value, query phrasing, ID or transition label reached
the probe. No explicit `supersede`, update, delete, retract, invalidate, archive
or maintenance call was made. No reader, LLM, ChatGPT sidecar or inference-server
GPU was used.

## Verification

Full suite: 110 passed, one existing warning, with `node` on `PATH`.
