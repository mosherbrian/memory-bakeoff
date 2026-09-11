/**
 * BUILD-20260911 smoke receipt: one REAL create -> supersede -> recall
 * cycle against a scratch vault, driven through the actual extension
 * wiring (default(pi) + the four tools), proving:
 *   - the 7c vault derivation (no db/keyFile/workspaceHash in config);
 *   - the confirmation gate (no write without the operator's code;
 *     status flip + status/valid_to delivered on the supersede receipt);
 *   - the §2 scope guard (disjoint environment blocked by default; the
 *     explicit override opens a DRAFT but never a write by itself);
 *   - key-reuse refusal;
 *   - post-supersede recall: only the current record is delivered.
 *
 * Run: bun extensions/pi-perseus-recall/smoke_receipt.ts
 * Env: PERSEUS_VAULT_BIN overrides the binary (default: the study binary).
 * Output: receipt text on stdout; scratch state under a mkdtemp dir.
 */

import { mkdtempSync, rmSync, mkdirSync, writeFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";

const BIN = process.env.PERSEUS_VAULT_BIN
  ?? "/var/home/bmosher/perseus-build/src/target/release/perseus-vault";
const EXPECTED_VERSION = "perseus-vault 2.23.2 (9c82920)";

const steps: { name: string; ok: boolean; evidence: string }[] = [];
function step(name: string, ok: boolean, evidence: string): void {
  steps.push({ name, ok, evidence });
  console.error(`${ok ? "PASS" : "FAIL"} ${name}${evidence ? ` — ${evidence}` : ""}`);
}

function text(t: any): string {
  return t?.content?.[0]?.text ?? "";
}

async function main(): Promise<boolean> {
  // binary provenance (mandatory per the reset provenance discipline)
  if (!existsSync(BIN)) {
    step("binary-provenance", false, `binary missing: ${BIN}`);
    return false;
  }
  const version = Bun.spawnSync([BIN, "--version"], { stdout: "pipe", stderr: "pipe" }).stdout.toString().trim();
  const binSha = createHash("sha256").update(new Uint8Array(await Bun.file(BIN).arrayBuffer())).digest("hex");
  const provenanceOk = version === EXPECTED_VERSION;
  step("binary-provenance", provenanceOk,
    `${BIN} sha256=${binSha} self-reports ${JSON.stringify(version)}`);
  if (!provenanceOk) return false;

  // scratch world: project cwd + agent dir, config WITHOUT db/keyFile/workspaceHash
  const scratch = mkdtempSync(join(tmpdir(), "perseus-decision-smoke-"));
  const project = join(scratch, "project");
  const agentDir = join(scratch, "agent");
  mkdirSync(project); mkdirSync(join(agentDir, "perseus"), { recursive: true });
  writeFileSync(join(agentDir, "settings.json"), JSON.stringify({
    perseusRecall: { bin: BIN, limit: 5, write: { notifiers: ["in-session", "file"] } },
  }));
  process.env.PI_CODING_AGENT_DIR = agentDir;
  process.chdir(project); // the 7c hash is taken from the process cwd

  const { default: registerExtension } = await import("./index.ts");
  const { hashCwd, resolveVaultPaths } = await import("./paths.ts");

  const tools = new Map<string, any>();
  registerExtension({
    registerTool: (t: any) => tools.set(t.name, t),
    on: () => {},
    getAllTools: () => [...tools.values()],
    appendEntry: () => {},
  } as any);
  const expectedDb = join(agentDir, "perseus", `${hashCwd(project)}.vault`);
  const resolved = resolveVaultPaths(project, {});
  step("registration-7d", tools.has("project_perseus_recall") && !tools.has("project_recall")
    && tools.has("project_perseus_remember") && tools.has("project_perseus_supersede")
    && tools.has("project_perseus_confirm"),
    `tools=${[...tools.keys()].join(",")}`);
  step("vault-path-7c", resolved.db === expectedDb && !existsSync(expectedDb),
    `db=${resolved.db} (derived, not yet created)`);

  const call = async (name: string, params: any) =>
    await tools.get(name).execute("smoke", params, undefined as any, undefined as any, undefined as any);

  // recall on a missing vault: truthful empty, no fabrication
  const r0 = text(await call("project_perseus_recall", { query: "anything" }));
  step("recall-truthful-empty", r0.includes("No vault exists yet"), r0.split("\n")[0]);

  // S3: draft remember — NOT written
  const d1 = text(await call("project_perseus_remember", {
    content: "STAGING-DEPLOY: staging deploys via helm on the kite-k8s cluster",
    key: "record-helm-001",
  }));
  const id1 = d1.match(/^draft_id: (draft-[0-9a-f]+)$/m)?.[1] ?? "";
  const code1 = d1.match(/^confirmation_code: ([0-9a-f]+)$/m)?.[1] ?? "";
  step("draft-remember", d1.includes("NOTHING IS WRITTEN YET") && !!id1 && !!code1
    && !existsSync(expectedDb), `draft_id=${id1} code=${code1}; vault still absent`);

  // S4: wrong code -> nothing written
  const wrong = text(await call("project_perseus_confirm", { draft_id: id1, confirmation_code: "00000000" }));
  step("gate-wrong-code", wrong.includes("NOT WRITTEN") && !existsSync(expectedDb),
    wrong.split("\n")[0]);

  // S5: operator's code -> write lands (CLI write creates the vault)
  const ok1 = text(await call("project_perseus_confirm", { draft_id: id1, confirmation_code: code1 }));
  const created = existsSync(expectedDb) && ok1.includes("WRITTEN") && ok1.includes("confirmed_by=operator");
  step("confirm-creates", created, ok1.split("\n")[0]);
  if (!created) return finish(scratch, false);

  // direct vault check: the record is active in the project environment
  const { VaultServer } = await import("./vault.ts");
  const srv = new VaultServer({ bin: BIN, db: resolved.db, keyFile: resolved.keyFile });
  await srv.start();
  try {
    const ws = resolved.workspaceHash;
    const rows1 = await srv.scan(ws, 100, true);
    const old = rows1.find((r: any) => r.key === "record-helm-001");
    step("vault-state-after-create",
      rows1.length === 1 && old?.status === "active" && old?.environment === "project",
      `scan: ${rows1.map((r: any) => `${r.key}/${r.status}/env=${r.environment}`).join(", ")}`);

    // S7: supersede draft + confirm — status flip + valid_to delivered
    const d2 = text(await call("project_perseus_supersede", {
      content: "STAGING-DEPLOY: staging deploys via argo rollouts on kite-k8s",
      key: "record-argo-002",
      from_key: "record-helm-001",
      reason: "platform moved from helm to argo rollouts",
    }));
    const id2 = d2.match(/^draft_id: (draft-[0-9a-f]+)$/m)?.[1] ?? "";
    const code2 = d2.match(/^confirmation_code: ([0-9a-f]+)$/m)?.[1] ?? "";
    step("draft-supersede", d2.includes("NOTHING IS WRITTEN YET") && !!id2,
      `draft_id=${id2}`);
    const ok2 = text(await call("project_perseus_confirm", { draft_id: id2, confirmation_code: code2 }));
    const flip = ok2.includes("status_updated=\"deprecated\"")
      && ok2.includes("from_valid_to_unix_ms=")
      && ok2.includes("confirmed_by=operator");
    step("confirm-supersede-status-delivery", flip, ok2.split("\n").slice(2).join(" | "));

    // S8: recall delivers only the current record as a hit (the new record's
    // body legitimately carries supersedes-provenance naming the old key)
    const rec = text(await call("project_perseus_recall", { query: "staging deploy" }));
    const headers = [...rec.matchAll(/^\[project_perseus_recall\] key=([^\s]+)/gm)].map((m) => m[1]);
    const deliversNew = headers.includes("record-argo-002") && rec.includes("argo rollouts");
    const hidesOld = headers.length === 1 && headers[0] === "record-argo-002";
    step("recall-after-supersede", deliversNew && hidesOld && rec.includes("status=active"),
      `hits=${headers.join(",")}; ${rec.split("\n")[0].slice(0, 120)}`);

    // S9: §2 scope guard — a genuinely disjoint environment is blocked by default
    const dq = text(await call("project_perseus_remember", {
      content: "QUARANTINE-EXCEPTION: temporary waiver for the flaky integration test",
      key: "record-quarantine-001",
      environment: "quarantine",
    }));
    const idq = dq.match(/^draft_id: (draft-[0-9a-f]+)$/m)?.[1] ?? "";
    const codeq = dq.match(/^confirmation_code: ([0-9a-f]+)$/m)?.[1] ?? "";
    await call("project_perseus_confirm", { draft_id: idq, confirmation_code: codeq });
    const d3 = text(await call("project_perseus_supersede", {
      content: "QUARANTINE-EXCEPTION: waiver made permanent",
      key: "record-quarantine-002",
      from_key: "record-quarantine-001",
      from_environment: "quarantine",
      environment: "project",
      reason: "the waiver should live with the project's other decisions",
    }));
    const guardBlocked = d3.includes("DRAFT REFUSED") && d3.includes("rejected by default");
    step("guard-blocks-disjoint-env", guardBlocked, d3.split("\n")[0]);

    // S10: the override is explicit and opens a DRAFT — never a write by itself
    const d4 = text(await call("project_perseus_supersede", {
      content: "QUARANTINE-EXCEPTION: waiver made permanent",
      key: "record-quarantine-002",
      from_key: "record-quarantine-001",
      from_environment: "quarantine",
      environment: "project",
      reason: "the waiver should live with the project's other decisions",
      allow_cross_environment: true,
    }));
    const id4 = d4.match(/^draft_id: (draft-[0-9a-f]+)$/m)?.[1] ?? "";
    const rowsAfterOverrideDraft = await srv.scan(resolved.workspaceHash, 100, true);
    const noWrite = !rowsAfterOverrideDraft.some((r: any) => r.key === "record-quarantine-002")
      && d4.includes("NOTHING IS WRITTEN YET") && !!id4;
    step("guard-override-drafts-but-writes-nothing", noWrite,
      `override draft ${id4} pending; project workspace still has `
      + `${rowsAfterOverrideDraft.length} record(s)`);

    // S11: key reuse refused (the CLI would update in place)
    const dup = text(await call("project_perseus_remember", {
      content: "duplicate key attempt", key: "record-argo-002",
    }));
    step("key-reuse-refused", dup.includes("DRAFT REFUSED") && dup.includes("never reused"),
      dup.split("\n")[0]);
  } finally {
    try { (srv as any).proc?.kill("SIGTERM"); } catch { /* exiting */ }
  }
  return finish(scratch, steps.every((s) => s.ok));
}

function finish(scratch: string, ok: boolean): boolean {
  step("no-vault-path-escape", scratch.startsWith(tmpdir()), `scratch=${scratch}`);
  rmSync(scratch, { recursive: true, force: true });
  const lines = [
    "BUILD-20260911 DECISION-MEMORY SMOKE RECEIPT",
    `binary: ${BIN} (self-reports ${EXPECTED_VERSION})`,
    `when: ${new Date().toISOString()}`,
    "",
    ...steps.map((s) => `[${s.ok ? "PASS" : "FAIL"}] ${s.name}${s.evidence ? ` — ${s.evidence}` : ""}`),
    "",
    ok ? "SMOKE RECEIPT: PASS — create -> supersede -> recall cycle proven "
      + "(status flip + status/valid_to delivered; gate + §2 guard + key rules enforced)"
      : "SMOKE RECEIPT: FAIL",
  ];
  console.log(lines.join("\n"));
  return ok;
}

const okFlag = await main();
process.exit(okFlag ? 0 : 1);
