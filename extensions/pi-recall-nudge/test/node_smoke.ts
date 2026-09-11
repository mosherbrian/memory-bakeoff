/**
 * Node-runtime smoke for pi-recall-nudge (same pattern as pi-project-recall):
 * prove the config loading and gate evaluation run under the ACTUAL Pi
 * runtime - node - not only under `bun test`. Run:
 *   node extensions/pi-recall-nudge/test/node_smoke.ts
 * Exits non-zero on any failure; prints one line per check.
 */

import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { loadConfig, evaluateGates, nudgeContent, F2_NUDGE, default as createExtension } from "../index.ts";

const checks: Array<[string, boolean]> = [];
function check(name: string, ok: boolean) {
  checks.push([name, ok]);
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}`);
}

// 1. Settings-driven config load under node.
const dir = mkdtempSync(join(tmpdir(), "pi-recall-nudge-nodesmoke-"));
mkdirSync(dir, { recursive: true });
writeFileSync(join(dir, "settings.json"), JSON.stringify({
  recallNudge: { onResume: true, everyNPrompts: 3, nudge: "check the past first" },
}));
const { config, problems } = loadConfig(dir);
check("settings recallNudge key loads (everyNPrompts=3, custom nudge)",
  problems.length === 0 && config.everyNPrompts === 3 && config.nudge === "check the past first");

// 2. Gate math under node: resume window + every-N.
const first = evaluateGates(config, { resumptionPending: true, promptsSeen: 0 });
check("resume prompt injects with gate onResume", first.inject && first.gates.includes("onResume"));
const third = evaluateGates(config, { resumptionPending: false, promptsSeen: 2 });
check("3rd prompt fires everyNPrompts", third.inject && third.gates.includes("everyNPrompts"));
check("delivery content has the [recall-nudge] prefix", nudgeContent(F2_NUDGE).startsWith("[recall-nudge] "));

// 3. The wiring drives the real events through a fake pi handle.
const handlers: Record<string, any[]> = {};
const entries: any[] = [];
createExtension({
  on: (ev: string, fn: any) => { (handlers[ev] ??= []).push(fn); },
  getAllTools: () => [{ name: "project_recall" }],
  appendEntry: (t: string, d: any) => entries.push([t, d]),
});
const event = { type: "before_agent_start", prompt: "fix it", systemPrompt: "S",
  systemPromptOptions: { cwd: dir, selectedTools: ["read", "project_recall"] } };
await handlers["session_start"][0]({ type: "session_start", reason: "resume" });
const r1 = await handlers["before_agent_start"][0](event);
const r2 = await handlers["before_agent_start"][0](event);
check("first post-resume prompt returns the visible recall-nudge message",
  r1?.message?.customType === "recall-nudge" && r1?.message?.display === true);
check("second prompt is not nudged again (window consumed)", r2 === undefined);
check("durable session entry recorded", entries.length === 1 && entries[0][1].gates.includes("onResume"));

rmSync(dir, { recursive: true, force: true });
const failed = checks.filter(([, ok]) => !ok).length;
console.log(failed === 0 ? "node smoke: ALL PASS" : `node smoke: ${failed} FAIL`);
process.exit(failed === 0 ? 0 : 1);
