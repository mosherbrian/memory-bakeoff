/**
 * pi-lcm store schema + seeding helper for tests and R2 one-time preparation.
 *
 * The DDL mirrors pi-lcm src/db/schema.ts for the tables project_recall reads
 * (conversations, messages, messages_fts + its triggers, summaries). Inserts
 * go through the same triggers pi-lcm uses, so the FTS index is populated
 * exactly as a live store would be.
 */

export interface SeedMessage {
  role: string;
  content_text: string;
  timestamp: number; // epoch ms
}

export interface SeedConversation {
  id: string;
  session_id: string;
  cwd: string;
  created_at: string;
  updated_at: string;
  messages: SeedMessage[];
  summaries?: { depth: number; text: string; token_estimate: number; created_at: string }[];
}

export function createSchema(db: {
  exec(sql: string): unknown;
  prepare(sql: string): { run(...p: unknown[]): unknown };
}): void {
  db.exec(`CREATE TABLE IF NOT EXISTS conversations (
    id            TEXT PRIMARY KEY,
    session_id    TEXT NOT NULL UNIQUE,
    session_file  TEXT,
    cwd           TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
  )`);
  db.exec(`CREATE TABLE IF NOT EXISTS messages (
    id             TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id),
    entry_id       TEXT,
    role           TEXT NOT NULL,
    content_text   TEXT NOT NULL,
    content_json   TEXT NOT NULL,
    tool_name      TEXT,
    token_estimate INTEGER NOT NULL,
    timestamp      INTEGER NOT NULL,
    seq            INTEGER NOT NULL
  )`);
  db.exec(`CREATE TABLE IF NOT EXISTS summaries (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id),
    depth           INTEGER NOT NULL,
    text            TEXT NOT NULL,
    token_estimate  INTEGER NOT NULL,
    metadata_json   TEXT,
    created_at      TEXT NOT NULL
  )`);
  db.exec(`CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content_text,
    content='messages',
    content_rowid='rowid'
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
}

export function seedConversation(
  db: { prepare(sql: string): { run(...p: unknown[]): unknown } },
  conv: SeedConversation,
): void {
  db.prepare(
    `INSERT INTO conversations (id, session_id, cwd, created_at, updated_at)
     VALUES (?, ?, ?, ?, ?)`
  ).run(conv.id, conv.session_id, conv.cwd, conv.created_at, conv.updated_at);
  let seq = 0;
  for (const m of conv.messages) {
    db.prepare(
      `INSERT INTO messages (id, conversation_id, entry_id, role, content_text, content_json,
                             tool_name, token_estimate, timestamp, seq)
       VALUES (?, ?, NULL, ?, ?, ?, NULL, ?, ?, ?)`
    ).run(
      `${conv.id}-m${seq}`, conv.id, m.role, m.content_text,
      JSON.stringify({ role: m.role, content: m.content_text }),
      Math.ceil(m.content_text.length / 3.5), m.timestamp, seq,
    );
    seq++;
  }
  for (const s of conv.summaries ?? []) {
    db.prepare(
      `INSERT INTO summaries (id, conversation_id, depth, text, token_estimate, metadata_json, created_at)
       VALUES (?, ?, ?, ?, ?, NULL, ?)`
    ).run(`${conv.id}-s${s.depth}-${s.created_at}`, conv.id, s.depth, s.text, s.token_estimate, s.created_at);
  }
}
