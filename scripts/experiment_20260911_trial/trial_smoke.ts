#!/usr/bin/env bun
/**
 * TRIAL-20260911 Part 1 smoke: scratch draft round-trip in the worker-pi
 * trial's settings SHAPE.
 *
 * 1. Validates the REAL trial config at
 *    /home/bmosher/acp-pi/.pi-agent/settings.json (packages path alive,
 *    perseusRecall shape per dispatch: explicit db in ~/acp-pi, write
 *    enabled, allowAgentConfirmed=false, in-session+file notifiers,
 *    explicit notifyFile). Read-only against the real files.
 * 2. Re-runs the decision-memory loop (draft -> gate refusals -> operator
 *    confirm -> supersede -> recall) against a SCRATCH copy of that shape
 *    (db + notifyFile in /tmp), so the trial vault and notify file stay
 *    pristine.
 *
 * The extension is FROZEN at e9e5621 - this driver only loads it.
 * Run: bun scripts/experiment_20260911_trial/trial_smoke.ts
 */

import { mkdtempSync, rmSync, mkdirSync, writeFileSync, existsSync, statSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const TRIAL_AGENT_DIR = "/home/bmosher/acp-pi/.pi-agent";
const TRIAL_CWD = "/home/bmosher/acp-pi";
const EXTENSION_PATH = "/var/home/bmosher/memory-bake-off/implementer/repo/extensions/pi-perseus-recall";
const REAL_BIN = "/var/home/bmosher/perseus-build/src/target/release/perseus-vault";

const steps: { name: string; ok: boolean; evidence: string }[] = [];
function step(name: string, ok: boolean, evidence: string): void {
  steps.push({ name, ok, evidence });
  console.error(`${ok ? "PASS" : "FAIL"} ${name}${evidence ? ` — ${evidence}` : ""}`);
}

function text(t: any): string {
  return t?.content?.[0]?.text ?? "";
}

async function main(): Promise<boolean> {
  // 1. real trial config validation (read-only)
  const settingsPath = join(TRIAL_AGENT_DIR, "settings.json");
  const raw = JSON.parse(readFileSync(settingsPath, "utf8"));
  const extListed = Array.isArray(raw.packages) && raw.packages.includes(EXTENSION_PATH);
  const extOnDisk = existsSync(join(EXTENSION_PATH, "index.ts"));
  step("trial-config-packages", extListed && extOnDisk, `packages=${JSON.stringify(raw.packages)}`);

  const pr = raw.perseusRecall ?? {};
  const binOk = pr.bin === REAL_BIN && existsSync(pr.bin) && !!(statSync(pr.bin).mode & 0o111);
  step("trial-config-bin", binOk, `bin=${pr.bin}`);

  const w = pr.write ?? {};
  const dbInTrial = typeof pr.db === "string" && pr.db.startsWith(TRIAL_CWD + "/");
  // out-of-band Signal is conductor-side: the worker ships in-session+file ONLY
  const notifiersExact = Array.isArray(w.notifiers)
    && w.notifiers.length === 2
    && w.notifiers.includes("in-session") && w.notifiers.includes("file");
  const shapeOk = w.enabled === true && w.allowAgentConfirmed === false
    && notifiersExact
    && w.notifyFile === join(TRIAL_CWD, "notifications.jsonl");
  step("trial-config-shape", dbInTrial && shapeOk,
    `db=${pr.db} (explicit, trial-owned); write.enabled=${w.enabled}; `
    + `allowAgentConfirmed=${w.allowAgentConfirmed}; notifiers=${JSON.stringify(w.notifiers)}; `
    + `notifyFile=${w.notifyFile}`);
  if (!(extListed && extOnDisk && binOk && dbInTrial && shapeOk)) {
    return finish(null, false);
  }

  // 2. scratch round-trip in the trial shape (db + notifyFile redirected)
  const scratch = mkdtempSync(join(tmpdir(), "trial-smoke-"));
  const agentDir = join(scratch, "agent");
  mkdirSync(join(agentDir, "perseus"), { recursive: true });
  const scratchDb = join(scratch, "trial.vault");
  const scratchNotify = join(scratch, "notifications.jsonl");
  writeFileSync(join(agentDir, "settings.json"), JSON.stringify({
    enableInstallTelemetry: false,
    packages: [EXTENSION_PATH],
    perseusRecall: { bin: REAL_BIN, db: scratchDb, write: {
      enabled: true, allowAgentConfirmed: false,
      notifiers: ["in-session", "file"], notifyFile: scratchNotify,
    } },
  }));

  process.env.PI_CODING_AGENT_DIR = agentDir;
  process.chdir(TRIAL_CWD); // worker's cwd: drives the derived workspace hash
  const { default: registerExtension } = await import(EXTENSION_PATH + "/index.ts");

  const tools = new Map<string, any>();
  registerExtension({
    registerTool: (t: any) => tools.set(t.name, t),
    on: () => {}, getAllTools: () => [...tools.values()], appendEntry: () => {},
  } as any);
  step("registration", tools.has("project_perseus_recall") && tools.has("project_perseus_remember")
    && tools.has("project_perseus_supersede") && tools.has("project_perseus_confirm"),
    `tools=${[...tools.keys()].join(",")}`);

  const call = async (name: string, params: any) =>
    await tools.get(name).execute("trial-smoke", params, undefined as any, undefined as any, undefined as any);

  // draft -> wrong code refused -> operator code writes -> notify file line
  const d = text(await call("project_perseus_remember", {
    content: "TRIAL SMOKE: decision-memory loop closes in the worker trial shape",
    key: "record-trial-smoke-1",
    source: { kind: "task", ref: "trial/part1-smoke" },
  }));
  const id = d.match(/^draft_id: (draft-[0-9a-f]+)$/m)?.[1] ?? "";
  const code = d.match(/^confirmation_code: ([0-9a-f]+)$/m)?.[1] ?? "";
  const wrong = text(await call("project_perseus_confirm", { draft_id: id, confirmation_code: "00000000" }));
  const ok = text(await call("project_perseus_confirm", { draft_id: id, confirmation_code: code }));
  step("draft-roundtrip", d.includes("NOTHING IS WRITTEN YET") && wrong.includes("NOT WRITTEN")
    && ok.includes("WRITTEN") && existsSync(scratchDb) && existsSync(scratchNotify)
    && readFileSync(scratchNotify, "utf8").includes(id),
    `draft=${id}; wrong-code refused; operator code wrote; notify line present`);

  // supersede + recall on the scratch vault
  const d2 = text(await call("project_perseus_supersede", {
    content: "TRIAL SMOKE: superseded by the second smoke record",
    key: "record-trial-smoke-2",
    source: { kind: "instruction", ref: "trial/part1-smoke supersede leg" },
    from_key: "record-trial-smoke-1",
    reason: "smoke: exercise the supersede leg of the loop",
  }));
  const id2 = d2.match(/^draft_id: (draft-[0-9a-f]+)$/m)?.[1] ?? "";
  const code2 = d2.match(/^confirmation_code: ([0-9a-f]+)$/m)?.[1] ?? "";
  const ok2 = text(await call("project_perseus_confirm", { draft_id: id2, confirmation_code: code2 }));
  const rec = text(await call("project_perseus_recall", { query: "TRIAL SMOKE" }));
  step("supersede-and-recall", ok2.includes("status_updated=\"deprecated\"")
    && rec.includes("record-trial-smoke-2") && rec.includes("part1-smoke supersede leg")
    && !/^\[project_perseus_recall\] key=record-trial-smoke-1$/m.test(rec),
    "status flip delivered; current record recalled with source; old record gone");

  rmSync(scratch, { recursive: true, force: true });
  return finish(scratch, steps.every((s) => s.ok));
}

function finish(scratch: string | null, ok: boolean): boolean {
  if (scratch) rmSync(scratch, { recursive: true, force: true });
  const lines = [
    "TRIAL-20260911 PART 1 SMOKE RECEIPT (worker-pi decision-memory trial)",
    `trial agent dir: ${TRIAL_AGENT_DIR} (real trial config validated read-only)`,
    `when: ${new Date().toISOString()}`,
    "",
    ...steps.map((s) => `[${s.ok ? "PASS" : "FAIL"}] ${s.name}${s.evidence ? ` — ${s.evidence}` : ""}`),
    "",
    ok ? "TRIAL SMOKE RECEIPT: PASS — extension registers in the worker trial shape; "
      + "scratch draft round-trips (gate, supersede, recall); kill switch verified separately "
      + "(PI_PERSEUS_RECALL=0 disables registration, see receipt in the runbook)"
      : "TRIAL SMOKE RECEIPT: FAIL",
  ];
  console.log(lines.join("\n"));
  return ok;
}

process.exit((await main()) ? 0 : 1);
