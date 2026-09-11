/**
 * Record model for the decision-memory write surface (BUILD-20260911).
 *
 * The write path is the P1B-proven harness path (supersession_binding.py
 * lineage, Gen102 correction): records land via the documented operator CLI
 * `perseus-vault write` (active verified records — NOT the MCP `remember`
 * tool, which creates non-serveable proposals), and lineage is applied via
 * the MCP `perseus_vault_supersede` call with from_key = the OLD record
 * (the parameter schema is authoritative; the tool summary says the
 * opposite — measured in Gen102).
 *
 * Environments: an opaque string recorded in the body (the vault projects
 * `environment` onto the record) and mapped onto the vault's workspace_hash
 * so recall/scan partition records exactly as the guard partitions them:
 *   - the project default environment uses the configured (or 7c-derived)
 *     workspace hash, unchanged from the read-only adapter;
 *   - any other environment hashes to sha256(environment), the same
 *     scope→workspace scheme the memory_bakeoff perseus provider uses.
 */

import { createHash, randomBytes } from "node:crypto";

export const SOURCE_KIND = "pi-perseus-recall-decision-memory-v1";
export const DEFAULT_ENVIRONMENT = "project";
export const DEFAULT_CATEGORY = "decision";

export interface ResolvedEnvironments {
  defaultEnvironment: string;
  workspaceHash: string;
}

/**
 * Map an environment name to the workspace hash the vault partitions on.
 * The default environment keeps the configured workspace hash (study
 * configs pass theirs explicitly); a named environment gets
 * sha256(environment) — injective, so two names never share a workspace.
 */
export function workspaceHashFor(environment: string, resolved: ResolvedEnvironments): string {
  if (environment === resolved.defaultEnvironment) return resolved.workspaceHash;
  return createHash("sha256").update(environment).digest("hex");
}

/** Non-semantic key, never reused: `record-<8 hex>`. */
export function freshKey(): string {
  return `record-${randomBytes(4).toString("hex")}`;
}

/** Keys identify records; the CLI silently UPDATES on duplicate category+key, so validate hard. */
export function validateKey(key: string): string | null {
  if (typeof key !== "string" || !key.trim()) return "key must be a non-empty string";
  if (/\s/.test(key)) return `key must not contain whitespace: ${JSON.stringify(key)}`;
  if (key.length > 128) return "key must be at most 128 characters";
  return null;
}

export function validateEnvironment(environment: string): string | null {
  if (typeof environment !== "string" || !environment.trim()) {
    return "environment must be a non-empty string";
  }
  if (/\s/.test(environment)) return `environment must not contain whitespace: ${JSON.stringify(environment)}`;
  return null;
}

export interface BodyEnvelopeInput {
  content: string;
  environment: string;
  recordedAtMs: number;
  supersession?: { supersedes_key: string; reason: string };
}

/**
 * The stored body. `assertion_text` and `environment` are projected by the
 * vault onto record columns (measured on the pinned 2.23.2 binary); the
 * remaining fields are provenance carried verbatim in body_json.
 */
export function bodyEnvelope(input: BodyEnvelopeInput): Record<string, unknown> {
  const body: Record<string, unknown> = {
    assertion_text: input.content,
    environment: input.environment,
    source_kind: SOURCE_KIND,
    recorded_at_unix_ms: input.recordedAtMs,
  };
  if (input.supersession) {
    body.supersedes = input.supersession;
  }
  return body;
}

/** One line the operator can read in the in-session prompt or the notify file. */
export function summarize(content: string, max = 120): string {
  const flat = content.replace(/\s+/g, " ").trim();
  return flat.length <= max ? flat : flat.slice(0, max - 1) + "…";
}
