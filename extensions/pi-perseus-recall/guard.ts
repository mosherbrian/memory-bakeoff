/**
 * §2 scope guard for the decision-memory write surface (BUILD-20260911,
 * scope item 3): supersession across NON-OVERLAPPING environments is
 * rejected by DEFAULT. The only way through is the explicit draft-time
 * parameter `allow_cross_environment: true` — never implied, never a
 * default, never a string.
 *
 * Environment semantics, deliberately conservative:
 *   - An environment is an opaque, non-empty string (default: the project
 *     environment, `project`).
 *   - Two environments overlap IFF they are byte-equal. No prefix, path or
 *     case folding: "Proj" and "project" are disjoint, "a/b" and "a" are
 *     disjoint. Anything that is not provably the same environment is
 *     treated as non-overlapping and blocked.
 *   - The old record's environment is verified against the vault's own
 *     stored value (fail-closed): unknown or mismatched means blocked.
 */

export const OVERRIDE_PARAM = "allow_cross_environment";

export type ScopeGuardVerdict =
  | "same_environment"
  | "cross_environment_allowed_by_override"
  | "blocked_cross_environment";

export interface ScopeGuardInput {
  from_environment: string;
  to_environment: string;
  /** Must be literally `true` to override; anything else is no override. */
  allow_cross_environment?: unknown;
}

export interface ScopeGuardResult {
  allowed: boolean;
  verdict: ScopeGuardVerdict;
  reason: string;
  override_param: string;
}

/**
 * Pure decision. The override is recognized ONLY as the boolean `true`:
 * `1`, `"true"`, a truthy object or an absent key all leave the block in
 * force — the override must never be implied.
 */
export function evaluateScopeGuard(input: ScopeGuardInput): ScopeGuardResult {
  const { from_environment, to_environment } = input;
  const same = from_environment === to_environment;
  if (same) {
    return {
      allowed: true,
      verdict: "same_environment",
      reason: `both records are in environment ${JSON.stringify(from_environment)}`,
      override_param: OVERRIDE_PARAM,
    };
  }
  const override = input.allow_cross_environment === true;
  if (override) {
    return {
      allowed: true,
      verdict: "cross_environment_allowed_by_override",
      reason: `environments differ (${JSON.stringify(from_environment)} vs `
        + `${JSON.stringify(to_environment)}) but ${OVERRIDE_PARAM}:true was passed `
        + `explicitly on the draft; the operator still confirms the write`,
      override_param: OVERRIDE_PARAM,
    };
  }
  return {
    allowed: false,
    verdict: "blocked_cross_environment",
    reason: `§2 scope guard: environments do not overlap `
      + `(${JSON.stringify(from_environment)} vs ${JSON.stringify(to_environment)}); `
      + `supersession across non-overlapping environments is rejected by default. `
      + `To proceed anyway, re-draft with ${OVERRIDE_PARAM}: true — an explicit `
      + `parameter, never implied — and the operator still confirms`,
    override_param: OVERRIDE_PARAM,
  };
}

export type SourceCheckVerdict =
  | "source_ok"
  | "blocked_source_not_found"
  | "blocked_source_environment_unverifiable"
  | "blocked_source_environment_mismatch"
  | "blocked_source_already_superseded";

export interface SourceRecordView {
  found: boolean;
  /** The vault's own stored environment for the old record, if it exposes one. */
  stored_environment?: string | null;
  status?: string | null;
}

/**
 * Fail-closed verification of the OLD record before any supersession draft
 * may reference it. Every refusal here is a default-on refusal: the caller
 * must make the record verifiable (or pass the explicit override upstream)
 * — nothing is assumed in the operator's favor.
 */
export function verifySourceRecord(
  claimed_environment: string,
  source: SourceRecordView,
): { allowed: boolean; verdict: SourceCheckVerdict; reason: string } {
  if (!source.found) {
    return {
      allowed: false,
      verdict: "blocked_source_not_found",
      reason: "§2 scope guard: the record named as superseded was not found in "
        + "its claimed environment's workspace; refusing to draft a lineage "
        + "edge to a record the vault cannot show",
    };
  }
  if (typeof source.stored_environment !== "string" || !source.stored_environment) {
    return {
      allowed: false,
      verdict: "blocked_source_environment_unverifiable",
      reason: "§2 scope guard: the old record carries no environment in the vault, "
        + "so overlap cannot be verified; supersession is rejected by default. "
        + `Re-draft with ${OVERRIDE_PARAM}: true to override explicitly`,
    };
  }
  if (source.stored_environment !== claimed_environment) {
    return {
      allowed: false,
      verdict: "blocked_source_environment_mismatch",
      reason: `§2 scope guard: the old record is stored in environment `
        + `${JSON.stringify(source.stored_environment)} but the draft claimed `
        + `${JSON.stringify(claimed_environment)}; refusing on the mismatch`,
    };
  }
  if (source.status === "deprecated" || source.status === "archived") {
    return {
      allowed: false,
      verdict: "blocked_source_already_superseded",
      reason: `§2 scope guard: the old record's status is ${JSON.stringify(source.status)}; `
        + "it is already retired and must not be superseded again",
    };
  }
  return { allowed: true, verdict: "source_ok", reason: "old record verified in a live, verifiable environment" };
}
