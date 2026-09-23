# P6-r18 — claim-filing check (independent)

- **Reviewer:** corvid-dsh
- **Action:** `P6r18-claimfilingcheck-1` (existing ≤5 m grant)
- **Brief:** `claim-filing-receipt.json` @ `1e2e320`; claim
  `completion-claims/ex-p6r18-manifest-repair-1.json`.
- **Scope:** read-only schema/identity/hash/no-drift check. No edits.

## Verdict

**PASS.** The new claim exists at the canonical path, its schema carries the
required fields, and every manifest-binding hash and entry count matches the
delivered manifests with **no drift, missing, duplicate or self-reference**
entries. The filing step changed only the claim (no executable/manifest edits).
Prior INCOMPLETE `c25493b1…` is correctly preserved and carried by reference.

## Checks

- **File present:** `completion-claims/ex-p6r18-manifest-repair-1.json`
  (`filed_at 2026-09-23T03:15:25Z`, `outcome COMPLETE-filing`).
- **Schema/identity:** keys `action_id`, `outcome`, `package_id`, `filed_at`,
  `backdating`, `scope`, `files_claim`, `manifest_binding`, `carried_evidence`,
  `repair_action`, `review`. Identity is well-formed; `backdating: none` honestly
  records actual filing time; `repair_action`/`review` link the repair and the
  preserved INCOMPLETE review. (The `action_id` is `P6r18-claim-filing-1` while the
  file is named for the manifest repair — a naming nuance, not a binding error,
  and the claim documents both.)
- **Hash binding (recomputed all three):**
  - `outer_manifest_sha256 ec30ac8a…` == `candidate/manifest.json` actual.
  - `composition_manifest_sha256 9128b0dd…` == `candidate/composition-manifest.json` actual.
  - `r3_descriptor_sha256 098e4abc…` == `candidate/src/r3harness/R3_REVISION.json` actual.
- **Counts match:** `outer_entries 83`, `composition_entries 74` (actual).
- **No drift:** every manifest entry exists with a matching recomputed sha256; no
  missing, duplicate, self-reference or nested `candidate/candidate/` entries.
- **Filing scope respected:** the step added only the claim; no executable or
  manifest byte changed (manifest hashes above are the post-repair bytes already
  reviewed).

## Carried / limits

The claimed `carried_evidence` (90/665.74 s, P5 83, P3 59) is carried on
frozen reviewed bytes, explicitly not re-run in the filing step; that limit is
acceptable for a filing-only action and preserved. This check certifies no
additional source behaviour or live runtime adoption.

## Effect

One bounded verdict: **PASS** — new claim schema/identity/hashes correct and
drift-free; the prior INCOMPLETE remains preserved. Returned to Tern.
