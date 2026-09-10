/**
 * R2 one-time preparation: materialise a prior-session transcript into a
 * pi-lcm store file. The DDL mirrors pi-lcm src/db/schema.ts v2 EXACTLY
 * (_schema_version=2, is_compacted, dedup_hash) so pi-lcm opens the seeded
 * store without running migrations, and project_recall reads the same shapes
 * it would see in a live store.
 *
 * Usage: node seed_store.ts <transcript.json> <out.db> <cwd>
 * Transcript format: { conversations: [ { id?, session_id?, created_at, updated_at,
 *   messages: [ {role, content_text, timestamp} ], summaries: [ {depth, text,
 *   token_estimate, created_at} ] } ] }
 * timestamps: epoch ms numbers; created_at/updated_at: ISO strings.
 */
import { createHash, randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";

const require_ = createRequire(import.meta.url);

interface SeedMessage { role: string; content_text: string; timestamp: number }
interface SeedSummary { depth: number; text: string; token_estimate: number; created_at: string }
interface SeedConversation {
  id?: string; session_id?: string; cwd?: string; created_at: string; updated_at: string;
  messages: SeedMessage[]; summaries?: SeedSummary[];
}

function computeDedupHash(role: string, timestamp: number, contentText: string): string {
  return createHash("sha1")
    .update(`${role}|${timestamp}|${contentText.slice(0, 200)}`)
    .digest("hex")
    .slice(0, 16);
}

function createSchema(db: any): void {
  db.exec(`CREATE TABLE IF NOT EXISTS _schema_version (version INTEGER NOT NULL)`);
  db.exec(`CREATE TABLE IF NOT EXISTS conversations (
    id            TEXT PRIMARY KEY,
    session_id    TEXT NOT NULL UNIQUE,
    session_file  TEXT,
    cwd           TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
  )`);
  db.exec(`CREATE TABLE IF NOT EXISTS messages (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id),
    entry_id        TEXT,
    role            TEXT NOT NULL,
    content_text    TEXT NOT NULL,
    content_json    TEXT NOT NULL,
    tool_name       TEXT,
    token_estimate  INTEGER NOT NULL,
    timestamp       INTEGER NOT NULL,
    seq             INTEGER NOT NULL,
    is_compacted    INTEGER DEFAULT 0,
    dedup_hash      TEXT NOT NULL,
    UNIQUE(conversation_id, seq),
    UNIQUE(conversation_id, dedup_hash)
  )`);
  db.exec(`CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content_text, content='messages', content_rowid='rowid'
  )`);
  db.exec(`CREATE TRIGGER IF NOT EXISTS messages_fts_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content_text) VALUES (new.rowid, new.content_text);
  END`);
  db.exec(`CREATE TRIGGER IF NOT EXISTS messages_fts_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content_text)
      VALUES ('delete', old.rowid, old.content_text);
  END`);
  db.exec(`CREATE TRIGGER IF NOT EXISTS messages_fts_au AFTER UPDATE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content_text)
      VALUES ('delete', old.rowid, old.content_text);
    INSERT INTO messages_fts(rowid, content_text) VALUES (new.rowid, new.content_text);
  END`);
  db.exec(`CREATE TABLE IF NOT EXISTS summaries (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id),
    depth           INTEGER NOT NULL,
    text            TEXT NOT NULL,
    token_estimate  INTEGER NOT NULL,
    metadata_json   TEXT,
    created_at      TEXT NOT NULL
  )`);
  db.exec(`CREATE TABLE IF NOT EXISTS summary_sources (
    summary_id  TEXT NOT NULL REFERENCES summaries(id),
    source_type TEXT NOT NULL,
    source_id   TEXT NOT NULL,
    seq         INTEGER NOT NULL,
    PRIMARY KEY (summary_id, source_type, source_id)
  )`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, seq)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(conversation_id, role)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(conversation_id, timestamp)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_summaries_conversation ON summaries(conversation_id, depth)`);
  db.exec(`INSERT INTO _schema_version (version) VALUES (2)`);
}

function main(): void {
  const [transcriptPath, dbPath, cwd] = process.argv.slice(2);
  if (!transcriptPath || !dbPath || !cwd) {
    console.error("usage: node seed_store.ts <transcript.json> <out.db> <cwd>");
    process.exit(2);
  }
  const seed = JSON.parse(readFileSync(transcriptPath, "utf8")) as { conversations: SeedConversation[] };
  const { DatabaseSync } = require_("node:sqlite") as any;
  const db = new DatabaseSync(dbPath);
  createSchema(db);
  let msgCount = 0, sumCount = 0;
  for (const conv of seed.conversations) {
    const id = conv.id ?? randomUUID();
    const sessionId = conv.session_id ?? randomUUID();
    db.prepare(
      `INSERT INTO conversations (id, session_id, session_file, cwd, created_at, updated_at)
       VALUES (?, ?, NULL, ?, ?, ?)`
    ).run(id, sessionId, cwd, conv.created_at, conv.updated_at);
    let seq = 0;
    for (const m of conv.messages) {
      db.prepare(
        `INSERT INTO messages (id, conversation_id, entry_id, role, content_text, content_json,
                               tool_name, token_estimate, timestamp, seq, is_compacted, dedup_hash)
         VALUES (?, ?, NULL, ?, ?, ?, NULL, ?, ?, ?, 0, ?)`
      ).run(
        `${id}-m${seq}`, id, m.role, m.content_text,
        JSON.stringify({ role: m.role, content: m.content_text }),
        Math.ceil(m.content_text.length / 3.5), m.timestamp, seq,
        computeDedupHash(m.role, m.timestamp, m.content_text),
      );
      seq++; msgCount++;
    }
    for (const s of conv.summaries ?? []) {
      db.prepare(
        `INSERT INTO summaries (id, conversation_id, depth, text, token_estimate, metadata_json, created_at)
         VALUES (?, ?, ?, ?, ?, NULL, ?)`
      ).run(`${id}-s${s.depth}-${s.created_at}`, id, s.depth, s.text, s.token_estimate, s.created_at);
      sumCount++;
    }
  }
  db.close();
  console.log(`seeded ${dbPath}: ${seed.conversations.length} conversation(s), ${msgCount} message(s), ${sumCount} summar(ies), cwd=${cwd}`);
}

main();
