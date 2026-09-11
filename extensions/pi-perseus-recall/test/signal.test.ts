/**
 * clawdbot Signal channel tests (7b amendment). The transport is ALWAYS
 * injected here — these tests never touch the network and never send a
 * Signal message. The wiring test uses a dead endpoint (port 1) so even
 * the real fetch path cannot reach the daemon.
 */

import { describe, test, expect, beforeEach, afterEach } from "bun:test";
import {
  ClawdbotSignalNotifier, validateSignalConfig, formatSignalMessage,
  SIGNAL_URL_DEFAULT, SIGNAL_TIMEOUT_MS_DEFAULT, type WriteNotification,
} from "../notifier.ts";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { default as registerExtension } from "../index.ts";

const NOTE: WriteNotification = {
  kind: "pending_confirmation",
  at: "2026-09-11T12:00:00.000Z",
  draft_id: "draft-abc123",
  confirmation_code: "abcd1234",
  tool: "project_perseus_remember",
  summary: "create decision/record-x in environment project: staging deploys via helm",
  expires_at: "2026-09-11T13:00:00.000Z",
  agent_confirmed_allowed: false,
};

describe("validateSignalConfig", () => {
  test("undefined means not configured, no problems", () => {
    const r = validateSignalConfig(undefined);
    expect(r.config).toBeNull();
    expect(r.problems).toEqual([]);
  });

  test("valid config with defaults applied", () => {
    const r = validateSignalConfig({ account: "+15412836540", recipients: ["u1"] });
    expect(r.problems).toEqual([]);
    expect(r.config).toEqual({
      account: "+15412836540", recipients: ["u1"],
      url: SIGNAL_URL_DEFAULT, timeoutMs: SIGNAL_TIMEOUT_MS_DEFAULT,
    });
  });

  test("missing account / recipients -> null config with named problems", () => {
    for (const raw of [{}, { account: "+1" }, { recipients: ["u1"] }, { account: "+1", recipients: [] },
      { account: "+1", recipients: "u1" }, { account: "+1", recipients: [""] }, "x", 7]) {
      const r = validateSignalConfig(raw);
      expect(r.config).toBeNull();
      expect(r.problems.length).toBeGreaterThanOrEqual(1);
    }
  });

  test("bad url/timeout types named, config still null", () => {
    const r = validateSignalConfig({ account: "+1", recipients: ["u1"], url: "", timeoutMs: -1 });
    expect(r.config).toBeNull();
    expect(r.problems.some((p) => p.includes("url"))).toBe(true);
    expect(r.problems.some((p) => p.includes("timeoutMs"))).toBe(true);
  });
});

describe("formatSignalMessage", () => {
  test("carries tool, draft id, code, expiry and summary", () => {
    const m = formatSignalMessage(NOTE);
    expect(m).toContain("project_perseus_remember");
    expect(m).toContain("draft-abc123");
    expect(m).toContain("abcd1234");
    expect(m).toContain("2026-09-11T13:00:00.000Z");
    expect(m).toContain("staging deploys via helm");
  });
});

describe("ClawdbotSignalNotifier (injected transport, no network)", () => {
  const CFG = { account: "+15412836540", recipients: ["uuid-brian"], url: "http://rpc.invalid/api/v1/rpc", timeoutMs: 100 };

  test("success: sends the clawdbot envelope, reports delivered", async () => {
    const calls: any[] = [];
    const n = new ClawdbotSignalNotifier(CFG, async (url, body) => {
      calls.push({ url, body });
      return { jsonrpc: "2.0", id: 1, result: { timestamp: "x" } };
    });
    const r = await n.notify(NOTE);
    expect(r.delivered).toBe(true);
    expect(r.channel).toBe("clawdbot-signal");
    expect(calls).toHaveLength(1);
    expect(calls[0].url).toBe(CFG.url);
    expect(calls[0].body.method).toBe("send");
    expect(calls[0].body.params.account).toBe("+15412836540");
    expect(calls[0].body.params.recipient).toEqual(["uuid-brian"]);
    expect(calls[0].body.params.message).toBe(formatSignalMessage(NOTE));
  });

  test("json-rpc error response -> not delivered, error named, no throw", async () => {
    const n = new ClawdbotSignalNotifier(CFG, async () => ({ jsonrpc: "2.0", id: 1, error: { code: -1, message: "nope" } }));
    const r = await n.notify(NOTE);
    expect(r.delivered).toBe(false);
    expect(r.detail).toContain("nope");
  });

  test("transport failure -> not delivered, never throws", async () => {
    const n = new ClawdbotSignalNotifier(CFG, async () => { throw new Error("ECONNREFUSED"); });
    const r = await n.notify(NOTE);
    expect(r.delivered).toBe(false);
    expect(r.detail).toContain("ECONNREFUSED");
  });

  test("a draft never fails because its notification failed (gate stays functional)", async () => {
    // the gate treats notifier output as informational; prove the notifier itself never rejects
    const n = new ClawdbotSignalNotifier(CFG, async () => { throw new Error("boom"); });
    await expect(n.notify(NOTE)).resolves.toBeTruthy();
  });
});

// ── wiring through the real extension (dead endpoint; no daemon contact) ────

let agentDir: string;
let prevAgentDir: string | undefined;

beforeEach(() => {
  agentDir = mkdtempSync(join(tmpdir(), "perseus-signal-wiring-"));
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
  bin: "/bin/true", db: "/tmp/signal-wiring-unused.sqlite", keyFile: "/tmp/signal-wiring-unused.key",
  workspaceHash: "b".repeat(64),
};

describe("signal channel wiring", () => {
  test("channel requested + valid config: drafts report the clawdbot channel (dead endpoint -> not delivered)", async () => {
    const { tools, problems } = register({
      perseusRecall: {
        ...BASE_CONFIG,
        write: {
          notifiers: ["in-session", "clawdbot-signal"],
          // dead endpoint + throwaway identifiers: nothing real is contacted
          signal: { account: "+10000000000", recipients: ["00000000-0000-0000-0000-000000000000"], url: "http://127.0.0.1:1/api/v1/rpc", timeoutMs: 500 },
        },
      },
    });
    expect(problems).toEqual([]);
    const draft = await tools.get("project_perseus_remember").execute("t", { content: "wiring check", source: { kind: "task", ref: "signal-wiring" } }, undefined as any, undefined as any, undefined as any);
    const notifierLine = draft.content[0].text.split("\n").find((l: string) => l.startsWith("notifier:"));
    expect(notifierLine).toContain("clawdbot-signal:false"); // refused fast, gate unaffected
    expect(notifierLine).toContain("in-session:true");
  });

  test("channel requested without signal config: loud problem, channel dropped, draft still works", async () => {
    const { tools, problems } = register({
      perseusRecall: { ...BASE_CONFIG, write: { notifiers: ["in-session", "clawdbot-signal"] } },
    });
    expect(problems.some((p) => p.includes("clawdbot-signal") && p.includes("dropped"))).toBe(true);
    const draft = await tools.get("project_perseus_remember").execute("t", { content: "wiring check", source: { kind: "task", ref: "signal-wiring" } }, undefined as any, undefined as any, undefined as any);
    const notifierLine = draft.content[0].text.split("\n").find((l: string) => l.startsWith("notifier:"));
    expect(notifierLine).not.toContain("clawdbot-signal");
    expect(notifierLine).toContain("in-session:true");
  });

  test("signal configured but channel not listed: config accepted, silently unused", () => {
    const { problems } = register({
      perseusRecall: {
        ...BASE_CONFIG,
        write: { signal: { account: "+10000000000", recipients: ["00000000-0000-0000-0000-000000000000"] } },
      },
    });
    expect(problems).toEqual([]);
  });
});
