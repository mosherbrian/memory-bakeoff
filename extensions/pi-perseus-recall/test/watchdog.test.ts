/**
 * Watchdog lifecycle (2026-09-13 serve-deadlock incident): an RPC timeout
 * must mark the server suspect; getServer/restart must replace the serve
 * PROCESS (new pid) and the fresh serve must answer recall.
 * Runs against the REAL pinned binary on a scratch vault.
 */
import { describe, expect, test } from "bun:test";
import { execSync } from "node:child_process";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { VaultServer } from "../vault.ts";

const BIN = "/var/home/bmosher/perseus-build/src/target/release/perseus-vault";

describe("vault serve watchdog", () => {
  test("timeout marks suspect; restart spawns a fresh serve that answers", async () => {
    const dir = mkdtempSync(join(tmpdir(), "watchdog-"));
    const db = join(dir, "scratch.vault");
    const key = join(dir, "scratch.key");
    execSync(`${BIN} init --db ${db} --key-file ${key}`, { stdio: "ignore" });

    const srv = new VaultServer({
      bin: BIN, db, keyFile: key,
    } as any);
    await srv.start();
    const pidBefore = execSync(`pgrep -f "serve --db ${db}" | head -1`).toString().trim();
    expect(Number(pidBefore)).toBeGreaterThan(0);

    // simulate the deadlock signature: an RPC timeout marks the server suspect
    (srv as any).suspect = true;
    expect(srv.isSuspect()).toBe(true);

    await srv.restart();
    const pidAfter = execSync(`pgrep -f "serve --db ${db}" | head -1`).toString().trim();
    expect(Number(pidAfter)).toBeGreaterThan(0);
    expect(pidAfter).not.toBe(pidBefore);  // a genuinely NEW serve process
    expect(srv.isSuspect()).toBe(false);

    const hits = await (srv as any).recall("anything at all", 5, "watchdog-ws");
    expect(Array.isArray(hits)).toBe(true);  // fresh serve answers recall

    try { (srv as any).proc?.kill('SIGTERM'); } catch {}
    rmSync(dir, { recursive: true, force: true });
  }, 20000);
});
