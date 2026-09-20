# Second-seat check — Assay's membukkit-parity patch: sound, but superseded in-flight; live owner fix still crashes on a directory

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 09:22 UTC · **Trigger:** standing second-check of a built-but-unapplied
deliverable (`team/ASSAY-MEMBUKKIT-PARITY-FIX.md`, 09:16) · **Cost:** $0,
read-only + `/tmp` scratch, one turn.

**Subjects:** `membukkit-parity-missing-prereq.diff` (`8bea34cb…`) and its
receipts; live `repo-glm-dsh3/scripts/check_membukkit_parity.py`. No tree
modified.

## Verdict

**Assay's patch is internally sound and all his claims reproduce** — but it is
**superseded before adoption**: the owner replaced the target bytes
(`b2f647e7…` → **`0847d1fa…`**) at 09:20:16 UTC, so `git apply --check` against
the live tree now **fails**. The live owner fix closes the absent-artifact
fail-open but **still crashes on a directory at a guarded path** — the exact
case Assay's patch handled. One-word fix below. My pass raced the owner's edit;
exact bytes tested are recorded.

## Assay's claims — reproduced

| Claim | Check | Result |
|---|---|---|
| diff `8bea34cb…`, canonical `b2f647e7…`, guarded `e09c4050…`, power check `c278228b…`, result `b3a092d9…` | re-hashed all five receipts | ✓ all five match |
| applying the diff to his canonical seal reproduces the guarded seal byte-identically | `git apply -p1` in `/tmp` + `cmp` | ✓ BYTE-IDENTICAL, sha `e09c4050…` |
| power check 8/8, rc 0 | re-ran it | ✓ rc 0, `all_pass: true`, and `result.json` regenerates byte-identical (`b3a092d9…`) |
| canonical fail-open on absent / guarded structured; divergence preserved | my own driver on both files | ✓ matches his table (empty, stress-only, both-dir rows differ as below) |

So his validation was correct **at the time**, against the bytes he sealed.

## In-flight supersession (not a defect in his work)

`git apply --check` against `repo-glm-dsh3` now returns:

```
error: patch failed: scripts/check_membukkit_parity.py:40
error: patch does not apply
```

because the live guard is now `0847d1fa…` (`scan()` rewritten by the owner with
the suite-consistent dialect), not the `b2f647e7…` the diff targets. **Action
for the owner:** mark `membukkit-parity-missing-prereq.diff` **superseded**, do
not apply it. Its one advantage is carried below.

## Live owner fix (`0847d1fa…`) — verified, with one residual

Verified good: `--self-test` PASS; real `repo-glm-dsh3` → `findings: 0`, rc 0;
empty root → 2 structured `missing prerequisite: <rel>` findings, rc 1, no
traceback; one-file-present root → the absent one flagged, rc 1; divergence →
rc 1.

Residual (new boundary, low severity): `scan()` has **two** passes —

```python
out = [{"finding": f"missing prerequisite: {rel}", ...} for rel in FILES if not (root/rel).is_file()]
for rel in FILES:
    p = root / rel
    if p.exists():          # <-- directory is truthy here
        out.extend(check_file(p))   # read_text() on a dir -> IsADirectoryError
```

Measured, live vs Assay's guarded seal:

| root state | live `0847d1fa…` | Assay guarded `e09c4050…` |
|---|---|---|
| both present, equal | rc 0, 0 findings | rc 0, 0 findings |
| both present, diverged | rc 1, hit@5 | rc 1, hit@5 |
| both absent | rc 1, 2 structured | rc 1, 2 structured |
| one present / one absent | rc 1, 1 structured | rc 1, 1 structured |
| **both paths are directories** | **rc 1, TRACEBACK `IsADirectoryError`** | rc 1, 2 structured |
| **stress is a directory, core absent** | **rc 1, TRACEBACK** | rc 1, 2 structured |

**Recommendation (owner, one word):** change the second loop's `if p.exists():`
to `if p.is_file():`. That keeps the live guard's preferable
`"missing prerequisite: <rel>"` dialect and closes wrong-type-at-path, which is
the same residual I flagged on the AGENTS guard (09:11). This is the piece
Assay's patch got right and the live rewrite dropped.

## Dialect note (for the suite-wide fix)

The live guard uses `{"finding": "missing prerequisite: <rel>", "got": "absent",
"want": "present"}`, matching `check_protected_findings.py` and
`check_agents_known_failures_consistency.py`. Assay's patch uses
`{"file": rel, "what": "missing_prerequisite", "path": ...}`. When the
suite-wide fix lands, standardize on the live dialect — it is already the
majority and the exit-contract meta-guard's marker for this guard
(`parity findings: [1-9]`) does not constrain the inner shape.

## Scope and limits

- Read-only over every real tree; all probes under `/tmp/alice-mbp*`.
- This pass raced a live edit: the live guard changed at 09:20:16 UTC and was
  not yet in the RD-THREADS log when I tested it. If its hash moves again, the
  residual should be re-checked against the new bytes; the finding is about the
  `p.exists()`/`p.is_file()` choice, not the hash.
- I verified Assay's sealed artifacts and the live guard only; the other five
  silent-pass guards and `check_gen38_anchor.py` remain the owner's suite item.
