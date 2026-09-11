/**
 * The 7b notifier seam (BUILD-20260911): when a draft is registered, the
 * confirmation gate notifies the OPERATOR that a write is waiting. This is
 * an INTERFACE plus in-repo stubs only — out-of-band sending is NOT an
 * extension feature. In the decision-memory experiment the CONDUCTOR sends
 * the Signal summons (see docs/TRIAL-20260911-runbook.md); any future
 * automated-experiment sender would live outside this extension too.
 *
 * Channels (config `perseusRecall.write.notifiers`, default in-session+file):
 *   - "in-session" — the draft tool result IS the in-session confirmation
 *     prompt (pi sessions, decision 7b first bullet); this notifier marks
 *     that channel as served and carries no payload of its own.
 *   - "file"       — stub: one JSON line per pending draft appended to the
 *     notify file. The conductor (or a human watcher) consumes it.
 *   - "noop"       — explicit no-op (tests).
 *
 * Unknown channel names are rejected loudly at load (index.ts) and fall
 * back to the defaults — a channel is never silently dropped.
 */

import { appendFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";

export interface WriteNotification {
  kind: "pending_confirmation";
  at: string;
  draft_id: string;
  confirmation_code: string;
  tool: string;
  /** One operator-readable line: what wants to be written, where. */
  summary: string;
  expires_at: string;
  /** Whether an agent-confirmed exception is even configured. */
  agent_confirmed_allowed: boolean;
}

export interface NotifyReceipt {
  delivered: boolean;
  channel: string;
  detail?: string;
}

export interface WriteNotifier {
  readonly channel: string;
  notify(n: WriteNotification): Promise<NotifyReceipt>;
}

/** In-session channel: the tool result carries the prompt; nothing to send. */
export class InSessionNotifier implements WriteNotifier {
  readonly channel = "in-session";
  async notify(n: WriteNotification): Promise<NotifyReceipt> {
    return { delivered: true, channel: this.channel, detail: `draft ${n.draft_id} presented in the draft tool result` };
  }
}

/** File-based stub: JSONL, one line per pending draft. Best-effort, never throws. */
export class FileNotifier implements WriteNotifier {
  readonly channel = "file";
  constructor(private path: string) {}

  async notify(n: WriteNotification): Promise<NotifyReceipt> {
    try {
      mkdirSync(dirname(this.path), { recursive: true });
      appendFileSync(this.path, JSON.stringify(n) + "\n");
      return { delivered: true, channel: this.channel, detail: this.path };
    } catch (e: any) {
      return { delivered: false, channel: this.channel, detail: `append failed: ${e?.message ?? e}` };
    }
  }
}

/** Explicit no-op (tests, or `notifiers: []`). */
export class NoopNotifier implements WriteNotifier {
  readonly channel = "noop";
  async notify(): Promise<NotifyReceipt> {
    return { delivered: false, channel: this.channel, detail: "noop" };
  }
}

/** Fan out to every channel; one channel failing never blocks the others. */
export class CompositeNotifier implements WriteNotifier {
  readonly channel: string;
  constructor(private inner: WriteNotifier[]) {
    this.channel = inner.map((n) => n.channel).join("+") || "none";
  }
  async notify(n: WriteNotification): Promise<NotifyReceipt> {
    const receipts = await Promise.all(this.inner.map((w) => w.notify(n).catch((e: any) => (
      { delivered: false, channel: "?", detail: `notifier failed: ${e?.message ?? e}` }
    ))));
    return {
      delivered: receipts.some((r) => r.delivered),
      channel: this.channel,
      detail: receipts.map((r) => `${r.channel}:${r.delivered}`).join(" "),
    };
  }
}

export function notifierFromConfig(notifiers: string[], notifyFile: string): WriteNotifier {
  const inner: WriteNotifier[] = [];
  for (const name of notifiers) {
    if (name === "in-session") inner.push(new InSessionNotifier());
    else if (name === "file") inner.push(new FileNotifier(notifyFile));
    else if (name === "noop") inner.push(new NoopNotifier());
  }
  return new CompositeNotifier(inner);
}
