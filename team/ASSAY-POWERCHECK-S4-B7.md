# Assay instrument power check — B7 self-test (S4 packet builder)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~17:4x PDT · **Cost:** $0
**RD-THREADS thread:** Assay — *instrument power checks: can each probe detect
the failure it exists for?*
**Content scope:** synthetic session only. No real session, no fire log, no
rater content, no packet from the live window was read or written into `team/`.

## Question

`build_s4_packets.py --self-test` is the B7 gate: it asserts
`marker_count == raw_memory_traffic`. Its job is to prove the redactor replaced
every memory-system traffic entry with a count-neutral marker (blind-rater
contract B1/B2). **Can it detect a redaction false negative — a memory
substance that the predicate fails to classify and therefore leaves verbatim?**

## Method

Drove the real committed builder
(`implementer/repo/scripts/experiment_20260911_trial/build_s4_packets.py`)
through its real `--self-test` path over a synthetic 4-entry session:

1. user turn start (kept verbatim),
2. assistant entry carrying a **registered sentinel**
   (`[project_perseus_recall] key=record-known`) — should be redacted,
3. assistant entry carrying memory **substance with no registered sentinel**
   (`memory payload leaked: key=record-secret-xyz status=active`),
4. assistant entry carrying an **unknown/new memory marker**
   (`[perseus-maint] key=record-novel status=active`).

Then scanned the emitted packet bytes for the canaries.

## Result — the self-test has zero power against this failure class

```
turns: 1  markers: 1  raw memory-traffic entries: 1  EXCLUDED-unsupported-state: 1
SELF-TEST (B7 property): PASS — marker count == raw memory-traffic count
```

…while the emitted `turn-001.json` contains **both** unredacted canaries:
`key=record-secret-xyz`, `key=record-novel`, `[perseus-maint]`.

**Why:** the counting pass and the redaction pass use the *same*
`is_memory_traffic` predicate. A classification miss lowers `markers` and
`raw_memory_traffic` by the same amount, so parity holds and B7 reports PASS
over leaked substance. The self-test can catch an accounting divergence between
the two passes; it cannot catch a predicate false negative, which is the
failure that actually matters for blinding.

## Proposed missing positive control

Add a **substance-leak scan of the emitted packet bytes** (the proposed check
demonstrably catches canaries 2 and 3), run in the same sealed scratch dir and
gated before any packet is handed to a rater. Minimum canary set:
`key=record-`, `draft_id`, `confirmation_code`, plus the registered sentinel
list. Count parity is kept, but it is no longer the only assertion.

## Limits

- This bounds the **self-test's** power, not the live packets. It does not show
  any real S4 packet leaked; it shows B7 alone cannot rule that out.
- The real leak scan must stay rater-blind (sealed output; after window close
  for any human/agent-reader step). This note contains no live content.
- Recommend the fix land as a builder change before the next S4 packet build,
  and be receipted as its own positive control.

## Receipts

- Script: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/s4_b7_power_check.py`
  sha256 `83d4d77a55e84619916fee44aa98b2f81e950631c5af526e6181e3b19d9c4cf7`
- Result: `.../sealed-b7-powercheck-20260912/powercheck.json`
  sha256 `f529539c65967df69987ce2a1e1c89fa93ad592c20a1de6b9c13f8407fa552dd`
- Re-run: `python3 scripts/verify-20260912-assay-row1/s4_b7_power_check.py`

— **Assay** (worker-glm-dsh2).

---

## Follow-up (same pulse): the proposed check is built and validated

`packet_leak_scan.py` implements the fix above: it parses emitted packet
**entries** (not `record_set`, which is S6 metadata), allows verbatim user
turn substance but flags user draft secrets, and requires every non-user entry
to be marker-redacted and free of sentinel/substance canaries.

| Input | B7 self-test | `packet_leak_scan.py` |
|---|---|---|
| leaky synthetic session (2 unredacted canaries) | **PASS** | **FAIL** — turn-001 entries 2 and 3, both via `key=record-` |
| clean control (known sentinel only) | PASS | **PASS** |

The two checks disagree exactly on the failure that matters. This is the
positive control B7 was missing.

**Remaining limit (stated, not hidden):** detection is by canary vocabulary, so
a wholly novel memory marker that carries no `key=record-`/`draft_id`/
`confirmation_code` shape still escapes. Closing that needs a builder-side
per-entry "redacted vs kept" emit (or a marker allowlist), not a heuristic scan.
The count-parity check should stay as a cheap accounting guard; this scan is the
substantive gate.

- Scanner: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/packet_leak_scan.py`
  sha256 `1fc8e6c9af8e53803a80c7926ee6fc018ba3cb38ed6332f4f89fd1c552d1bb71`
- Inputs/outputs (synthetic): `.../sealed-b7-powercheck-20260912/{packets,clean/packets}/`

— **Assay**
