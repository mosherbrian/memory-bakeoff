# Second-seat check — S4 value-shape canary patch (Assay) + a case-sensitivity boundary

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 12:25 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-check of `team/ASSAY-S4-VALUE-CANARY-FIX.md` (the unapplied patch that
closes my `draft_id`-word census finding). No tree modified.

**Subject:** `s4-value-canary-builder.diff` (`557cb5bb…`),
`s4-value-canary-scanner.diff` (`60c7c14e…`), guarded files `b211037c…` /
`5aa670c4…`, power check `5e1261c8…`, result `65aa02db…`.

## Verdict

**PASS / AGREE.** All six hashes match; both diffs `git apply --check` cleanly;
the power check re-runs rc 0 and the all-packet census reproduces **24 findings /
58 value occurrences** (was 8 / 5) with the 5 word-only false positives dropped.
**One latent boundary:** the value regex is **lowercase-hex only**
(`draft-[0-9a-f]{6,}`), so an uppercase or non-hex draft value escapes both the
detector **and the redaction** — a one-character fix (`re.I`) before adoption.
Zero live misses on this snapshot (all 58 real tokens are lowercase hex).

## Verified claims

| Claim | Check | Result |
|---|---|---|
| six receipt hashes | re-hashed | ✓ 6/6 match |
| builder diff applies in `implementer/repo`; scanner diff in `repo-glm-dsh2` | `git apply --check` | ✓ both rc 0 |
| power check 13/13, rc 0 | re-ran | ✓ rc 0; `guarded_findings=24`, `guarded_value_occurrences=58`, `packets=134` |
| census: canonical 8/5 → guarded 24/58 | read result + my own counts | ✓ matches my `ALICE-S4-LEAK-VALUE-ONLY-CENSUS.md` exactly |
| bare `draft_id` removed from detector; value shape added; sentinels/`key=record-`/`confirmation_code` kept | read guarded `SUBSTANCE` | ✓ `('key=record-', 'confirmation_code')` + `SECRET_VALUE_RE` |

## Boundary — the value regex is case- and charset-narrow

`SECRET_VALUE_RE = re.compile(r"draft-[0-9a-f]{6,}")` has no `re.I` and no
non-hex charset. Synthetic unredacted non-user entries:

```
draft-abcdef  -> flagged
draft-123456  -> flagged        (digits are hex)
draft-ABC123  -> NOT flagged
draft-Ab12Cd  -> NOT flagged
draft-xyz789  -> NOT flagged
```

The same predicate is used for **redaction** (`is_memory_traffic`), so an
uppercase value would be **emitted unredacted** as well as unflagged — it is a
recall *and* privacy gap, not only a detector gap.

**Live exposure on the frozen snapshot: 0.** A census of every
`draft-<alnum>{6,}` token in all 134 packets gives **58 tokens, 58 lowercase-hex
matches, 0 not matched** — so the patch's recall equals my earlier census here.
The risk is latent: any change in the id generator's alphabet (uppercase, base32,
UUIDs) reopens it.

**Fix:** `re.compile(r"draft-[0-9a-f]{6,}", re.I)` (one flag), or broaden to the
generator's real charset with a comment. Because the shape is used on the
redaction side too, this should land before the patch is adopted.

## Minor observation

The patch drops the bare `draft_id` canary from the **non-user** detector but
keeps it for user entries (per the note). That asymmetry is intentional and the
power check covers the user-value case; no action.

## Scope and limits

- Synthetic probes under `/tmp` plus read-only census of the already-emitted
  frozen packets; no content printed and no tree modified.
- I did not adopt the patch; the recommendation is for the owner before it lands.
- The patch's stated limit (a secret in another format is still missed;
  `confirmation_code` remains a word canary) stands and is consistent with my
  boundary.
