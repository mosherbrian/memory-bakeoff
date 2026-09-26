# kiln (Practitioner) — c23: fix the tool first, save second, reconstruct last

**kiln · 2026-09-26 · ≤300w · from existing evidence, no new sources. Quoting ROLES.md: "maintenance, fit". Roadmap inputs + principles as context.**

## The rule

1. **Fix tool/default** when the pain is a wrong default or missing guard — e.g. tests skipped before commit → a `PreToolUse`/pre-commit hook, not a remembered rule. Existing implementation (hooks), zero per-use cost, fails closed.
2. **Save runbook** (textual skill) when judgment is required each time but steps repeat — e.g. rollout sequencing across hosts. Existing pattern (c5/c9); fails open, needs the trigger prose.
3. **Executable helper** when steps are machine-checkable and stable (≥3 unchanged successes): the helper *is* the fix for its slice — e.g. a verify script. Proposed per case, promoted on evidence.
4. **Reconstruct** when the situation is rare or prerequisites churn: grep-to-expand (c19) over stored originals beats maintaining a procedure nobody reuses. Changed condition test: if the environment moved, a saved procedure misleads while reconstruction re-grounds.

Concrete: a rollout step failing on a new host's paths — fix the script's path default (1); if host judgment is needed, runbook it (2); if the check is scriptable, helper (3); if rollouts are quarterly, recover the last attempt via transcript search instead of maintaining a skill (4). Failure alternative preserved at each level per the Correction-doc shape.

## Correction accepted

My c22 "nothing is enforced" overstates: `allowed/disallowed-tools`, model/effort overrides, and hook-executed skills *are* runtime enforcement — what prose alone cannot do is force the model to follow wisely. The precise claim: prose doesn't compel judgment; runtime scoping constrains action. Both belong in the arrangement. **Medium-low confidence** (rule argued from assembled evidence, not measured comparatively).
