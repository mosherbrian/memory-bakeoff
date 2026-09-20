/** Alice second-seat of A2 rev 2 (StringDecoder + EOF flush). */
import { EventEmitter } from "node:events";
import { VaultServer as Current } from "/var/home/bmosher/memory-bake-off/implementer/repo/extensions/pi-perseus-recall/vault.ts";
import { VaultServer as V2 } from "/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh2/scripts/verify-20260913-assay-a2-buffer/vault.fixed.ts";
import { VaultServer as V1 } from "/var/home/bmosher/memory-bake-off/implementer/repo-glm-dsh2/scripts/verify-20260913-assay-a2-buffer/vault.fixed_v1.ts";

const REAL = globalThis.setTimeout.bind(globalThis);
const RESULT = { ok: true, n: 70000 };
const RESP = JSON.stringify({ jsonrpc: "2.0", id: 1, result: RESULT }) + "\n";
type Out = { status: string; resolved?: any; error?: string; data_listeners?: number; end_listeners?: number };

function make(Server: any) {
  const srv: any = new Server({ bin: "x", db: "x", keyFile: "x" });
  const proc: any = {
    stdin: { write: (_l: string, cb?: (e?: unknown) => void) => { cb?.(null); return true; } },
    stdout: new EventEmitter(),
  };
  srv.proc = proc;
  return { srv, proc };
}
async function drive(Server: any, chunks: (string | Buffer)[], end = false, settle = 300): Promise<Out> {
  const { srv, proc } = make(Server);
  const orig = globalThis.setTimeout;
  globalThis.setTimeout = ((fn: any, ms?: number, ...a: any[]) => orig(fn, Math.min(ms ?? 0, 120), ...a)) as any;
  const out: Out = { status: "pending" };
  (srv.rpc("m", {}) as Promise<unknown>).then((r) => { out.status = "resolved"; out.resolved = r; })
    .catch((e) => { out.status = "rejected"; out.error = String(e?.message ?? e); });
  for (const c of chunks) proc.stdout.emit("data", Buffer.isBuffer(c) ? c : Buffer.from(c));
  if (end) proc.stdout.emit("end");
  await new Promise((r) => REAL(r, settle));
  globalThis.setTimeout = orig;
  out.data_listeners = proc.stdout.listenerCount("data");
  out.end_listeners = proc.stdout.listenerCount("end");
  return out;
}

const R: Record<string, boolean> = {}; const C: Record<string, unknown> = {};

// UTF-8 split round-trip on v2
{
  const payload = "caf\u00e9 \u2603 " + "x".repeat(70000);
  const r = JSON.stringify({ jsonrpc: "2.0", id: 1, result: { text: payload } }) + "\n";
  const b = Buffer.from(r, "utf8");
  const idx = r.indexOf("\u00e9");
  const k = Buffer.byteLength(r.slice(0, idx), "utf8") + 1;
  const o = await drive(V2, [b.subarray(0, k), b.subarray(k)]);
  R.v2_utf8_roundtrips = o.status === "resolved" && o.resolved?.text === payload;
  C.utf8 = { status: o.status, equal: o.resolved?.text === payload };
}
// no trailing newline, flushed on end
{
  const noNl = JSON.stringify({ jsonrpc: "2.0", id: 1, result: RESULT });
  const o = await drive(V2, [noNl], true);
  R.v2_no_newline_resolves = o.status === "resolved" && JSON.stringify(o.resolved) === JSON.stringify(RESULT);
  C.no_newline = { status: o.status, error: o.error };
}
// controls still hold
{
  const b = Buffer.from(RESP); const k = Math.floor(b.length / 2);
  const o = await drive(V2, [b.subarray(0, k), b.subarray(k)]);
  R.v2_split_resolves = o.status === "resolved";
}
{
  const other = JSON.stringify({ jsonrpc: "2.0", id: 999, result: { other: 1 } }) + "\n";
  const o = await drive(V2, [other + RESP]);
  R.v2_foreign_then_ours = o.status === "resolved";
}
// v1 corrupts the UTF-8 split; v2 does not (contrast)
{
  const payload = "caf\u00e9 " + "x".repeat(70000);
  const r = JSON.stringify({ jsonrpc: "2.0", id: 1, result: { text: payload } }) + "\n";
  const b = Buffer.from(r, "utf8");
  const idx = r.indexOf("\u00e9");
  const k = Buffer.byteLength(r.slice(0, idx), "utf8") + 1;
  const o = await drive(V1, [b.subarray(0, k), b.subarray(k)]);
  R.v1_corrupts_utf8 = o.status === "resolved" && o.resolved?.text !== payload;
}
// RESIDUAL probe: a timed-out call leaves listeners attached
{
  const o = await drive(V2, [], false, 300);
  R.v2_timeout_cleans_listeners = o.status === "rejected" && o.data_listeners === 0 && o.end_listeners === 0;
  C.timeout_listeners = { status: o.status, data: o.data_listeners, end: o.end_listeners };
}
const problems = Object.entries(R).filter(([, v]) => !v).map(([k]) => k);
console.log(JSON.stringify({ results: R, cases: C, problems }, null, 1));
process.exit(0);
