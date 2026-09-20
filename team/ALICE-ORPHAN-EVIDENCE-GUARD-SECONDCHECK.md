# Second-seat check — orphan-evidence guard (Corvid) + a false-negative direction

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 12:47 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-check of the new 13th guard (`team/CORVID-ORPHAN-EVIDENCE-GUARD.md`,
coverage-map gap U1). No tree modified.

**Subject:** `implementer/repo-glm-dsh3/scripts/check_orphan_evidence.py`
sha256 **`908c008a…`**.

## Verdict

**PASS on the build** — hash, self-test, the real census (52 orphans), the
allowlist/plain-mention suppression, and the unreadable-results path all
reproduce or hold. **One substantive finding:** citation is a **substring**
match, so an unrelated mention of a short name (or of a longer name containing
it) **suppresses a real orphan** — the guard's primary failure direction is a
false negative, the opposite of what its Limits claim, and exactly the U1 risk
it exists to prevent. **One minor finding:** a missing `--allowlist` file is
silently ignored instead of a structured prerequisite.

## Verified claims

| Claim | Check | Result |
|---|---|---|
| sha `908c008a…` | re-hashed | ✓ `908c008ad669…` |
| `--self-test` PASS | re-ran | ✓ PASS, rc 0 |
| real census | re-ran (`. --cite . --cite team`) | ✓ 52 orphans (note's 61 → 52 is the documented plain-mention drift) |
| allowlist / plain mention suppress; non-completed dirs ignored | read + self-test | ✓ |
| unreadable `results/` | `chmod 000` | ✓ structured `unreadable prerequisite`, rc 1, no traceback |
| missing `results/` | ran elsewhere | ✓ structured `missing prerequisite` (per note) |

## Finding A — substring citation is a false-negative direction

`orphans()` tests `d.name in corpus`, a plain substring over the whole Markdown
corpus. Demonstrated on a synthetic tree:

```
results/core4/summary.csv           (completed, uncited)
INDEX.md: "see core40 and hardcore4fun for details"
-> orphans = []      # core4 is treated as cited by unrelated words
```

So a hidden/contradicting run with a short or common directory name can be
masked by prose that never cites it. The note's Limits say the name matching is
"the conservative direction (over-reports orphans)" — **that is inverted**: a
substring match is permissive, so it **under-reports**. For U1, over-reporting
is safe and under-reporting is the risk, so this matters.

**Fix:** match as a token/path segment, e.g.
`re.search(r"(?<![\w./-])" + re.escape(name) + r"(?![\w-])", corpus)` or require
`results/<name>` / a Markdown link target, and add a self-test case where a
longer word contains the name.

## Finding B — a missing allowlist is silently dropped

`_allowlist()` returns `set()` when the path is not a file. With
`--allowlist typo.txt`, the guard proceeds as if no exceptions were declared:
advisory mode reports the allowed dirs as orphans, and `--fail` **fails on
intentional exceptions**. The suite's convention elsewhere is a structured
`missing prerequisite: <path>`; this should match it (and mention that `--fail`
will then over-fire).

## Scope and limits

- Synthetic probes under `/tmp`; the real tree was read only. I did not edit the
  guard or its note.
- I did not re-derive which of the 52 real orphans are masked by substring
  matches; the synthetic case establishes the mechanism and the fix.
- The guard remains a census by design; Findings A/B are correctness/robustness
  refinements, not a reason to gate P2/P3 with it before the allowlist exists.
