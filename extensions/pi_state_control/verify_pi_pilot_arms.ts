/** Gen44: prove both pilot arms behave as frozen, inside the installed Pi. No model. */
const PI_DIST = process.env.PI_DIST!;
const { loadExtensions } = await import(`${PI_DIST}/core/extensions/loader.js`);
const { VERSION } = await import(`${PI_DIST}/config.js`);

const extPath = process.argv[2];

const transcript: any[] = [];
for (let turn = 0; turn < 12; turn++) {
  transcript.push({ role: "user", content: [{ type: "text", text: `ask ${turn} ` + "u".repeat(300) }] });
  transcript.push({ role: "assistant", content: [{ type: "text", text: `reply ${turn} ` + "a".repeat(300) }] });
  transcript.push({ role: "toolResult", content: [{ type: "text", text: `tool ${turn} ` + "t".repeat(2000) }] });
}

const runArm = async (arm: string) => {
  process.env.PI_PILOT_ARM = arm;
  const result = await loadExtensions([extPath], process.cwd());
  const ext = result.extensions?.[0];
  const handlers = ext?.handlers.get("context") ?? [];
  const before = JSON.stringify(transcript);
  let out: any;
  for (const fn of handlers) out = await fn({ type: "context", messages: transcript }, {});
  const unchanged = JSON.stringify(transcript) === before;
  const capture = (globalThis as any).__piPilotCapture;
  const compactHandlers = ext?.handlers.get("session_before_compact") ?? [];
  let compact: any;
  for (const fn of compactHandlers) compact = await fn({ type: "session_before_compact" }, {});
  return {
    arm,
    load_errors: result.errors ?? [],
    returned_replacement: Boolean(out?.messages),
    replacement_messages: out?.messages?.length ?? null,
    replacement_bytes: out?.messages ? JSON.stringify(out.messages).length : null,
    incoming_messages: transcript.length,
    incoming_bytes: before.length,
    pi_message_array_unmutated: unchanged,
    captured_requests: capture?.requests ?? [],
    compaction_cancelled: compact?.cancel === true,
  };
};

const a = await runArm("pi_default_v1");
const b = await runArm("pi_state_control_v1");

console.log(JSON.stringify({
  pi_version: VERSION,
  core_patched: false,
  arm_a: a,
  arm_b: b,
  checks: {
    a_does_not_replace_context: a.returned_replacement === false,
    a_leaves_pi_array_untouched: a.pi_message_array_unmutated,
    a_keeps_pi_compaction: a.compaction_cancelled === false,
    b_replaces_context: b.returned_replacement === true,
    b_cancels_compaction: b.compaction_cancelled === true,
    b_window_is_bounded: (b.replacement_bytes ?? Infinity) < a.incoming_bytes / 2,
    both_capture_request_sizes: a.captured_requests.length === 1 && b.captured_requests.length === 1,
  },
}, null, 2));
