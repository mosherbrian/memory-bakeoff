/**
 * pi-project-recall: read-only cross-session recall over the project's pi-lcm store.
 *
 * pi-lcm persists every message of every session in the project into one SQLite
 * store (~/.pi/agent/lcm/<sha256(cwd)[:16]>.db) with an FTS5 index - but every
 * search it exposes (lcm_grep/lcm_expand/lcm_describe) filters to the CURRENT
 * conversation_id. A new session in the same project starts blind to all prior
 * sessions. This extension adds exactly one tool, project_recall, that runs the
 * same queries WITHOUT the conversation filter, so a fresh session can retrieve
 * decisions, failed approaches and rationale recorded in earlier sessions.
 *
 * Properties that are load-bearing for the R2 pilot (RESET_STATUS.md):
 *   - READ-ONLY: opens the store with the driver's readOnly flag; no code path
 *     writes. Concurrent with pi-lcm's writer via WAL, separate connection.
 *   - NO new dependencies: node builtins only; parameters are a plain JSON
 *     schema object. Driver selection mirrors pi-lcm src/db/driver.ts
 *     (node:sqlite preferred - Pi 0.84.4 runs under node - bun:sqlite fallback).
 *   - Kill switch: PI_PROJECT_RECALL=0 makes the tool return a disabled notice.
 *   - Stale-recall guard: every hit carries timestamp, conversation_id and
 *     session start, and the output header warns that history may contain
 *     superseded values.
 */

import { createRequire } from "node:module";
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve, normalize } from "node:path";

const require_ = createRequire(import.meta.url);

// ── Driver selection (pi-lcm src/db/driver.ts pattern) ────────────────────

export type DriverName = "node:sqlite" | "bun:sqlite";

export function detectDriver(): DriverName {
  try {
    require_("node:sqlite");
    return "node:sqlite";
  } catch {
    return "bun:sqlite";
  }
}

interface Stmt {
  all(...params: unknown[]): unknown[];
}
interface ReadOnlyDb {
  prepare(sql: string): Stmt;
  close(): void;
}

/** Open strictly read-only. Throws if the file cannot be opened. */
function openReadOnly(path: string): ReadOnlyDb {
  if (detectDriver() === "node:sqlite") {
    const { DatabaseSync } = require_("node:sqlite");
    const raw = new DatabaseSync(path, { readOnly: true });
    return { prepare: (sql) => raw.prepare(sql) as Stmt, close: () => raw.close() };
  }
  const { Database } = require_("bun:sqlite");
  const raw = new Database(path, { readonly: true });
  return { prepare: (sql) => raw.prepare(sql) as Stmt, close: () => raw.close() };
}

// ── Store location (pi-lcm src/config.ts + src/utils.ts parity) ───────────

/** sha256(cwd) truncated to 16 hex chars - pi-lcm's per-project DB filename. */
export function hashCwd(cwd: string): string {
  return createHash("sha256").update(cwd).digest("hex").slice(0, 16);
}

/**
 * Resolve the pi-lcm store directory with the same precedence pi-lcm uses:
 * LCM_DB_DIR env, else lcm.dbDir in the agent settings.json, else
 * <agentDir>/lcm where agentDir is PI_CODING_AGENT_DIR else ~/.pi/agent.
 * Fix-14 style guard: reject '..' in an explicit dbDir.
 */
export function resolveDbDir(): string {
  const agentDir = process.env.PI_CODING_AGENT_DIR
    ?? join(homedir(), ".pi", "agent");
  let dir = process.env.LCM_DB_DIR ?? null;
  if (!dir) {
    try {
      const settings = JSON.parse(readFileSync(join(agentDir, "settings.json"), "utf8"));
      if (typeof settings?.lcm?.dbDir === "string" && settings.lcm.dbDir) dir = settings.lcm.dbDir;
    } catch { /* no settings or no lcm.dbDir - fall through to default */ }
  }
  if (!dir) dir = join(agentDir, "lcm");
  const resolved = resolve(normalize(dir));
  if (resolved.includes("..")) throw new Error(`pi-project-recall: dbDir must not contain '..': ${dir}`);
  return resolved;
}

export function storePathFor(cwd: string): string {
  return join(resolveDbDir(), `${hashCwd(cwd)}.db`);
}

// ── Query (pi-lcm store.ts searchFts5/searchSummaries minus the
//    conversation_id filter, plus session metadata from conversations) ─────

/**
 * FTS5 injection guard, verbatim behaviour of pi-lcm's sanitizeFtsQuery:
 * split on whitespace, double internal quotes, wrap each token in quotes,
 * rejoin with spaces (implicit AND).
 */
export function sanitizeFtsQuery(query: string): string {
  return query
    .split(/\s+/)
    .filter(Boolean)
    .map((token) => `"${token.replace(/"/g, '""')}"`)
    .join(" ");
}

/**
 * Relaxation candidates for a multi-term AND query: progressively drop
 * trailing terms (keep the leading, usually most content-bearing,
 * vocabulary). Bounded by MAX_RELAXATION_ATTEMPTS.
 */
export const MAX_RELAXATION_ATTEMPTS = 6;

export function relaxedVariants(query: string): string[] {
  const tokens = query.split(/\s+/).filter(Boolean);
  const variants: string[] = [];
  for (let keep = tokens.length - 1; keep >= 2 && variants.length < MAX_RELAXATION_ATTEMPTS; keep--) {
    variants.push(tokens.slice(0, keep).join(" "));
  }
  // Then each single token, last first - prefix drops keep leading terms, so
  // the trailing vocabulary (often the discriminating one) is tried here.
  for (let i = tokens.length - 1; i >= 0 && variants.length < MAX_RELAXATION_ATTEMPTS; i--) {
    variants.push(tokens[i]);
  }
  return variants;
}

/** Newest session start + conversation count, to detect live-only results. */
function storeSessionBounds(db: ReadOnlyDb): { maxStart: string; conversations: number } {
  const row = db.prepare(
    "SELECT MAX(created_at) AS maxStart, COUNT(*) AS n FROM conversations",
  ).all() as any[];
  return { maxStart: iso(row[0]?.maxStart), conversations: Number(row[0]?.n ?? 0) };
}

export interface RecallHit {
  source: "messages" | "summaries";
  conversation_id: string;
  session_id: string | null;
  session_start: string;
  timestamp: string;
  role: string;
  snippet: string;
}

function iso(ts: unknown): string {
  if (typeof ts === "number" && Number.isFinite(ts)) return new Date(ts).toISOString();
  return typeof ts === "string" ? ts : String(ts);
}

/** Truncate around the first query term occurrence, else the head of the text. */
function snippetFor(text: string, query: string, max = 280): string {
  if (!text) return "";
  const firstTerm = query.split(/\s+/).filter(Boolean)[0] ?? "";
  const at = firstTerm ? text.toLowerCase().indexOf(firstTerm.toLowerCase()) : -1;
  const start = at > 40 ? at - 40 : 0;
  const cut = text.slice(start, start + max).replace(/\s+/g, " ").trim();
  return (start > 0 ? "…" : "") + cut + (start + max < text.length ? "…" : "");
}

function tsFilter(after?: string, before?: string): { clause: string; params: unknown[] } {
  const params: unknown[] = [];
  let clause = "";
  if (after) {
    const t = Date.parse(after);
    if (!Number.isNaN(t)) { clause += " AND m.timestamp >= ?"; params.push(t); }
  }
  if (before) {
    const t = Date.parse(before);
    if (!Number.isNaN(t)) { clause += " AND m.timestamp <= ?"; params.push(t); }
  }
  return { clause, params };
}

export function queryMessages(
  db: ReadOnlyDb, query: string, limit: number,
  after?: string, before?: string,
): RecallHit[] {
  const sanitized = sanitizeFtsQuery(query);
  if (!sanitized) return [];
  const { clause, params } = tsFilter(after, before);

  // NOTE: no conversation_id filter - this is the entire point of the tool.
  // Joins conversations to annotate every hit with its session identity.
  const sql =
    `SELECT m.role, m.content_text, m.timestamp, c.id AS conversation_id,
            c.session_id, c.created_at AS session_start
     FROM messages m
     JOIN messages_fts fts ON m.rowid = fts.rowid
     JOIN conversations c ON c.id = m.conversation_id
     WHERE fts.messages_fts MATCH ?${clause}
     ORDER BY m.timestamp DESC, m.seq DESC
     LIMIT ?`;
  try {
    const rows = db.prepare(sql).all(sanitized, ...params, limit) as any[];
    return rows.map((r) => ({
      source: "messages" as const,
      conversation_id: r.conversation_id,
      session_id: r.session_id ?? null,
      session_start: iso(r.session_start),
      timestamp: iso(r.timestamp),
      role: r.role,
      snippet: snippetFor(r.content_text ?? "", query),
    }));
  } catch {
    // FTS5 unavailable or errored: fall back to LIKE, as pi-lcm's searchFts5 does.
    const escaped = query.replace(/\\/g, "\\\\").replace(/%/g, "\\%").replace(/_/g, "\\_");
    const like =
      `SELECT m.role, m.content_text, m.timestamp, c.id AS conversation_id,
              c.session_id, c.created_at AS session_start
       FROM messages m
       JOIN conversations c ON c.id = m.conversation_id
       WHERE m.content_text LIKE ? ESCAPE '\\'${clause}
       ORDER BY m.timestamp DESC, m.seq DESC
       LIMIT ?`;
    const rows = db.prepare(like).all(`%${escaped}%`, ...params, limit) as any[];
    return rows.map((r) => ({
      source: "messages" as const,
      conversation_id: r.conversation_id,
      session_id: r.session_id ?? null,
      session_start: iso(r.session_start),
      timestamp: iso(r.timestamp),
      role: r.role,
      snippet: snippetFor(r.content_text ?? "", query),
    }));
  }
}

export function querySummaries(
  db: ReadOnlyDb, query: string, limit: number,
): RecallHit[] {
  if (!query?.trim()) return [];
  // LIKE search, exactly as pi-lcm's searchSummaries does - minus the filter.
  const escaped = query.replace(/\\/g, "\\\\").replace(/%/g, "\\%").replace(/_/g, "\\_");
  const sql =
    `SELECT s.text, s.created_at, c.id AS conversation_id,
            c.session_id, c.created_at AS session_start
     FROM summaries s
     JOIN conversations c ON c.id = s.conversation_id
     WHERE s.text LIKE ? ESCAPE '\\'
     ORDER BY s.created_at DESC
     LIMIT ?`;
  const rows = db.prepare(sql).all(`%${escaped}%`, limit) as any[];
  return rows.map((r) => ({
    source: "summaries" as const,
    conversation_id: r.conversation_id,
    session_id: r.session_id ?? null,
    session_start: iso(r.session_start),
    timestamp: iso(r.created_at),
    role: "summary",
    snippet: snippetFor(r.text ?? "", query),
  }));
}

export function openStore(cwd: string): { db: ReadOnlyDb; path: string } | null {
  const path = storePathFor(cwd);
  if (!existsSync(path)) return null;
  return { db: openReadOnly(path), path };
}

// ── The tool ──────────────────────────────────────────────────────────────

const parameters = {
  type: "object",
  properties: {
    query: { type: "string", description: "Search query (FTS5 text; terms are ANDed; auto-relaxes by dropping terms - marked relaxation-sourced - when the exact query returns nothing or no hits from any prior session)" },
    scope: {
      type: "string",
      enum: ["messages", "summaries", "all"],
      description: "Where to search (default: all)",
    },
    limit: { type: "number", description: "Max results per scope (default 20, max 100)" },
    after: { type: "string", description: "Only hits at/after this ISO timestamp" },
    before: { type: "string", description: "Only hits at/before this ISO timestamp" },
  },
  required: ["query"],
} as const;

function formatHits(hits: RecallHit[]): string {
  return hits.map((h) =>
    `[${h.source}] ${h.timestamp} (session started ${h.session_start}, conversation ${h.conversation_id}) ${h.role}: ${h.snippet}`
  ).join("\n");
}

/** Tool core, separated from execute() only so tests can pass an explicit cwd. */
export async function runRecall(
  cwd: string,
  params: {
    query: string;
    scope?: "messages" | "summaries" | "all";
    limit?: number;
    after?: string;
    before?: string;
  },
): Promise<{ content: { type: "text"; text: string }[] }> {
  if (process.env.PI_PROJECT_RECALL === "0") {
    return {
      content: [{ type: "text", text: "project_recall is disabled (PI_PROJECT_RECALL=0)." }],
    };
  }
  const query = (params?.query ?? "").trim();
  if (!query) {
    return { content: [{ type: "text", text: "project_recall: empty query - nothing searched." }] };
  }
  const scope = params?.scope ?? "all";
  const limit = Math.min(Math.max(Math.floor(params?.limit ?? 20), 1), 100);

  const store = openStore(cwd);
  if (!store) {
    // Truthful empty: no store, no fabricated recall.
    const path = storePathFor(cwd);
    return {
      content: [{
        type: "text",
        text: `project_recall: no project memory store exists yet for this project (${path}). Nothing recorded to recall.`,
      }],
    };
  }
  try {
    const parts: string[] = [];
    let mHits: RecallHit[] = [];
    let sHits: RecallHit[] = [];
    let relaxedWith: string | null = null;
    let relaxReason = "";
    const search = (q: string) => {
      const m = scope === "messages" || scope === "all"
        ? queryMessages(store.db, q, limit, params?.after, params?.before) : [];
      const s = scope === "summaries" || scope === "all"
        ? querySummaries(store.db, q, limit) : [];
      return { m, s };
    };
    ({ m: mHits, s: sHits } = search(query));
    // Read-path relaxation, bounded and marked. The tool's entire purpose is
    // CROSS-session recall, so relaxation fires when the exact AND query
    // returns nothing at all OR nothing outside the current (most recent)
    // session - the recorded c1 failure mode, where the query terms all
    // matched the live prompt echo. A relaxed variant is accepted only if it
    // reaches prior-session content; otherwise the original result stands,
    // unmarked. Read-only throughout: same queries, less restrictive.
    const bounds = storeSessionBounds(store.db);
    const reachesPrior = (m: RecallHit[], s: RecallHit[]) =>
      [...m, ...s].some((h) => h.session_start < bounds.maxStart);
    const liveOnly = (mHits.length || sHits.length) && !reachesPrior(mHits, sHits)
      ? "matched only the current (most recent) session"
      : "";
    if (bounds.conversations > 1 && (!mHits.length && !sHits.length || liveOnly)) {
      relaxReason = liveOnly || "returned nothing";
      for (const variant of relaxedVariants(query)) {
        const r = search(variant);
        if (reachesPrior(r.m, r.s)) {
          mHits = r.m; sHits = r.s; relaxedWith = variant;
          break;
        }
      }
      if (!relaxedWith) relaxReason = "";
    }
    parts.push(
      `project_recall "${query}" (scope ${scope}, store ${store.path}, driver ${detectDriver()}, read-only): ` +
      `${mHits.length} message hit(s), ${sHits.length} summary hit(s). ` +
      (relaxedWith
        ? `RELAXATION-SOURCED: the exact query ${relaxReason}; results come from the relaxed query "${relaxedWith}" ` +
          `(progressive term-drop, still AND semantics) - check that these hits actually match your intent. `
        : "") +
      `Hits span ALL sessions of this project. Timestamps and source sessions are shown per hit - ` +
      `prefer the most recent statement of any value; older hits may be superseded.`
    );
    if (mHits.length) parts.push("Messages (newest first):\n" + formatHits(mHits));
    if (sHits.length) parts.push("Summaries (newest first):\n" + formatHits(sHits));
    if (!mHits.length && !sHits.length) parts.push("No matches. Nothing was fabricated.");
    return { content: [{ type: "text", text: parts.join("\n\n") }] };
  } finally {
    store.db.close();
  }
}

export default function (pi: any) {
  pi.registerTool({
    name: "project_recall",
    label: "Project Recall",
    description:
      "Search THIS PROJECT's memory store across ALL past sessions (not just this conversation): " +
      "messages and summaries recorded by earlier sessions in the same project directory. " +
      "Use it to find decisions, rejected approaches, failure explanations and prior work state " +
      "from previous sessions. Every hit carries its timestamp and source session - check them: " +
      "history may contain superseded values, and a later message overrides an earlier one.",
    promptSnippet: "Search all past sessions of this project",
    parameters,
    async execute(
      _toolCallId: string,
      params: {
        query: string;
        scope?: "messages" | "summaries" | "all";
        limit?: number;
        after?: string;
        before?: string;
      },
      _signal: AbortSignal,
      _onUpdate: any,
      _ctx: any,
    ) {
      return runRecall(process.cwd(), params);
    },
  });
  console.error(`pi-project-recall: registered project_recall (read-only, driver ${detectDriver()})`);
}
