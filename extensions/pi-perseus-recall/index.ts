/**
 * pi-perseus-recall: Pi recall path backed by a Perseus vault (MCP).
 *
 * STUDY-20260911-P1 adapter. Separate path by design: pi-project-recall/
 * and pi-recall-nudge/ stay untouched. Registers the SAME tool name
 * `project_recall` (same description text) so the untouched pi-recall-nudge
 * companion's active-tool guard and the F2-style nudge work unchanged.
 *
 * The extension is READ-ONLY over the vault: it spawns `perseus-vault serve`
 * and speaks newline-delimited JSON-RPC on stdio, issuing only
 * `perseus_vault_recall`. Supersession (EXPLICIT_LINEAGE) is applied at
 * SEED time (Gen102 binding_on pattern) — arm B/C vaults differ only in
 * lineage state; this extension is byte-identical in both arms.
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
 *   { bin, db, keyFile, workspaceHash, limit? }
 * Env kill switch: PI_PERSEUS_RECALL=0.
 */
import { spawn, type ChildProcess } from "node:child_process";
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

interface PerseusRecallConfig {
  bin: string;
  db: string;
  keyFile: string;
  workspaceHash: string;
  limit: number;
}

const DEFAULTS = { limit: 5 };

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
  for (const k of ["bin", "db", "keyFile", "workspaceHash"]) {
    if (typeof raw[k] !== "string" || !raw[k]) {
      problems.push(`perseusRecall.${k} must be a non-empty string`);
    }
  }
  if (raw.limit !== undefined && (typeof raw.limit !== "number" || raw.limit < 1)) {
    problems.push("perseusRecall.limit must be a number >= 1 - using default");
  }
  const config: PerseusRecallConfig = {
    bin: raw.bin, db: raw.db, keyFile: raw.keyFile, workspaceHash: raw.workspaceHash,
    limit: typeof raw.limit === "number" && raw.limit >= 1 ? raw.limit : DEFAULTS.limit,
  };
  return { config: problems.some(p => !p.includes("limit")) ? null : config, problems };
}

/** One vault server connection; newline-delimited JSON-RPC over stdio. */
class VaultServer {
  private proc: ChildProcess;
  private nextId = 1;

  constructor(cfg: PerseusRecallConfig) {
    this.proc = spawn(cfg.bin, ["serve", "--db", cfg.db, "--encryption-key", cfg.keyFile], {
      stdio: ["pipe", "pipe", "inherit"],
    });
    const kill = () => { try { this.proc.kill("SIGTERM"); } catch { /* exiting */ } };
    process.on("exit", kill);
    process.on("SIGTERM", () => { kill(); process.exit(0); });
    process.on("SIGINT", () => { kill(); process.exit(0); });
  }

  private rpc(method: string, params: unknown): Promise<any> {
    const id = this.nextId++;
    const line = JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n";
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("vault rpc timeout")), 30_000);
      const onData = (chunk: Buffer) => {
        // newline-delimited framing; only resolve on OUR id
        for (const l of chunk.toString().split("\n")) {
          if (!l.trim()) continue;
          try {
            const resp = JSON.parse(l);
            if (resp.id !== id) continue;
            this.proc.stdout!.off("data", onData);
            clearTimeout(timer);
            if (resp.error) reject(new Error(`vault rpc error: ${JSON.stringify(resp.error)}`));
            else resolve(resp.result);
            return;
          } catch { /* partial or non-JSON line */ }
        }
      };
      this.proc.stdout!.on("data", onData);
      this.proc.stdin!.write(line, (err) => { if (err) { clearTimeout(timer); reject(err); } });
    });
  }

  async initialize(): Promise<string> {
    const info = await this.rpc("initialize", {
      protocolVersion: "2025-03-26", capabilities: {},
      clientInfo: { name: "pi-perseus-recall", version: "1" },
    });
    return info?.serverInfo?.version ?? "unknown";
  }

  async recall(query: string, limit: number, workspaceHash: string): Promise<any[]> {
    const result = await this.rpc("tools/call", {
      name: "perseus_vault_recall",
      arguments: { query, limit, mode: "hybrid", workspace_hash: workspaceHash },
    });
    const payload = result?.structuredContent
      ?? (result?.content?.[0]?.text ? JSON.parse(result.content[0].text) : {});
    return Array.isArray(payload?.items) ? payload.items : [];
  }
}

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
  let server: VaultServer | null = null;
  let serverVersion: string | null = null;
  const getServer = async (): Promise<VaultServer> => {
    if (!server) {
      server = new VaultServer(config!);
      serverVersion = await server.initialize();
      console.error(`pi-perseus-recall: vault server ${serverVersion} on ${config!.db}`);
    }
    return server;
  };

  const parameters = {
    type: "object",
    properties: {
      query: { type: "string", description: "Search text for this project's past sessions." },
      limit: { type: "number", description: "Maximum hits to return." },
    },
    required: ["query"],
  };

  pi.registerTool({
    name: "project_recall",
    label: "Project Recall",
    description:
      "Search THIS PROJECT's memory store across ALL past sessions (not just this conversation): " +
      "messages and summaries recorded by earlier sessions in the same project directory. " +
      "Use it to find decisions, rejected approaches, failure explanations and prior work state " +
      "from previous sessions. Every hit carries its timestamp and source session - check them: " +
      "history may contain superseded values, and a later message overrides an earlier one.",
    promptSnippet: "Search all past sessions of this project",
    parameters,
    async execute(
      _toolCallId: string,
      params: { query: string; limit?: number },
      _signal: AbortSignal,
      _onUpdate: any,
      _ctx: any,
    ) {
      try {
        const srv = await getServer();
        const limit = typeof params.limit === "number" && params.limit >= 1
          ? params.limit : config!.limit;
        const hits = await srv.recall(params.query, limit, config!.workspaceHash);
        // P1B fix: return the MCP tool-result shape — a bare string is recorded
        // in the execution stream but delivered to the model as an EMPTY
        // toolResult (STUDY-20260911-P1 root cause 1). Same shape as
        // pi-project-recall/index.ts.
        if (hits.length === 0) {
          return { content: [{ type: "text", text: "No prior-session records matched that query." }] };
        }
        const text = hits.map((h: any) => {
          const body = typeof h.body_json === "string" ? h.body_json
            : JSON.stringify(h.body_json ?? h.assertion_text ?? h, null, 1);
          return `[project_recall] key=${h.key} id=${h.id} recorded=${h.created_at_unix_ms}`
            + (h.status ? ` status=${h.status}` : "")
            + (h.valid_to_unix_ms ? ` valid_to=${h.valid_to_unix_ms}` : "")
            + `\n${body}`;
        }).join("\n---\n");
        return { content: [{ type: "text", text }] };
      } catch (e: any) {
        return { content: [{ type: "text", text: `project_recall failed: ${e?.message ?? e}` }] };
      }
    },
  });
  console.error("pi-perseus-recall: registered project_recall (Perseus vault, read-only, "
    + `db=${config.db})`);
}
