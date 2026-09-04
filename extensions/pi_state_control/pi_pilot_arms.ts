/**
 * Gen44 pilot arms as a single Pi extension, selected by PI_PILOT_ARM.
 *
 *   pi_default_v1        observe only. Every provider request is captured for
 *                        measurement and Pi's own message array is returned
 *                        untouched, so the baseline is stock Pi behaviour.
 *   pi_state_control_v1  compose. The context hook returns the bounded view:
 *                        instructions, control, state, the last two complete
 *                        interaction units under a byte cap, the latest
 *                        observation, and validated artifact references.
 *
 * Both arms capture identical measurements. The difference between them is the
 * treatment, and it is confined to this file plus the three state/control tools.
 */

export const ARMS = ["pi_default_v1", "pi_state_control_v1"] as const;
export type Arm = (typeof ARMS)[number];

export const STATE_BYTE_CAP = 4096;
export const RECENT_WINDOW_UNITS = 2;
export const RECENT_WINDOW_BYTE_CAP = 8192;
export const LATEST_OBSERVATION_BYTE_CAP = 8192;

export const IMMUTABLE_INSTRUCTIONS =
  "You are working under an executable control layer. Move only along legal " +
  "transitions. Do not claim completion; earn it with a validated artifact.";

type Message = { role: string; content: unknown };

/** A unit starts at a user message and runs to the message before the next one. */
export function interactionUnits(messages: Message[]): Message[][] {
  const units: Message[][] = [];
  let current: Message[] | null = null;
  for (const message of messages) {
    if (message.role === "user") {
      if (current) units.push(current);
      current = [message];
    } else if (current) {
      current.push(message);
    }
  }
  if (current) units.push(current);
  return units;
}

export function recentWindow(
  messages: Message[],
  units = RECENT_WINDOW_UNITS,
  byteCap = RECENT_WINDOW_BYTE_CAP,
): { kept: Message[]; bytes: number } {
  const selected = interactionUnits(messages).slice(-units).flat();
  const kept: Message[] = [];
  let used = 0;
  for (let i = selected.length - 1; i >= 0; i--) {
    const size = JSON.stringify(selected[i]).length;
    if (used + size > byteCap) break;
    kept.unshift(selected[i]);
    used += size;
  }
  return { kept, bytes: used };
}

export interface RunCapture {
  arm: Arm;
  requests: Array<{ index: number; bytes: number; messages: number; composed: boolean }>;
  toolLog: Array<Record<string, unknown>>;
  state: Record<string, unknown>;
  phase: string;
  artifactRefs: unknown[];
  observation: unknown;
  historyEvents: number;
}

export function newCapture(arm: Arm): RunCapture {
  return {
    arm,
    requests: [],
    toolLog: [],
    state: { schema_version: 1, phase: "inspect", goal: "", next_actions: [] },
    phase: "inspect",
    artifactRefs: [],
    observation: null,
    historyEvents: 0,
  };
}

function cap(value: unknown, bytes: number): unknown {
  const text = JSON.stringify(value ?? null);
  if (text.length <= bytes) return value;
  return { truncated: true, kept_bytes: bytes, note: "full text retained in history" };
}

export function composed(capture: RunCapture, messages: Message[]): Message[] {
  const window = recentWindow(messages);
  const view = {
    instructions: IMMUTABLE_INSTRUCTIONS,
    control: { phase: capture.phase },
    state: cap(capture.state, STATE_BYTE_CAP),
    artifact_refs: capture.artifactRefs,
    latest_observation: cap(capture.observation, LATEST_OBSERVATION_BYTE_CAP),
  };
  return [
    { role: "user", content: [{ type: "text", text: JSON.stringify(view) }] },
    ...window.kept,
  ];
}

export default function pilotArm(pi: any) {
  const arm = (process.env.PI_PILOT_ARM ?? "pi_default_v1") as Arm;
  const capture = newCapture(arm);
  (globalThis as any).__piPilotCapture = capture;

  pi.on("context", (event: any) => {
    const incoming: Message[] = event.messages ?? [];
    if (arm === "pi_default_v1") {
      // Observation only. Returning nothing leaves Pi's array exactly as it was.
      capture.requests.push({
        index: capture.requests.length + 1,
        bytes: JSON.stringify(incoming).length,
        messages: incoming.length,
        composed: false,
      });
      return;
    }
    const replacement = composed(capture, incoming);
    capture.requests.push({
      index: capture.requests.length + 1,
      bytes: JSON.stringify(replacement).length,
      messages: replacement.length,
      composed: true,
    });
    return { messages: replacement };
  });

  pi.on("session_before_compact", () => {
    // Arm A keeps Pi's own compaction. Arm B externalizes history instead.
    if (arm === "pi_state_control_v1") return { cancel: true };
  });

  pi.on("tool_call", (event: any) => {
    capture.toolLog.push({ tool: event.toolName ?? event.type, args: event.input ?? {} });
    return {};
  });

  pi.on("tool_result", (event: any) => {
    const text = JSON.stringify(event.result ?? event.content ?? "");
    capture.observation = { bytes: text.length, text: text.slice(0, LATEST_OBSERVATION_BYTE_CAP) };
    capture.historyEvents += 1;
    return {};
  });
}
