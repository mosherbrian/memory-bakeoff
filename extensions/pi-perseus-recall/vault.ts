/**
 * Vault operations for the decision-memory write surface.
 *
 * Creation goes through the documented operator CLI (`perseus-vault write`)
 * — the P1B-proven harness write path that lands ACTIVE verified records;
 * the public MCP `remember` tool deliberately creates non-serveable
 * proposals and is never used here. Lineage goes through the MCP
 * `perseus_vault_supersede` call, from_key = the OLD record (parameter
 * schema authoritative; supersession_binding.py Gen102 correction).
 *
 * Measured on the pinned 2.23.2 binary (2026-09-11 probe, scratch vault):
 *   - `write` creates a missing database file;
 *   - writing to an existing category+key UPDATES in place (callers must
 *     pre-check key uniqueness — the adapter refuses duplicates);
 *   - `perseus_vault_supersede` responds with status_updated
 *     ("deprecated") + from_valid_to_unix_ms — the status-flip delivery;
 *   - scan rows carry the native `environment` column projected from the
 *     record body, which the §2 scope guard verifies against;
 *   - deprecated records leave both scan and hybrid recall.
 */

import { spawn, type ChildProcess } from "node:child_process";
import { existsSync } from "node:fs";

export interface VaultConnectionConfig {
  bin: string;
  db: string;
  keyFile: string;
}

/** One vault server connection; newline-delimited JSON-RPC over stdio, lazily started. */
export class VaultServer {
  private proc: ChildProcess | null = null;
  private nextId = 1;
  private starting: Promise<void> | null = null;

  constructor(private cfg: VaultConnectionConfig) {}

  private spawnProc(): ChildProcess {
    const proc = spawn(this.cfg.bin, ["serve", "--db", this.cfg.db, "--encryption-key", this.cfg.keyFile], {
      stdio: ["pipe", "pipe", "inherit"],
    });
    const kill = () => { try { proc.kill("SIGTERM"); } catch { /* exiting */ } };
    process.on("exit", kill);
    process.on("SIGTERM", () => { kill(); process.exit(0); });
    process.on("SIGINT", () => { kill(); process.exit(0); });
    return proc;
  }

  private rpc(method: string, params: unknown): Promise<any> {
    if (!this.proc || !this.proc.stdin || !this.proc.stdout) {
      return Promise.reject(new Error("vault server not running"));
    }
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
            this.proc!.stdout!.off("data", onData);
            clearTimeout(timer);
            if (resp.error) reject(new Error(`vault rpc error: ${JSON.stringify(resp.error)}`));
            else resolve(resp.result);
            return;
          } catch { /* partial or non-JSON line */ }
        }
      };
      this.proc.stdout.on("data", onData);
      this.proc.stdin.write(line, (err) => { if (err) { clearTimeout(timer); reject(err); } });
    });
  }

  /** Start + initialize once; concurrent callers share the promise. */
  start(): Promise<void> {
    if (!this.starting) {
      this.starting = (async () => {
        this.proc = this.spawnProc();
        const info = await this.rpc("initialize", {
          protocolVersion: "2025-03-26", capabilities: {},
          clientInfo: { name: "pi-perseus-recall", version: "1" },
        });
        this.version = info?.serverInfo?.version ?? "unknown";
      })();
    }
    return this.starting;
  }

  version: string | null = null;

  async recall(query: string, limit: number, workspaceHash: string): Promise<any[]> {
    const result = await this.rpc("tools/call", {
      name: "perseus_vault_recall",
      arguments: { query, limit, mode: "hybrid", workspace_hash: workspaceHash },
    });
    const payload = structuredBody(result);
    return Array.isArray(payload?.items) ? payload.items : [];
  }

  /**
   * EXPLICIT_LINEAGE binding (supersession_binding.py): from = the OLD
   * entity, to = the NEW entity, relationship "supersedes". The receipt
   * carries the status flip (status_updated: "deprecated") and the old
   * record's valid_to — both are delivered verbatim to the caller.
   */
  async supersede(args: {
    from_category: string; from_key: string;
    to_category: string; to_key: string;
    relationship: "supersedes"; reason: string;
  }): Promise<any> {
    const result = await this.rpc("tools/call", {
      name: "perseus_vault_supersede",
      arguments: { ...args, relationship: "supersedes" },
    });
    return structuredBody(result);
  }

  async scan(workspaceHash: string, limit = 1000, includeArchived = true): Promise<any[]> {
    const result = await this.rpc("tools/call", {
      name: "perseus_vault_scan",
      arguments: { workspace_hash: workspaceHash, include_archived: includeArchived, limit },
    });
    const payload = structuredBody(result);
    return Array.isArray(payload?.items) ? payload.items : [];
  }

  async stats(): Promise<any> {
    const result = await this.rpc("tools/call", { name: "perseus_vault_stats", arguments: {} });
    return structuredBody(result);
  }
}

/** MCP tool-result body: structuredContent, else the single JSON text block. */
export function structuredBody(result: any): any {
  if (result?.structuredContent && typeof result.structuredContent === "object") {
    return result.structuredContent;
  }
  const text = result?.content?.[0]?.text;
  if (typeof text === "string") {
    try { return JSON.parse(text); } catch { /* fall through */ }
  }
  return {};
}

/** One operator CLI write; resolves to the JSON receipt ({ok, id, ...}). */
export function cliWrite(cfg: VaultConnectionConfig, args: {
  category: string; key: string; body: Record<string, unknown>; workspaceHash: string;
}): Promise<any> {
  return new Promise((resolve, reject) => {
    const child = spawn(cfg.bin, [
      "write", "--db", cfg.db, "--encryption-key", cfg.keyFile,
      "--category", args.category, "--key", args.key,
      "--body", JSON.stringify(args.body),
      "--workspace-hash", args.workspaceHash,
    ], { stdio: ["ignore", "pipe", "pipe"] });
    let out = "", err = "";
    child.stdout.on("data", (c) => { out += c; });
    child.stderr.on("data", (c) => { err += c; });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0) return reject(new Error(`perseus write failed (rc=${code}): ${err.slice(-400)}`));
      try { resolve(JSON.parse(out)); }
      catch (e) { reject(new Error(`perseus write did not return a JSON receipt: ${out.slice(-200)}`)); }
    });
  });
}

/** keygen only when the key file does not exist yet (first write in a fresh vault). */
export function ensureKeyFile(cfg: VaultConnectionConfig): Promise<void> {
  if (existsSync(cfg.keyFile)) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const child = spawn(cfg.bin, ["keygen", "--key-file", cfg.keyFile], { stdio: ["ignore", "pipe", "pipe"] });
    let err = "";
    child.stderr.on("data", (c) => { err += c; });
    child.on("error", reject);
    child.on("close", (code) => code === 0 ? resolve() : reject(new Error(`perseus keygen failed (rc=${code}): ${err.slice(-400)}`)));
  });
}
