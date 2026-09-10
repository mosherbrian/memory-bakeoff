/**
 * Node-runtime driver smoke (R2 spec, review Note 1): prove the store opens and
 * queries under the ACTUAL Pi runtime - node with node:sqlite - not only under
 * `bun test`. Run: node extensions/pi-project-recall/test/node_smoke.ts
 * Exits non-zero on any failure; prints one line per check.
 */

import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createRequire } from "node:module";

import {
  detectDriver, openStore, storePathFor, queryMessages, querySummaries, runRecall,
} from "../index.ts";
import { createSchema, seedConversation } from "./pilot_store.ts";

const require_ = createRequire(import.meta.url);
const checks: Array<[string, boolean]> = [];

function check(name: string, ok: boolean) {
  checks.push([name, ok]);
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}`);
}

// 1. node:sqlite loads under this runtime (Pi 0.84.4 runs under node >= 22.13).
let DatabaseSync: any = null;
try {
  ({ DatabaseSync } = require_("node:sqlite"));
} catch { /* handled below */ }
check("node:sqlite loads under the current node runtime", DatabaseSync !== null);
check("detectDriver() selects node:sqlite here", detectDriver() === "node:sqlite");

const CWD = "/tmp/project-recall-node-smoke";
const NOW = Date.now();
const dbDir = mkdtempSync(join(tmpdir(), "pi-project-recall-nodesmoke-"));
process.env.LCM_DB_DIR = dbDir;

// 2. Seed a prior conversation through the pi-lcm-shaped schema.
const dbPath = storePathFor(CWD);
const seed = new DatabaseSync(dbPath);
createSchema(seed);
seedConversation(seed, {
  id: "conv-prior", session_id: "session-prior", cwd: CWD,
  created_at: new Date(NOW - 86_400_000).toISOString(),
  updated_at: new Date(NOW - 86_000_000).toISOString(),
  messages: [{
    role: "assistant",
    content_text: "Decision: the retry cap is 3 attempts, then escalate - decided in this prior session.",
    timestamp: NOW - 86_400_000,
  }],
  summaries: [{
    depth: 0, token_estimate: 12,
    text: "Prior session: retry cap fixed at 3 attempts.",
    created_at: new Date(NOW - 86_300_000).toISOString(),
  }],
});
seed.close();

// 3. Read-only open + cross-conversation query under node:sqlite.
const store = openStore(CWD);
check("store opens read-only under node:sqlite", store !== null);
const mHits = store ? queryMessages(store.db, "retry cap", 20) : [];
check("prior-session message found without conversation filter", mHits.length === 1 && mHits[0].conversation_id === "conv-prior");
const sHits = store ? querySummaries(store.db, "retry cap", 20) : [];
check("prior-session summary found", sHits.length === 1 && sHits[0].role === "summary");

// 4. Writes blocked through the read-only connection the tool uses.
let writeBlocked = false;
try {
  store?.db.prepare("DELETE FROM messages").all();
} catch { writeBlocked = true; }
check("write through the tool's connection is rejected", writeBlocked);

// 5. Tool end-to-end under node, including the staleness header.
const out = await runRecall(CWD, { query: "retry cap" });
check(
  "runRecall returns hits with session identity and stale-history warning",
  out.content[0].text.includes("conv-prior") && out.content[0].text.includes("superseded"),
);

store?.db.close();
delete process.env.LCM_DB_DIR;
rmSync(dbDir, { recursive: true, force: true });

const failed = checks.filter(([, ok]) => !ok);
console.log(failed.length === 0
  ? `node smoke: ${checks.length}/${checks.length} checks passed`
  : `node smoke: ${failed.length}/${checks.length} FAILED`);
process.exit(failed.length === 0 ? 0 : 1);
