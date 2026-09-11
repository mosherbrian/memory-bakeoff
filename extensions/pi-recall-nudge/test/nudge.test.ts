/**
 * pi-recall-nudge unit tests. The dispatch's predeclared controls:
 *  - default nudge text = the F2 sentence byte-for-byte
 *  - gates as a pure function: resume-only, everyPrompt, every-N (incl. the
 *    per-process counter), union dedupe, tool-absent skip, env kill switch
 *  - config validation: loud rejection of nonsensical values, defaults hold
 *  - delivery shape: { message: { customType "recall-nudge", "[recall-nudge] "
 *    prefix, display true } }, at most ONE nudge per prompt
 */

import { describe, test, expect } from "bun:test";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import {
  F2_NUDGE, DEFAULT_CONFIG, validateConfig, loadConfig, evaluateGates,
  recallToolActive, nudgeContent, default as createExtension,
} from "../index.ts";

function state(resumptionPending: boolean, promptsSeen: number) {
  return { resumptionPending, promptsSeen };
}

describe("the nudge sentence", () => {
  test("default nudge text is the F2 sentence byte-for-byte", () => {
    expect(F2_NUDGE).toBe(
      "Before you edit anything, use the project_recall tool to check this " +
      "project's past sessions for decisions or constraints relevant to the task.",
    );
    expect(DEFAULT_CONFIG.nudge).toBe(F2_NUDGE);
  });

  test("delivery content carries the required prefix", () => {
    expect(nudgeContent("check history")).toBe("[recall-nudge] check history");
    expect(nudgeContent(F2_NUDGE)).toBe(`[recall-nudge] ${F2_NUDGE}`);
  });
});

describe("gate: onResume (default true, resume-only)", () => {
  const cfg = { ...DEFAULT_CONFIG }; // onResume true, others off

  test("fires on the first prompt after a resume and not after that", () => {
    const first = evaluateGates(cfg, state(true, 0));
    expect(first).toMatchObject({ inject: true, gates: ["onResume"], consumeResume: true });
    const second = evaluateGates(cfg, state(false, 1));
    expect(second).toMatchObject({ inject: false, gates: [], consumeResume: false });
  });

  test("never fires on plain startup/new sessions", () => {
    expect(evaluateGates(cfg, state(false, 0)).inject).toBe(false);
  });

  test("the resumption window is consumed even when nothing is injected", () => {
    const killed = evaluateGates({ ...cfg, enabled: false }, state(true, 0));
    expect(killed).toMatchObject({ inject: false, consumeResume: true });
  });
});

describe("gate: everyPrompt", () => {
  const cfg = { ...DEFAULT_CONFIG, everyPrompt: true };

  test("fires on every prompt regardless of resume state", () => {
    for (let i = 0; i < 4; i++) {
      expect(evaluateGates(cfg, state(false, i)).gates).toEqual(["everyPrompt"]);
    }
    expect(evaluateGates(cfg, state(true, 0)).gates).toEqual(["onResume", "everyPrompt"]);
  });
});

describe("gate: everyNPrompts (in-memory counter, resets per process)", () => {
  test("fires on every Nth prompt (1-based counting)", () => {
    const cfg = { ...DEFAULT_CONFIG, everyNPrompts: 3 };
    const fires = [1, 2, 3, 4, 5, 6, 7].map((n) =>
      evaluateGates(cfg, state(false, n - 1)).inject); // promptsSeen = prompts already evaluated
    expect(fires).toEqual([false, false, true, false, false, true, false]);
  });

  test("N=1 degenerates to every prompt; 0 stays off", () => {
    const n1 = { ...DEFAULT_CONFIG, everyNPrompts: 1 };
    expect(evaluateGates(n1, state(false, 0)).gates).toEqual(["everyNPrompts"]);
    expect(evaluateGates(n1, state(false, 9)).gates).toEqual(["everyNPrompts"]);
    const off = { ...DEFAULT_CONFIG, everyNPrompts: 0 };
    expect(evaluateGates(off, state(false, 2)).inject).toBe(false);
  });

  test("a fresh process starts the counter at zero (documented caveat)", () => {
    // The counter lives in the extension instance: a new load (new Pi process)
    // begins at promptsSeen=0, so with N=2 the second prompt of the new
    // process fires again.
    const cfg = { ...DEFAULT_CONFIG, everyNPrompts: 2 };
    expect(evaluateGates(cfg, state(false, 5)).inject).toBe(true); // 6th prompt of process A
    expect(evaluateGates(cfg, state(false, 1)).inject).toBe(true); // 2nd prompt of process B
  });
});

describe("union of gates, deduped: at most ONE nudge per prompt", () => {
  test("everyPrompt + everyNPrompts both firing yields one inject, both named", () => {
    const cfg = { ...DEFAULT_CONFIG, everyPrompt: true, everyNPrompts: 2 };
    const d = evaluateGates(cfg, state(false, 1)); // prompt 2: both gates fire
    expect(d.inject).toBe(true);
    expect(d.gates).toEqual(["everyPrompt", "everyNPrompts"]);
    expect(new Set(d.gates).size).toBe(d.gates.length); // deduped
  });
});

describe("tool guard", () => {
  test("defined selectedTools without project_recall -> skip; with it -> inject", () => {
    expect(recallToolActive(["read", "bash", "edit", "write"], true)).toBe(false);
    expect(recallToolActive(["read", "bash", "project_recall"], true)).toBe(true);
  });

  test("undefined selectedTools falls back to registration", () => {
    expect(recallToolActive(undefined, true)).toBe(true);
    expect(recallToolActive(undefined, false)).toBe(false);
    expect(recallToolActive(null, true)).toBe(true);
  });
});

describe("config validation: loud rejection, defaults hold", () => {
  test("undefined and empty objects give clean defaults", () => {
    expect(validateConfig(undefined)).toEqual({ config: DEFAULT_CONFIG, problems: [] });
    expect(validateConfig({}).problems).toEqual([]);
  });

  test("nonsensical values are rejected with named problems", () => {
    const { config, problems } = validateConfig({
      enabled: "yes", onResume: 1, everyPrompt: null, everyNPrompts: -2,
      nudge: 42, delivery: "banner", surprise: true,
    });
    expect(problems.length).toBe(7);
    expect(problems.join("\n")).toContain("recallNudge.everyNPrompts");
    expect(problems.join("\n")).toContain("unknown key");
    expect(config).toEqual(DEFAULT_CONFIG); // every rejected key kept its default
  });

  test("fractional N is rejected; 0 and integers pass", () => {
    expect(validateConfig({ everyNPrompts: 1.5 }).problems.length).toBe(1);
    expect(validateConfig({ everyNPrompts: 0 }).problems).toEqual([]);
    expect(validateConfig({ everyNPrompts: 4 }).config.everyNPrompts).toBe(4);
  });

  test("loadConfig reads the agent settings recallNudge key", () => {
    const dir = mkdtempSync(join(tmpdir(), "pi-recall-nudge-cfg-"));
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, "settings.json"),
      JSON.stringify({ recallNudge: { everyNPrompts: 3, enabled: false } }));
    const { config, problems } = loadConfig(dir);
    expect(problems).toEqual([]);
    expect(config.everyNPrompts).toBe(3);
    expect(config.enabled).toBe(false);
    rmSync(dir, { recursive: true, force: true });
    // missing settings file: quiet defaults
    const empty = mkdtempSync(join(tmpdir(), "pi-recall-nudge-nocfg-"));
    expect(loadConfig(empty)).toEqual({ config: DEFAULT_CONFIG, problems: [] });
    rmSync(empty, { recursive: true, force: true });
  });
});

describe("extension wiring (fake pi handle)", () => {
  function fakePi(selectedTools?: string[]) {
    const handlers: Record<string, any[]> = {};
    const entries: any[] = [];
    return {
      handlers, entries,
      pi: {
        on: (ev: string, fn: any) => { (handlers[ev] ??= []).push(fn); },
        getAllTools: () => [{ name: "read" }, { name: "project_recall" }],
        appendEntry: (t: string, d: any) => entries.push([t, d]),
      },
      event: {
        type: "before_agent_start", prompt: "fix the gate positions",
        systemPrompt: "SYSTEM.",
        systemPromptOptions: selectedTools === undefined
          ? { cwd: "/tmp" }
          : { cwd: "/tmp", selectedTools },
      },
    };
  }

  test("resume -> first prompt injected as a visible, persistent message", async () => {
    const f = fakePi();
    createExtension(f.pi);
    await f.handlers["session_start"][0]({ type: "session_start", reason: "resume" });
    const r = await f.handlers["before_agent_start"][0](f.event);
    expect(r.message).toEqual({
      customType: "recall-nudge",
      content: `[recall-nudge] ${F2_NUDGE}`,
      display: true,
    });
    expect(r.systemPrompt).toBeUndefined(); // default delivery is message-only
    expect(f.entries[0][0]).toBe("pi-recall-nudge");
    expect(f.entries[0][1].gates).toEqual(["onResume"]);
    // second prompt: window consumed, exactly one nudge total
    const r2 = await f.handlers["before_agent_start"][0](f.event);
    expect(r2).toBeUndefined();
  });

  test("session_start reasons startup/new do not arm the resume gate", async () => {
    const f = fakePi();
    createExtension(f.pi);
    await f.handlers["session_start"][0]({ type: "session_start", reason: "new" });
    expect(await f.handlers["before_agent_start"][0](f.event)).toBeUndefined();
  });

  test("tool absent from the turn's selectedTools -> silent skip, window still consumed", async () => {
    const f = fakePi(["read", "bash", "edit", "write"]);
    createExtension(f.pi);
    await f.handlers["session_start"][0]({ type: "session_start", reason: "resume" });
    expect(await f.handlers["before_agent_start"][0](f.event)).toBeUndefined();
    const second = fakePi();
    createExtension(second.pi); // counter at 0 again in a fresh process
    await second.handlers["session_start"][0]({ type: "session_start", reason: "resume" });
    expect((await second.handlers["before_agent_start"][0](second.event)).message).toBeDefined();
  });

  test("PI_RECALL_NUDGE=0 kills everything, loudly quiet (no injection)", async () => {
    const f = fakePi();
    createExtension(f.pi);
    process.env.PI_RECALL_NUDGE = "0";
    try {
      await f.handlers["session_start"][0]({ type: "session_start", reason: "resume" });
      expect(await f.handlers["before_agent_start"][0](f.event)).toBeUndefined();
      expect(f.entries).toEqual([]);
    } finally {
      delete process.env.PI_RECALL_NUDGE;
    }
  });

  test("everyNPrompts injects on the Nth prompt with a named gate", async () => {
    const dir = mkdtempSync(join(tmpdir(), "pi-recall-nudge-nth-"));
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, "settings.json"),
      JSON.stringify({ recallNudge: { onResume: false, everyNPrompts: 2 } }));
    const prev = process.env.PI_CODING_AGENT_DIR;
    process.env.PI_CODING_AGENT_DIR = dir;
    try {
      const f = fakePi();
      createExtension(f.pi);
      const e1 = { ...f.event, prompt: "one" };
      const e2 = { ...f.event, prompt: "two" };
      expect(await f.handlers["before_agent_start"][0](e1)).toBeUndefined();
      const r2 = await f.handlers["before_agent_start"][0](e2);
      expect(r2.message.content).toBe(`[recall-nudge] ${F2_NUDGE}`);
      expect(f.entries[0][1].gates).toEqual(["everyNPrompts"]);
    } finally {
      process.env.PI_CODING_AGENT_DIR = prev;
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test("delivery systemPrompt appends the sentence to the system prompt too", async () => {
    const dir = mkdtempSync(join(tmpdir(), "pi-recall-nudge-sysp-"));
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, "settings.json"),
      JSON.stringify({ recallNudge: { delivery: "systemPrompt" } }));
    const prev = process.env.PI_CODING_AGENT_DIR;
    process.env.PI_CODING_AGENT_DIR = dir;
    try {
      const f = fakePi();
      createExtension(f.pi);
      await f.handlers["session_start"][0]({ type: "session_start", reason: "resume" });
      const r = await f.handlers["before_agent_start"][0](f.event);
      expect(r.message.display).toBe(true); // the visible message is always delivered
      expect(r.systemPrompt).toBe(`SYSTEM.\n\n${F2_NUDGE}`);
    } finally {
      process.env.PI_CODING_AGENT_DIR = prev;
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
