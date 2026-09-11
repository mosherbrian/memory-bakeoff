/**
 * Record model tests: environment→workspace-hash resolution (project default
 * keeps the configured hash, named environments hash to sha256(environment)
 * — injective), key rules, and the body envelope.
 */

import { describe, test, expect } from "bun:test";
import { createHash } from "node:crypto";
import {
  workspaceHashFor, freshKey, validateKey, validateEnvironment, validateSource, bodyEnvelope,
  DEFAULT_ENVIRONMENT, DEFAULT_CATEGORY, SOURCE_KIND,
} from "../records.ts";

const RESOLVED = { defaultEnvironment: DEFAULT_ENVIRONMENT, workspaceHash: "b".repeat(64) };

describe("environment -> workspace hash", () => {
  test("default environment keeps the configured workspace hash", () => {
    expect(workspaceHashFor(DEFAULT_ENVIRONMENT, RESOLVED)).toBe("b".repeat(64));
  });

  test("named environment hashes to sha256(environment)", () => {
    const expectSha = (s: string) => createHash("sha256").update(s).digest("hex");
    expect(workspaceHashFor("experiment-foo", RESOLVED)).toBe(expectSha("experiment-foo"));
    expect(workspaceHashFor("worktree-2", RESOLVED)).toBe(expectSha("worktree-2"));
  });

  test("the mapping is injective: distinct environments never share a workspace", () => {
    const ws = new Set([RESOLVED.workspaceHash]);
    for (const env of ["Project", "project2", "a", "a/b", "experiment-foo"]) {
      const h = workspaceHashFor(env, RESOLVED);
      expect(ws.has(h)).toBe(false);
      ws.add(h);
    }
  });
});

describe("keys and environments", () => {
  test("fresh keys are record- prefixed and unique across draws", () => {
    const seen = new Set<string>();
    for (let i = 0; i < 50; i++) {
      const k = freshKey();
      expect(k.startsWith("record-")).toBe(true);
      expect(validateKey(k)).toBeNull();
      expect(seen.has(k)).toBe(false);
      seen.add(k);
    }
  });

  test("validateKey rejects empty, whitespace-bearing and oversized keys", () => {
    expect(validateKey("")).toBeTruthy();
    expect(validateKey("  ")).toBeTruthy();
    expect(validateKey("record a b")).toBeTruthy();
    expect(validateKey("a".repeat(129))).toBeTruthy();
    expect(validateKey("decision-staging-deploy")).toBeNull();
  });

  test("validateEnvironment rejects empty/whitespace values", () => {
    expect(validateEnvironment("")).toBeTruthy();
    expect(validateEnvironment("two words")).toBeTruthy();
    expect(validateEnvironment("experiment-foo")).toBeNull();
  });
});

describe("body envelope", () => {
  test("carries assertion_text + environment (vault-projected), structured source, and provenance", () => {
    const body = bodyEnvelope({
      content: "staging deploys via helm", environment: "project",
      recordedAtMs: 1_789_154_697_908,
      source: { kind: "task", ref: "task-123", timestamp: "2026-09-11T10:00:00.000Z" },
    });
    expect(body.assertion_text).toBe("staging deploys via helm");
    expect(body.environment).toBe("project");
    expect(body.source_kind).toBe(SOURCE_KIND); // constant surface tag retained
    expect(body.source).toEqual({ kind: "task", ref: "task-123", timestamp: "2026-09-11T10:00:00.000Z" });
    expect(body.recorded_at_unix_ms).toBe(1_789_154_697_908);
    expect(body.supersedes).toBeUndefined();
  });

  test("source block is present without timestamp when omitted", () => {
    const body = bodyEnvelope({
      content: "x", environment: "project", recordedAtMs: 1,
      source: { kind: "artifact", ref: "docs/plan.md" },
    });
    expect(body.source).toEqual({ kind: "artifact", ref: "docs/plan.md" });
  });

  test("supersession provenance is recorded when the write is part of a supersede", () => {
    const body = bodyEnvelope({
      content: "staging deploys via argo rollouts", environment: "project",
      recordedAtMs: 1, source: { kind: "instruction", ref: "operator in-session" },
      supersession: { supersedes_key: "record-helm-001", reason: "platform moved" },
    });
    expect(body.supersedes).toEqual({ supersedes_key: "record-helm-001", reason: "platform moved" });
    expect((body.source as any).kind).toBe("instruction");
  });
});

describe("structured source provenance (proposal §1, R1)", () => {
  test("all three kinds validate; ref is trimmed; timestamp optional", () => {
    for (const kind of ["task", "artifact", "instruction"]) {
      const r = validateSource({ kind, ref: "  some ref  " });
      expect(r.problem).toBeNull();
      expect(r.source).toEqual({ kind, ref: "some ref" });
    }
    const withTs = validateSource({ kind: "task", ref: "t1", timestamp: "2026-09-11T09:30:00Z" });
    expect(withTs.source).toEqual({ kind: "task", ref: "t1", timestamp: "2026-09-11T09:30:00Z" });
  });

  test("missing source is a problem (fail-closed, not optional)", () => {
    for (const raw of [undefined, null]) {
      const r = validateSource(raw);
      expect(r.source).toBeNull();
      expect(r.problem).toContain("source is required");
    }
  });

  test("bad kind / empty ref / non-object / bad timestamp all refused", () => {
    for (const raw of [
      {}, { kind: "other", ref: "x" }, { kind: "task" }, { kind: "task", ref: "" },
      { kind: "task", ref: "   " }, "task", 42,
      { kind: "task", ref: "x", timestamp: "not-a-date" },
      { kind: "task", ref: "x", timestamp: 17 },
    ]) {
      const r = validateSource(raw);
      expect(r.source).toBeNull();
      expect(r.problem).toBeTruthy();
    }
  });
});

describe("defaults", () => {
  test("category and environment defaults", () => {
    expect(DEFAULT_CATEGORY).toBe("decision");
    expect(DEFAULT_ENVIRONMENT).toBe("project");
  });
});
