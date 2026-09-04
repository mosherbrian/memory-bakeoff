/**
 * Gen46 arm C: harness-maintained state and control, for the Gen47 live ablation.
 *
 * The composer, the caps and the history treatment are byte-for-byte arm B's.
 * The only difference is where the state and the phase come from: they are
 * derived here from ordinary visible tool events instead of waiting for the
 * model to call three tools it did not call in Gen45.
 *
 * The rules mirror `harness_state.py` exactly, and the preflight replays the
 * same synthetic event log through both to prove they agree. No semantic
 * interpretation, and nothing hidden — the final verifier and the reference
 * fixes are outside this path by construction.
 */
import { createHash } from "node:crypto";
import { appendFileSync, mkdirSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join } from "node:path";

export const DERIVATION_VERSION = "harness-state-v1";

export const READ_TOOLS = new Set(["read", "ls", "grep", "find", "glob"]);
export const MUTATION_TOOLS = new Set(["edit", "write", "multi_edit"]);
export const VALIDATION_PATTERNS = [
  /\bpytest\b/,
  /\bpython3?\s+-m\s+pytest\b/,
  /\bpython3?\s+-m\s+unittest\b/,
  /\bpython3?\s+run_checks\.py\b/,
];
export const FORBIDDEN_IN_VALIDATION = ["verifier.py", "verifier_path", "reference_fix"];
export const INSPECTION_CALLS_TO_LEAVE_INSPECT = 2;

export const AUTOMATIC_TRANSITIONS: Record<string, string[]> = {
  inspect: ["plan", "implement", "blocked"],
  plan: ["implement", "inspect", "blocked"],
  implement: ["validate", "plan", "blocked"],
  validate: ["done", "implement", "blocked"],
  done: ["implement"],
  blocked: ["inspect", "plan", "implement", "validate"],
};

const STATE_BYTE_CAP = 4096;
const RECENT_FILES_BOUND = 6;
const CHECKPOINT_BOUND = 6;
const RECENT_WINDOW_UNITS = 2;
const RECENT_WINDOW_BYTE_CAP = 8192;
const LATEST_OBSERVATION_BYTE_CAP = 8192;

const IMMUTABLE_INSTRUCTIONS =
  "You are working under an executable control layer. Phases are inspect, plan, " +
  "implement, validate, done. The phase and the recorded state below are maintained " +
  "for you from what you do: reading moves you on from inspect, changing a file moves " +
  "you to implement, and running the project's own checks moves you to validate. " +
  "Completion is recorded only when a passing check matches the current tree.";

const canonical = (v: unknown) => JSON.stringify(v ?? null);
const sha256 = (t: string) => createHash("sha256").update(t).digest("hex");

export function isValidationCommand(command: string): boolean {
  if (!command) return false;
  if (FORBIDDEN_IN_VALIDATION.some((token) => command.includes(token))) return false;
  return VALIDATION_PATTERNS.some((pattern) => pattern.test(command));
}

const bounded = (values: string[], bound: number) => values.slice(Math.max(0, values.length - bound));

export interface DerivedState {
  schema_version: number;
  derivation: string;
  phase: string;
  revision: number;
  tree_digest: string;
  files_read: string[];
  files_modified: string[];
  last_tool: string;
  last_tool_ref: string;
  last_observation_ref: string;
  checkpoints: string[];
  validation: Record<string, unknown>;
  validated_artifact_refs: Array<Record<string, unknown>>;
}

export function newState(): DerivedState {
  return {
    schema_version: 1, derivation: DERIVATION_VERSION, phase: "inspect", revision: 0,
    tree_digest: "", files_read: [], files_modified: [], last_tool: "", last_tool_ref: "",
    last_observation_ref: "", checkpoints: [], validation: {}, validated_artifact_refs: [],
  };
}

export class Derivation {
  state = newState();
  transitions: Array<Record<string, unknown>> = [];
  receipts: Array<Record<string, unknown>> = [];
  invalidations: Array<Record<string, unknown>> = [];
  inspectionCalls = 0;

  private move(target: string, because: string, ref: string) {
    const current = this.state.phase;
    if (target === current) return;
    if (!(AUTOMATIC_TRANSITIONS[current] ?? []).includes(target)) {
      this.transitions.push({ from: current, to: target, accepted: false,
        reason: "not an automatic transition", event: ref });
      return;
    }
    this.state.phase = target;
    this.state.revision += 1;
    this.transitions.push({ from: current, to: target, accepted: true, because, event: ref });
  }

  private checkpoint(name: string) {
    this.state.checkpoints = bounded([...this.state.checkpoints, name], CHECKPOINT_BOUND);
  }

  private invalidateOnMutation(ref: string) {
    if (this.state.validated_artifact_refs.length === 0) return;
    this.invalidations.push({ reason: "repository mutated after the check",
      receipt: this.state.validated_artifact_refs[0], event: ref });
    this.state.validated_artifact_refs = [];
  }

  toolCall(tool: string, args: any, ref: string) {
    this.state.last_tool = tool;
    this.state.last_tool_ref = ref;
    this.state.revision += 1;
    if (READ_TOOLS.has(tool)) {
      this.inspectionCalls += 1;
      const path = args?.path ?? args?.pattern ?? "";
      if (path) {
        this.state.files_read = bounded(
          [...this.state.files_read.filter((p) => p !== path), path], RECENT_FILES_BOUND);
      }
      if (this.state.phase === "inspect" && this.inspectionCalls >= INSPECTION_CALLS_TO_LEAVE_INSPECT) {
        this.move("plan", "enough inspection activity to have looked around", ref);
      }
    } else if (MUTATION_TOOLS.has(tool)) {
      const path = args?.path ?? "";
      if (path) {
        this.state.files_modified = bounded(
          [...this.state.files_modified.filter((p) => p !== path), path], RECENT_FILES_BOUND);
      }
      this.checkpoint("repository_mutated");
      this.invalidateOnMutation(ref);
      if (["inspect", "plan", "validate", "done"].includes(this.state.phase)) {
        this.move("implement", "the repository was modified", ref);
      }
    }
  }

  toolResult(command: string, exitCode: number | undefined, isError: boolean, tree: string, ref: string) {
    this.state.last_observation_ref = ref;
    if (tree) this.state.tree_digest = tree;
    const trimmed = (command ?? "").trim();
    if (!trimmed || !isValidationCommand(trimmed)) return;
    const passed = exitCode === undefined ? !isError : exitCode === 0;
    this.state.validation = { command: trimmed, passed, tree_digest: this.state.tree_digest, event: ref };
    if (this.state.phase === "implement") this.move("validate", "a visible check ran after a change", ref);
    if (passed) {
      this.checkpoint("validation_passed");
      const receipt = { kind: "validation_receipt", command: trimmed,
        tree_digest: this.state.tree_digest, passed: true, event: ref };
      this.state.validated_artifact_refs = [receipt];
      this.receipts.push(receipt);
    } else {
      this.checkpoint("validation_failed");
      this.state.validated_artifact_refs = [];
      if (this.state.phase === "validate") this.move("implement", "the visible check failed", ref);
    }
  }

  sessionEnd(ref: string) {
    if (this.validReceipt() && this.state.phase === "validate") {
      this.move("done", "the run ended with a valid receipt for this tree", ref);
    }
  }

  validReceipt(): Record<string, unknown> | null {
    for (const receipt of this.state.validated_artifact_refs) {
      if (receipt.passed && receipt.tree_digest === this.state.tree_digest) return receipt;
    }
    return null;
  }

  summary() {
    return {
      state: this.state,
      state_bytes: canonical(this.state).length,
      transitions: this.transitions,
      transitions_accepted: this.transitions.filter((t) => t.accepted).length,
      transitions_rejected: this.transitions.filter((t) => !t.accepted).length,
      receipts: this.receipts,
      receipt_invalidations: this.invalidations,
      valid_receipt_at_end: this.validReceipt() !== null,
    };
  }
}

// --- the extension -----------------------------------------------------------

type Message = { role: string; content: unknown };

function interactionUnits(messages: Message[]): Message[][] {
  const units: Message[][] = [];
  let current: Message[] | null = null;
  for (const message of messages) {
    if (message.role === "user") { if (current) units.push(current); current = [message]; }
    else if (current) current.push(message);
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

export default function harnessArm(pi: any) {
  const OUT = process.env.PI_PILOT_OUT ?? "/tmp/pi-pilot-run";
  const WORKTREE = process.env.PI_PILOT_WORKTREE ?? process.cwd();
  mkdirSync(OUT, { recursive: true });
  const line = (name: string, payload: unknown) =>
    appendFileSync(join(OUT, name), canonical(payload) + "\n");

  const derivation = new Derivation();
  let latestObservation: unknown = null;
  let seq = 0;
  const nextRef = () => `e${String(seq++).padStart(6, "0")}`;

  const treeDigest = () => {
    try {
      execFileSync("git", ["add", "-A"], { cwd: WORKTREE, stdio: "ignore" });
      return execFileSync("git", ["write-tree"], { cwd: WORKTREE }).toString().trim();
    } catch { return ""; }
  };

  const persist = () => writeFileSync(join(OUT, "harness_state.json"),
    canonical({ ...derivation.summary(), derivation_version: DERIVATION_VERSION }));

  pi.on("context", (event: any) => {
    const incoming: Message[] = event.messages ?? [];
    const observation = canonical(latestObservation).length > LATEST_OBSERVATION_BYTE_CAP
      ? { truncated: true, note: "full tool output retained in history" } : latestObservation;
    const stateView = canonical(derivation.state).length > STATE_BYTE_CAP
      ? { truncated: true, phase: derivation.state.phase } : derivation.state;
    const view = {
      instructions: IMMUTABLE_INSTRUCTIONS,
      control: { phase: derivation.state.phase,
                 legal_next: AUTOMATIC_TRANSITIONS[derivation.state.phase] ?? [],
                 maintained_by: "harness" },
      state: stateView,
      latest_observation: observation,
      artifact_refs: derivation.state.validated_artifact_refs,
    };
    const replacement = [
      { role: "user", content: [{ type: "text", text: canonical(view) }] },
      ...recentWindow(incoming),
    ];
    line("requests.ndjson", { bytes: canonical(replacement).length, messages: replacement.length,
      composed: true, pi_would_have_sent_bytes: canonical(incoming).length,
      state_bytes: canonical(derivation.state).length, phase: derivation.state.phase });
    return { messages: replacement };
  });

  pi.on("session_before_compact", () => ({ cancel: true }));

  pi.on("tool_call", (event: any) => {
    const ref = nextRef();
    const tool = event.toolName ?? event.type;
    derivation.toolCall(tool, event.input ?? {}, ref);
    line("tools.ndjson", { phase: "call", tool, args: event.input ?? {} });
    line("derivation.ndjson", { ref, kind: "tool_call", tool, phase: derivation.state.phase });
    persist();
    return {};
  });

  pi.on("tool_result", (event: any) => {
    const ref = nextRef();
    const text = canonical(event.result ?? event.content ?? "");
    const command = event?.input?.command ?? event?.input?.cmd ?? "";
    const tool = event.toolName ?? "";
    const exit = event?.result?.exitCode ?? event?.details?.exitCode;
    derivation.toolResult(command, exit, Boolean(event.isError), treeDigest(), ref);
    latestObservation = { event_id: ref, bytes: text.length,
      text: text.slice(0, LATEST_OBSERVATION_BYTE_CAP) };
    line("tools.ndjson", { phase: "result", tool, bytes: text.length });
    line("derivation.ndjson", { ref, kind: "tool_result", command,
      phase: derivation.state.phase, validation: derivation.state.validation });
    persist();
    return {};
  });

  pi.on("session_shutdown", () => {
    derivation.sessionEnd(nextRef());
    persist();
  });
}
