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

// ── structured source provenance (proposal §1, REPAIR-20260911 R1) ──────────
//
// §4: source "is part of the record at creation time" — so every NEW write
// REQUIRES a validated source block (fail-closed, consistent with the
// guard). It lands in the stored body as `source` alongside the constant
// `source_kind` surface tag (kept for compatibility), and is recall-visible
// through body_json.

export const SOURCE_KINDS = ["task", "artifact", "instruction"] as const;
export type SourceKind = (typeof SOURCE_KINDS)[number];

export interface SourceProvenance {
  kind: SourceKind;
  /** Non-empty pointer to where the assertion came from. */
  ref: string;
  /** Optional ISO-8601 timestamp of the source event. */
  timestamp?: string;
}

/** Validate raw source input; null source + problem string = refuse the draft. */
export function validateSource(raw: unknown): { source: SourceProvenance | null; problem: string | null } {
  if (raw === null || raw === undefined) {
    return { source: null, problem: "source is required: {kind: task|artifact|instruction, ref, timestamp?} — provenance is part of the record at creation time (proposal §1)" };
  }
  if (typeof raw !== "object" || Array.isArray(raw)) {
    return { source: null, problem: "source must be an object {kind, ref, timestamp?}" };
  }
  const o = raw as Record<string, unknown>;
  if (typeof o.kind !== "string" || !(SOURCE_KINDS as readonly string[]).includes(o.kind)) {
    return { source: null, problem: `source.kind must be one of: ${SOURCE_KINDS.join(", ")}` };
  }
  if (typeof o.ref !== "string" || !o.ref.trim()) {
    return { source: null, problem: "source.ref must be a non-empty string" };
  }
  if (o.timestamp !== undefined
    && (typeof o.timestamp !== "string" || !o.timestamp.trim() || Number.isNaN(Date.parse(o.timestamp)))) {
    return { source: null, problem: "source.timestamp must be an ISO-8601 string when set" };
  }
  const source: SourceProvenance = {
    kind: o.kind as SourceKind,
    ref: o.ref.trim(),
    ...(o.timestamp !== undefined ? { timestamp: o.timestamp as string } : {}),
  };
  return { source, problem: null };
}

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
  /** Required structured provenance (proposal §1) for the new record. */
  source: SourceProvenance;
  supersession?: { supersedes_key: string; reason: string };
}

/**
 * The stored body. `assertion_text` and `environment` are projected by the
 * vault onto record columns (measured on the pinned 2.23.2 binary); the
 * structured `source` provenance block (proposal §1, mandatory on new
 * writes) and the remaining fields are carried verbatim in body_json and
 * are therefore recall-visible. `source_kind` stays as the constant
 * surface tag for compatibility with the provider-lineage field set.
 */
export function bodyEnvelope(input: BodyEnvelopeInput): Record<string, unknown> {
  const body: Record<string, unknown> = {
    assertion_text: input.content,
    environment: input.environment,
    source_kind: SOURCE_KIND,
    source: input.source,
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
