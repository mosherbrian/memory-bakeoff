/**
 * The 7b notifier seam (BUILD-20260911): when a draft is registered, the
 * confirmation gate notifies the OPERATOR that a write is waiting. This is
 * an INTERFACE plus stubs — the Signal sender for automated experiments is
 * deliberately NOT built here; its exact send-path gets pinned separately.
 * A future SignalNotifier implements WriteNotifier and is appended to the
 * configured channel list; nothing else in the gate changes.
 *
 * Channels (config `perseusRecall.write.notifiers`, default both):
 *   - "in-session" — the draft tool result IS the in-session confirmation
 *     prompt (pi sessions, decision 7b first bullet); this notifier marks
 *     that channel as served and carries no payload of its own.
 *   - "file"       — the out-of-band STUB: one JSON line per pending draft
 *     appended to the notify file. A watcher (or the future Signal sender)
 *     consumes it. Nothing reads or waits on it in this build.
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

// ── clawdbot Signal channel (7b amendment, BUILD-20260911) ──────────────────
//
// Brian confirmed clawdbot as the Signal channel. The send-path is clean and
// production-proven: the signal-cli daemon (0.14.1, Podman pod) exposes
// JSON-RPC on 127.0.0.1:8081, and clawdbot's own trigger scripts
// (~/clawdbot/trigger-*.py) send with exactly this envelope:
//   {"jsonrpc":"2.0","method":"send","params":{"account":...,
//    "recipient":[<recipient uuid>...],"message":...}}
// Verified read-only on 2026-09-11 (method "version" -> 0.14.1). The
// account number and recipient UUIDs are operator identifiers and are NOT
// hardcoded here — they come from settings.json (perseusRecall.write.signal)
// so nothing private lands in the repository.

export const SIGNAL_URL_DEFAULT = "http://127.0.0.1:8081/api/v1/rpc";
export const SIGNAL_TIMEOUT_MS_DEFAULT = 10_000;

export interface ClawdbotSignalConfig {
  /** The daemon's own Signal account (E.164), from clawdbot's config. */
  account: string;
  /** Recipient UUIDs (typically the operator's). */
  recipients: string[];
  /** JSON-RPC endpoint; default: the clawdbot daemon. */
  url: string;
  timeoutMs: number;
}

/**
 * Validate the raw `perseusRecall.write.signal` value. Undefined means "not
 * configured" (no problems, null config). Any problem yields a null config
 * so the caller can drop the channel LOUDLY — never half-configured.
 */
export function validateSignalConfig(raw: unknown): { config: ClawdbotSignalConfig | null; problems: string[] } {
  if (raw === undefined || raw === null) return { config: null, problems: [] };
  const problems: string[] = [];
  if (typeof raw !== "object" || Array.isArray(raw)) {
    problems.push("perseusRecall.write.signal must be an object - signal channel not configured");
    return { config: null, problems };
  }
  const o = raw as Record<string, unknown>;
  if (typeof o.account !== "string" || !o.account.trim()) {
    problems.push("perseusRecall.write.signal.account must be a non-empty string (the daemon's Signal account)");
  }
  const recipientsOk = Array.isArray(o.recipients)
    && o.recipients.length > 0
    && o.recipients.every((r: unknown) => typeof r === "string" && !!r.trim());
  if (!recipientsOk) {
    problems.push("perseusRecall.write.signal.recipients must be a non-empty array of recipient UUID strings");
  }
  if (o.url !== undefined && (typeof o.url !== "string" || !o.url.trim())) {
    problems.push("perseusRecall.write.signal.url must be a non-empty string when set");
  }
  if (o.timeoutMs !== undefined && (typeof o.timeoutMs !== "number" || !(o.timeoutMs > 0))) {
    problems.push("perseusRecall.write.signal.timeoutMs must be a positive number when set");
  }
  if (problems.length) return { config: null, problems };
  return {
    config: {
      account: o.account as string,
      recipients: o.recipients as string[],
      url: (o.url as string) ?? SIGNAL_URL_DEFAULT,
      timeoutMs: (o.timeoutMs as number) ?? SIGNAL_TIMEOUT_MS_DEFAULT,
    },
    problems,
  };
}

/** Transport seam: injectable so tests never touch the network. */
export type PostJsonRpc = (url: string, body: Record<string, unknown>, timeoutMs: number) => Promise<any>;

export const defaultPostJsonRpc: PostJsonRpc = async (url, body, timeoutMs) => {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(timeoutMs),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
};

/** One operator-readable block: what wants to be written, and how to confirm it. */
export function formatSignalMessage(n: WriteNotification): string {
  return [
    `[perseus-write] ${n.tool}: draft ${n.draft_id} awaiting operator confirmation`,
    `code: ${n.confirmation_code} (expires ${n.expires_at})`,
    n.summary,
    "— pi-perseus-recall decision memory, this host",
  ].join("\n");
}

/** Best-effort Signal send via the clawdbot signal-cli daemon; never throws. */
export class ClawdbotSignalNotifier implements WriteNotifier {
  readonly channel = "clawdbot-signal";
  constructor(private cfg: ClawdbotSignalConfig, private post: PostJsonRpc = defaultPostJsonRpc) {}

  async notify(n: WriteNotification): Promise<NotifyReceipt> {
    try {
      const resp = await this.post(this.cfg.url, {
        jsonrpc: "2.0",
        method: "send",
        id: 1,
        params: {
          account: this.cfg.account,
          recipient: this.cfg.recipients,
          message: formatSignalMessage(n),
        },
      }, this.cfg.timeoutMs);
      if (resp && typeof resp === "object" && "error" in resp && resp.error) {
        return { delivered: false, channel: this.channel, detail: `signal-cli error: ${JSON.stringify(resp.error).slice(0, 200)}` };
      }
      return { delivered: true, channel: this.channel, detail: `sent via ${this.cfg.url}` };
    } catch (e: any) {
      return { delivered: false, channel: this.channel, detail: `send failed: ${e?.message ?? e}` };
    }
  }
}

export function notifierFromConfig(
  notifiers: string[],
  notifyFile: string,
  signal?: ClawdbotSignalConfig | null,
): WriteNotifier {
  const inner: WriteNotifier[] = [];
  for (const name of notifiers) {
    if (name === "in-session") inner.push(new InSessionNotifier());
    else if (name === "file") inner.push(new FileNotifier(notifyFile));
    else if (name === "noop") inner.push(new NoopNotifier());
    else if (name === "clawdbot-signal" && signal) inner.push(new ClawdbotSignalNotifier(signal));
  }
  return new CompositeNotifier(inner);
}
