/**
 * Vault location per BUILD-20260911 decision 7c:
 *   ~/.pi/agent/perseus/<sha256-cwd-hash>.vault
 * with the SAME hash scheme as pi-project-recall's hashCwd
 * (sha256(cwd), hex, truncated to 16 chars), so one project always maps to
 * one vault file. Explicit config (db / keyFile / workspaceHash) still wins
 * — the STUDY-20260911 configs supply all three and behave exactly as
 * before.
 */

import { createHash } from "node:crypto";
import { homedir } from "node:os";
import { join } from "node:path";

/** sha256(cwd) truncated to 16 hex chars — byte-identical to pi-project-recall's hashCwd. */
export function hashCwd(cwd: string): string {
  return createHash("sha256").update(cwd).digest("hex").slice(0, 16);
}

export interface PathConfig {
  db?: string;
  keyFile?: string;
  workspaceHash?: string;
}

export interface ResolvedVaultPaths {
  db: string;
  keyFile: string;
  workspaceHash: string;
  vaultDir: string;
}

export function agentDir(): string {
  return process.env.PI_CODING_AGENT_DIR ?? join(homedir(), ".pi", "agent");
}

/**
 * Explicit config wins; otherwise the 7c convention: db and key live under
 * <agentDir>/perseus/, named by the project's cwd hash, and the default
 * workspace hash IS the project cwd hash (per-project isolation on both
 * the file and the workspace axis).
 */
export function resolveVaultPaths(cwd: string, cfg: PathConfig): ResolvedVaultPaths {
  const dir = join(agentDir(), "perseus");
  const db = cfg.db && cfg.db.trim() ? cfg.db : join(dir, `${hashCwd(cwd)}.vault`);
  const keyFile = cfg.keyFile && cfg.keyFile.trim() ? cfg.keyFile : `${db}.key`;
  const workspaceHash = cfg.workspaceHash && cfg.workspaceHash.trim() ? cfg.workspaceHash : hashCwd(cwd);
  return { db, keyFile, workspaceHash, vaultDir: dir };
}
