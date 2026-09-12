/**
 * pi-change-trigger tests (CAMPAIGN-1 workstream B). The S4 feed contract is
 * the load-bearing part: every evaluation logged, prompt TEXT never logged,
 * fired-or-not always recorded.
 */

import { describe, test, expect, beforeEach, afterEach } from "bun:test";
import {
  validateConfig, loadConfig, tokensOf, topicsFromNotifyFile, topicMatches,
  evaluateFire, triggerMessage, default as registerExtension,
} from "../index.ts";
import { mkdtempSync, rmSync, writeFileSync, readFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

let agentDir: string;
let prevAgentDir: string | undefined;

beforeEach(() => {
  agentDir = mkdtempSync(join(tmpdir(), "change-trigger-"));
  prevAgentDir = process.env.PI_CODING_AGENT_DIR;
  process.env.PI_CODING_AGENT_DIR = agentDir;
  delete process.env.PI_CHANGE_TRIGGER;
});

afterEach(() => {
  rmSync(agentDir, { recursive: true, force: true });
  if (prevAgentDir === undefined) delete process.env.PI_CODING_AGENT_DIR;
  else process.env.PI_CODING_AGENT_DIR = prevAgentDir;
});

const TOPICS = new Set(["helm", "staging", "argo", "kite-k8s", "vault"]);

describe("config", () => {
  test("defaults when key absent", () => {
    const r = validateConfig(undefined);
    expect(r.problems).toEqual([]);
    expect(r.config).toEqual({ enabled: true, gapMinutes: 30, topicsFile: null, fireLog: null });
  });

  test("loadConfig reads the agent-dir settings.json", () => {
    writeFileSync(join(agentDir, "settings.json"), JSON.stringify({
      changeTrigger: { gapMinutes: 15, topicsFile: "/tmp/t.jsonl", fireLog: "/tmp/f.jsonl" },
    }));
    const r = loadConfig(agentDir);
    expect(r.problems).toEqual([]);
    expect(r.config.gapMinutes).toBe(15);
    expect(r.config.fireLog).toBe("/tmp/f.jsonl");
  });

  test("bad values named loudly, defaults kept", () => {
    const r = validateConfig({ enabled: "yes", gapMinutes: 0, fireLog: 7 });
    expect(r.config.enabled).toBe(true);
    expect(r.config.gapMinutes).toBe(30);
    expect(r.config.fireLog).toBeNull();
    expect(r.problems.length).toBe(3);
  });
});

describe("topic tokens", () => {
  test("tokensOf: len>=4, lowercase, stopwords stripped", () => {
    expect(tokensOf("Production now uses Helm for staging deploys.")).toEqual([
      "production", "helm", "staging", "deploys",
    ]);
  });

  test("topicsFromNotifyFile: summaries feed the set; bad lines skipped", () => {
    const dir = mkdtempSync(join(tmpdir(), "ct-topics-"));
    try {
      const p = join(dir, "n.jsonl");
      writeFileSync(p, [
        JSON.stringify({ summary: "create decision/record-x: staging deploys via helm on kite-k8s" }),
        "not json",
        JSON.stringify({ summary: "Identity + role: trial ledger convention with trial-ledger.py" }),
      ].join("\n"));
      const { topics, notes } = topicsFromNotifyFile(p);
      expect(topics.has("staging")).toBe(true);
      expect(topics.has("helm")).toBe(true);
      expect(topics.has("ledger")).toBe(true);
      expect(notes.some((n) => n.includes("unparseable"))).toBe(true);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test("topicMatches: returns distinct matched tokens in prompt order", () => {
    expect(topicMatches("we deploy staging with helm now, helm again", TOPICS))
      .toEqual(["staging", "helm"]);
    expect(topicMatches("unrelated turn about testing", TOPICS)).toEqual([]);
  });
});

describe("fire decision", () => {
  test("fresh session fires", () => {
    const d = evaluateFire({ isFirstPrompt: true, minutesSinceLastPrompt: null, prompt: "hello", topics: TOPICS, gapMinutes: 30 });
    expect(d.fired).toBe(true);
    expect(d.reasons).toContain("fresh");
  });

  test("gap >= threshold fires with actual minutes", () => {
    const d = evaluateFire({ isFirstPrompt: false, minutesSinceLastPrompt: 42, prompt: "hello", topics: TOPICS, gapMinutes: 30 });
    expect(d.reasons).toContain("gap");
    expect(d.gapMinutesActual).toBe(42);
  });

  test("topic overlap fires and names the tokens", () => {
    const d = evaluateFire({ isFirstPrompt: false, minutesSinceLastPrompt: 2, prompt: "switch staging to argo", topics: TOPICS, gapMinutes: 30 });
    expect(d.fired).toBe(true);
    expect(d.reasons).toContain("topic");
    expect(d.matchedTokens.sort()).toEqual(["argo", "staging"]);
  });

  test("no condition: does not fire", () => {
    const d = evaluateFire({ isFirstPrompt: false, minutesSinceLastPrompt: 5, prompt: "continue the unit tests", topics: TOPICS, gapMinutes: 30 });
    expect(d.fired).toBe(false);
    expect(d.reasons).toEqual([]);
  });

  test("trigger message names the evidence", () => {
    const m = triggerMessage(["topic"], ["helm", "staging"]);
    expect(m).toContain("[change-trigger]");
    expect(m).toContain("project_perseus_recall");
    expect(m).toContain("helm");
  });
});

describe("extension wiring (real registration)", () => {
  function register(settings: Record<string, unknown>, notifyLines: string[]) {
    writeFileSync(join(agentDir, "settings.json"), JSON.stringify(settings));
    const notify = join(agentDir, "notifications.jsonl");
    writeFileSync(notify, notifyLines.join("\n") + "\n");
    let handler: any = null;
    registerExtension({
      registerTool: () => {},
      on: (ev: string, h: any) => { if (ev === "before_agent_start") handler = h; },
      getAllTools: () => [],
      appendEntry: () => {},
    } as any);
    return { handler, notify };
  }

  test("fresh+topic turn: fires, injects visible message, logs WITHOUT prompt text", async () => {
    const fireLog = join(agentDir, "fire.jsonl");
    const { handler } = register({
      changeTrigger: { gapMinutes: 30, topicsFile: null, fireLog },
    }, []);
    const out = await handler({ prompt: "staging deploy question" });
    expect(out.message.display).toBe(true);
    expect(out.message.content).toContain("[change-trigger]");
    const line = JSON.parse(readFileSync(fireLog, "utf8").trim());
    expect(line.fired).toBe(true);
    expect(line.reasons).toContain("fresh");
    expect(line.prompt_sha256).toMatch(/^[0-9a-f]{64}$/);
    expect(line.prompt_len).toBe("staging deploy question".length);
    expect(JSON.stringify(line)).not.toContain("staging deploy question");
  });

  test("non-firing turn is ALSO logged (S4 false-fire denominator)", async () => {
    const fireLog = join(agentDir, "fire.jsonl");
    const { handler } = register({
      changeTrigger: { gapMinutes: 30, topicsFile: null, fireLog },
    }, []);
    await handler({ prompt: "first" });           // fresh: fires
    const out = await handler({ prompt: "second" }); // no gap, no topic: silent
    expect(out).toBeUndefined();
    const lines = readFileSync(fireLog, "utf8").trim().split("\n").map((l) => JSON.parse(l));
    expect(lines).toHaveLength(2);
    expect(lines[1].fired).toBe(false);
  });

  test("topicsFile missing: topic trigger inert, gap trigger still works", async () => {
    const fireLog = join(agentDir, "fire.jsonl");
    const { handler } = register({
      changeTrigger: { gapMinutes: 30, topicsFile: join(agentDir, "nope.jsonl"), fireLog },
    }, []);
    const first = await handler({ prompt: "anything at all" });
    expect(first.message.content).toContain("fresh");
    handler; // second prompt without gap: no fire
    const second = await handler({ prompt: "more work" });
    expect(second).toBeUndefined();
  });

  test("kill switch disables registration", () => {
    process.env.PI_CHANGE_TRIGGER = "0";
    let registered = false;
    registerExtension({
      registerTool: () => { registered = true; },
      on: () => {}, getAllTools: () => [], appendEntry: () => {},
    } as any);
    expect(registered).toBe(false);
  });
});
