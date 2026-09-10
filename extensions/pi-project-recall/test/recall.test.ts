/**
 * project_recall unit tests. Validation controls required by the R2 spec:
 *  - negative control: a query matching nothing returns empty without fabricating
 *  - positive control: a known message from a PRIOR conversation is found
 *  - driver smoke: node:sqlite opens the store read-only and writes are blocked
 *  - kill switch: PI_PROJECT_RECALL=0 disables the tool
 *  - FTS fallback: LIKE path when messages_fts is unavailable
 */

import { describe, test, expect, beforeAll, afterAll } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createRequire } from "node:module";

import {
  detectDriver, openStore, storePathFor, queryMessages, querySummaries,
  sanitizeFtsQuery, runRecall, default as registerExtension,
} from "../index.ts";
import { createSchema, seedConversation } from "./pilot_store.ts";

const require_ = createRequire(import.meta.url);
// Driver-aware open for seeding: node:sqlite when present (node runtime),
// else bun:sqlite (bun test on bun 1.3.13, which has no node:sqlite).
function openWritable(path: string): any {
  try {
    const { DatabaseSync } = require_("node:sqlite");
    return new DatabaseSync(path);
  } catch {
    const { Database } = require_("bun:sqlite");
    return new Database(path);
  }
}

let dbDir: string;
let dbPath: string;
const CWD = "/tmp/project-recall-fixture";

const DAY = 86_400_000;
const NOW = Date.parse("2026-09-09T20:00:00.000Z");
const PRIOR_START = new Date(NOW - 3 * DAY).toISOString(); // session that ended 3 days ago
const RECENT_START = new Date(NOW - DAY).toISOString();

function buildStore(): void {
  const db = openWritable(dbPath);
  createSchema(db);
  seedConversation(db, {
    id: "conv-prior",
    session_id: "session-prior",
    cwd: CWD,
    created_at: PRIOR_START,
    updated_at: new Date(NOW - 3 * DAY + 3_600_000).toISOString(),
    messages: [
      { role: "user", content_text: "Should we keep the JSON config loader?", timestamp: NOW - 3 * DAY },
      {
        role: "assistant",
        content_text:
          "Decision: we migrated config handling to config.toml. The JSON loader in loader_json.ts is " +
          "deprecated - do not add new callers. It misorders array merges, which broke the release checklist once.",
        timestamp: NOW - 3 * DAY + 60_000,
      },
    ],
    summaries: [{
      depth: 0,
      text: "Session decision: config.json loader deprecated after array-merge ordering bug; config.toml is authoritative.",
      token_estimate: 24,
      created_at: new Date(NOW - 3 * DAY + 120_000).toISOString(),
    }],
  });
  seedConversation(db, {
    id: "conv-recent",
    session_id: "session-recent",
    cwd: CWD,
    created_at: RECENT_START,
    updated_at: new Date(NOW - DAY + 1_800_000).toISOString(),
    messages: [
      {
        role: "user",
        content_text: "Unrelated: rename the build script to build_all.sh please.",
        timestamp: NOW - DAY,
      },
    ],
  });
  db.close();
}

beforeAll(() => {
  dbDir = mkdtempSync(join(tmpdir(), "pi-project-recall-test-"));
  process.env.LCM_DB_DIR = dbDir;
  dbPath = storePathFor(CWD);
  buildStore();
});

afterAll(() => {
  delete process.env.LCM_DB_DIR;
  rmSync(dbDir, { recursive: true, force: true });
});

describe("driver smoke (node:sqlite, the Pi 0.84.4 runtime)", () => {
  test("detects node:sqlite under node and bun tests still open the store", () => {
    // Under `bun test` this may legitimately report bun:sqlite; under the
    // node driver smoke script it must report node:sqlite. Either way the
    // store must open and the readOnly flag must hold.
    expect(["node:sqlite", "bun:sqlite"]).toContain(detectDriver());
  });

  test("opens the store read-only and blocks writes at the driver level", () => {
    const store = openStore(CWD);
    expect(store).not.toBeNull();
    // Direct write attempt through the same statement machinery the tool uses.
    expect(() =>
      (store!.db as any).prepare("INSERT INTO messages (id, conversation_id, role, content_text, content_json, token_estimate, timestamp, seq) VALUES ('x','conv-prior','user','x','x',1,0,999)").all()
    ).toThrow();
    store!.db.close();
  });
});

describe("positive control: a prior conversation is visible from a new session", () => {
  test("message search crosses the conversation boundary with session metadata", () => {
    const store = openStore(CWD)!;
    const hits = queryMessages(store.db, "config.toml deprecated", 20);
    store.db.close();
    expect(hits.length).toBeGreaterThanOrEqual(1);
    const decision = hits.find((h) => h.conversation_id === "conv-prior");
    expect(decision).toBeDefined();
    expect(decision!.source).toBe("messages");
    expect(decision!.role).toBe("assistant");
    expect(decision!.session_start).toBe(PRIOR_START);
    expect(decision!.snippet).toContain("config.toml");
  });

  test("summary search crosses the boundary too", () => {
    const store = openStore(CWD)!;
    const hits = querySummaries(store.db, "deprecated", 20);
    store.db.close();
    expect(hits.length).toBeGreaterThanOrEqual(1);
    expect(hits[0].conversation_id).toBe("conv-prior");
    expect(hits[0].role).toBe("summary");
  });

  test("after/before filters bound the search window", () => {
    const store = openStore(CWD)!;
    const beforeHit = queryMessages(store.db, "config.toml", 20, undefined, new Date(NOW - 2 * DAY).toISOString());
    const afterMiss = queryMessages(store.db, "config.toml", 20, new Date(NOW - 2 * DAY).toISOString(), undefined);
    store.db.close();
    expect(beforeHit.some((h) => h.conversation_id === "conv-prior")).toBe(true);
    expect(afterMiss.some((h) => h.conversation_id === "conv-prior")).toBe(false);
  });
});

describe("negative control: no match means empty, never fabrication", () => {
  test("unmatched query returns zero hits from both scopes", () => {
    const store = openStore(CWD)!;
    expect(queryMessages(store.db, "zxqquux nonexistentterm", 20)).toEqual([]);
    expect(querySummaries(store.db, "zxqquux nonexistentterm", 20)).toEqual([]);
    store.db.close();
  });

  test("empty or injection-shaped query sanitizes to a safe FTS string", () => {
    expect(sanitizeFtsQuery("")).toBe("");
    // Every token is quoted, so FTS operators cannot be injected: the output
    // is exactly the three quoted phrase tokens and nothing else.
    expect(sanitizeFtsQuery('OR " NEAR(')).toBe('"OR" """" "NEAR("');
    expect(sanitizeFtsQuery('a"b')).toBe('"a""b"');
  });

  test("tool reports no-store truthfully instead of inventing history", async () => {
    const tmp = mkdtempSync(join(tmpdir(), "pi-project-recall-nostore-"));
    process.env.LCM_DB_DIR = tmp;
    const out = await runRecall(CWD, { query: "anything" });
    expect(out.content[0].text).toContain("no project memory store exists");
    expect(out.content[0].text).not.toContain("session");
    delete process.env.LCM_DB_DIR;
    process.env.LCM_DB_DIR = dbDir;
    rmSync(tmp, { recursive: true, force: true });
  });
});

describe("tool registration and kill switch", () => {
  test("registers exactly one tool named project_recall", () => {
    let tool: any;
    registerExtension({ registerTool: (t: any) => { tool = t; } });
    expect(tool.name).toBe("project_recall");
    expect(tool.parameters.required).toEqual(["query"]);
  });

  test("PI_PROJECT_RECALL=0 disables the tool with an explicit notice", async () => {
    const prev = process.env.PI_PROJECT_RECALL;
    process.env.PI_PROJECT_RECALL = "0";
    const out = await runRecall(CWD, { query: "config" });
    process.env.PI_PROJECT_RECALL = prev;
    expect(out.content[0].text).toContain("disabled");
  });

  test("tool output carries per-hit session identity and the stale-history warning", async () => {
    const out = await runRecall(CWD, { query: "config.toml deprecated" });
    const text = out.content[0].text;
    expect(text).toContain("conv-prior");
    expect(text).toContain(PRIOR_START);
    expect(text).toContain("superseded");
  });
});

describe("FTS fallback", () => {
  test("LIKE path serves queries when messages_fts cannot (schema without FTS)", () => {
    const tmp = mkdtempSync(join(tmpdir(), "pi-project-recall-nofts-"));
    process.env.LCM_DB_DIR = tmp;
    const db = openWritable(storePathFor(CWD));
    createSchema(db);
    db.exec("DROP TABLE messages_fts");
    db.exec("DROP TRIGGER messages_fts_ai");
    db.exec("DROP TRIGGER messages_fts_ad");
    db.exec("DROP TRIGGER messages_fts_au");
    seedConversation(db, {
      id: "conv-only", session_id: "session-only", cwd: CWD,
      created_at: PRIOR_START, updated_at: PRIOR_START,
      messages: [{ role: "assistant", content_text: "the quota limit is 40 requests per minute", timestamp: NOW - 2 * DAY }],
    });
    db.close();
    const store = openStore(CWD)!;
    const hits = queryMessages(store.db, "quota limit", 20);
    store.db.close();
    delete process.env.LCM_DB_DIR;
    process.env.LCM_DB_DIR = dbDir;
    rmSync(tmp, { recursive: true, force: true });
    expect(hits.length).toBe(1);
    expect(hits[0].snippet).toContain("quota limit");
  });
});
