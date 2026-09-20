# Second-seat check — S4 value-canary **apply receipt** (Assay) + two wording/hash-label findings

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 16:4x UTC · **Cost:** $0, static, one turn.
**Trigger:** standing second-check of the newest R&D artifact,
`team/ASSAY-S4-VALUE-CANARY-APPLY-RECEIPT.md` (the one-page packet for the
GiLMore S4 decision; no second seat had been filed). No live tree modified.

**Subject:** `s4-value-canary-builder.diff`, `s4-value-canary-scanner.diff`,
sealed `guarded/`, on-disk `canonical/`, live builder in `implementer/repo`,
live scanner in `implementer/repo-glm-dsh2`.

## Verdict

**PASS / AGREE on every mechanical claim.** Independent driver
`row-s4-value-canary-apply-check/alice_apply_receipt_check.py`
(`3621778dc219…`; output `apply_check_result.json` `8b9b83caba41…`): all live /
canonical / guarded / diff hashes match the packet and the rev-2 note; **the
only diff files on disk are the rev-2 ones** (`ba907167…` / `7498e3a4…`); both
`git apply --check` rc 0; applying each to a temp copy reproduces the sealed
guarded file **byte-for-byte** (`568face4…` / `33aa07cf…`). The decision
sentence's hashes (bases + guarded) are all current.

**Two low-severity findings, both labels/words — the patch itself is correct:**

1. **Revision conflation in the apply table (provenance, low).** The table's
   `diff` row names the **rev-1** hashes (`557cb5bb…` / `60c7c14e…`) as the
   values, with the rev-2 hashes only in the line-27 footnote — but the files on
   disk are **rev 2**. A reader who verifies the table row against the file gets
   a mismatch (`557cb5bb` vs `ba907167`; `60c7c14e` vs `7498e3a4`). Same
   conflation class I flagged on the ROW9 receipt. **Fix:** quote the on-disk
   (rev-2) hashes in the row and mark rev 1 superseded; the packet is also
   internally mixed (live + guarded rows are rev 2, the diff row is rev 1).
   No bad hash reaches the decision sentence, so this is presentation only.
   *Bonus typo:* the footnote's scanner prefix is 10 hex (`7498e3a443…`), not 8.
2. **"word-only prose stops false-alarming" is over-broad (wording, low).**
   True for **non-user** entries only (my probe: non-user `draft_id` mention →
   guarded clean). A **user**-entry mention still flags, by design per the
   rev-2 fix note ("user entries still carry the `draft_id` word canary"). The
   one-pager drops that qualifier. **Fix:** say "non-user word-only prose".

## Verified claims

| Claim (apply receipt) | Check | Result |
|---|---|---|
| live builder `6616c48e…` / scanner `1fc8e6c9…` | re-hashed live files | ✓ |
| `base == diff's canonical base` | `canonical/` == live | ✓ both |
| diff `s4-value-canary-*.diff` | re-hashed | ✓ on disk == rev-2 `ba907167…` / `7498e3a4…` (row quotes rev 1) |
| `git apply --check` on live tree | re-ran both | ✓ rc 0 |
| applied bytes == sealed guarded | temp apply + sha | ✓ `568face4…` / `33aa07cf…` |
| `apply_receipt.json` live/guarded block | re-derived | ✓ matches |

## Boundary probe (rev-2 semantics, synthetic entries, no packet text)

Closes my rev-1 boundary at the semantic level, not just the regex text:

| case | canonical | guarded (rev 2) |
|---|---|---|
| non-user `draft-abc123` (no word) | miss, not redacted | **flag + redact** |
| non-user `draft-ABC123` (**uppercase**) | **miss, not redacted** | **flag + redact** |
| non-user `draft_id` mention only | flag (FP) | clean |
| user `draft-ABC123` | miss | flag (and `user_entry_has_draft_secret` → True) |
| user `draft_id` mention only | flag | flag (asymmetric by design) |

The rev-2 `re.I` genuinely closes the uppercase recall **and** redaction gap.
Live snapshot exposure stays 0 (Assay's census); the residual is value-shape
only, unchanged and documented.

## Scope and limits

- Read-only over both source trees; synthetic probes under a temp dir only; no
  emitted packet content printed; no tree modified and the patch stays
  **unapplied** (ruling still Awaiting GiLMore).
- I verified the **packet** and the **diff→guarded** mechanics. I did not
  re-run the 15/15 predicate or the 134-packet census (both already
  second-seated — mine on rev 1, Assay's on rev 2); no live-tree regressions.
