/**
 * Confirmation gate tests (BUILD-20260911 scope item 6, "gate: no write
 * without confirm"). The gate runs against a SPY executor: any execution
 * observed here would otherwise require the operator's code, so these
 * tests prove the gate refuses everything else — wrong code, unknown
 * draft, expired draft, agent confirmation without the configured
 * exception — and that the write path runs exactly once on a valid
 * operator confirmation.
 */

import { describe, test, expect } from "bun:test";
import { ConfirmationGate, type PendingOperation, type WriteExecutor } from "../gate.ts";
import { InSessionNotifier, FileNotifier, NoopNotifier, CompositeNotifier } from "../notifier.ts";
import { mkdtempSync, rmSync, readFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

function spyExecutor(): WriteExecutor & { calls: PendingOperation[] } {
  const calls: PendingOperation[] = [];
  return {
    calls,
    async execute(op: PendingOperation) {
      calls.push(op);
      return { kind: op.kind, key: op.key, write_receipt: { ok: true, id: "native-1" } };
    },
  };
}

function op(over: Partial<PendingOperation> = {}): PendingOperation {
  return {
    kind: "remember", category: "decision", key: "record-test-1",
    content: "staging deploys via helm", environment: "project",
    workspaceHash: "b".repeat(64),
    source: { kind: "task", ref: "unit-test" },
    ...over,
  };
}

const OPTS = { ttlMs: 60_000, randomToken: (n: number) => "a".repeat(n * 2) };

describe("confirmation gate: no write without confirm", () => {
  test("register does NOT execute; it returns a draft + code and notifies", async () => {
    const ex = spyExecutor();
    const notified: any[] = [];
    const gate = new ConfirmationGate(ex, { notify: async (n) => { notified.push(n); return { delivered: true, channel: "in-session" }; } }, OPTS);
    const p = await gate.register("project_perseus_remember", op(), "summary");
    expect(ex.calls).toHaveLength(0); // nothing written at draft time
    expect(p.draft_id).toMatch(/^draft-/);
    expect(p.confirmation_code).toHaveLength(8);
    expect(notified).toHaveLength(1);
    expect(notified[0].draft_id).toBe(p.draft_id);
    expect(notified[0].confirmation_code).toBe(p.confirmation_code);
  });

  test("wrong code -> rejected, nothing executed, draft survives", async () => {
    const ex = spyExecutor();
    const gate = new ConfirmationGate(ex, { notify: async () => ({ delivered: true }) }, OPTS);
    const p = await gate.register("project_perseus_remember", op(), "s");
    const out = await gate.confirm(p.draft_id, "00000000", "operator");
    expect(out.ok).toBe(false);
    expect(out.stage).toBe("rejected");
    expect(out.reason).toContain("nothing was written");
    expect(ex.calls).toHaveLength(0);
    expect(gate.pending()).toBe(1);
  });

  test("correct operator code -> executes exactly once and consumes the draft", async () => {
    const ex = spyExecutor();
    const gate = new ConfirmationGate(ex, { notify: async () => ({ delivered: true }) }, OPTS);
    const p = await gate.register("project_perseus_remember", op(), "s");
    const out = await gate.confirm(p.draft_id, p.confirmation_code, "operator");
    expect(out.ok).toBe(true);
    expect(out.stage).toBe("executed");
    expect(ex.calls).toHaveLength(1);
    expect(ex.calls[0].source).toEqual({ kind: "task", ref: "unit-test" }); // provenance rides to the executor
    expect((out.receipt as any).write_receipt.ok).toBe(true);
    const again = await gate.confirm(p.draft_id, p.confirmation_code, "operator");
    expect(again.ok).toBe(false); // one-time use
    expect(ex.calls).toHaveLength(1);
  });

  test("unknown draft id -> rejected", async () => {
    const ex = spyExecutor();
    const gate = new ConfirmationGate(ex, { notify: async () => ({ delivered: true }) }, OPTS);
    const out = await gate.confirm("draft-nope", "a".repeat(8), "operator");
    expect(out.ok).toBe(false);
    expect(ex.calls).toHaveLength(0);
  });

  test("expired draft -> rejected and dropped", async () => {
    const ex = spyExecutor();
    let t = 1_000_000;
    const gate = new ConfirmationGate(ex, { notify: async () => ({ delivered: true }) }, { ttlMs: 10, now: () => t, randomToken: OPTS.randomToken });
    const p = await gate.register("tool", op(), "s");
    t += 11;
    const out = await gate.confirm(p.draft_id, p.confirmation_code, "operator");
    expect(out.ok).toBe(false);
    expect(out.reason).toContain("expired");
    expect(gate.pending()).toBe(0);
    expect(ex.calls).toHaveLength(0);
  });

  test("agent confirmation is the 7a exception: refused unless configured", async () => {
    const ex = spyExecutor();
    const gate = new ConfirmationGate(ex, { notify: async () => ({ delivered: true }) }, OPTS);
    const p = await gate.register("tool", op(), "s");
    const out = await gate.confirm(p.draft_id, p.confirmation_code, "agent");
    expect(out.ok).toBe(false);
    expect(out.reason).toContain("allowAgentConfirmed");
    expect(ex.calls).toHaveLength(0);
    // draft survives a policy refusal so the operator can still confirm
    expect(gate.pending()).toBe(1);
  });

  test("agent confirmation allowed when explicitly configured", async () => {
    const ex = spyExecutor();
    const gate = new ConfirmationGate(ex, { notify: async () => ({ delivered: true }) }, { ...OPTS, allowAgentConfirmed: true });
    const p = await gate.register("tool", op(), "s");
    const out = await gate.confirm(p.draft_id, p.confirmation_code, "agent");
    expect(out.ok).toBe(true);
    expect(ex.calls).toHaveLength(1);
  });

  test("executor failure consumes the draft and reports the failure", async () => {
    const failing: WriteExecutor = { async execute() { throw new Error("disk gone"); } };
    const gate = new ConfirmationGate(failing, { notify: async () => ({ delivered: true }) }, OPTS);
    const p = await gate.register("tool", op(), "s");
    const out = await gate.confirm(p.draft_id, p.confirmation_code, "operator");
    expect(out.ok).toBe(false);
    expect(out.reason).toContain("write FAILED");
    expect(gate.pending()).toBe(0);
  });

  test("max wrong codes destroys the draft", async () => {
    const ex = spyExecutor();
    const gate = new ConfirmationGate(ex, { notify: async () => ({ delivered: true }) }, { ...OPTS, maxWrongCodes: 2 });
    const p = await gate.register("tool", op(), "s");
    await gate.confirm(p.draft_id, "wrong1", "operator");
    await gate.confirm(p.draft_id, "wrong2", "operator");
    expect(gate.pending()).toBe(0);
    const out = await gate.confirm(p.draft_id, p.confirmation_code, "operator");
    expect(out.ok).toBe(false);
    expect(ex.calls).toHaveLength(0);
  });
});

describe("notifier seam stubs", () => {
  test("file stub appends one JSONL line per notification", async () => {
    const dir = mkdtempSync(join(tmpdir(), "perseus-notify-"));
    try {
      const path = join(dir, "nested", "notifications.jsonl");
      const n = new FileNotifier(path);
      const r = await n.notify({
        kind: "pending_confirmation", at: "t", draft_id: "draft-1",
        confirmation_code: "code", tool: "tool", summary: "s",
        expires_at: "e", agent_confirmed_allowed: false,
      });
      expect(r.delivered).toBe(true);
      const lines = readFileSync(path, "utf8").trim().split("\n");
      expect(lines).toHaveLength(1);
      expect(JSON.parse(lines[0]).draft_id).toBe("draft-1");
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test("file stub reports failure without throwing", async () => {
    const n = new FileNotifier("/proc/definitely/not/writable/x.jsonl");
    const r = await n.notify({} as any);
    expect(r.delivered).toBe(false);
    expect(r.detail).toContain("append failed");
  });

  test("noop reports undelivered; composite fans out", async () => {
    expect((await new NoopNotifier().notify({} as any)).delivered).toBe(false);
    const c = new CompositeNotifier([new InSessionNotifier(), new NoopNotifier()]);
    const r = await c.notify({} as any);
    expect(r.delivered).toBe(true);
    expect(r.channel).toBe("in-session+noop");
  });
});
