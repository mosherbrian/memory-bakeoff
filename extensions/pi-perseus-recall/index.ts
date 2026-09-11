/**
 * pi-perseus-recall: Perseus-backed project recall + human-confirmed
 * decision-memory writes (MCP + operator CLI).
 *
 * STUDY-20260911-P1 adapter. Separate path by design: pi-project-recall/
 * and pi-recall-nudge/ stay untouched. BUILD-20260911 decision 7d RENAMED
 * this adapter's tool from `project_recall` to `project_perseus_recall`
 * so both recall paths can be registered side by side: pi-project-recall
 * keeps `project_recall`, and the untouched pi-recall-nudge companion
 * keeps gating on `project_recall` (pi-project-recall's tool).
 *
 * BUILD-20260911 adds the agent-facing WRITE surface (decisions 7a/7b/7c/7e):
 *   - project_perseus_remember  — draft a new record (NOT written)
 *   - project_perseus_supersede — draft "new record replaces old" (NOT
 *     written; §2 scope guard enforced HERE, at the write surface)
 *   - project_perseus_confirm   — execute a draft, only with the operator's
 *     one-time confirmation code from the in-session draft presentation
 *   Writes go through the P1B-proven harness path (supersession_binding.py
 *   lineage): creation via the documented operator CLI `perseus-vault write`
 *   (active verified records — never the non-serveable MCP `remember`
 *   proposal tool), lineage via MCP `perseus_vault_supersede` with
 *   from_key = the OLD record (parameter schema authoritative; the summary
 *   description says the opposite — Gen102 correction, measured).
 *
 * The vault lives per decision 7c: ~/.pi/agent/perseus/<sha256-cwd-hash>.vault
 * (same hash scheme as pi-project-recall's hashCwd, sha256 hex [:16]);
 * explicit db/keyFile/workspaceHash config still wins (study configs are
 * byte-compatible).
 *
 * §2 scope guard: supersession across NON-OVERLAPPING environments is
 * rejected by default. Environments are opaque strings; overlap is byte
 * equality; the only way through is `allow_cross_environment: true` passed
 * EXPLICITLY on the draft (never implied) — and the operator still
 * confirms the write. The old record's environment is verified against the
 * vault's own stored value, fail-closed.
 *
 * Notifier seam (7b, as amended): the confirmation gate notifies the
 * operator through a clean WriteNotifier interface — in-session + file
 * stubs, plus the clawdbot Signal channel wired behind the seam (local
 * signal-cli daemon JSON-RPC "send", the exact path clawdbot's own
 * trigger scripts use; account/recipients come from settings.json, never
 * hardcoded). See notifier.ts.
 *
 * Provenance (recorded per conductor instruction, mandatory in every run
 * record + results doc): study binary
 * /var/home/bmosher/perseus-build/src/target/release/perseus-vault
 * sha256 c8a222ec7077d713212c2414d440586f564338aaa153eeb13b08ebf14854a172,
 * self-reports 2.23.2 (9c82920) — source-identical, NOT byte-identical to
 * the Gen21-measured arm64 tarball (e9b0912c5a2279f84d59a5ec8fb98e437a8f
 * 0feea8dac63dbca36759ff920dcb); built via build.sh GIT_HASH=9c82920, rust
 * 1.97.1 bookworm, DEFAULT features (the Dockerfile lean build is
 * FORBIDDEN — keyword-only wearing the version string). Supersede
 * direction: from_key = OLD (parameters authoritative).
 *
 * Config: agent settings.json key `perseusRecall`:
 *   { bin, db?, keyFile?, workspaceHash?, limit?,
 *     write?: { enabled?, defaultEnvironment?, allowAgentConfirmed?,
 *               notifyFile?, notifiers? } }
 * Env kill switch: PI_PERSEUS_RECALL=0 (kills recall AND write tools).
 */
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

import { VaultServer, cliWrite, ensureKeyFile } from "./vault.ts";
import { resolveVaultPaths } from "./paths.ts";
import {
  workspaceHashFor, bodyEnvelope, freshKey, validateKey, validateEnvironment,
  validateSource, summarize, DEFAULT_ENVIRONMENT, DEFAULT_CATEGORY,
} from "./records.ts";
import { evaluateScopeGuard, verifySourceRecord, OVERRIDE_PARAM } from "./guard.ts";
import { ConfirmationGate, type PendingOperation, type ConfirmOutcome, type DraftPresentation } from "./gate.ts";
import { notifierFromConfig, validateSignalConfig, type ClawdbotSignalConfig } from "./notifier.ts";

interface WriteConfig {
  enabled: boolean;
  defaultEnvironment: string;
  allowAgentConfirmed: boolean;
  notifyFile: string | null;
  notifiers: string[];
  signal: ClawdbotSignalConfig | null;
}

interface PerseusRecallConfig {
  bin: string;
  db: string | null;
  keyFile: string | null;
  workspaceHash: string | null;
  limit: number;
  write: WriteConfig;
}

const DEFAULTS = { limit: 5 };

const KNOWN_NOTIFIERS = ["in-session", "file", "noop", "clawdbot-signal"];

function loadConfig(): { config: PerseusRecallConfig | null; problems: string[] } {
  const problems: string[] = [];
  const dir = process.env.PI_CODING_AGENT_DIR ?? join(homedir(), ".pi", "agent");
  let raw: any;
  try {
    raw = JSON.parse(readFileSync(join(dir, "settings.json"), "utf8"))?.perseusRecall;
  } catch {
    raw = undefined;
  }
  if (raw === undefined || raw === null) {
    return { config: null, problems: ["perseusRecall key absent - tool disabled"] };
  }
  if (typeof raw.bin !== "string" || !raw.bin) {
    problems.push("perseusRecall.bin must be a non-empty string");
  }
  for (const k of ["db", "keyFile", "workspaceHash"] as const) {
    // optional since BUILD-20260911 (7c derivation); must be a string when present
    if (raw[k] !== undefined && (typeof raw[k] !== "string" || !raw[k])) {
      problems.push(`perseusRecall.${k} must be a non-empty string when set`);
    }
  }
  if (raw.limit !== undefined && (typeof raw.limit !== "number" || raw.limit < 1)) {
    problems.push("perseusRecall.limit must be a number >= 1 - using default");
  }

  // write sub-config: loud per-key rejection, default fallback (nudge pattern)
  const writeRaw = raw.write ?? {};
  const write: WriteConfig = {
    enabled: true,
    defaultEnvironment: DEFAULT_ENVIRONMENT,
    allowAgentConfirmed: false,
    notifyFile: null,
    notifiers: ["in-session", "file"],
    signal: null,
  };
  if (typeof writeRaw !== "object" || Array.isArray(writeRaw)) {
    problems.push("perseusRecall.write must be an object - using all write defaults");
  } else {
    if (writeRaw.enabled !== undefined && typeof writeRaw.enabled !== "boolean") {
      problems.push("perseusRecall.write.enabled must be a boolean - using default true");
    } else if (writeRaw.enabled !== undefined) {
      write.enabled = writeRaw.enabled;
    }
    if (writeRaw.defaultEnvironment !== undefined) {
      if (typeof writeRaw.defaultEnvironment !== "string" || !writeRaw.defaultEnvironment.trim()) {
        problems.push("perseusRecall.write.defaultEnvironment must be a non-empty string - using default 'project'");
      } else {
        write.defaultEnvironment = writeRaw.defaultEnvironment;
      }
    }
    if (writeRaw.allowAgentConfirmed !== undefined) {
      if (typeof writeRaw.allowAgentConfirmed !== "boolean") {
        problems.push("perseusRecall.write.allowAgentConfirmed must be a boolean - using default false");
      } else {
        write.allowAgentConfirmed = writeRaw.allowAgentConfirmed;
      }
    }
    if (writeRaw.notifyFile !== undefined) {
      if (typeof writeRaw.notifyFile !== "string" || !writeRaw.notifyFile) {
        problems.push("perseusRecall.write.notifyFile must be a non-empty string - using <vaultDir>/notifications.jsonl");
      } else {
        write.notifyFile = writeRaw.notifyFile;
      }
    }
    // 7b amendment: clawdbot Signal channel config (identifiers live here, never in the repo)
    const signal = validateSignalConfig(writeRaw.signal);
    for (const p of signal.problems) problems.push(p);
    write.signal = signal.config;
    if (writeRaw.notifiers !== undefined) {
      const ok = Array.isArray(writeRaw.notifiers)
        && writeRaw.notifiers.every((n: unknown) => typeof n === "string" && KNOWN_NOTIFIERS.includes(n));
      if (!ok) {
        problems.push(`perseusRecall.write.notifiers must be a subset of ${JSON.stringify(KNOWN_NOTIFIERS)} - using default`);
      } else if (Array.isArray(writeRaw.notifiers) && writeRaw.notifiers.includes("clawdbot-signal") && !write.signal) {
        // requested but not usable: drop the channel loudly, keep the rest
        problems.push('perseusRecall.write.signal (account + recipients) is required for the "clawdbot-signal" notifier - channel dropped');
        write.notifiers = (writeRaw.notifiers as string[]).filter((n) => n !== "clawdbot-signal");
      } else {
        write.notifiers = writeRaw.notifiers;
      }
    }
  }

  if (!raw.bin || typeof raw.bin !== "string") {
    return { config: null, problems };
  }
  const config: PerseusRecallConfig = {
    bin: raw.bin,
    db: typeof raw.db === "string" ? raw.db : null,
    keyFile: typeof raw.keyFile === "string" ? raw.keyFile : null,
    workspaceHash: typeof raw.workspaceHash === "string" ? raw.workspaceHash : null,
    limit: typeof raw.limit === "number" && raw.limit >= 1 ? raw.limit : DEFAULTS.limit,
    write,
  };
  return { config, problems };
}

// ── formatting helpers (pure; testable through the tools) ──────────────────

function text(t: string) {
  return { content: [{ type: "text" as const, text: t }] };
}

function formatDraft(p: DraftPresentation): string {
  const op = p.operations;
  const lines = [
    "[perseus-write] DRAFT — NOTHING IS WRITTEN YET",
    `tool: ${p.tool}`,
    `draft_id: ${p.draft_id}`,
    `confirmation_code: ${p.confirmation_code}`,
    `expires_at: ${p.expires_at}`,
    `notifier: ${p.notifier_receipts}`,
    `record: category=${op.category} key=${op.key}`,
    `environment: ${op.environment} (workspace ${op.workspaceHash.slice(0, 16)}…)`,
    `source: kind=${op.source.kind} ref=${op.source.ref}`
      + (op.source.timestamp ? ` at=${op.source.timestamp}` : ""),
    `content: ${op.content}`,
  ];
  if (op.kind === "supersede" && op.supersede) {
    lines.push(
      `replaces: ${op.supersede.from_category}/${op.supersede.from_key} `
      + `(environment ${op.supersede.from_environment})`,
      `reason: ${op.supersede.reason}`,
    );
  }
  lines.push(
    "PRESENT THIS DRAFT TO THE OPERATOR. The write happens ONLY after the operator "
    + "confirms in this session: call project_perseus_confirm with draft_id + "
    + 'confirmation_code (confirmed_by defaults to "operator"; "agent" is the '
    + "decision-7a exception and requires allowAgentConfirmed=true in config).",
  );
  return lines.join("\n");
}

function formatConfirmOutcome(outcome: ConfirmOutcome): string {
  if (outcome.stage === "rejected") {
    return `[perseus-write] NOT WRITTEN — ${outcome.reason}`;
  }
  const r: any = outcome.receipt ?? {};
  const lines = [
    `[perseus-write] WRITTEN (draft ${outcome.draft_id ?? "?"}, ${outcome.reason})`,
    `create: key=${r.key} written to the vault (write receipt id=${r.write_receipt?.id ?? "?"} ok=${r.write_receipt?.ok ?? "?"})`,
  ];
  if (r.kind === "supersede" && r.supersede_receipt) {
    const s = r.supersede_receipt;
    lines.push(
      "supersede: lineage applied —",
      `  status flip delivered: ${s.from_entity_key} status_updated=${JSON.stringify(s.status_updated)}`,
      `  valid_to delivered: from_valid_to_unix_ms=${s.from_valid_to_unix_ms ?? "?"}`,
      "  (the superseded record has left hybrid recall; this receipt is the status delivery)",
    );
  }
  return lines.join("\n");
}

function refusal(...reasons: string[]) {
  return text(`[perseus-write] DRAFT REFUSED — NOTHING IS WRITTEN.\n${reasons.join("\n")}`);
}

// ── the extension ───────────────────────────────────────────────────────────

export default function (pi: any) {
  if (process.env.PI_PERSEUS_RECALL === "0") {
    console.error("pi-perseus-recall: disabled (PI_PERSEUS_RECALL=0)");
    return;
  }
  const { config, problems } = loadConfig();
  for (const p of problems) console.error(`pi-perseus-recall: ${p}`);
  if (!config) {
    console.error("pi-perseus-recall: no usable perseusRecall config - not registering");
    return;
  }
  const cwd = process.cwd();
  const paths = resolveVaultPaths(cwd, config);
  const writeCfg = config.write;
  const conn = { bin: config.bin, db: paths.db, keyFile: paths.keyFile };
  const resolvedEnv = { defaultEnvironment: writeCfg.defaultEnvironment, workspaceHash: paths.workspaceHash };
  console.error(`pi-perseus-recall: vault ${paths.db} (workspace ${paths.workspaceHash.slice(0, 16)}…)`);

  let server: VaultServer | null = null;
  const getServer = async (): Promise<VaultServer> => {
    if (!server) {
      server = new VaultServer(conn);
      await server.start();
      console.error(`pi-perseus-recall: vault server ${server.version} on ${paths.db}`);
    }
    return server;
  };

  // ── read path: project_perseus_recall (renamed per 7d) ──
  pi.registerTool({
    name: "project_perseus_recall",
    label: "Project Recall (Perseus)",
    description:
      "Search THIS PROJECT's Perseus decision memory across ALL past sessions (not just this conversation): " +
      "messages and summaries recorded by earlier sessions in the same project directory. " +
      "Use it to find decisions, rejected approaches, failure explanations and prior work state " +
      "from previous sessions. Every hit carries its timestamp and source session - check them: " +
      "history may contain superseded values, and a later message overrides an earlier one.",
    promptSnippet: "Search all past sessions of this project",
    parameters: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search text for this project's past sessions." },
        limit: { type: "number", description: "Maximum hits to return." },
      },
      required: ["query"],
    },
    async execute(
      _toolCallId: string,
      params: { query: string; limit?: number },
      _signal: AbortSignal,
      _onUpdate: any,
      _ctx: any,
    ) {
      try {
        if (!existsSync(paths.db)) {
          return text(`No vault exists yet for this project (${paths.db}). Nothing recorded to recall.`);
        }
        const srv = await getServer();
        const limit = typeof params.limit === "number" && params.limit >= 1
          ? params.limit : config!.limit;
        const hits = await srv.recall(params.query, limit, paths.workspaceHash);
        // P1B fix: return the MCP tool-result shape — a bare string is recorded
        // in the execution stream but delivered to the model as an EMPTY
        // toolResult (STUDY-20260911-P1 root cause 1).
        if (hits.length === 0) {
          return text("No prior-session records matched that query.");
        }
        const body = hits.map((h: any) => {
          const bj = typeof h.body_json === "string" ? h.body_json
            : JSON.stringify(h.body_json ?? h.assertion_text ?? h, null, 1);
          return `[project_perseus_recall] key=${h.key} id=${h.id} recorded=${h.created_at_unix_ms}`
            + (h.status ? ` status=${h.status}` : "")
            + (h.valid_to_unix_ms ? ` valid_to=${h.valid_to_unix_ms}` : "")
            + `\n${bj}`;
        }).join("\n---\n");
        return text(body);
      } catch (e: any) {
        return text(`project_perseus_recall failed: ${e?.message ?? e}`);
      }
    },
  });

  // ── write surface (BUILD-20260911; guarded + gated) ──
  if (!writeCfg.enabled) {
    console.error("pi-perseus-recall: write surface disabled (perseusRecall.write.enabled=false); "
      + "registered project_perseus_recall (read-only)");
    return;
  }

  const executor = {
    async execute(op: PendingOperation): Promise<unknown> {
      await ensureKeyFile(conn);
      const body = bodyEnvelope({
        content: op.content,
        environment: op.environment,
        recordedAtMs: Date.now(),
        source: op.source,
        supersession: op.supersede
          ? { supersedes_key: op.supersede.from_key, reason: op.supersede.reason }
          : undefined,
      });
      const write_receipt = await cliWrite(conn, {
        category: op.category, key: op.key, body, workspaceHash: op.workspaceHash,
      });
      if (op.kind === "remember") {
        return { kind: "remember", key: op.key, write_receipt };
      }
      // EXPLICIT_LINEAGE, from_key = the OLD record (supersession_binding.py Gen102)
      const srv = await getServer();
      const supersede_receipt = await srv.supersede({
        from_category: op.supersede!.from_category,
        from_key: op.supersede!.from_key,
        to_category: op.category,
        to_key: op.key,
        relationship: "supersedes",
        reason: op.supersede!.reason,
      });
      return { kind: "supersede", key: op.key, write_receipt, supersede_receipt };
    },
  };

  const gate = new ConfirmationGate(
    executor,
    notifierFromConfig(writeCfg.notifiers, writeCfg.notifyFile ?? join(paths.vaultDir, "notifications.jsonl"), writeCfg.signal),
    { allowAgentConfirmed: writeCfg.allowAgentConfirmed },
  );

  /** Active-key uniqueness in one workspace (the CLI updates in place on duplicates). */
  const keyInUse = async (ws: string, category: string, key: string): Promise<boolean> => {
    if (!existsSync(paths.db)) return false;
    const items = await (await getServer()).scan(ws, 1000, true);
    return items.some((i: any) => i.category === category && i.key === key);
  };

  interface CommonParams {
    content?: string; category?: string; key?: string; environment?: string;
    source?: unknown;
  }

  function parseCommon(params: CommonParams): {
    error?: string; category: string; key: string; environment: string; ws: string;
    source: ReturnType<typeof validateSource>["source"];
  } {
    const content = typeof params.content === "string" ? params.content.trim() : "";
    if (!content) return { error: "content must be a non-empty string (the assertion to record)", category: "", key: "", environment: "", ws: "", source: null };
    const category = typeof params.category === "string" && params.category.trim()
      ? params.category.trim() : DEFAULT_CATEGORY;
    const key = params.key === undefined || params.key === "" ? freshKey() : params.key;
    const keyProblem = validateKey(key);
    if (keyProblem) return { error: keyProblem, category: "", key: "", environment: "", ws: "", source: null };
    const environment = typeof params.environment === "string" && params.environment
      ? params.environment : resolvedEnv.defaultEnvironment;
    const envProblem = validateEnvironment(environment);
    if (envProblem) return { error: envProblem, category: "", key: "", environment: "", ws: "", source: null };
    const src = validateSource(params.source);
    if (src.problem) return { error: src.problem, category: "", key: "", environment: "", ws: "", source: null };
    return { category, key, environment, ws: workspaceHashFor(environment, resolvedEnv), source: src.source };
  }

  pi.registerTool({
    name: "project_perseus_remember",
    label: "Remember (Perseus, draft)",
    description:
      "DRAFT a decision record for THIS project's Perseus memory. Nothing is written until the "
      + "operator confirms: the tool returns a draft_id + confirmation_code that MUST be presented "
      + "in-session; the write happens only after project_perseus_confirm is called with them.",
    promptSnippet: "Draft a project decision record (operator-confirmed write)",
    parameters: {
      type: "object",
      properties: {
        content: { type: "string", description: "The decision/assertion text to record." },
        source: {
          type: "object",
          description: "REQUIRED provenance of this record (proposal §1): where the assertion came from.",
          properties: {
            kind: { type: "string", enum: ["task", "artifact", "instruction"], description: "What kind of source this came from." },
            ref: { type: "string", description: "Non-empty pointer to the source (task id, artifact path, instruction context...)." },
            timestamp: { type: "string", description: "Optional ISO-8601 timestamp of the source event." },
          },
          required: ["kind", "ref"],
        },
        category: { type: "string", description: `Record category (default "${DEFAULT_CATEGORY}").` },
        key: { type: "string", description: "Record key (default: fresh record-<hex>; keys are never reused)." },
        environment: { type: "string", description: `Environment scope (default "${writeCfg.defaultEnvironment}").` },
      },
      required: ["content", "source"],
    },
    async execute(_toolCallId: string, params: CommonParams) {
      try {
        const p = parseCommon(params);
        if (p.error) return refusal(p.error);
        if (await keyInUse(p.ws, p.category, p.key)) {
          return refusal(`key ${p.category}/${p.key} already exists in environment ${p.environment}; `
            + "keys are never reused (the CLI would update the old record in place). "
            + "Use a fresh key, or supersede the existing record.");
        }
        const op: PendingOperation = {
          kind: "remember", category: p.category, key: p.key,
          content: (params.content as string).trim(), environment: p.environment, workspaceHash: p.ws,
          source: p.source!,
        };
        const presentation = await gate.register(
          "project_perseus_remember", op,
          `create ${p.category}/${p.key} in environment ${p.environment}: ${summarize(op.content)}`,
        );
        return text(formatDraft(presentation));
      } catch (e: any) {
        return refusal(`draft failed: ${e?.message ?? e}`);
      }
    },
  });

  pi.registerTool({
    name: "project_perseus_supersede",
    label: "Supersede (Perseus, draft)",
    description:
      "DRAFT a supersession: write a NEW decision record that replaces an existing one "
      + "(EXPLICIT_LINEAGE, old record retained). Nothing is written until the operator confirms. "
      + "Supersession across non-overlapping environments is rejected by default; overriding needs "
      + "allow_cross_environment: true passed explicitly, and the operator still confirms.",
    promptSnippet: "Draft a record that replaces an outdated one (operator-confirmed)",
    parameters: {
      type: "object",
      properties: {
        content: { type: "string", description: "The NEW decision/assertion text." },
        source: {
          type: "object",
          description: "REQUIRED provenance of the NEW record (proposal §1): where the new assertion came from.",
          properties: {
            kind: { type: "string", enum: ["task", "artifact", "instruction"], description: "What kind of source this came from." },
            ref: { type: "string", description: "Non-empty pointer to the source." },
            timestamp: { type: "string", description: "Optional ISO-8601 timestamp of the source event." },
          },
          required: ["kind", "ref"],
        },
        from_key: { type: "string", description: "Key of the OLD record being superseded." },
        from_category: { type: "string", description: "Category of the OLD record (default: same as category)." },
        reason: { type: "string", description: "Why the new record replaces the old one (required)." },
        category: { type: "string", description: `New record category (default "${DEFAULT_CATEGORY}").` },
        key: { type: "string", description: "NEW record key (default: fresh record-<hex>)." },
        environment: { type: "string", description: `New record environment (default "${writeCfg.defaultEnvironment}").` },
        from_environment: { type: "string", description: `Old record's environment (default "${writeCfg.defaultEnvironment}").` },
        allow_cross_environment: { type: "boolean", description: "Explicit §2 override for non-overlapping environments (default false)." },
      },
      required: ["content", "source", "from_key", "reason"],
    },
    async execute(_toolCallId: string, params: {
      content?: string; from_key?: string; from_category?: string; reason?: string;
    } & CommonParams & { allow_cross_environment?: boolean }) {
      try {
        const p = parseCommon(params);
        if (p.error) return refusal(p.error);
        const from_key = params.from_key ?? "";
        const keyProblem = validateKey(from_key);
        if (keyProblem) return refusal(`from_key: ${keyProblem}`);
        const reason = typeof params.reason === "string" ? params.reason.trim() : "";
        if (!reason) return refusal("reason is required: why does the new record replace the old one?");
        const from_category = typeof params.from_category === "string" && params.from_category.trim()
          ? params.from_category.trim() : p.category;
        const fromEnvClaim = typeof params.from_environment === "string" && params.from_environment
          ? params.from_environment : resolvedEnv.defaultEnvironment;
        if (!existsSync(paths.db)) {
          return refusal(`no vault exists yet (${paths.db}) — there is nothing to supersede`);
        }
        const srv = await getServer();
        const fromWs = workspaceHashFor(fromEnvClaim, resolvedEnv);
        const rows = await srv.scan(fromWs, 1000, true);
        const old = rows.find((i: any) => i.category === from_category && i.key === from_key) ?? null;
        const source = verifySourceRecord(fromEnvClaim, {
          found: !!old,
          stored_environment: old?.environment ?? null,
          status: old?.status ?? null,
        });
        if (!source.allowed) return refusal(source.reason);
        // the stored environment is authoritative and now verified equal to the claim
        const fromEnvVerified = old!.environment as string;
        const guard = evaluateScopeGuard({
          from_environment: fromEnvVerified,
          to_environment: p.environment,
          allow_cross_environment: params.allow_cross_environment,
        });
        if (!guard.allowed) return refusal(guard.reason);
        if (await keyInUse(p.ws, p.category, p.key)) {
          return refusal(`key ${p.category}/${p.key} already exists in environment ${p.environment}; keys are never reused`);
        }
        const op: PendingOperation = {
          kind: "supersede", category: p.category, key: p.key,
          content: (params.content as string).trim(), environment: p.environment, workspaceHash: p.ws,
          source: p.source!,
          supersede: {
            from_category, from_key,
            from_environment: fromEnvVerified, from_workspace_hash: fromWs,
            reason,
          },
        };
        const presentation = await gate.register(
          "project_perseus_supersede", op,
          `write ${p.category}/${p.key} in environment ${p.environment} superseding `
          + `${from_category}/${from_key} (environment ${fromEnvVerified}): ${summarize(op.content)} — ${summarize(reason, 60)}`,
        );
        return text(formatDraft(presentation));
      } catch (e: any) {
        return refusal(`draft failed: ${e?.message ?? e}`);
      }
    },
  });

  pi.registerTool({
    name: "project_perseus_confirm",
    label: "Confirm (Perseus, executes a draft)",
    description:
      "Execute a pending Perseus write draft — ONLY with the operator's in-session confirmation: "
      + "pass the draft_id and the one-time confirmation_code from the presented draft. "
      + 'confirmed_by defaults to "operator" (decision 7a); "agent" is an explicit exception '
      + "that this deployment rejects unless allowAgentConfirmed=true is configured.",
    promptSnippet: "Execute an operator-confirmed Perseus write draft",
    parameters: {
      type: "object",
      properties: {
        draft_id: { type: "string", description: "The pending draft's id." },
        confirmation_code: { type: "string", description: "The one-time code from the draft presentation." },
        confirmed_by: { type: "string", enum: ["operator", "agent"], description: 'Who confirmed (default "operator").' },
      },
      required: ["draft_id", "confirmation_code"],
    },
    async execute(_toolCallId: string, params: { draft_id?: string; confirmation_code?: string; confirmed_by?: string }) {
      try {
        if (typeof params.draft_id !== "string" || !params.draft_id) {
          return text("[perseus-write] NOT WRITTEN — draft_id is required");
        }
        if (typeof params.confirmation_code !== "string" || !params.confirmation_code) {
          return text("[perseus-write] NOT WRITTEN — confirmation_code is required (the operator's code from the in-session draft)");
        }
        const by = params.confirmed_by === "agent" ? "agent" : "operator";
        const outcome = await gate.confirm(params.draft_id, params.confirmation_code, by);
        return text(formatConfirmOutcome(outcome));
      } catch (e: any) {
        return text(`[perseus-write] NOT WRITTEN — confirm failed: ${e?.message ?? e}`);
      }
    },
  });

  console.error(
    `pi-perseus-recall: registered project_perseus_recall + write surface `
    + `(remember/supersede draft, operator-gated confirm; env "${writeCfg.defaultEnvironment}", `
    + `allowAgentConfirmed=${writeCfg.allowAgentConfirmed}, notifiers=${writeCfg.notifiers.join("+")}; `
    + `db=${paths.db})`,
  );
}
