/**
 * pi-recall-nudge: companion to pi-project-recall that AUTOMATICALLY delivers
 * the tested recall nudge (dispatch/recall-nudge-20260910.md).
 *
 * The rerun-20260910 evidence: the model never used project_recall
 * spontaneously (F1, 0/8), used it in 8/8 runs when the fixed F2 nudge
 * sentence was appended to the prompt (F2), and relaxed recall then flipped
 * the failure-critical case (f3, n=2, suggestive). This extension delivers
 * that nudge on Brian's prompts with no manual coaxing, visibly: every
 * injection is a persistent, displayed `[recall-nudge]` session message he
 * can log for his one-sentence-per-resumption trial record.
 *
 * Predeclared behavior (dispatch, "Behavior" section):
 *   - session_start with reason "resume" or "fork" sets a once-per-process
 *     "resumption pending" flag.
 *   - before_agent_start evaluates the gates on EACH prompt and injects at
 *     most ONE nudge per prompt (union of gates, deduped):
 *       onResume      first prompt after a resume/fork session_start
 *       everyPrompt   every prompt
 *       everyNPrompts every Nth prompt (N >= 1); the counter is IN-MEMORY and
 *                    resets per Pi process - a deck worker's Pi process can
 *                    live for days, which is exactly why this gate exists
 *   - Guard: inject only if project_recall is active this turn
 *     (systemPromptOptions.selectedTools); absent -> skip silently.
 *   - Delivery: { message: { customType: "recall-nudge", content:
 *     "[recall-nudge] " + nudgeText, display: true } } - message injection,
 *     not system-prompt, is the required default because it matches what
 *     F2/f3 actually tested (nudge carried in the message stream).
 *   - Env kill switch PI_RECALL_NUDGE=0 overrides everything.
 *
 * Overlapping-gate resolution (predeclared implementer choice): UNION - each
 * gate fires independently and a prompt matching several gates is nudged
 * exactly once; the receipt names every gate that fired.
 *
 * Config lives under the `recallNudge` key in the agent settings.json (the
 * same file/mechanism pi-lcm uses for its `lcm` key). Nonsensical values are
 * rejected LOUDLY at load: an explicit stderr notice names each problem and
 * the affected key falls back to its default.
 *
 * pi-project-recall/ stays byte-identical - this extension only reads
 * whether its tool is present. No tools, no store access, no writes.
 */

import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

/** The F2 nudge sentence, byte-for-byte (scripts/run_pi_pilot_r2.py F2_NUDGE). */
export const F2_NUDGE =
  "Before you edit anything, use the project_recall tool to check this " +
  "project's past sessions for decisions or constraints relevant to the task.";

export interface RecallNudgeConfig {
  enabled: boolean;
  nudge: string;
  onResume: boolean;
  everyPrompt: boolean;
  /** 0 = off; N >= 1 = every Nth prompt. Counter is in-memory, per process. */
  everyNPrompts: number;
  /** "message" = the visible session message; "systemPrompt" = that PLUS the sentence appended to the system prompt. */
  delivery: "message" | "systemPrompt";
}

export const DEFAULT_CONFIG: RecallNudgeConfig = {
  enabled: true,
  nudge: F2_NUDGE,
  onResume: true,
  everyPrompt: false,
  everyNPrompts: 0,
  delivery: "message",
};

export interface LoadedConfig {
  config: RecallNudgeConfig;
  /** One human-readable problem per rejected key/value; empty when clean. */
  problems: string[];
}

/** Validate a raw `recallNudge` value (undefined -> defaults, no problems). */
export function validateConfig(raw: unknown): LoadedConfig {
  const config: RecallNudgeConfig = { ...DEFAULT_CONFIG };
  const problems: string[] = [];
  if (raw === undefined || raw === null) return { config, problems };
  if (typeof raw !== "object" || Array.isArray(raw)) {
    return { config, problems: [`recallNudge must be an object, got ${typeof raw} - using all defaults`] };
  }
  const obj = raw as Record<string, unknown>;
  const known: Record<string, string> = {
    enabled: "boolean", nudge: "string", onResume: "boolean",
    everyPrompt: "boolean", everyNPrompts: "number", delivery: "string",
  };
  for (const key of Object.keys(obj)) {
    if (!(key in known)) {
      problems.push(`recallNudge.${key}: unknown key - ignored`);
    }
  }
  for (const [key, type] of Object.entries(known)) {
    if (!(key in obj) || obj[key] === undefined) continue;
    const v = obj[key];
    const bad = (why: string) => problems.push(`recallNudge.${key}: ${why} - using default ${JSON.stringify((DEFAULT_CONFIG as any)[key])}`);
    if (key === "everyNPrompts") {
      if (typeof v !== "number" || !Number.isInteger(v) || v < 0) {
        bad("must be an integer >= 0 (0 = off)");
        continue;
      }
      config.everyNPrompts = v;
    } else if (key === "delivery") {
      if (v !== "message" && v !== "systemPrompt") {
        bad(`must be "message" or "systemPrompt"`);
        continue;
      }
      config.delivery = v;
    } else if (key === "nudge") {
      if (typeof v !== "string" || !v.trim()) {
        bad("must be a non-empty string");
        continue;
      }
      config.nudge = v;
    } else if (typeof v !== typeof (DEFAULT_CONFIG as any)[key]) {
      bad(`must be ${type}`);
      continue;
    } else {
      (config as any)[key] = v;
    }
  }
  return { config, problems };
}

/** Read the agent settings.json (pi-lcm's mechanism: PI_CODING_AGENT_DIR else ~/.pi/agent) and extract recallNudge. */
export function loadConfig(agentDir?: string): LoadedConfig {
  const dir = agentDir ?? process.env.PI_CODING_AGENT_DIR ?? join(homedir(), ".pi", "agent");
  try {
    const settings = JSON.parse(readFileSync(join(dir, "settings.json"), "utf8"));
    return validateConfig(settings?.recallNudge);
  } catch {
    return { config: { ...DEFAULT_CONFIG }, problems: [] }; // no settings file/key: defaults, quietly
  }
}

// ── Gate evaluation (pure; the pi wiring is a thin shell) ───────────────────

export interface GateState {
  /** True from a resume/fork session_start until the first evaluated prompt. */
  resumptionPending: boolean;
  /** Prompts already evaluated in this Pi process (this prompt is +1). */
  promptsSeen: number;
}

export interface GateDecision {
  inject: boolean;
  /** Every gate that fired, deduped (one nudge regardless of count). */
  gates: string[];
  /** Whether this evaluation consumes the resumption-pending flag. */
  consumeResume: boolean;
}

/**
 * Union of gates, deduped. The resumption window is the FIRST prompt after a
 * resume/fork: it is consumed on evaluation regardless of whether anything
 * was injected (kill switch, disabled config or an absent tool do not move
 * the window to the next prompt).
 */
export function evaluateGates(config: RecallNudgeConfig, state: GateState): GateDecision {
  const gates: string[] = [];
  if (config.enabled) {
    if (config.onResume && state.resumptionPending) gates.push("onResume");
    if (config.everyPrompt) gates.push("everyPrompt");
    if (config.everyNPrompts >= 1 && (state.promptsSeen + 1) % config.everyNPrompts === 0) {
      gates.push("everyNPrompts");
    }
  }
  return { inject: gates.length > 0, gates, consumeResume: state.resumptionPending };
}

/**
 * Is project_recall active this turn? When the turn's selectedTools list is
 * defined, the tool must be in it; when it is undefined (no tool restriction
 * recorded) fall back to whether the tool is registered at all.
 */
export function recallToolActive(selectedTools: unknown, registered: boolean): boolean {
  if (Array.isArray(selectedTools)) return selectedTools.includes("project_recall");
  return registered;
}

/** The required visible delivery content. */
export function nudgeContent(nudge: string): string {
  return `[recall-nudge] ${nudge}`;
}

// ── The extension ───────────────────────────────────────────────────────────

export default function (pi: any) {
  const { config, problems } = loadConfig();
  for (const p of problems) {
    console.error(`pi-recall-nudge: CONFIG REJECTED - ${p}`);
  }
  if (!config.enabled) {
    console.error("pi-recall-nudge: disabled (recallNudge.enabled=false)");
  }
  console.error(
    `pi-recall-nudge: registered (onResume=${config.onResume} everyPrompt=${config.everyPrompt} ` +
    `everyNPrompts=${config.everyNPrompts} delivery=${config.delivery}; PI_RECALL_NUDGE=0 kills everything)`);

  let resumptionPending = false; // set by session_start resume|fork, consumed by the first evaluated prompt
  let promptsSeen = 0;           // in-memory, resets per Pi process (DOCUMENTED caveat)

  pi.on("session_start", (event: any) => {
    if (event?.reason === "resume" || event?.reason === "fork") {
      resumptionPending = true;
      console.error(`pi-recall-nudge: resumption pending (session_start reason=${event.reason})`);
    }
  });

  pi.on("before_agent_start", async (event: any) => {
    try {
      const killed = process.env.PI_RECALL_NUDGE === "0";
      let registered = false;
      try {
        registered = (pi.getAllTools?.() ?? []).some((t: any) => t?.name === "project_recall");
      } catch { /* stale extension ctx: a later copy owns this session */ }
      const toolOk = recallToolActive(event?.systemPromptOptions?.selectedTools, registered);

      const decision = evaluateGates(killed ? { ...config, enabled: false } : config, {
        resumptionPending,
        promptsSeen,
      });
      promptsSeen += 1;
      if (decision.consumeResume) resumptionPending = false;

      if (!decision.inject) return undefined;
      if (!toolOk) return undefined; // skip silently: never nudge toward an inactive tool

      const message = {
        customType: "recall-nudge",
        content: nudgeContent(config.nudge),
        display: true,
      };
      const receipt = {
        at: new Date().toISOString(),
        gates: decision.gates,
        promptChars: typeof event?.prompt === "string" ? event.prompt.length : 0,
        killed: false,
      };
      console.error(`pi-recall-nudge: injecting nudge (gates: ${decision.gates.join("+")})`);
      try { pi.appendEntry?.("pi-recall-nudge", receipt); } catch { /* receipt is best-effort */ }

      if (config.delivery === "systemPrompt" && typeof event?.systemPrompt === "string") {
        return { message, systemPrompt: `${event.systemPrompt}\n\n${config.nudge}` };
      }
      return { message };
    } catch (e: any) {
      // A nudge must never break the turn that triggered it.
      console.error(`pi-recall-nudge: PROBLEM nudge evaluation failed, continuing without nudge: ${e?.message ?? e}`);
      return undefined;
    }
  });
}
