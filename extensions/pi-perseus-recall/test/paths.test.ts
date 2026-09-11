/**
 * 7c vault-path tests: ~/.pi/agent/perseus/<sha256-cwd-hash>.vault with the
 * SAME hash scheme as pi-project-recall's hashCwd (sha256 hex [:16]);
 * explicit config still wins (STUDY-20260911 configs stay byte-compatible).
 */

import { describe, test, expect, beforeEach, afterEach } from "bun:test";
import { createHash } from "node:crypto";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { hashCwd, resolveVaultPaths } from "../paths.ts";

let agentDir: string;
let prev: string | undefined;

beforeEach(() => {
  agentDir = mkdtempSync(join(tmpdir(), "perseus-paths-"));
  prev = process.env.PI_CODING_AGENT_DIR;
  process.env.PI_CODING_AGENT_DIR = agentDir;
});

afterEach(() => {
  rmSync(agentDir, { recursive: true, force: true });
  if (prev === undefined) delete process.env.PI_CODING_AGENT_DIR;
  else process.env.PI_CODING_AGENT_DIR = prev;
});

describe("7c vault path derivation", () => {
  test("hashCwd matches pi-project-recall's scheme: sha256 hex truncated to 16", () => {
    const expectHash = (cwd: string) => createHash("sha256").update(cwd).digest("hex").slice(0, 16);
    for (const cwd of ["/home/bmosher/some/repo", "/", "/tmp/x"]) {
      expect(hashCwd(cwd)).toBe(expectHash(cwd));
      expect(hashCwd(cwd)).toMatch(/^[0-9a-f]{16}$/);
    }
  });

  test("db defaults to <agentDir>/perseus/<hash16>.vault with sibling key and same workspace hash", () => {
    const cwd = "/home/bmosher/example";
    const p = resolveVaultPaths(cwd, {});
    const h = hashCwd(cwd);
    expect(p.db).toBe(join(agentDir, "perseus", `${h}.vault`));
    expect(p.keyFile).toBe(join(agentDir, "perseus", `${h}.vault.key`));
    expect(p.workspaceHash).toBe(h);
    expect(p.vaultDir).toBe(join(agentDir, "perseus"));
  });

  test("distinct projects map to distinct vault files", () => {
    const a = resolveVaultPaths("/home/bmosher/repo-a", {});
    const b = resolveVaultPaths("/home/bmosher/repo-b", {});
    expect(a.db).not.toBe(b.db);
    expect(a.workspaceHash).not.toBe(b.workspaceHash);
  });

  test("explicit db/keyFile/workspaceHash win (study configs unchanged)", () => {
    const p = resolveVaultPaths("/some/cwd", {
      db: "/scratch/vault-on.sqlite",
      keyFile: "/scratch/vault.key",
      workspaceHash: "b".repeat(64),
    });
    expect(p.db).toBe("/scratch/vault-on.sqlite");
    expect(p.keyFile).toBe("/scratch/vault.key");
    expect(p.workspaceHash).toBe("b".repeat(64));
  });

  test("partial override: explicit db, derived key sibling", () => {
    const p = resolveVaultPaths("/some/cwd", { db: "/scratch/v.vault" });
    expect(p.keyFile).toBe("/scratch/v.vault.key");
  });
});
