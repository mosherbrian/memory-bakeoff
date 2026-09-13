/**
 * Differential harness, TypeScript side: builds ONE store with the
 * extension's own committed schema/seed helpers (pilot_store.ts) and runs
 * the extension's own queryMessages over it. py_side.py runs the Python
 * port against the SAME store file; normalized outputs must be identical.
 * Display-only timestamp strings (JS toISOString vs Python isoformat) are
 * masked — they are not retrieval semantics.
 */
import { Database } from "bun:sqlite";
import { writeFileSync, mkdirSync } from "node:fs";
import { createSchema, seedConversation } from "../../extensions/pi-project-recall/test/pilot_store.ts";
import { queryMessages } from "../../extensions/pi-project-recall/index.ts";

const QUERIES = ["ledger convention", "docker compose", "helm kite", "deploy", "the", "zzz-nothing"];

const db = new Database(new URL("./receipts/differential.db", import.meta.url).pathname);
createSchema(db);
const T = (h: number) => Date.parse(`2026-09-01T${12 + h}:00:00.000Z`);
seedConversation(db, { id: "conv-a", session_id: "sess-a", cwd: "memory-bakeoff-differential",
  created_at: "2026-09-01T12:00:00.000Z", updated_at: "2026-09-01T12:00:00.000Z",
  messages: [{ role: "user", content_text: "staging deploys via helm on the kite cluster", timestamp: T(1) }] });
seedConversation(db, { id: "conv-b", session_id: "sess-b", cwd: "memory-bakeoff-differential",
  created_at: "2026-09-01T12:00:00.000Z", updated_at: "2026-09-01T12:00:00.000Z",
  messages: [{ role: "user", content_text: "development still uses docker compose", timestamp: T(2) }] });
seedConversation(db, { id: "conv-c", session_id: "sess-c", cwd: "memory-bakeoff-differential",
  created_at: "2026-09-01T12:00:00.000Z", updated_at: "2026-09-01T12:00:00.000Z",
  messages: [{ role: "user", content_text: "the ledger convention lives in trial-ledger.py", timestamp: T(3) }] });

const out: Record<string, unknown> = {};
for (const q of QUERIES) {
  out[q] = queryMessages(db as never, q, 5).map((h) => ({
    source: h.source, conversation_id: h.conversation_id, role: h.role, snippet: h.snippet,
  }));
}
mkdirSync(new URL("./receipts/", import.meta.url).pathname, { recursive: true });
writeFileSync(new URL("./receipts/ts-hits.json", import.meta.url).pathname, JSON.stringify(out, null, 2) + "\n");
db.close();
console.log("ts-side done:", QUERIES.length, "queries");
