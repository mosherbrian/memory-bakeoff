"""DIAGNOSTIC probe. Not the experiment. Finds phrasing this reader complies with.

Legitimate against already-seen cases: we are choosing an INSTRUCTION, and will
confirm on a fresh fixture. Nothing here is evidence.
"""
import json, sys, urllib.request
from pathlib import Path

ROOT = Path("/var/home/bmosher/pilot-gen45")
ENDPOINT = "http://strix-halo.local:8080/v1/chat/completions"
MODEL = "qwen3.6-35b-vulkan-nothink"
canon = ROOT / "results/gen118" / (ROOT / "results/gen118/CANONICAL_ATTEMPT.md").read_text().split("`")[1]
cases = [c for c in json.loads((canon / "reader_interference_v6_schedule.json").read_text())["cases"]
         if c["expected_value"]][:8]

SCHEMA = ('{"disposition": "RESOLVED|UNRESOLVED|INSUFFICIENT", "selected_record_id": '
          '"<record id or null>", "selected_value": "<value or null>", '
          '"prior_values": ["<value>", ...], "citations": ["<record id>", ...]}')

RULE = ("Select the record whose effective_revision is exactly equal to as_of_revision. "
        "If no record has that exact effective_revision, you must answer INSUFFICIENT "
        "rather than infer, extrapolate, or choose the closest record.")

VARIANTS = {
 "V1-current": RULE + (" For selected_value, copy the ENTIRE value phrase exactly as "
   "written in the selected record. Do not abbreviate it, omit a word, return only the "
   "distinguishing word, paraphrase it, or place it inside a sentence."),

 "V2-example": RULE + (" For selected_value, copy the ENTIRE value phrase exactly as "
   "written in the selected record. Do not abbreviate it, omit a word, return only the "
   "distinguishing word, paraphrase it, or place it inside a sentence.\n"
   'EXAMPLE. Record: "The Ashford junction routes via lane merridew." '
   'CORRECT selected_value: "lane merridew". '
   'WRONG: "The Ashford junction routes via lane merridew." (a sentence). '
   'WRONG: "merridew" (only the distinguishing word).'),

 "V3-anchor": RULE + (" Each record states a subject, a verb phrase, and then a VALUE "
   "which runs from after the verb phrase to the end of the sentence, excluding the "
   "final full stop. For selected_value, return exactly that span, character for "
   "character. It is normally two words. Do not include the subject or verb."),

 "V4-both": RULE + (" Each record states a subject, a verb phrase, and then a VALUE "
   "which runs from after the verb phrase to the end of the sentence, excluding the "
   "final full stop. For selected_value, return exactly that span, character for "
   "character.\n"
   'EXAMPLE. Record: "The Ashford junction routes via lane merridew." '
   'CORRECT selected_value: "lane merridew". '
   'WRONG: "The Ashford junction routes via lane merridew." '
   'WRONG: "merridew".'),
}

def ask(rule, case):
    lines = [f"[{r['record_id']}] effective_revision: {r['effective_revision']} | {r['statement']}"
             for r in case["records"]]
    prompt = (f"Answer using only the records provided.\n{rule}\n"
              f"Reply with a single JSON object and nothing else:\n{SCHEMA}\n\nRECORDS:\n"
              + "\n".join(lines) +
              f"\n\nas_of_revision: {case['as_of_revision']}\nQUESTION: {case['question']}")
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0.0, "seed": 0, "max_tokens": 512, "stream": False})
    req = urllib.request.Request(ENDPOINT, data=body.encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        obj = json.loads(r.read().decode())
    return json.loads(obj["choices"][0]["message"]["content"])

print(f"{len(cases)} cases per variant, exact match required\n")
for name, rule in VARIANTS.items():
    exact = record_ok = 0
    misses = []
    for c in cases:
        try:
            a = ask(rule, c)
        except Exception as e:
            misses.append(f"ERROR {e}"); continue
        if a.get("selected_record_id") == c["expected_record_id"]: record_ok += 1
        sv = (a.get("selected_value") or "").strip()
        if " ".join(sv.split()).casefold() == " ".join(c["expected_value"].split()).casefold():
            exact += 1
        else:
            misses.append(f"want {c['expected_value']!r} got {sv!r}")
    print(f"{name:<12} exact {exact}/{len(cases)}   record {record_ok}/{len(cases)}")
    for m in misses[:2]: print(f"             {m}")
