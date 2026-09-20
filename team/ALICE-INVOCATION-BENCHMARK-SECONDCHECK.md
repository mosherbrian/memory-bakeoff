# Second-seat check — invocation-benchmark §11 verification (Assay) + the schema mismatch is broader than C1

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 15:35 UTC · **Cost:** $0, static read, one turn · **Trigger:**
standing second-check of `team/ASSAY-INVOCATION-BENCHMARK-VERIFY.md`. Read-only.

**Subject:** `team/DESIGN-INVOCATION-BENCHMARK.md` §3 (adapter schema,
lines 207–236), §4.2/Addendum B3 (lines 530–579), §5 (controls).

## Verdict

**AGREE with all six §11 items, with C1 and C2 confirmed.** **One extension that
widens C1:** the schema/contract mismatch is not limited to the persistence
clause. B3's **primary** predicate needs `channel` and `seq`, and **§3 declares
neither** — so `FBMR_topic` itself is not computable from the declared adapter
schema, not just `CBMR`/`FBMR_persist`.

## C1 extension — B3 fields vs §3 fields

| B3 predicate field (lines 543–549) | §3 schema (lines 207–236) |
|---|---|
| `e.channel == "memory"` | ✗ absent (`integration_mode` is an arm label, not a channel) |
| `e.mechanism == "proactive_topic"` | `kind` (≈, but not the B3 name list) |
| `e.reasons` (token array) | `reasons` ✓ |
| `covering_id(M) ∈ e.record_ids` | `delivered_ids` (≈, different name) |
| **`e.seq < action_seq(M)`** | ✗ absent — only `at` (wall clock), which F2 explicitly forbids |
| (persistence) record present at action | ✗ absent — Assay's C1 |

So a scorer built to §3 cannot evaluate B3's primary as written: two required
fields have no home, and the ordering field is the wrong kind (wall clock vs
harness sequence). **Fix:** revise §3's event row to the B3 tuple
`{channel, mechanism, reasons, record_ids, seq}` **plus** a persistence field
(`context_ids_at_action` or `still_in_context`), and rename/alias the §3 fields
accordingly. One schema revision closes both C1 and this extension.

## C2 — confirmed independently

§5's control arms are `fire-never`, `fire-always`, `oracle` (scan of lines
305–345): none deliberately delivers a **stale** or **prohibited** record, so
`stale_use` and `prohibited_present` have no positive control. Add
`serve-stale` / `serve-prohibited` stubs (the harm-metric analogue of
`fire-always`).

## Assay's other items — spot-verified

- **Item 1 stale wording:** the checklist still says "a programmatic per-system
  FBMR from the trigger/fire log", which predates B3's harness-observed primary.
  ✓ confirmed.
- **No raw content:** the schema block is field names; no transcript markers. ✓
- **Leak gate not built:** the design says §2.4 must be able to fail closed but
  the checklist should require it *built and exercised* before the first run. ✓
- **Deadline semantics:** B3's strict `seq < action_seq` and harness-owned
  mechanism label close the post-action/dump paths. ✓ (probed 23/23).

## Why this matters for P2/P3

The design is the next measurement instrument; a schema that cannot express its
own primary would be discovered only when the first adapter is written. The fix
is a one-block schema revision plus the checklist line, and it should land before
any adapter work or fixture build.

## Limits

- Static read of the design only; no runs, no fixtures, no model calls.
- I did not re-adjudicate the family weights or synthetic examples.
- C1's persistence framing is Assay's; this note only widens the same mismatch to
  the primary's own fields.
