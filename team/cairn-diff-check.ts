// Differential check: real TS trigger (evaluateFire) vs CAIRN-ROW36-SMOKE-FIRE-MATRIX.md
// Usage: bun team/cairn-diff-check.ts   ($0, no LLM, no fire-log write — evaluateFire is pure)
import { tokensOf, evaluateFire } from "/home/bmosher/memory-bake-off/implementer/repo/extensions/pi-change-trigger/index.ts";
import { readFileSync } from "fs";
const corpus = readFileSync("/home/bmosher/memory-bake-off/team/invocation-corpus-v1/corpus.jsonl","utf8").split("\n").filter(Boolean).map(l=>JSON.parse(l));
for (const s of corpus) {
  const topics = new Set<string>();
  for (const r of s.records) for (const t of tokensOf(r.summary)) topics.add(t);
  s.turns.forEach((t, i) => {
    const d = evaluateFire({ isFirstPrompt: i===0, minutesSinceLastPrompt: null, prompt: t.text, topics, gapMinutes: 30 });
    console.log(`${s.scenario_id}\t${t.turn}\t${t.type}\tfired=${d.fired}\treasons=${d.reasons.join("+")||"-"}\tmatched=${d.matchedTokens.join(",")||"-"}`);
  });
}
