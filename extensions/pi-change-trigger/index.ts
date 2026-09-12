/**
 * pi-change-trigger — CAMPAIGN-1 workstream B (change-aware retrieval
 * triggering). The measured weakness (RETRO-1/R2 record): memory is present
 * and correct but the agent does not LOOK unless nudged, and the standing
 * nudge is static. This extension fires a visible check-memory prompt when
 * circumstances suggest a stored decision is relevant:
 *
 *   fresh  — first evaluated prompt of the process (new/resumed session);
 *   gap    — ≥ changeTrigger.gapMinutes since the previous evaluated prompt
 *            (in-process; cross-process gaps are a documented v1 limit);
 *   topic  — the prompt shares a topic token (len ≥ 4, stopword-filtered)
 *            with a stored decision, sourced from the trial's plaintext
 *            notify ledger summaries (every confirmed record was drafted, so
 *            every confirmed record has a summary line; operator CLI seeds
 *            do not — documented v1 limit).
 *
 * Frozen-rule conformance (team/S4-ADJUDICATION.md): the fire log records
 * EVERY evaluation — fired or not — with the prompt's sha256 and length,
 * NEVER the prompt text (the blind rater's packets are built from session
 * logs by the committed redaction script; trigger state reaches her only at
 * unblinding, B4.6). The log is the S4(a) numerator + false-fire feed; it is
 * not an input to any ruling.
 *
 * Delivery: one visible session message (same shape as pi-recall-nudge).
 * Read-only over the vault; registers no tools; never blocks the turn (any
 * internal failure → log the failure, inject nothing, return undefined).
 * Kill switch: PI_CHANGE_TRIGGER=0.
 */
import { createHash } from "node:crypto";
import { appendFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";

export interface ChangeTriggerConfig {
  enabled: boolean;
  gapMinutes: number;
  topicsFile: string | null;
  fireLog: string | null;
}

export const DEFAULTS: ChangeTriggerConfig = {
  enabled: true,
  gapMinutes: 30,
  topicsFile: null,
  fireLog: null,
};

export interface LoadedConfig {
  config: ChangeTriggerConfig;
  problems: string[];
}

export function validateConfig(raw: unknown): LoadedConfig {
  const config: ChangeTriggerConfig = { ...DEFAULTS };
  const problems: string[] = [];
  if (raw === undefined || raw === null) return { config, problems };
  if (typeof raw !== "object" || Array.isArray(raw)) {
    problems.push("changeTrigger must be an object - using all defaults");
    return { config, problems };
  }
  const o = raw as Record<string, unknown>;
  if (o.enabled !== undefined) {
    if (typeof o.enabled !== "boolean") problems.push("changeTrigger.enabled must be a boolean - using default true");
    else config.enabled = o.enabled;
  }
  if (o.gapMinutes !== undefined) {
    if (typeof o.gapMinutes !== "number" || !Number.isInteger(o.gapMinutes) || o.gapMinutes < 1) {
      problems.push("changeTrigger.gapMinutes must be an integer >= 1 - using default 30");
    } else config.gapMinutes = o.gapMinutes;
  }
  if (o.topicsFile !== undefined) {
    if (typeof o.topicsFile !== "string" || !o.topicsFile.trim()) {
      problems.push("changeTrigger.topicsFile must be a non-empty string when set");
    } else config.topicsFile = o.topicsFile;
  }
  if (o.fireLog !== undefined) {
    if (typeof o.fireLog !== "string" || !o.fireLog.trim()) {
      problems.push("changeTrigger.fireLog must be a non-empty string when set");
    } else config.fireLog = o.fireLog;
  }
  return { config, problems };
}

export function loadConfig(agentDir?: string): LoadedConfig {
  const dir = agentDir ?? process.env.PI_CODING_AGENT_DIR ?? join(homedir(), ".pi", "agent");
  try {
    const settings = JSON.parse(readFileSync(join(dir, "settings.json"), "utf8"));
    return validateConfig(settings?.changeTrigger);
  } catch {
    return { config: { ...DEFAULTS }, problems: [] };
  }
}

// ── topic tokens from the plaintext notify ledger ───────────────────────────

const STOPWORDS = new Set([
  "this", "that", "with", "from", "into", "have", "been", "will", "shall",
  "they", "them", "their", "there", "then", "than", "when", "what", "which",
  "where", "were", "been", "also", "only", "over", "under", "about", "after",
  "before", "while", "being", "does", "done", "each", "such", "some", "more",
  "most", "other", "same", "very", "upon", "said", "create", "created",
  "decision", "environment", "project", "trial", "record", "tool", "call",
  "confirm", "confirmed", "draft", "pending", "campaign1", "campaign-1",
  "window", "opening", "exists", "never", "still", "uses", "using", "used",
]);

/** Tokens (len ≥ 4, stopword-filtered, lowercase) of a summary string. */
export function tokensOf(text: string): string[] {
  return (text.toLowerCase().match(/[a-z0-9][a-z0-9-]{3,}/g) ?? [])
    .filter((t) => !STOPWORDS.has(t));
}

/** Topic set from the notify ledger's plaintext summaries. Best-effort. */
export function topicsFromNotifyFile(path: string): { topics: Set<string>; notes: string[] } {
  const topics = new Set<string>();
  const notes: string[] = [];
  if (!path || !existsSync(path)) {
    notes.push(`topicsFile missing/unreadable: ${path}`);
    return { topics, notes };
  }
  const lines = readFileSync(path, "utf8").split("\n").filter((l) => l.trim());
  for (const line of lines) {
    try {
      const rec = JSON.parse(line);
      if (typeof rec?.summary === "string") {
        for (const t of tokensOf(rec.summary)) topics.add(t);
      }
    } catch {
      notes.push("skipped unparseable notify line");
    }
  }
  return { topics, notes };
}

/** Prompt tokens that hit the topic set (the trigger's evidence). */
export function topicMatches(prompt: string, topics: Set<string>): string[] {
  const seen = new Set<string>();
  for (const t of tokensOf(prompt)) if (topics.has(t) && !seen.has(t)) seen.add(t);
  return [...seen];
}

// ── fire decision ───────────────────────────────────────────────────────────

export type FireReason = "fresh" | "gap" | "topic";

export interface FireDecision {
  fired: boolean;
  reasons: FireReason[];
  matchedTokens: string[];
  gapMinutesActual: number | null;
}

export function evaluateFire(input: {
  isFirstPrompt: boolean;
  minutesSinceLastPrompt: number | null;
  prompt: string;
  topics: Set<string>;
  gapMinutes: number;
}): FireDecision {
  const reasons: FireReason[] = [];
  if (input.isFirstPrompt) reasons.push("fresh");
  if (input.minutesSinceLastPrompt !== null && input.minutesSinceLastPrompt >= input.gapMinutes) {
    reasons.push("gap");
  }
  const matched = topicMatches(input.prompt, input.topics);
  if (matched.length >= 1) reasons.push("topic");
  return { fired: reasons.length > 0, reasons, matchedTokens: matched, gapMinutesActual: input.minutesSinceLastPrompt };
}

export function triggerMessage(reasons: FireReason[], matched: string[]): string {
  const why = reasons.includes("topic") && matched.length
    ? `this turn mentions: ${matched.slice(0, 6).join(", ")}`
    : reasons.join(" + ");
  return "[change-trigger] A stored project decision may be relevant to this turn — "
    + `check project memory with project_perseus_recall before acting (${why}).`;
}

// ── the extension ───────────────────────────────────────────────────────────

export default function (pi: any) {
  if (process.env.PI_CHANGE_TRIGGER === "0") {
    console.error("pi-change-trigger: disabled (PI_CHANGE_TRIGGER=0)");
    return;
  }
  const { config, problems } = loadConfig();
  for (const p of problems) console.error(`pi-change-trigger: CONFIG REJECTED - ${p}`);
  if (!config.enabled) {
    console.error("pi-change-trigger: disabled (changeTrigger.enabled=false)");
    return;
  }
  if (!config.fireLog) {
    console.error("pi-change-trigger: no fireLog configured - S4 feed would be unrecordable; not registering");
    return;
  }

  let isFirstPrompt = true;
  let lastPromptAt: number | null = null;
  let turnIndex = 0;

  pi.on("before_agent_start", (event: any) => {
    try {
      const prompt: string = typeof event?.prompt === "string" ? event.prompt : "";
      turnIndex += 1;
      const now = Date.now();
      const minutesSinceLastPrompt = lastPromptAt === null ? null : (now - lastPromptAt) / 60000;
      const { topics } = topicsFromNotifyFile(config.topicsFile ?? "");
      const decision = evaluateFire({
        isFirstPrompt,
        minutesSinceLastPrompt,
        prompt,
        topics,
        gapMinutes: config.gapMinutes,
      });
      isFirstPrompt = false;
      lastPromptAt = now;

      // S4 feed: every evaluation logged; prompt TEXT never leaves this file.
      const logLine = {
        at: new Date(now).toISOString(),
        turn: turnIndex,
        prompt_sha256: createHash("sha256").update(prompt).digest("hex"),
        prompt_len: prompt.length,
        fired: decision.fired,
        reasons: decision.reasons,
        matched_tokens: decision.matchedTokens,
        gap_minutes: decision.gapMinutesActual === null ? null
          : Math.round(decision.gapMinutesActual * 1000) / 1000,
      };
      try {
        mkdirSync(dirname(config.fireLog!), { recursive: true });
        appendFileSync(config.fireLog!, JSON.stringify(logLine) + "\n");
      } catch (e: any) {
        console.error(`pi-change-trigger: fire-log append failed: ${e?.message ?? e}`);
      }

      if (!decision.fired) return undefined;
      console.error(`pi-change-trigger: FIRING (${decision.reasons.join("+")}) turn ${turnIndex}`);
      try { pi.appendEntry?.("pi-change-trigger", logLine); } catch { /* best-effort */ }
      return {
        message: {
          customType: "change-trigger",
          content: triggerMessage(decision.reasons, decision.matchedTokens),
          display: true,
        },
      };
    } catch (e: any) {
      console.error(`pi-change-trigger: evaluation failed, continuing without trigger: ${e?.message ?? e}`);
      return undefined;
    }
  });

  console.error(
    `pi-change-trigger: registered (gapMinutes=${config.gapMinutes}, `
    + `topicsFile=${config.topicsFile ?? "none"}, fireLog=${config.fireLog ?? "NONE"}; `
    + `PI_CHANGE_TRIGGER=0 kills)`,
  );
}
