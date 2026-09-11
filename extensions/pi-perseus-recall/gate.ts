/**
 * The 7a+7b confirmation gate (BUILD-20260911): NOTHING is written when an
 * agent drafts a record. The gate holds the pending operation until the
 * OPERATOR's in-session confirmation arrives — relayed as the draft's
 * one-time confirmation code, which exists only because the draft tool
 * result was presented in this session.
 *
 * Policy (decision 7a): human-confirmed writes by default
 * (`confirmed_by: "operator"`). The agent-confirmed exception exists only
 * when the operator configured `perseusRecall.write.allowAgentConfirmed:
 * true` AND the caller passes `confirmed_by: "agent"` explicitly.
 *
 * The gate is a pure state machine: writes go through an injected
 * WriteExecutor, so tests run it against a spy and the smoke runs it
 * against the real vault.
 */

import { randomBytes } from "node:crypto";

export interface PendingOperation {
  kind: "remember" | "supersede";
  category: string;
  key: string;
  content: string;
  environment: string;
  workspaceHash: string;
  /** Present only on supersede drafts (the OLD record). */
  supersede?: {
    from_category: string;
    from_key: string;
    from_environment: string;
    from_workspace_hash: string;
    reason: string;
  };
}

export interface DraftPresentation {
  draft_id: string;
  confirmation_code: string;
  confirmed_by: "operator";
  expires_at: string;
  tool: string;
  summary: string;
  operations: PendingOperation;
  notifier_receipts: string;
}

interface Draft {
  id: string;
  code: string;
  tool: string;
  summary: string;
  op: PendingOperation;
  createdAtMs: number;
  expiresAtMs: number;
  wrongCodes: number;
}

export interface WriteExecutor {
  execute(op: PendingOperation): Promise<unknown>;
}

export type ConfirmStage = "executed" | "rejected";

export interface ConfirmOutcome {
  ok: boolean;
  stage: ConfirmStage;
  /** On stage "executed": whatever the executor returned (receipts). */
  receipt?: unknown;
  draft_id?: string;
  /** Always present on rejection; describes exactly why nothing was written. */
  reason?: string;
}

export interface GateOptions {
  /** Draft time-to-live; expired drafts are refused and dropped. */
  ttlMs?: number;
  /** Decision 7a exception switch (config allowAgentConfirmed). */
  allowAgentConfirmed?: boolean;
  /** Wrong-code attempts before the draft is destroyed. */
  maxWrongCodes?: number;
  now?: () => number;
  randomToken?: (bytes: number) => string;
}

const DEFAULT_TTL_MS = 60 * 60 * 1000;
const DEFAULT_MAX_WRONG = 5;

export class ConfirmationGate {
  private drafts = new Map<string, Draft>();
  private ttlMs: number;
  private maxWrong: number;
  private now: () => number;
  private token: (bytes: number) => string;
  private allowAgent: boolean;

  constructor(
    private executor: WriteExecutor,
    private notifier: { notify(n: any): Promise<any> },
    opts: GateOptions = {},
  ) {
    this.ttlMs = opts.ttlMs ?? DEFAULT_TTL_MS;
    this.maxWrong = opts.maxWrongCodes ?? DEFAULT_MAX_WRONG;
    this.now = opts.now ?? (() => Date.now());
    this.token = opts.randomToken ?? ((bytes: number) => randomBytes(bytes).toString("hex"));
    this.allowAgent = opts.allowAgentConfirmed === true;
  }

  /**
   * Register a fully-validated pending operation. Fires the notifier seam
   * (best-effort; a notifier failure never blocks or registers nothing) and
   * returns the operator-facing presentation.
   */
  async register(tool: string, op: PendingOperation, summary: string): Promise<DraftPresentation> {
    const id = `draft-${this.token(3)}`;
    const code = this.token(4); // 8 hex chars
    const draft: Draft = {
      id, code, tool, summary, op,
      createdAtMs: this.now(),
      expiresAtMs: this.now() + this.ttlMs,
      wrongCodes: 0,
    };
    this.drafts.set(id, draft);
    let notifierReceipts = "none configured";
    try {
      const receipt = await this.notifier.notify({
        kind: "pending_confirmation",
        at: new Date(draft.createdAtMs).toISOString(),
        draft_id: id,
        confirmation_code: code,
        tool,
        summary,
        expires_at: new Date(draft.expiresAtMs).toISOString(),
        agent_confirmed_allowed: this.allowAgent === true,
      });
      notifierReceipts = receipt?.detail ?? JSON.stringify(receipt);
    } catch (e: any) {
      notifierReceipts = `notifier failed: ${e?.message ?? e}`;
    }
    return {
      draft_id: id,
      confirmation_code: code,
      confirmed_by: "operator",
      expires_at: new Date(draft.expiresAtMs).toISOString(),
      tool,
      summary,
      operations: op,
      notifier_receipts: notifierReceipts,
    };
  }

  async confirm(draftId: string, code: string, confirmedBy: "operator" | "agent"): Promise<ConfirmOutcome> {
    const draft = this.drafts.get(draftId);
    if (!draft) {
      return { ok: false, stage: "rejected", reason: `no pending draft ${JSON.stringify(draftId)} — nothing was written` };
    }
    if (this.now() >= draft.expiresAtMs) {
      this.drafts.delete(draftId);
      return { ok: false, stage: "rejected", draft_id: draftId, reason: `draft expired at ${new Date(draft.expiresAtMs).toISOString()} — nothing was written; re-draft` };
    }
    if (typeof code !== "string" || code !== draft.code) {
      draft.wrongCodes += 1;
      const killed = draft.wrongCodes >= this.maxWrong;
      if (killed) this.drafts.delete(draftId);
      return {
        ok: false, stage: "rejected", draft_id: draftId,
        reason: `confirmation code does not match draft ${draftId} (attempt ${draft.wrongCodes}/${this.maxWrong}${killed ? ", draft destroyed" : ""}) — nothing was written; the operator's code arrives only from the in-session draft presentation`,
      };
    }
    if (confirmedBy === "agent" && !this.allowAgent) {
      return {
        ok: false, stage: "rejected", draft_id: draftId,
        reason: 'confirmed_by "agent" is the decision-7a exception and this deployment does not have perseusRecall.write.allowAgentConfirmed=true — writes need the OPERATOR\'s confirmation; nothing was written',
      };
    }
    this.drafts.delete(draftId); // one-time: consume before executing
    try {
      const receipt = await this.executor.execute(draft.op);
      return { ok: true, stage: "executed", draft_id: draftId, receipt, reason: `confirmed_by=${confirmedBy}` };
    } catch (e: any) {
      return {
        ok: false, stage: "rejected", draft_id: draftId,
        reason: `the operator's confirmation was accepted but the write FAILED and the draft was consumed: ${e?.message ?? e}`,
      };
    }
  }

  pending(): number {
    return this.drafts.size;
  }
}
