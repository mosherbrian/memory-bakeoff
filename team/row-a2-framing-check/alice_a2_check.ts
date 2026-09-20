/**
 * Alice second-seat of A2 (vault.ts carry-over buffer). Drives the REAL
 * VaultServer.rpc() with fake stdio. Independent of Assay's power check; adds
 * two adversarial cases: a UTF-8 character split across a chunk boundary, and
 * a reply with no trailing newline.
 * Run: bun run alice_a2_check.ts
 */
import { EventEmitter } from "node:events";
import { VaultServer as Current } from "/var/home/bmosher/memory-bake-off/implementer/repo/extensions/pi-perseus-recall/vault.ts";
import { VaultServer as Fixed } from "/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh2/scripts/verify-20260913-assay-a2-buffer/vault.fixed.ts";

const REAL = globalThis.setTimeout.bind(globalThis);
const RESULT = { ok: true, n: 70000 };
const RESP = JSON.stringify({ jsonrpc: "2.0", id: 1, result: RESULT }) + "\n";

type Out = { status: string; resolved?: unknown; error?: string };

async function drive(Server: any, chunks: (string | Buffer)[], settleMs = 260): Promise<Out> {
  const srv: any = new Server({ bin: "x", db: "x", keyFile: "x" });
  const proc: any = {
    stdin: { write: (_l: string, cb?: (e?: unknown) => void) => { cb?.(null); return true; } },
    stdout: new EventEmitter(),
  };
  srv.proc = proc;
  const orig = globalThis.setTimeout;
  globalThis.setTimeout = ((fn: any, ms?: number, ...a: any[]) =>
    orig(fn, Math.min(ms ?? 0, 150), ...a)) as any;
  const out: Out = { status: "pending" };
  (srv.rpc("m", {}) as Promise<unknown>)
    .then((r) => { out.status = "resolved"; out.resolved = r; })
    .catch((e) => { out.status = "rejected"; out.error = String(e?.message ?? e); });
  for (const c of chunks) proc.stdout.emit("data", Buffer.isBuffer(c) ? c : Buffer.from(c));
  await new Promise((r) => REAL(r, settleMs));
  globalThis.setTimeout = orig;
  return out;
}

const cases: Record<string, unknown> = {};
const problems: string[] = [];
const results: Record<string, boolean> = {};

// control: live drops a split reply
{
  const b = Buffer.from(RESP);
  const k = Math.floor(b.length / 2);
  const o = await drive(Current, [b.subarray(0, k), b.subarray(k)]);
  results.current_split_times_out = o.status === "rejected" && o.error === "vault rpc timeout";
}
// fixed resolves a plain split reply
{
  const b = Buffer.from(RESP);
  const k = Math.floor(b.length / 2);
  const o = await drive(Fixed, [b.subarray(0, k), b.subarray(k)]);
  results.fixed_split_resolves = o.status === "resolved";
}
// ADversarial 1: UTF-8 multibyte char straddling the chunk boundary
{
  const payload = "caf\u00e9 \u2603 " + "x".repeat(70000);      // é (2B), ☃ (3B)
  const RESP2 = JSON.stringify({ jsonrpc: "2.0", id: 1, result: { text: payload } }) + "\n";
  const b = Buffer.from(RESP2, "utf8");
  // find a boundary inside a multibyte sequence: after the first 'é'
  const idx = RESP2.indexOf("\u00e9");
  const boundary = Buffer.byteLength(RESP2.slice(0, idx), "utf8") + 1; // 1 byte into the 2-byte é
  const o = await drive(Fixed, [b.subarray(0, boundary), b.subarray(boundary)]);
  const got = (o.resolved as any)?.text;
  results.fixed_utf8_split_roundtrips = o.status === "resolved" && got === payload;
  cases.utf8_split = { status: o.status, expected_len: payload.length, got_len: got?.length, equal: got === payload,
                       boundary_byte: boundary };
  if (!results.fixed_utf8_split_roundtrips) problems.push("fixed corrupts a UTF-8 char split across chunks");
}
// Adversarial 2: reply with no trailing newline
{
  const RESP3 = JSON.stringify({ jsonrpc: "2.0", id: 1, result: RESULT }); // no \n
  const o = await drive(Fixed, [RESP3], 400);
  results.fixed_no_trailing_newline_resolves = o.status === "resolved";
  cases.no_trailing_newline = { status: o.status, error: o.error };
  if (!results.fixed_no_trailing_newline_resolves) problems.push("fixed cannot resolve a final line without a trailing newline");
}
// foreign reply first, ours second, same chunk
{
  const other = JSON.stringify({ jsonrpc: "2.0", id: 999, result: { other: true } }) + "\n";
  const o = await drive(Fixed, [other + RESP]);
  results.fixed_foreign_then_ours = o.status === "resolved" &&
    JSON.stringify(o.resolved) === JSON.stringify(RESULT);
}
// split exactly at the newline
{
  const o = await drive(Fixed, [RESP, ""]);
  results.fixed_newline_boundary = o.status === "resolved";
}

for (const [k, v] of Object.entries(results)) {
  if (!v) problems.push(`case failed: ${k}`);
}
console.log(JSON.stringify({ results, cases, problems }, null, 1));
process.exit(0);
