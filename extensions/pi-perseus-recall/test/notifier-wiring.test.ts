/**
 * Notifier config wiring: the WriteNotifier seam ships with in-session /
 * file / noop only — any UNKNOWN channel name is rejected loudly and the
 * default channels take over (never a silent drop).
 */

import { describe, test, expect, beforeEach, afterEach } from "bun:test";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { default as registerExtension } from "../index.ts";

let agentDir: string;
let prevAgentDir: string | undefined;

beforeEach(() => {
  agentDir = mkdtempSync(join(tmpdir(), "perseus-notify-wiring-"));
  prevAgentDir = process.env.PI_CODING_AGENT_DIR;
  process.env.PI_CODING_AGENT_DIR = agentDir;
  delete process.env.PI_PERSEUS_RECALL;
});

afterEach(() => {
  rmSync(agentDir, { recursive: true, force: true });
  if (prevAgentDir === undefined) delete process.env.PI_CODING_AGENT_DIR;
  else process.env.PI_CODING_AGENT_DIR = prevAgentDir;
});

function register(settings: Record<string, unknown>): { tools: Map<string, any>; problems: string[] } {
  writeFileSync(join(agentDir, "settings.json"), JSON.stringify(settings));
  const tools = new Map<string, any>();
  const lines: string[] = [];
  const err = console.error;
  console.error = (...a: any[]) => { lines.push(a.join(" ")); };
  try {
    registerExtension({
      registerTool: (t: any) => tools.set(t.name, t),
      on: () => {}, getAllTools: () => [...tools.values()], appendEntry: () => {},
    } as any);
  } finally {
    console.error = err;
  }
  // info logs (vault path, registration) are not problems
  const problems = lines.filter((l) => !l.includes(": vault ") && !l.includes(": registered ") && !l.includes(": disabled"));
  return { tools, problems };
}

const BASE_CONFIG = {
  bin: "/bin/true", db: "/tmp/notify-wiring-unused.sqlite", keyFile: "/tmp/notify-wiring-unused.key",
  workspaceHash: "b".repeat(64),
};

async function draftNotifierLine(tools: Map<string, any>): Promise<string> {
  const draft = await tools.get("project_perseus_remember").execute("t", {
    content: "wiring check", source: { kind: "task", ref: "notify-wiring" },
  }, undefined as any, undefined as any, undefined as any);
  return draft.content[0].text.split("\n").find((l: string) => l.startsWith("notifier:")) ?? "";
}

describe("notifier channel wiring", () => {
  test("known channels only: no problems, channels serve the draft", async () => {
    const { tools, problems } = register({
      perseusRecall: { ...BASE_CONFIG, write: { notifiers: ["in-session", "file"] } },
    });
    expect(problems).toEqual([]);
    const line = await draftNotifierLine(tools);
    expect(line).toContain("in-session:true");
    expect(line).toContain("file:true");
  });

  test("unknown channel name: loud problem, defaults take over (never silent)", async () => {
    const { tools, problems } = register({
      perseusRecall: { ...BASE_CONFIG, write: { notifiers: ["in-session", "clawdbot-signal"] } },
    });
    expect(problems.some((p) => p.includes("must be a subset"))).toBe(true);
    const line = await draftNotifierLine(tools);
    expect(line).not.toContain("clawdbot-signal");
    expect(line).toContain("in-session:true"); // default channels active
    expect(line).toContain("file:true");
  });

  test("noop-only channel list is honored (explicitly silent)", async () => {
    const { tools, problems } = register({
      perseusRecall: { ...BASE_CONFIG, write: { notifiers: ["noop"] } },
    });
    expect(problems).toEqual([]);
    const line = await draftNotifierLine(tools);
    expect(line).toContain("noop:false");
  });
});
