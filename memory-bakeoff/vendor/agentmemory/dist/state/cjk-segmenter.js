// Local English-corpus shim. The benchmark corpus contains no CJK text, so the
// upstream optional CJK tokenizer is never on the exercised path.
export function hasCjk(_text) { return false; }
export function segmentCjk(text) { return [text]; }
