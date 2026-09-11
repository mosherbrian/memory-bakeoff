/**
 * pi-recall-nudge unit tests. Controls:
 *  - the nudge sentence is the predeclared F2 wording, verbatim
 *  - append is idempotent; message objects are never mutated
 *  - the controller gates: kill switch, tool registration, prior-session
 *    store, already-nudged prompt, recall already used
 *  - mid-turn consistency: the applied swap persists across context events
 *    of the same turn, and stops once a later user message appears
 *  - priorSessionsExist: 2 conversations true, 1 conversation false, no
 *    store false (fresh projects get no nudge)
 */

import { describe, test, expect, beforeAll, afterAll } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createRequire } from "node:module";

import {
  NUDGE_SENTENCE, nudgeAppend, applyNudge, swapNudged, userText,
  priorSessionsExist, storePathFor, createNudgeController,
} from "../index.ts";
import { createSchema, seedConversation } from "../../pi-project-recall/test/pilot_store.ts";

const require_ = createRequire(import.meta.url);
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
const CWD = "/tmp/pi-recall-nudge-fixture";

beforeAll(() => {
  dbDir = mkdtempSync(join(tmpdir(), "pi-recall-nudge-test-"));
  process.env.LCM_DB_DIR = dbDir;
});

afterAll(() => {
  delete process.env.LCM_DB_DIR;
  rmSync(dbDir, { recursive: true, force: true });
});

describe("the nudge sentence", () => {
  test("is the predeclared F2 wording, verbatim", () => {
    expect(NUDGE_SENTENCE).toBe(
      "Before you edit anything, use the project_recall tool to check this " +
      "project's past sessions for decisions or constraints relevant to the task.",
    );
  });
});

describe("text handling", () => {
  test("appends once and is idempotent", () => {
    const once = nudgeAppend("Fix the gate positions.");
    expect(once).toBe(`Fix the gate positions. ${NUDGE_SENTENCE}`);
    expect(nudgeAppend(once)).toBe(once);
  });

  test("applyNudge appends to the last user message without mutating it", () => {
    const messages: any[] = [
      { role: "user", content: "old turn", timestamp: 1 },
      { role: "assistant", content: [{ type: "text", text: "done" }] },
      { role: "user", content: "new turn", timestamp: 2 },
    ];
    const out = applyNudge(messages)!;
    expect(out.messages[0]).toBe(messages[0]); // untouched by reference
    expect(out.messages[2].content).toBe(`new turn ${NUDGE_SENTENCE}`);
    expect(messages[2].content).toBe("new turn"); // original not mutated
    expect(out.original).toBe("new turn");
  });

  test("array content is nudged in its last text block only (no duplication)", () => {
    const messages: any[] = [{
      role: "user",
      content: [{ type: "text", text: "part one" }, { type: "text", text: "part two" }],
    }];
    const out = applyNudge(messages)!;
    expect(out.messages[0].content[0].text).toBe("part one");
    expect(out.messages[0].content[1].text).toBe(`part two ${NUDGE_SENTENCE}`);
    expect(userText(out.messages[0])).toBe(`part one part two ${NUDGE_SENTENCE}`);
    // original not mutated
    expect(messages[0].content[1].text).toBe("part two");
  });

  test("no user message, or an already-nudged prompt, yields null", () => {
    expect(applyNudge([{ role: "assistant", content: "hi" }])).toBeNull();
    expect(applyNudge([{ role: "user", content: `prompt ${NUDGE_SENTENCE}` }])).toBeNull();
  });

  test("swapNudged keeps mid-turn consistency and stops at a new turn", () => {
    const first = [{ role: "user", content: "task" }];
    const { messages: nudgedFirst, original, nudged } = applyNudge(first)!;
    // next LLM call of the same turn re-receives the ORIGINAL session message
    const again = swapNudged([{ role: "user", content: "task" }], original, nudged)!;
    expect(again[0].content).toBe(nudgedFirst[0].content);
    // already-nudged list passes through unchanged (null = no transform)
    expect(swapNudged(nudgedFirst, original, nudged)).toBeNull();
    // a different, later user message ends the armed turn (null = no transform)
    expect(swapNudged([{ role: "user", content: "second turn" }], original, nudged)).toBeNull();
  });
});

describe("priorSessionsExist gate", () => {
  test("two conversations (live + prior) pass; one or none fails; no store fails", () => {
    const dbPath = storePathFor(CWD);
    const db = openWritable(dbPath);
    createSchema(db);
    seedConversation(db, {
      id: "conv-live", session_id: "s-live", cwd: CWD,
      created_at: "2026-09-10T00:00:00.000Z", updated_at: "2026-09-10T00:01:00.000Z",
      messages: [{ role: "user", content_text: "live", timestamp: Date.now() }],
    });
    expect(priorSessionsExist(CWD)).toBe(false); // 1 conversation: nothing prior
    seedConversation(db, {
      id: "conv-prior", session_id: "s-prior", cwd: CWD,
      created_at: "2026-09-07T00:00:00.000Z", updated_at: "2026-09-07T00:01:00.000Z",
      messages: [{ role: "assistant", content_text: "prior decision", timestamp: Date.now() - 86_400_000 }],
    });
    db.close();
    expect(priorSessionsExist(CWD)).toBe(true); // live + prior
    expect(priorSessionsExist("/tmp/never-seen-project")).toBe(false); // no store file
  });
});

describe("controller state machine", () => {
  function makeController(over: Partial<Parameters<typeof createNudgeController>[0]> = {}) {
    return createNudgeController({
      cwd: () => CWD,
      recallToolRegistered: () => true,
      priorSessions: () => true,
      now: () => "2026-09-10T12:00:00.000Z",
      ...over,
    });
  }
  const prompt = (text: string) => [{ role: "user", content: text }];

  test("happy path: nudges the first armed prompt, logs and records a receipt entry", () => {
    const c = makeController();
    const d = c.onContext(prompt("resume the work"));
    expect(d.messages).toBeDefined();
    expect(d.messages![0].content).toBe(`resume the work ${NUDGE_SENTENCE}`);
    expect(d.log).toContain("appended the F2 nudge sentence");
    expect(d.entry!.action).toBe("nudge");
    expect(c.state().phase).toBe("applied");
  });

  test("kill switch skips with an explicit reason", () => {
    process.env.PI_RECALL_NUDGE = "0";
    const c = makeController();
    const d = c.onContext(prompt("resume"));
    expect(d.messages).toBeUndefined();
    expect(d.entry!.action).toBe("skip");
    expect(d.entry!.reason).toBe("PI_RECALL_NUDGE=0");
    process.env.PI_RECALL_NUDGE = undefined;
  });

  test("no project_recall tool registered means no nudge", () => {
    const c = makeController({ recallToolRegistered: () => false });
    const d = c.onContext(prompt("resume"));
    expect(d.messages).toBeUndefined();
    expect(d.entry!.reason).toBe("project_recall not registered");
  });

  test("no prior-session store means no nudge (fresh projects stay quiet)", () => {
    const c = makeController({ priorSessions: () => false });
    const d = c.onContext(prompt("resume"));
    expect(d.messages).toBeUndefined();
    expect(d.entry!.reason).toBe("no prior-session store for this project");
  });

  test("already-nudged prompt disarms without double-appending", () => {
    const c = makeController();
    const d = c.onContext(prompt(`resume ${NUDGE_SENTENCE}`));
    expect(d.messages).toBeUndefined();
    expect(d.entry!.reason).toContain("already present");
  });

  test("spontaneous recall use disarms an unapplied nudge", () => {
    const c = makeController();
    c.onRecallUsed();
    const d = c.onContext(prompt("resume"));
    expect(d.messages).toBeUndefined();
    expect(c.state().phase).toBe("off");
  });

  test("session_start re-arms after a skip or an application", () => {
    const c = makeController();
    c.onContext(prompt("resume")); // applied
    c.onSessionStart();
    expect(c.state().phase).toBe("armed");
    const d = c.onContext(prompt("new session prompt"));
    expect(d.messages![0].content).toContain(NUDGE_SENTENCE);
  });
});
