/**
 * §2 scope guard tests (BUILD-20260911 scope item 6):
 *   - allow same-env
 *   - block disjoint-env
 *   - explicit override works
 * plus the fail-closed source-record checks and the never-implied override.
 */

import { describe, test, expect } from "bun:test";
import {
  evaluateScopeGuard, verifySourceRecord, OVERRIDE_PARAM,
} from "../guard.ts";

describe("scope guard: environment overlap", () => {
  test("same environment is allowed", () => {
    const r = evaluateScopeGuard({ from_environment: "project", to_environment: "project" });
    expect(r.allowed).toBe(true);
    expect(r.verdict).toBe("same_environment");
  });

  test("disjoint environments are blocked by default", () => {
    const r = evaluateScopeGuard({ from_environment: "project", to_environment: "experiment-foo" });
    expect(r.allowed).toBe(false);
    expect(r.verdict).toBe("blocked_cross_environment");
    expect(r.reason).toContain("rejected by default");
  });

  test("explicit boolean-true override allows the cross-environment draft", () => {
    const r = evaluateScopeGuard({
      from_environment: "project", to_environment: "experiment-foo",
      [OVERRIDE_PARAM]: true,
    });
    expect(r.allowed).toBe(true);
    expect(r.verdict).toBe("cross_environment_allowed_by_override");
  });

  test("the override is never implied: every other value leaves the block", () => {
    for (const bad of [undefined, false, null, 1, "true", "yes", {}]) {
      const r = evaluateScopeGuard({
        from_environment: "project", to_environment: "other",
        [OVERRIDE_PARAM]: bad as any,
      });
      expect(r.allowed).toBe(false);
      expect(r.verdict).toBe("blocked_cross_environment");
    }
  });

  test("overlap is byte equality only: case and prefix differences are disjoint", () => {
    for (const [a, b] of [["project", "Project"], ["a/b", "a"], ["worktree", "worktree-2"]]) {
      const r = evaluateScopeGuard({ from_environment: a, to_environment: b });
      expect(r.allowed).toBe(false);
    }
  });
});

describe("scope guard: fail-closed source verification", () => {
  test("source not found -> blocked", () => {
    const r = verifySourceRecord("project", { found: false });
    expect(r.allowed).toBe(false);
    expect(r.verdict).toBe("blocked_source_not_found");
  });

  test("source with no stored environment -> blocked (unverifiable)", () => {
    for (const stored of [undefined, null, ""]) {
      const r = verifySourceRecord("project", { found: true, stored_environment: stored as any });
      expect(r.allowed).toBe(false);
      expect(r.verdict).toBe("blocked_source_environment_unverifiable");
    }
  });

  test("stored environment mismatching the claim -> blocked", () => {
    const r = verifySourceRecord("project", { found: true, stored_environment: "elsewhere" });
    expect(r.allowed).toBe(false);
    expect(r.verdict).toBe("blocked_source_environment_mismatch");
    expect(r.reason).toContain("elsewhere");
  });

  test("already-retired source -> blocked", () => {
    for (const status of ["deprecated", "archived"]) {
      const r = verifySourceRecord("project", { found: true, stored_environment: "project", status });
      expect(r.allowed).toBe(false);
      expect(r.verdict).toBe("blocked_source_already_superseded");
    }
  });

  test("live source with matching stored environment -> allowed", () => {
    const r = verifySourceRecord("project", { found: true, stored_environment: "project", status: "active" });
    expect(r.allowed).toBe(true);
    expect(r.verdict).toBe("source_ok");
  });
});
