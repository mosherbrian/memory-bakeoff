/**
 * Gen43 Pi-native binding for the state/control prototype.
 *
 * Pi-native, not a fork: every capability below is a public extension hook of
 * the installed Pi. The extension owns nothing scientific — it records events
 * to the lossless history and replaces the live context with the composed
 * state/control view. The rules live in the Python contract; this file proves
 * the separations are reachable from Pi's own API.
 *
 * The load-bearing hook is `context`: its handler returns a replacement
 * message array, which is what makes "do not replay the whole transcript"
 * implementable without patching Pi core.
 */

type Handler = (event: any, ctx?: any) => any;

export interface ComposedView {
  instructions: string;
  phase: string;
  legalNext: string[];
  state: Record<string, unknown>;
  observation: unknown;
  recalled: unknown[];
}

/** Minimal in-process mirror of the frozen contract, for the Pi side. */
export const TRANSITIONS: Record<string, string[]> = {
  inspect: ["plan", "blocked"],
  plan: ["implement", "inspect", "blocked"],
  implement: ["validate", "plan", "blocked"],
  validate: ["done", "implement", "blocked"],
  done: [],
  blocked: ["inspect", "plan", "implement", "validate"],
};

export const IMMUTABLE_INSTRUCTIONS =
  "You are working under an executable control layer. Move only along legal " +
  "transitions. Do not claim completion; earn it with a validated artifact.";

export function legalTransition(current: string, target: string): boolean {
  return (TRANSITIONS[current] ?? []).includes(target);
}

export interface StateControlStore {
  phase: string;
  state: Record<string, unknown>;
  observation: unknown;
  history: Array<{ id: string; type: string; payload: unknown }>;
}

export function createStore(goal: string): StateControlStore {
  return {
    phase: "inspect",
    state: { schema_version: 1, phase: "inspect", goal, next_actions: [] },
    observation: null,
    history: [],
  };
}

export function record(store: StateControlStore, type: string, payload: unknown) {
  const event = { id: `e${String(store.history.length).padStart(6, "0")}`, type, payload };
  store.history.push(event);
  return event;
}

/** The composed live context. The transcript is never replayed. */
export function compose(store: StateControlStore): ComposedView {
  return {
    instructions: IMMUTABLE_INSTRUCTIONS,
    phase: store.phase,
    legalNext: TRANSITIONS[store.phase] ?? [],
    state: store.state,
    observation: store.observation,
    recalled: [],
  };
}

export default function piStateControl(pi: any) {
  const store = createStore(process.env.PI_STATE_CONTROL_GOAL ?? "unset");

  pi.on("session_start", (event: any) => {
    record(store, "session_start", { reason: event.reason });
  });

  pi.on("input", (event: any) => {
    record(store, "user_input", { text: event.text, source: event.source });
    return { action: "continue" };
  });

  // The context-control hook. Returning `messages` replaces what Pi sends.
  pi.on("context", (event: any) => {
    record(store, "context_replaced", { incoming: event.messages?.length ?? 0 });
    return {
      messages: [
        {
          role: "user",
          content: [{ type: "text", text: JSON.stringify(compose(store)) }],
        },
      ],
    };
  });

  pi.on("before_agent_start", () => {
    record(store, "before_agent_start", {});
    return { systemPrompt: IMMUTABLE_INSTRUCTIONS };
  });

  pi.on("tool_call", (event: any) => {
    record(store, "tool_call", { tool: event.toolName ?? event.type });
    return {};
  });

  pi.on("tool_result", (event: any) => {
    const text = JSON.stringify(event.result ?? event.content ?? "");
    record(store, "tool_result", { bytes: text.length });
    store.observation = { bytes: text.length };
    return {};
  });

  pi.on("turn_end", (event: any) => {
    record(store, "turn_end", { turnIndex: event.turnIndex });
  });

  // Compaction is not how history is bounded here; history stays lossless.
  pi.on("session_before_compact", () => {
    record(store, "compaction_declined", {});
    return { cancel: true };
  });

  pi.on("session_shutdown", (event: any) => {
    record(store, "session_shutdown", { reason: event.reason });
  });

  (globalThis as any).__piStateControlStore = store;
}
