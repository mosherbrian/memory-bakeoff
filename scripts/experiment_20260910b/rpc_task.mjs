/**
 * rpc_task.mjs — EXPERIMENT-20260910B task invocation driver.
 *
 * Why: `pi --print --session <file>` opens the session but reports
 * session_start reason "startup" (CLI initial-runtime default), so the
 * deployed pi-recall-nudge onResume gate never arms. The RPC path has a
 * switch_session command that goes through AgentSessionRuntime.switchSession
 * and emits a REAL session_start reason "resume" (pi 0.84.4
 * dist/core/agent-session-runtime.js:141) — the same mechanism the deck
 * uses on reconnect. This driver spawns pi in RPC mode, switches to the
 * prime session file, sends the task prompt, and records the full event
 * stream to a file. Used for the TASK invocation of ALL arms (uniform path).
 *
 * Usage: node rpc_task.mjs <sessionFile> <promptFile> <outEvents.jsonl>
 * Env expected from caller: PI_CODING_AGENT_DIR, LCM_DB_DIR; cwd = worktree.
 * Exit codes: 0 = settled; 2 = switch_session failed; 3 = timeout; 4 = no settle.
 */
import { spawn } from "node:child_process";
import { readFileSync, appendFileSync } from "node:fs";

const [sessionFile, promptFile, outEvents] = process.argv.slice(2);
if (!sessionFile || !promptFile || !outEvents) {
  console.error("usage: node rpc_task.mjs <sessionFile> <promptFile> <outEvents>");
  process.exit(64);
}
const prompt = readFileSync(promptFile, "utf8");

const PI = "/var/home/bmosher/.bun/bin/pi";
const args = [
  "--mode", "rpc",
  "--session", sessionFile, // open the target at startup: no bootstrap session/conversation
  "--provider", "bosgame", "--model", "bosgame/qwen3.6-35b-vulkan-nothink",
  "--no-skills", "--no-context-files", "--no-prompt-templates", "--no-themes",
];
const child = spawn(PI, args, {
  cwd: process.cwd(),
  env: process.env,
  stdio: ["pipe", "pipe", "pipe"],
});

let nextId = 1;
const send = (obj) => child.stdin.write(JSON.stringify(obj) + "\n");
const eventsSeen = [];
let promptSent = false;
let settledAfterPrompt = false;
let switchOk = false;
let switchFail = null;
let finished = false;

const TIMEOUT_MS = 480_000; // spec 8-minute ceiling on the task invocation
const timer = setTimeout(() => finish(3, "timeout"), TIMEOUT_MS);

function finish(code, reason) {
  if (finished) return;
  finished = true;
  clearTimeout(timer);
  try { child.kill("SIGTERM"); } catch {}
  setTimeout(() => { try { child.kill("SIGKILL"); } catch {}; process.exit(code); }, 2000).unref();
  child.on("exit", () => process.exit(code));
}

child.stderr.pipe(process.stderr); // extension receipts (pi-recall-nudge lines etc.)
child.stdout.setEncoding("utf8");
let buf = "";
child.stdout.on("data", (chunk) => {
  buf += chunk;
  let nl;
  while ((nl = buf.indexOf("\n")) >= 0) {
    const line = buf.slice(0, nl).trim();
    buf = buf.slice(nl + 1);
    if (!line) continue;
    appendFileSync(outEvents, line + "\n");
    let e;
    try { e = JSON.parse(line); } catch { continue; }
    eventsSeen.push(e.type || "?");
    if (e.type === "response" && e.success === false && !switchOk) {
      switchFail = e;
      finish(2, `rpc ${e.command} failed: ${e.error}`);
    }
    if (e.type === "response" && e.command === "switch_session") {
      if (!e.success) { switchFail = e; finish(2, "switch_session failed"); }
      else {
        switchOk = true;
        // The resumed runtime is bound now; deliver the task prompt.
        send({ id: nextId++, type: "prompt", message: prompt });
        promptSent = true;
      }
    }
    if (e.type === "agent_settled" && promptSent) {
      settledAfterPrompt = true;
      finish(0, "settled");
    }
  }
});
child.on("exit", (code) => {
  if (!finished) finish(code === 0 ? (settledAfterPrompt ? 0 : 4) : 5, `pi exited ${code}`);
});

// Startup: wait briefly for the rpc server to be ready, then switch session.
setTimeout(() => send({ id: nextId++, type: "switch_session", sessionPath: sessionFile }), 500);
