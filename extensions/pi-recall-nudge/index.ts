/**
 * pi-recall-nudge: companion to pi-project-recall that supplies the prompted
 * half of the F2 finding automatically.
 *
 * The RERUN-20260910 evidence chain: with the store reachable, the model never
 * used project_recall spontaneously (F1, 0/8), but used it in 8/8 runs when a
 * fixed nudge sentence was appended to the resume prompt (F2), and relaxed
 * recall then flipped the failure-critical case (f3, n=2, suggestive). This
 * extension automates exactly that nudge - same fixed wording, same delivery
 * shape (appended to the current user prompt, seen on the model's first LLM
 * call of the session) - so the prompted habit does not depend on the user
 * remembering to type it.
 *
 * Properties:
 *   - No tools, no writes: it only transforms the message list the `context`
 *     event hands it, per request. The session transcript and the pi-lcm store
 *     are never modified - the user's recorded words stay exactly as typed.
 *   - Once per session: appended to the first armed user prompt of each
 *     session; later turns are left alone (F2 parity: the sentence was in the
 *     one opening prompt). Within that first turn the appended sentence is
 *     re-applied to every LLM call so the context the model sees stays
 *     consistent (the transform is not persisted between requests).
 *   - Gates, checked before the first application: the kill switch
 *     PI_RECALL_NUDGE=0; the project_recall tool actually registered (never
 *     nudge toward a tool that is not there); the project's store exists with
 *     at least 2 conversations (the live one plus a prior one - a fresh
 *     project has nothing to recall and gets no nudge); the prompt does not
 *     already contain the sentence; project_recall not already invoked this
 *     session.
 *   - Receipts: one stderr line per application and a durable session entry
 *     (appendEntry) recording when and why - evidence, not claims.
 */

import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve, normalize } from "node:path";
import { createRequire } from "node:module";

const require_ = createRequire(import.meta.url);

/** The F2 nudge sentence, verbatim (dispatch/RERUN-20260910.md, fixed wording). */
export const NUDGE_SENTENCE =
  "Before you edit anything, use the project_recall tool to check this " +
  "project's past sessions for decisions or constraints relevant to the task.";

// ── Store gate (parity: pi-project-recall resolveDbDir/hashCwd, duplicated
//    deliberately - separate packages, no cross-package import) ──────────────

export function hashCwd(cwd: string): string {
  return createHash("sha256").update(cwd).digest("hex").slice(0, 16);
}

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
  if (resolved.includes("..")) throw new Error(`pi-recall-nudge: dbDir must not contain '..': ${dir}`);
  return resolved;
}

export function storePathFor(cwd: string): string {
  return join(resolveDbDir(), `${hashCwd(cwd)}.db`);
}

function openReadOnly(path: string): { prepare(sql: string): { all(...p: unknown[]): unknown[] }; close(): void } | null {
  try {
    const { DatabaseSync } = require_("node:sqlite");
    const raw = new DatabaseSync(path, { readOnly: true });
    return { prepare: (sql) => raw.prepare(sql), close: () => raw.close() };
  } catch {
    try {
      const { Database } = require_("bun:sqlite");
      const raw = new Database(path, { readonly: true });
      return { prepare: (sql) => raw.prepare(sql), close: () => raw.close() };
    } catch {
      return null;
    }
  }
}

/**
 * True when the project's store exists and holds at least 2 conversations -
 * the live session pi-lcm opens at startup plus at least one prior session.
 * Read-only, best effort: any error means "do not nudge" (this extension must
 * never be the reason a request fails).
 */
export function priorSessionsExist(cwd: string): boolean {
  const path = storePathFor(cwd);
  if (!existsSync(path)) return false;
  const db = openReadOnly(path);
  if (!db) return false;
  try {
    const rows = db.prepare("SELECT COUNT(*) AS n FROM conversations").all() as any[];
    return Number(rows[0]?.n ?? 0) >= 2;
  } catch {
    return false;
  } finally {
    try { db.close(); } catch { /* already closed */ }
  }
}

// ── Message handling (loose structural, like pi-lcm's slim.ts MessageLike) ──

/** Plain-text view of a user message, joining its text blocks. */
export function userText(message: any): string {
  const content = message?.content;
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content.filter((b) => b?.type === "text").map((b) => b.text ?? "").join(" ");
  }
  return "";
}

/** Idempotent append: never doubles a sentence that is already there. */
export function nudgeAppend(text: string): string {
  return text.includes(NUDGE_SENTENCE) ? text : `${text} ${NUDGE_SENTENCE}`.trimStart();
}

/**
 * A copy of the message with the sentence appended to its textual content:
 * string content gains a suffix; block content gains it on its LAST text
 * block (earlier blocks are never duplicated into it); a block list with no
 * text gains one text block. Returns null when the sentence is already
 * present (idempotent) or the content shape is unusable.
 */
export function appendSentence(message: any, sentence: string): any | null {
  const content = message?.content;
  if (content === undefined || content === null || typeof content === "string") {
    const base = content ?? "";
    if (base.includes(sentence)) return null;
    return { ...message, content: base ? `${base} ${sentence}` : sentence };
  }
  if (Array.isArray(content)) {
    if (userText(message).includes(sentence)) return null;
    const idx = content.map((b: any) => b?.type).lastIndexOf("text");
    if (idx === -1) return { ...message, content: [...content, { type: "text", text: sentence }] };
    const blocks = content.slice();
    const prev = blocks[idx].text ?? "";
    blocks[idx] = { ...blocks[idx], text: prev ? `${prev} ${sentence}` : sentence };
    return { ...message, content: blocks };
  }
  return null;
}

/**
 * Return the message list with the nudge appended to its last user message.
 * The original message objects are never mutated. Returns null when there is
 * no user message, or when the sentence is already present.
 */
export function applyNudge(messages: any[]): { messages: any[]; original: string; nudged: string } | null {
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    if (m?.role !== "user") continue;
    const updated = appendSentence(m, NUDGE_SENTENCE);
    if (!updated) return null; // already nudged, or unusable content shape
    const out = messages.slice();
    out[i] = updated;
    return { messages: out, original: userText(m), nudged: userText(updated) };
  }
  return null;
}

/** Same append for later requests in the armed turn: original text in, nudged out. */
export function swapNudged(messages: any[], original: string, _nudged: string): any[] | null {
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    if (m?.role !== "user") continue;
    if (userText(m) === original) {
      const updated = appendSentence(m, NUDGE_SENTENCE);
      if (!updated) return null;
      const out = messages.slice();
      out[i] = updated;
      return out;
    }
    return null; // already nudged, or a different, later user message - the armed turn is over
  }
  return null;
}

// ── Controller (pure state machine; the pi wiring is a thin shell) ──────────

export type NudgePhase = "armed" | "applied" | "off";

export interface NudgeDeps {
  cwd(): string;
  recallToolRegistered(): boolean;
  priorSessions(cwd: string): boolean;
  now(): string;
}

export interface NudgeDecision {
  messages?: any[];
  /** stderr receipt line; absent when nothing happened. */
  log?: string;
  /** durable session-entry payload for appendEntry; absent when nothing happened. */
  entry?: { at: string; action: string; reason?: string; promptChars?: number };
}

export function createNudgeController(deps: NudgeDeps) {
  let phase: NudgePhase = "armed";
  let original = "";
  let nudged = "";
  let offReason = "";

  function disarm(reason: string): NudgeDecision {
    phase = "off";
    offReason = reason;
    return {
      log: `pi-recall-nudge: not nudging this session (${reason})`,
      entry: { at: deps.now(), action: "skip", reason },
    };
  }

  return {
    onSessionStart(): void {
      phase = "armed";
      original = "";
      nudged = "";
      offReason = "";
    },

    /** Fires on tool_execution_start: spontaneous/manual recall use disarms an unapplied nudge. */
    onRecallUsed(): void {
      if (phase === "armed") {
        phase = "off";
        offReason = "project_recall already invoked";
      }
    },

    onContext(messages: any[]): NudgeDecision {
      if (phase === "off") return {};
      if (process.env.PI_RECALL_NUDGE === "0") {
        return disarm("PI_RECALL_NUDGE=0");
      }
      if (phase === "applied") {
        const swapped = swapNudged(messages, original, nudged);
        return swapped ? { messages: swapped } : {};
      }
      // armed: evaluate the gates once, then commit either way.
      if (!deps.recallToolRegistered()) return disarm("project_recall not registered");
      if (!deps.priorSessions(deps.cwd())) return disarm("no prior-session store for this project");
      const applied = applyNudge(messages);
      if (!applied) return disarm("no user prompt to nudge, or sentence already present");
      phase = "applied";
      original = applied.original;
      nudged = applied.nudged;
      return {
        messages: applied.messages,
        log: `pi-recall-nudge: appended the F2 nudge sentence to this session's first prompt ` +
          `(${original.length} -> ${nudged.length} chars, session store has prior conversations; ` +
          `the session transcript keeps the prompt as typed)`,
        entry: {
          at: deps.now(),
          action: "nudge",
          reason: "first prompt of session; project_recall registered; prior sessions exist",
          promptChars: original.length,
        },
      };
    },

    state(): { phase: NudgePhase; reason: string } {
      return { phase, reason: offReason };
    },
  };
}

// ── The extension ───────────────────────────────────────────────────────────

export default function (pi: any) {
  const controller = createNudgeController({
    cwd: () => process.cwd(),
    recallToolRegistered() {
      try {
        return (pi.getAllTools?.() ?? []).some((t: any) => t?.name === "project_recall");
      } catch {
        // Stale extension ctx (session replaced) - a later copy owns this now.
        return false;
      }
    },
    priorSessions: priorSessionsExist,
    now: () => new Date().toISOString(),
  });

  pi.on("session_start", () => controller.onSessionStart());
  pi.on("tool_execution_start", (event: any) => {
    if (event?.toolName === "project_recall") controller.onRecallUsed();
  });

  pi.on("context", async (event: any) => {
    try {
      const decision = controller.onContext(event?.messages ?? []);
      if (decision.log) console.error(decision.log);
      if (decision.entry) {
        try { pi.appendEntry?.("pi-recall-nudge", decision.entry); } catch { /* receipt is best-effort */ }
      }
      return decision.messages ? { messages: decision.messages } : undefined;
    } catch (e: any) {
      // A nudge must never break the request that triggered it.
      console.error(`pi-recall-nudge: PROBLEM nudge transform failed, sending the context untouched: ${e?.message ?? e}`);
      return undefined;
    }
  });

  console.error("pi-recall-nudge: registered (F2 nudge companion for project_recall; PI_RECALL_NUDGE=0 disables)");
}
