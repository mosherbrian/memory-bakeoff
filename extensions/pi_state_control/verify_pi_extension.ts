/**
 * Gen43: load the prototype extension into the INSTALLED Pi and exercise its
 * hooks with synthetic events. No model, no network, no session.
 */
// The package exports map exposes only "." and "./hooks", so the loader is
// imported by its absolute path inside the INSTALLED package. Nothing is
// patched or copied; this reads the same files Pi itself runs.
const PI_DIST = process.env.PI_DIST!;
const { loadExtensions } = await import(`${PI_DIST}/core/extensions/loader.js`);
const { VERSION } = await import(`${PI_DIST}/config.js`);

const extPath = process.argv[2];
const result = await loadExtensions([extPath], process.cwd());

const errors = result.errors ?? [];
const ext = result.extensions?.[0];
const handlers = ext ? [...ext.handlers.keys()].sort() : [];

const call = async (name: string, event: any) => {
  const fns = ext?.handlers.get(name) ?? [];
  let out: any;
  for (const fn of fns) out = await fn(event, {});
  return out;
};

await call("session_start", { type: "session_start", reason: "startup" });
await call("input", { type: "input", text: "make the importer accept the second format", source: "user" });

const bigTranscript = Array.from({ length: 80 }, (_, i) => ({
  role: i % 2 ? "assistant" : "user",
  content: [{ type: "text", text: `historical turn ${i} ` + "x".repeat(500) }],
}));
const incomingBytes = JSON.stringify(bigTranscript).length;
const replaced = await call("context", { type: "context", messages: bigTranscript });
const outgoingBytes = JSON.stringify(replaced?.messages ?? []).length;

const beforeStart = await call("before_agent_start", {
  type: "before_agent_start", prompt: "p", systemPrompt: "original", systemPromptOptions: {},
});
const compact = await call("session_before_compact", { type: "session_before_compact" });
await call("tool_result", { type: "tool_result", result: { output: "y".repeat(4000) } });
await call("session_shutdown", { type: "session_shutdown", reason: "quit" });

const store = (globalThis as any).__piStateControlStore;

console.log(JSON.stringify({
  pi_version: VERSION,
  extension_loaded: Boolean(ext),
  load_errors: errors,
  registered_handlers: handlers,
  context_hook: {
    incoming_messages: bigTranscript.length,
    incoming_bytes: incomingBytes,
    replacement_messages: replaced?.messages?.length ?? null,
    replacement_bytes: outgoingBytes,
    transcript_replayed: outgoingBytes >= incomingBytes,
  },
  before_agent_start_can_replace_system_prompt: beforeStart?.systemPrompt === undefined ? false : true,
  compaction_cancelled: compact?.cancel === true,
  history_events_recorded: store?.history?.length ?? 0,
  core_patched: false,
}, null, 2));
