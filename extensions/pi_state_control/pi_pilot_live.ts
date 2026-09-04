/**
 * Gen45 live pilot extension: both arms, in the installed Pi, with no core patch.
 *
 * PI_PILOT_ARM selects the arm.
 *
 *   pi_default_v1        capture only. The context handler records the request
 *                        size and returns nothing, so Pi's own message array is
 *                        what goes to the model and Pi's compaction stays on.
 *   pi_state_control_v1  the Gen43/44 treatment. The context handler returns the
 *                        composed view, Pi compaction is cancelled because the
 *                        history is externalized, and three tools let the model
 *                        drive state and control through validation rather than
 *                        by writing prose.
 *
 * Everything the harness measures is written to PI_PILOT_OUT as it happens, so a
 * crashed run still leaves its evidence behind.
 */
import { createHash } from "node:crypto";
import { appendFileSync, mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { Type } from "@sinclair/typebox";

// --- frozen contract mirror --------------------------------------------------

const TRANSITIONS: Record<string, string[]> = {
  inspect: ["plan", "blocked"],
  plan: ["implement", "inspect", "blocked"],
  implement: ["validate", "plan", "blocked"],
  validate: ["done", "implement", "blocked"],
  done: [],
  blocked: ["inspect", "plan", "implement", "validate"],
};
const GATED = { done: "validation_receipt" } as const;

const STATE_BYTE_CAP = 4096;
const RECENT_WINDOW_UNITS = 2;
const RECENT_WINDOW_BYTE_CAP = 8192;
const LATEST_OBSERVATION_BYTE_CAP = 8192;

const LIST_BOUNDS: Record<string, number> = {
  active_files: 6,
  important_findings: 8,
  completed_checkpoints: 6,
  next_actions: 5,
  open_questions: 5,
  blockers: 4,
  validated_artifact_refs: 4,
};

const IMMUTABLE_INSTRUCTIONS =
  "You are working under an executable control layer. Phases are inspect, plan, " +
  "implement, validate, done. Move only along legal transitions with request_transition. " +
  "Record what matters with propose_state_patch; the state below is all you carry forward. " +
  "Do not claim completion: record a validation receipt with record_receipt and then " +
  "request the done transition, which is refused unless the receipt still validates.";

const canonical = (value: unknown) => JSON.stringify(value ?? null);
const sha256 = (text: string) => createHash("sha256").update(text).digest("hex");

// --- run-local storage -------------------------------------------------------

const ARM = (process.env.PI_PILOT_ARM ?? "pi_default_v1") as string;
const OUT = process.env.PI_PILOT_OUT ?? "/tmp/pi-pilot-run";
const WORKTREE = process.env.PI_PILOT_WORKTREE ?? process.cwd();
mkdirSync(OUT, { recursive: true });

const HISTORY = join(OUT, "history.ndjson");
const REQUESTS = join(OUT, "requests.ndjson");
const TOOLS = join(OUT, "tools.ndjson");
const STATE_FILE = join(OUT, "state.json");
const EVENTS = join(OUT, "control.ndjson");

const line = (path: string, payload: unknown) => appendFileSync(path, canonical(payload) + "\n");

let historyCount = 0;
let historyBytes = 0;
let historyOnlyBytes = 0;
let previousDigest = "0".repeat(64);

function record(type: string, payload: unknown) {
  const event: Record<string, unknown> = {
    seq: historyCount,
    id: `e${String(historyCount).padStart(6, "0")}`,
    type,
    payload,
    prev_digest: previousDigest,
  };
  event.digest = sha256(canonical(event));
  previousDigest = event.digest as string;
  historyCount += 1;
  const text = canonical(event);
  historyBytes += text.length;
  appendFileSync(HISTORY, text + "\n");
  return event;
}

// --- state -------------------------------------------------------------------

type State = Record<string, unknown>;

let state: State = {
  schema_version: 1,
  phase: "inspect",
  goal: process.env.PI_PILOT_GOAL ?? "",
  active_files: [],
  important_findings: [],
  completed_checkpoints: [],
  current_process_or_tool: "",
  next_actions: [],
  open_questions: [],
  blockers: [],
  validated_artifact_refs: [],
  last_observation_ref: "",
};
let revision = 0;

const counters = {
  patches_accepted: 0,
  patches_rejected: 0,
  transitions_accepted: 0,
  transitions_rejected: 0,
  blocked_completions: 0,
  artifact_revalidations: 0,
  artifact_failures: 0,
  compaction_cancelled: 0,
};

const persist = () => writeFileSync(STATE_FILE, canonical({ state, revision, counters }));
persist();

function applyOps(base: State, ops: any[]): State {
  const next: State = JSON.parse(canonical(base));
  for (const op of ops) {
    const field = op?.field;
    if (typeof field !== "string" || !(field in next)) throw new Error(`unknown field ${field}`);
    if (field === "phase") throw new Error("phase changes go through request_transition");
    if (op.op === "set") {
      if (Array.isArray(next[field]) && !Array.isArray(op.value)) {
        throw new Error(
          `${field} holds a list; send {"op":"append","field":"${field}","value":<one item>} ` +
          `to add a single entry, or set it with a JSON array`,
        );
      }
      if (!Array.isArray(next[field]) && Array.isArray(op.value)) {
        throw new Error(`${field} holds a single value, not a list`);
      }
      next[field] = op.value;
    } else if (op.op === "append") {
      if (!Array.isArray(next[field])) throw new Error(`${field} is not a list`);
      (next[field] as unknown[]).push(op.value);
    } else if (op.op === "remove") {
      if (!Array.isArray(next[field])) throw new Error(`${field} is not a list`);
      next[field] = (next[field] as unknown[]).filter((v) => canonical(v) !== canonical(op.value));
    } else {
      throw new Error(`unknown op ${op.op}`);
    }
  }
  for (const [field, bound] of Object.entries(LIST_BOUNDS)) {
    const values = next[field] as unknown[];
    if (Array.isArray(values) && values.length > bound) {
      const overflow = values.slice(0, values.length - bound);
      record("state_overflow_archived", { field, entries: overflow });
      next[field] = values.slice(values.length - bound);
    }
  }
  if (canonical(next).length > STATE_BYTE_CAP) {
    throw new Error(`state would be ${canonical(next).length} bytes, over the ${STATE_BYTE_CAP} bound`);
  }
  return next;
}

function artifactValid(ref: any): { ok: boolean; reason: string } {
  const target = resolve(WORKTREE, String(ref?.path ?? ""));
  if (!existsSync(target)) return { ok: false, reason: "artifact missing" };
  const now = sha256(readFileSync(target).toString("binary"));
  if (now !== ref.digest) return { ok: false, reason: "digest changed since the receipt" };
  if (!ref.passed) return { ok: false, reason: "receipt records a failed check" };
  return { ok: true, reason: "valid" };
}

// --- context composition -----------------------------------------------------

type Message = { role: string; content: unknown };

function interactionUnits(messages: Message[]): Message[][] {
  const units: Message[][] = [];
  let current: Message[] | null = null;
  for (const message of messages) {
    if (message.role === "user") {
      if (current) units.push(current);
      current = [message];
    } else if (current) current.push(message);
  }
  if (current) units.push(current);
  return units;
}

function recentWindow(messages: Message[]): Message[] {
  const selected = interactionUnits(messages).slice(-RECENT_WINDOW_UNITS).flat();
  const kept: Message[] = [];
  let used = 0;
  for (let i = selected.length - 1; i >= 0; i--) {
    const size = canonical(selected[i]).length;
    if (used + size > RECENT_WINDOW_BYTE_CAP) break;
    kept.unshift(selected[i]);
    used += size;
  }
  return kept;
}

let latestObservation: unknown = null;

function compose(messages: Message[]): Message[] {
  const observation = canonical(latestObservation).length > LATEST_OBSERVATION_BYTE_CAP
    ? { truncated: true, note: "full tool output retained in history" }
    : latestObservation;
  const view = {
    instructions: IMMUTABLE_INSTRUCTIONS,
    control: { phase: state.phase, legal_next: TRANSITIONS[String(state.phase)] ?? [], gates: GATED },
    state_revision: revision,
    patchable_fields: Object.keys(state).filter((f) => f !== "phase" && f !== "schema_version"),
    state,
    latest_observation: observation,
    artifact_refs: state.validated_artifact_refs,
  };
  return [
    { role: "user", content: [{ type: "text", text: canonical(view) }] },
    ...recentWindow(messages),
  ];
}

// --- extension ---------------------------------------------------------------

export default function pilot(pi: any) {
  const armB = ARM === "pi_state_control_v1";
  record("run_start", { arm: ARM, goal: state.goal, worktree: WORKTREE });

  pi.on("context", (event: any) => {
    const incoming: Message[] = event.messages ?? [];
    if (!armB) {
      line(REQUESTS, {
        index: undefined,
        bytes: canonical(incoming).length,
        messages: incoming.length,
        composed: false,
        state_bytes: null,
        history_bytes: historyBytes,
      });
      return;
    }
    const replacement = compose(incoming);
    line(REQUESTS, {
      bytes: canonical(replacement).length,
      messages: replacement.length,
      composed: true,
      pi_would_have_sent_bytes: canonical(incoming).length,
      state_bytes: canonical(state).length,
      history_bytes: historyBytes,
      history_only_bytes: historyOnlyBytes,
    });
    return { messages: replacement };
  });

  // Observation only. Pi's runner keeps the original payload unless a handler
  // returns something (`if (handlerResult !== undefined)` in runner.js), so
  // returning nothing here cannot rewrite the request. This is the only place
  // the FULL provider payload is visible, including tool schemas, which matters
  // because the two arms offer different tool surfaces.
  pi.on("before_provider_request", (event: any) => {
    line(REQUESTS.replace("requests.ndjson", "payloads.ndjson"),
         { bytes: JSON.stringify(event.payload ?? null).length });
  });

  pi.on("session_before_compact", () => {
    if (armB) {
      counters.compaction_cancelled += 1;
      record("compaction_cancelled", {});
      persist();
      return { cancel: true };
    }
    record("compaction_allowed", {});
  });

  pi.on("tool_call", (event: any) => {
    line(TOOLS, { phase: "call", tool: event.toolName ?? event.type, args: event.input ?? {} });
    return {};
  });

  pi.on("tool_result", (event: any) => {
    const text = canonical(event.result ?? event.content ?? "");
    const event_id = record("tool_result", { tool: event.toolName ?? "", output: text }).id;
    if (text.length > LATEST_OBSERVATION_BYTE_CAP) historyOnlyBytes += text.length;
    latestObservation = { event_id, bytes: text.length, text: text.slice(0, LATEST_OBSERVATION_BYTE_CAP) };
    state.last_observation_ref = event_id;
    line(TOOLS, { phase: "result", tool: event.toolName ?? "", bytes: text.length });
    return {};
  });

  pi.on("session_shutdown", (event: any) => {
    record("session_shutdown", { reason: event.reason });
    persist();
  });

  if (!armB) return;

  pi.registerTool({
    name: "propose_state_patch",
    label: "Update execution state",
    description:
      "Update the structured execution state. Send base_revision, which must equal the " +
      "state_revision shown in the context, and a list of ops. Each op is " +
      "{op, field, value} where op is set, append or remove, and field is one of: " +
      "goal, active_files, important_findings, completed_checkpoints, current_process_or_tool, " +
      "next_actions, open_questions, blockers, validated_artifact_refs, last_observation_ref. " +
      "The value must match that field's type: a string for goal and " +
      "current_process_or_tool, a list otherwise, and for append or remove a single element. " +
      "phase is NOT patchable; use request_transition. Rejected patches change nothing. " +
      "Example: {\"base_revision\": 0, \"ops\": [{\"op\": \"append\", \"field\": " +
      "\"important_findings\", \"value\": \"the parser ignores its second argument\"}]}",
    parameters: Type.Object({
      base_revision: Type.Number(),
      ops: Type.Array(Type.Object({
        op: Type.String(),
        field: Type.String(),
        value: Type.Any(),
      })),
    }),
    async execute(_id: string, params: any) {
      try {
        if (params.base_revision !== revision) {
          throw new Error(`stale patch: base ${params.base_revision} != ${revision}`);
        }
        state = applyOps(state, params.ops);
        revision += 1;
        counters.patches_accepted += 1;
        record("state_patch_accepted", { ops: params.ops, revision });
        persist();
        return { output: `state accepted at revision ${revision}`, isError: false };
      } catch (error: any) {
        counters.patches_rejected += 1;
        record("state_patch_rejected", { ops: params.ops, reason: String(error?.message ?? error) });
        persist();
        return { output: `patch rejected: ${error?.message ?? error}`, isError: true };
      }
    },
  });

  pi.registerTool({
    name: "request_transition",
    label: "Change phase",
    description:
      "Request a control transition to one of inspect, plan, implement, validate, done, blocked. " +
      "Illegal transitions are refused. done additionally requires a validation receipt that " +
      "still matches its artifact.",
    parameters: Type.Object({ to: Type.String() }),
    async execute(_id: string, params: any) {
      const from = String(state.phase);
      const target = String(params.to);
      if (!(TRANSITIONS[from] ?? []).includes(target)) {
        counters.transitions_rejected += 1;
        record("transition_rejected", { from, to: target, reason: "illegal transition" });
        persist();
        return { output: `refused: ${from} -> ${target} is not a legal transition`, isError: true };
      }
      if (target in GATED) {
        const refs = (state.validated_artifact_refs as any[]) ?? [];
        if (refs.length === 0) {
          counters.transitions_rejected += 1;
          counters.blocked_completions += 1;
          record("transition_rejected", { from, to: target, reason: "no validation receipt" });
          persist();
          return { output: "refused: done needs a validation receipt recorded first", isError: true };
        }
        for (const ref of refs) {
          counters.artifact_revalidations += 1;
          const { ok, reason } = artifactValid(ref);
          if (!ok) {
            counters.transitions_rejected += 1;
            counters.blocked_completions += 1;
            counters.artifact_failures += 1;
            record("transition_rejected", { from, to: target, reason: `${ref.path}: ${reason}` });
            persist();
            return { output: `refused: ${ref.path} ${reason}`, isError: true };
          }
        }
      }
      state.phase = target;
      revision += 1;
      counters.transitions_accepted += 1;
      record("transition_accepted", { from, to: target, revision });
      persist();
      return { output: `phase is now ${target}`, isError: false };
    },
  });

  pi.registerTool({
    name: "record_receipt",
    label: "Record a validation receipt",
    description:
      "Record that a file in the working tree is the evidence for a check, taking its digest " +
      "now. Pass path, kind (use validation_receipt for completion evidence) and passed.",
    parameters: Type.Object({
      path: Type.String(),
      kind: Type.String(),
      passed: Type.Boolean(),
    }),
    async execute(_id: string, params: any) {
      const target = resolve(WORKTREE, params.path);
      if (!existsSync(target)) {
        record("receipt_rejected", { path: params.path, reason: "file does not exist" });
        return { output: `no such file: ${params.path}`, isError: true };
      }
      const digest = sha256(readFileSync(target).toString("binary"));
      const ref = {
        path: params.path,
        digest,
        kind: params.kind,
        passed: Boolean(params.passed),
        validated_at_event: record("artifact_validated", {
          path: params.path, kind: params.kind, passed: Boolean(params.passed), digest,
        }).id,
      };
      try {
        state = applyOps(state, [{ op: "set", field: "validated_artifact_refs", value: [ref] }]);
        revision += 1;
        counters.patches_accepted += 1;
        persist();
        return { output: `receipt recorded for ${params.path}`, isError: false };
      } catch (error: any) {
        counters.patches_rejected += 1;
        return { output: `receipt rejected: ${error?.message ?? error}`, isError: true };
      }
    },
  });
}
