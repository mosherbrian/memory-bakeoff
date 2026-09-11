/**
 * Node-runtime smoke for pi-recall-nudge (mirrors pi-project-recall's
 * node_smoke.ts): prove the store gate and the transform run under the ACTUAL
 * Pi runtime - node with node:sqlite - not only under `bun test`.
 * Run: node extensions/pi-recall-nudge/test/node_smoke.ts
 * Exits non-zero on any failure; prints one line per check.
 */

import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createRequire } from "node:module";

import { priorSessionsExist, storePathFor, createNudgeController, NUDGE_SENTENCE } from "../index.ts";
import { createSchema, seedConversation } from "../../pi-project-recall/test/pilot_store.ts";

const require_ = createRequire(import.meta.url);
const checks: Array<[string, boolean]> = [];

function check(name: string, ok: boolean) {
  checks.push([name, ok]);
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}`);
}

// 1. node:sqlite loads (Pi 0.84.4 runs under node >= 22.13).
let DatabaseSync: any = null;
try {
  ({ DatabaseSync } = require_("node:sqlite"));
} catch { /* handled below */ }
check("node:sqlite loads under the current node runtime", DatabaseSync !== null);

// 2. Seed a store with a live + a prior conversation, as pi-lcm would leave it.
const CWD = "/tmp/pi-recall-nudge-node-smoke";
const dbDir = mkdtempSync(join(tmpdir(), "pi-recall-nudge-nodesmoke-"));
process.env.LCM_DB_DIR = dbDir;
const seed = new DatabaseSync(storePathFor(CWD));
createSchema(seed);
const NOW = Date.now();
seedConversation(seed, {
  id: "conv-live", session_id: "s-live", cwd: CWD,
  created_at: new Date(NOW).toISOString(), updated_at: new Date(NOW).toISOString(),
  messages: [{ role: "user", content_text: "live prompt", timestamp: NOW }],
});
seedConversation(seed, {
  id: "conv-prior", session_id: "s-prior", cwd: CWD,
  created_at: new Date(NOW - 86_400_000).toISOString(), updated_at: new Date(NOW - 86_400_000).toISOString(),
  messages: [{ role: "assistant", content_text: "prior decision", timestamp: NOW - 86_400_000 }],
});
seed.close();
check("priorSessionsExist true for live+prior store under node:sqlite", priorSessionsExist(CWD) === true);

// 3. The controller nudges the first prompt and stays consistent mid-turn.
const controller = createNudgeController({
  cwd: () => CWD,
  recallToolRegistered: () => true,
  priorSessions: priorSessionsExist,
  now: () => new Date().toISOString(),
});
const first = controller.onContext([{ role: "user", content: "resume the work" }]);
check("first prompt gets the nudge", first.messages?.[0]?.content === `resume the work ${NUDGE_SENTENCE}`);
const again = controller.onContext([{ role: "user", content: "resume the work" }]);
check("same turn re-receives the nudged prompt", again.messages?.[0]?.content === `resume the work ${NUDGE_SENTENCE}`);
const later = controller.onContext([{ role: "user", content: "a second turn" }]);
check("a later turn is left alone", later.messages === undefined);

rmSync(dbDir, { recursive: true, force: true });
const failed = checks.filter(([, ok]) => !ok).length;
console.log(failed === 0 ? "node smoke: ALL PASS" : `node smoke: ${failed} FAIL`);
process.exit(failed === 0 ? 0 : 1);
