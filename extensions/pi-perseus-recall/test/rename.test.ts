/**
 * BUILD-20260911 decision 7d: the perseus adapter's tool is renamed
 * `project_recall` -> `project_perseus_recall` so it can coexist with
 * pi-project-recall (which keeps `project_recall`). Gate: the old name is
 * GONE from this extension's registrations and the new name registers.
 */

import { describe, test, expect, beforeEach, afterEach } from "bun:test";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { default as registerExtension } from "../index.ts";

let agentDir: string;
let prevAgentDir: string | undefined;
let prevKill: string | undefined;

function withConfig(settings: Record<string, unknown>): void {
  writeFileSync(join(agentDir, "settings.json"), JSON.stringify(settings));
}

const STUDY_CONFIG = {
  bin: "/bin/true", // never spawned at registration time
  db: "/tmp/rename-test-unused.sqlite",
  keyFile: "/tmp/rename-test-unused.key",
  workspaceHash: "b".repeat(64),
};

beforeEach(() => {
  agentDir = mkdtempSync(join(tmpdir(), "perseus-rename-"));
  prevAgentDir = process.env.PI_CODING_AGENT_DIR;
  prevKill = process.env.PI_PERSEUS_RECALL;
  process.env.PI_CODING_AGENT_DIR = agentDir;
  delete process.env.PI_PERSEUS_RECALL;
});

afterEach(() => {
  rmSync(agentDir, { recursive: true, force: true });
  if (prevAgentDir === undefined) delete process.env.PI_CODING_AGENT_DIR;
  else process.env.PI_CODING_AGENT_DIR = prevAgentDir;
  if (prevKill === undefined) delete process.env.PI_PERSEUS_RECALL;
  else process.env.PI_PERSEUS_RECALL = prevKill;
});

function register(): { names: string[]; tools: any[] } {
  const tools: any[] = [];
  registerExtension({
    registerTool: (t: any) => tools.push(t),
    on: () => {},
    getAllTools: () => tools,
    appendEntry: () => {},
  } as any);
  return { names: tools.map((t) => t.name), tools };
}

describe("7d rename", () => {
  test("old name project_recall is gone; project_perseus_recall registers", () => {
    withConfig({ perseusRecall: STUDY_CONFIG });
    const { names } = register();
    expect(names).toContain("project_perseus_recall");
    expect(names).not.toContain("project_recall");
    expect(names.filter((n) => n === "project_perseus_recall").length).toBe(1);
  });

  test("description text names the Perseus decision memory, not pi-project-recall's tool", () => {
    withConfig({ perseusRecall: STUDY_CONFIG });
    const { tools } = register();
    const t = tools.find((x) => x.name === "project_perseus_recall");
    expect(t.description).toContain("Perseus decision memory");
    expect(t.promptSnippet).toBeTruthy();
    expect(t.parameters.required).toEqual(["query"]);
  });

  test("kill switch still disables registration entirely", () => {
    withConfig({ perseusRecall: STUDY_CONFIG });
    process.env.PI_PERSEUS_RECALL = "0";
    const { names } = register();
    expect(names).toEqual([]);
  });
});
