"""`evidence-generation-gen59-v1`: a ruler where right and wrong answers coexist.

Gen58 could not be scored, and the reason was the corpus rather than the idea.
Every historical wrong implementation lived in the two tasks whose generated
test banks rejected known-good code, and both trustworthy banks covered tasks
with nothing wrong in them. Sensitivity and specificity had no shared ground.

So this file builds a new set of tasks where each one carries, at the same time,
two genuinely different correct implementations and three wrong ones — and where
at least two of the wrong ones sail past the project's own shipped tests. That
last property is the whole point: it is the situation an evidence generator is
supposed to help with, and it has to be present before the generator can be
judged.

Nothing here is written by a model, and the hidden evaluator never touches the
files a future generator is allowed to read.
"""
from __future__ import annotations

from typing import Any

# Each task: a visible spec, a shipped repo, and an evaluator-only truth package.
# `positives` and `wrongs` are file overlays applied to the shipped repo.
TASKS: dict[str, dict[str, Any]] = {}


def task(name: str, **kwargs: Any) -> None:
    TASKS[name] = kwargs


# --- T1 culvert: a shared constant with two consumers -------------------------
task(
    "culvert",
    title="a shared constant that only one consumer should follow",
    mechanism="cross_file_compatibility",
    spec="""The gate controller firmware changed. It now reports 8 encoder steps per
millimetre of gate travel, where it previously reported 4.

Update the package so that gate positions are computed from the new ratio: a
reading of 80 steps must report 10 millimetres.

The control room's telemetry frames must keep reporting the SAME number of steps
for a given millimetre position as they did before the firmware change. A
telemetry frame for 10 millimetres must still say 40 steps.""",
    repo={
        "culvert/__init__.py": "",
        "culvert/units.py": "STEPS_PER_MM = 4\n\n\ndef to_millimetres(steps: int) -> int:\n    return steps // STEPS_PER_MM\n\n\ndef to_steps(millimetres: int) -> int:\n    return millimetres * STEPS_PER_MM\n",
        "culvert/gauge.py": "from culvert.units import to_millimetres\n\n\ndef position_mm(steps: int) -> int:\n    return to_millimetres(steps)\n",
        "culvert/telemetry.py": "from culvert.units import to_steps\n\n\ndef frame(millimetres: int) -> dict:\n    return {\"mm\": millimetres, \"steps\": to_steps(millimetres)}\n",
        "tests/test_gauge.py": "from culvert.gauge import position_mm\n\n\ndef test_position_is_millimetres():\n    assert position_mm(40) == 10\n",
        "README.md": "# culvert\n\nGate position helpers.\n",
    },
    requirements={
        "A": "position_mm(80) == 10 and position_mm(40) == 5 under the new ratio",
        "B": "frame(10)['steps'] == 40, unchanged by the firmware change",
    },
    verifier="""from culvert.gauge import position_mm
from culvert.telemetry import frame

assert position_mm(80) == 10, f"A: position_mm(80) -> {position_mm(80)}, expected 10"
assert position_mm(40) == 5, f"A: position_mm(40) -> {position_mm(40)}, expected 5"
assert frame(10)["steps"] == 40, f"B: frame(10) -> {frame(10)}, expected 40 steps"
print("VERIFIER OK")
""",
    positives={
        "separate_constant": {
            "culvert/units.py": "STEPS_PER_MM = 8\nTELEMETRY_STEPS_PER_MM = 4\n\n\ndef to_millimetres(steps: int) -> int:\n    return steps // STEPS_PER_MM\n\n\ndef to_steps(millimetres: int) -> int:\n    return millimetres * TELEMETRY_STEPS_PER_MM\n",
            "tests/test_gauge.py": "from culvert.gauge import position_mm\n\n\ndef test_position_is_millimetres():\n    assert position_mm(80) == 10\n",
        },
        "telemetry_owns_its_ratio": {
            "culvert/units.py": "STEPS_PER_MM = 8\n\n\ndef to_millimetres(steps: int) -> int:\n    return steps // STEPS_PER_MM\n\n\ndef to_steps(millimetres: int) -> int:\n    return millimetres * STEPS_PER_MM\n",
            "culvert/telemetry.py": "LEGACY_STEPS_PER_MM = 4\n\n\ndef frame(millimetres: int) -> dict:\n    return {\"mm\": millimetres, \"steps\": millimetres * LEGACY_STEPS_PER_MM}\n",
            "tests/test_gauge.py": "from culvert.gauge import position_mm\n\n\ndef test_position_is_millimetres():\n    assert position_mm(80) == 10\n",
        },
    },
    wrongs={
        "shared_constant_breaks_telemetry": {
            "failed_requirement": "B",
            "why": "bumped the single shared constant, so telemetry frames silently changed too",
            "passes_visible": True,
            "overlay": {
                "culvert/units.py": "STEPS_PER_MM = 8\n\n\ndef to_millimetres(steps: int) -> int:\n    return steps // STEPS_PER_MM\n\n\ndef to_steps(millimetres: int) -> int:\n    return millimetres * STEPS_PER_MM\n",
                "tests/test_gauge.py": "from culvert.gauge import position_mm\n\n\ndef test_position_is_millimetres():\n    assert position_mm(80) == 10\n",
            },
        },
        "edited_the_test_to_agree": {
            "failed_requirement": "A",
            "why": "left the old ratio in place and rewrote the shipped test to assert the old behaviour",
            "passes_visible": True,
            "self_modified_visible_test": True,
            "overlay": {
                "tests/test_gauge.py": "from culvert.gauge import position_mm\n\n\ndef test_position_is_millimetres():\n    # firmware ratio confirmed unchanged\n    assert position_mm(40) == 10\n",
            },
        },
        "inverted_the_consumers": {
            "failed_requirement": "A",
            "why": "applied the new ratio to telemetry and left the gauge on the old one",
            "passes_visible": False,
            "overlay": {
                "culvert/units.py": "STEPS_PER_MM = 4\nTELEMETRY_STEPS_PER_MM = 8\n\n\ndef to_millimetres(steps: int) -> int:\n    return steps // STEPS_PER_MM\n\n\ndef to_steps(millimetres: int) -> int:\n    return millimetres * TELEMETRY_STEPS_PER_MM\n",
            },
        },
    },
)


# --- T2 valve: what happens below zero ----------------------------------------
task(
    "valve",
    title="a limit that is stated at both ends",
    mechanism="boundary_and_negative_input",
    spec="""`opening_percent(raw)` reports a valve opening as a percentage.

The reading must be clamped to the range 0 to 100 inclusive. A raw reading above
100 reports 100. A raw reading below 0 reports 0 — negative openings are not
physically meaningful and must not be passed through or made positive.

A reading already inside the range is reported unchanged.""",
    repo={
        "valve/__init__.py": "",
        "valve/limits.py": "MAX_PERCENT = 100\n\n\ndef opening_percent(raw: int) -> int:\n    if raw > MAX_PERCENT:\n        return MAX_PERCENT\n    return raw\n",
        "tests/test_limits.py": "from valve.limits import opening_percent\n\n\ndef test_upper_bound_is_clamped():\n    assert opening_percent(150) == 100\n\n\ndef test_in_range_is_unchanged():\n    assert opening_percent(40) == 40\n",
        "README.md": "# valve\n\nValve opening helpers.\n",
    },
    requirements={
        "A": "opening_percent(150) == 100 and opening_percent(40) == 40",
        "B": "opening_percent(-5) == 0 and opening_percent(-1) == 0",
    },
    verifier="""from valve.limits import opening_percent

assert opening_percent(150) == 100, f"A: opening_percent(150) -> {opening_percent(150)}"
assert opening_percent(40) == 40, f"A: opening_percent(40) -> {opening_percent(40)}"
assert opening_percent(-5) == 0, f"B: opening_percent(-5) -> {opening_percent(-5)}, expected 0"
assert opening_percent(-1) == 0, f"B: opening_percent(-1) -> {opening_percent(-1)}, expected 0"
print("VERIFIER OK")
""",
    positives={
        "min_max": {
            "valve/limits.py": "MAX_PERCENT = 100\nMIN_PERCENT = 0\n\n\ndef opening_percent(raw: int) -> int:\n    return max(MIN_PERCENT, min(MAX_PERCENT, raw))\n",
        },
        "explicit_branches": {
            "valve/limits.py": "MAX_PERCENT = 100\nMIN_PERCENT = 0\n\n\ndef opening_percent(raw: int) -> int:\n    if raw > MAX_PERCENT:\n        return MAX_PERCENT\n    if raw < MIN_PERCENT:\n        return MIN_PERCENT\n    return raw\n",
        },
    },
    wrongs={
        "upper_bound_only": {
            "failed_requirement": "B",
            "why": "kept the shipped upper-bound clamp and never added the lower bound",
            "passes_visible": True,
            "overlay": {},
        },
        "absolute_value": {
            "failed_requirement": "B",
            "why": "made negatives positive instead of clamping them to zero",
            "passes_visible": True,
            "overlay": {
                "valve/limits.py": "MAX_PERCENT = 100\n\n\ndef opening_percent(raw: int) -> int:\n    raw = abs(raw)\n    if raw > MAX_PERCENT:\n        return MAX_PERCENT\n    return raw\n",
            },
        },
        "off_by_one_ceiling": {
            "failed_requirement": "A",
            "why": "clamped the top of the range to 99",
            "passes_visible": False,
            "overlay": {
                "valve/limits.py": "MAX_PERCENT = 99\nMIN_PERCENT = 0\n\n\ndef opening_percent(raw: int) -> int:\n    return max(MIN_PERCENT, min(MAX_PERCENT, raw))\n",
            },
        },
    },
)


# --- T3 tally: behaviour that only shows up over a sequence --------------------
task(
    "tally",
    title="a counter whose rule only appears across several calls",
    mechanism="sequence_and_state",
    spec="""`Session` accumulates weighed amounts.

`add(n)` adds n to the running total. `total()` reports the running total.

`close()` returns the running total AND resets the session to zero, so that a
session reused after `close()` starts from zero again. Calling `total()` after
`close()` must report 0 until something new is added.""",
    repo={
        "tally/__init__.py": "",
        "tally/session.py": "class Session:\n    def __init__(self) -> None:\n        self._total = 0\n\n    def add(self, n: int) -> None:\n        self._total += n\n\n    def total(self) -> int:\n        return self._total\n\n    def close(self) -> int:\n        return self._total\n",
        "tests/test_session.py": "from tally.session import Session\n\n\ndef test_add_accumulates():\n    s = Session()\n    s.add(3)\n    s.add(4)\n    assert s.total() == 7\n",
        "README.md": "# tally\n\nWeighing session helpers.\n",
    },
    requirements={
        "A": "add accumulates and total reports the running total",
        "B": "close returns the total and resets the session, so total() is 0 afterwards",
    },
    verifier="""from tally.session import Session

s = Session()
s.add(3)
s.add(4)
assert s.total() == 7, f"A: total -> {s.total()}, expected 7"
assert s.close() == 7, f"B: close -> returned wrong total"
assert s.total() == 0, f"B: total after close -> {s.total()}, expected 0"
s.add(2)
assert s.total() == 2, f"B: reuse after close -> {s.total()}, expected 2"
print("VERIFIER OK")
""",
    positives={
        "reset_in_close": {
            "tally/session.py": "class Session:\n    def __init__(self) -> None:\n        self._total = 0\n\n    def add(self, n: int) -> None:\n        self._total += n\n\n    def total(self) -> int:\n        return self._total\n\n    def close(self) -> int:\n        closing = self._total\n        self._total = 0\n        return closing\n",
        },
        "delegated_reset": {
            "tally/session.py": "class Session:\n    def __init__(self) -> None:\n        self.reset()\n\n    def reset(self) -> None:\n        self._total = 0\n\n    def add(self, n: int) -> None:\n        self._total += n\n\n    def total(self) -> int:\n        return self._total\n\n    def close(self) -> int:\n        closing = self.total()\n        self.reset()\n        return closing\n",
        },
    },
    wrongs={
        "close_does_not_reset": {
            "failed_requirement": "B",
            "why": "close reports the total but leaves the session holding it",
            "passes_visible": True,
            "overlay": {},
        },
        "reset_only_on_next_add": {
            "failed_requirement": "B",
            "why": "defers the reset until the next add, so total() straight after close is stale",
            "passes_visible": True,
            "overlay": {
                "tally/session.py": "class Session:\n    def __init__(self) -> None:\n        self._total = 0\n        self._closed = False\n\n    def add(self, n: int) -> None:\n        if self._closed:\n            self._total = 0\n            self._closed = False\n        self._total += n\n\n    def total(self) -> int:\n        return self._total\n\n    def close(self) -> int:\n        self._closed = True\n        return self._total\n",
            },
        },
        "add_multiplies": {
            "failed_requirement": "A",
            "why": "combined amounts with multiplication instead of addition",
            "passes_visible": False,
            "overlay": {
                "tally/session.py": "class Session:\n    def __init__(self) -> None:\n        self._total = 1\n\n    def add(self, n: int) -> None:\n        self._total *= n\n\n    def total(self) -> int:\n        return self._total\n\n    def close(self) -> int:\n        closing = self._total\n        self._total = 1\n        return closing\n",
            },
        },
    },
)


# --- T4 manifest: the empty field ---------------------------------------------
task(
    "manifest",
    title="a blank field is not an empty string",
    mechanism="parser_edge_case",
    spec="""`parse_row(line)` splits a comma-separated manifest line into a dictionary
with the keys `code`, `label` and `depot`, in that order.

Surrounding whitespace is stripped from every field.

A field that is blank — empty, or only whitespace — must be reported as `None`,
not as an empty string, so that a missing label is distinguishable from a label
that happens to be empty.""",
    repo={
        "manifest/__init__.py": "",
        "manifest/rows.py": "FIELDS = (\"code\", \"label\", \"depot\")\n\n\ndef parse_row(line: str) -> dict:\n    parts = line.split(\",\")\n    return {name: parts[index] for index, name in enumerate(FIELDS)}\n",
        "tests/test_rows.py": "from manifest.rows import parse_row\n\n\ndef test_full_row():\n    assert parse_row(\"A1,widget,north\") == {\n        \"code\": \"A1\", \"label\": \"widget\", \"depot\": \"north\"}\n",
        "README.md": "# manifest\n\nManifest row parsing.\n",
    },
    requirements={
        "A": "fields are stripped of surrounding whitespace and mapped in order",
        "B": "a blank or whitespace-only field is None, not an empty string",
    },
    verifier="""from manifest.rows import parse_row

full = parse_row("A1,widget,north")
assert full == {"code": "A1", "label": "widget", "depot": "north"}, f"A: {full}"
spaced = parse_row(" A1 , widget , north ")
assert spaced == {"code": "A1", "label": "widget", "depot": "north"}, f"A: {spaced}"
blank = parse_row("A1,,north")
assert blank["label"] is None, f"B: blank label -> {blank['label']!r}, expected None"
spaces = parse_row("A1,   ,north")
assert spaces["label"] is None, f"B: whitespace label -> {spaces['label']!r}, expected None"
print("VERIFIER OK")
""",
    positives={
        "guard_clause": {
            "manifest/rows.py": "FIELDS = (\"code\", \"label\", \"depot\")\n\n\ndef parse_row(line: str) -> dict:\n    parts = [part.strip() for part in line.split(\",\")]\n    row = {}\n    for index, name in enumerate(FIELDS):\n        value = parts[index]\n        row[name] = value if value else None\n    return row\n",
        },
        "helper_function": {
            "manifest/rows.py": "FIELDS = (\"code\", \"label\", \"depot\")\n\n\ndef _clean(value: str):\n    stripped = value.strip()\n    return stripped or None\n\n\ndef parse_row(line: str) -> dict:\n    parts = line.split(\",\")\n    return {name: _clean(parts[index]) for index, name in enumerate(FIELDS)}\n",
        },
    },
    wrongs={
        "blank_stays_empty_string": {
            "failed_requirement": "B",
            "why": "stripped the fields but left a blank one as an empty string",
            "passes_visible": True,
            "overlay": {
                "manifest/rows.py": "FIELDS = (\"code\", \"label\", \"depot\")\n\n\ndef parse_row(line: str) -> dict:\n    parts = [part.strip() for part in line.split(\",\")]\n    return {name: parts[index] for index, name in enumerate(FIELDS)}\n",
            },
        },
        "only_empty_counts_as_blank": {
            "failed_requirement": "B",
            "why": "treated the empty string as blank but not a whitespace-only field",
            "passes_visible": True,
            "overlay": {
                "manifest/rows.py": "FIELDS = (\"code\", \"label\", \"depot\")\n\n\ndef parse_row(line: str) -> dict:\n    parts = line.split(\",\")\n    row = {}\n    for index, name in enumerate(FIELDS):\n        value = parts[index]\n        row[name] = None if value == \"\" else value.strip()\n    return row\n",
            },
        },
        "fields_out_of_order": {
            "failed_requirement": "A",
            "why": "mapped the columns in the wrong order",
            "passes_visible": False,
            "overlay": {
                "manifest/rows.py": "FIELDS = (\"code\", \"depot\", \"label\")\n\n\ndef parse_row(line: str) -> dict:\n    parts = [part.strip() for part in line.split(\",\")]\n    row = {}\n    for index, name in enumerate(FIELDS):\n        value = parts[index]\n        row[name] = value if value else None\n    return row\n",
            },
        },
    },
)


# --- T5 ledger: a midpoint that floats cannot represent -----------------------
# The first draft of this task asked for half-away-from-zero rounding of a float.
# That premise was unsound: 2.345 is stored slightly ABOVE the midpoint, so
# Python's round already returns 2.35 and the "wrong" candidates were correct.
# The interface is decimal strings, where the midpoint is exact and the rule bites.
task(
    "ledger",
    title="a rounding rule that only shows at an exact midpoint",
    mechanism="numeric_convention",
    spec="""`charge(amount)` takes a money amount as a decimal string and returns it
rounded to two decimal places, also as a string with exactly two decimals.

Rounding is half away from zero: an amount exactly halfway between two hundredths
goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68".

Amounts are given as strings precisely so that a halfway value means what it says.
Converting through a binary float loses that, because a value such as 2.675 is not
stored exactly and can round the wrong way.""",
    repo={
        "ledger/__init__.py": "",
        "ledger/money.py": "def charge(amount: str) -> str:\n    return f\"{round(float(amount), 2):.2f}\"\n",
        "tests/test_money.py": "from ledger.money import charge\n\n\ndef test_rounds_to_two_places():\n    assert charge(\"2.341\") == \"2.34\"\n    assert charge(\"7.812\") == \"7.81\"\n",
        "README.md": "# ledger\n\nMoney rounding helpers.\n",
    },
    requirements={
        "A": "ordinary amounts round to two decimal places and keep two decimals in the output",
        "B": "an exact midpoint rounds away from zero, for positive and negative amounts",
    },
    verifier="""from ledger.money import charge

assert charge("2.341") == "2.34", f"A: charge('2.341') -> {charge('2.341')!r}"
assert charge("7.812") == "7.81", f"A: charge('7.812') -> {charge('7.812')!r}"
assert charge("2.675") == "2.68", f"B: charge('2.675') -> {charge('2.675')!r}, expected '2.68'"
# 2.665 separates half-away-from-zero from half-to-even: the even neighbour is 2.66.
assert charge("2.665") == "2.67", f"B: charge('2.665') -> {charge('2.665')!r}, expected '2.67'"
assert charge("-2.675") == "-2.68", f"B: charge('-2.675') -> {charge('-2.675')!r}, expected '-2.68'"
print("VERIFIER OK")
""",
    positives={
        "decimal_half_up": {
            "ledger/money.py": "from decimal import Decimal, ROUND_HALF_UP\n\n\ndef charge(amount: str) -> str:\n    value = Decimal(amount).quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)\n    return f\"{value:.2f}\"\n",
        },
        "explicit_remainder": {
            "ledger/money.py": "from decimal import Decimal\n\n\ndef charge(amount: str) -> str:\n    value = Decimal(amount)\n    scaled = value * 100\n    whole = int(scaled)\n    remainder = abs(scaled - whole)\n    if remainder >= Decimal(\"0.5\"):\n        whole += 1 if value >= 0 else -1\n    result = Decimal(whole) / 100\n    return f\"{result:.2f}\"\n",
        },
    },
    wrongs={
        "through_a_float": {
            "failed_requirement": "B",
            "why": "kept the shipped float conversion, which stores 2.675 just below the midpoint",
            "passes_visible": True,
            "overlay": {},
        },
        "half_to_even": {
            "failed_requirement": "B",
            "why": "used decimals but rounded halves to even instead of away from zero",
            "passes_visible": True,
            "overlay": {
                "ledger/money.py": "from decimal import Decimal, ROUND_HALF_EVEN\n\n\ndef charge(amount: str) -> str:\n    value = Decimal(amount).quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_EVEN)\n    return f\"{value:.2f}\"\n",
            },
        },
        "truncates_instead_of_rounding": {
            "failed_requirement": "A",
            "why": "cut the amount at two decimals rather than rounding it",
            "passes_visible": False,
            "overlay": {
                "ledger/money.py": "from decimal import Decimal, ROUND_DOWN\n\n\ndef charge(amount: str) -> str:\n    value = Decimal(amount).quantize(Decimal(\"0.01\"), rounding=ROUND_DOWN)\n    return f\"{value:.2f}\"\n",
            },
        },
    },
)


# --- T6 dispatch: order that one call cannot reveal ---------------------------
task(
    "dispatch",
    title="a queue whose ordering rule needs several items to show",
    mechanism="sequence_and_state",
    spec="""`Queue` releases jobs to a depot.

`push(name)` adds an ordinary job. `push(name, urgent=True)` adds an urgent one.
`pop()` removes and returns the next job to run.

Ordinary jobs run in the order they were added. An urgent job runs before every
ordinary job currently waiting, and urgent jobs run among themselves in the order
they were added.""",
    repo={
        "dispatch/__init__.py": "",
        "dispatch/queue.py": "class Queue:\n    def __init__(self) -> None:\n        self._jobs = []\n\n    def push(self, name: str, urgent: bool = False) -> None:\n        self._jobs.append(name)\n\n    def pop(self) -> str:\n        return self._jobs.pop(0)\n",
        "tests/test_queue.py": "from dispatch.queue import Queue\n\n\ndef test_single_job_comes_back():\n    q = Queue()\n    q.push(\"a\")\n    assert q.pop() == \"a\"\n\n\ndef test_ordinary_jobs_keep_their_order():\n    q = Queue()\n    q.push(\"a\")\n    q.push(\"b\")\n    assert q.pop() == \"a\"\n    assert q.pop() == \"b\"\n",
        "README.md": "# dispatch\n\nJob queue.\n",
    },
    requirements={
        "A": "ordinary jobs come out in the order they were pushed",
        "B": "an urgent job overtakes every waiting ordinary job, and urgent jobs keep their own order",
    },
    verifier="""from dispatch.queue import Queue

q = Queue()
q.push("a")
q.push("b")
assert q.pop() == "a", "A: ordinary order"
assert q.pop() == "b", "A: ordinary order"

q = Queue()
q.push("a")
q.push("b")
q.push("u1", urgent=True)
q.push("u2", urgent=True)
order = [q.pop(), q.pop(), q.pop(), q.pop()]
assert order == ["u1", "u2", "a", "b"], f"B: order -> {order}, expected ['u1','u2','a','b']"
print("VERIFIER OK")
""",
    positives={
        "two_lists": {
            "dispatch/queue.py": "class Queue:\n    def __init__(self) -> None:\n        self._urgent = []\n        self._ordinary = []\n\n    def push(self, name: str, urgent: bool = False) -> None:\n        (self._urgent if urgent else self._ordinary).append(name)\n\n    def pop(self) -> str:\n        if self._urgent:\n            return self._urgent.pop(0)\n        return self._ordinary.pop(0)\n",
        },
        "sorted_by_rank": {
            "dispatch/queue.py": "class Queue:\n    def __init__(self) -> None:\n        self._jobs = []\n        self._sequence = 0\n\n    def push(self, name: str, urgent: bool = False) -> None:\n        self._jobs.append((0 if urgent else 1, self._sequence, name))\n        self._sequence += 1\n\n    def pop(self) -> str:\n        self._jobs.sort()\n        return self._jobs.pop(0)[2]\n",
        },
    },
    wrongs={
        "urgency_ignored": {
            "failed_requirement": "B",
            "why": "kept the shipped single list, so an urgent job waits its turn",
            "passes_visible": True,
            "overlay": {},
        },
        "urgent_jobs_reversed": {
            "failed_requirement": "B",
            "why": "put each urgent job at the very front, so urgent jobs come out backwards",
            "passes_visible": True,
            "overlay": {
                "dispatch/queue.py": "class Queue:\n    def __init__(self) -> None:\n        self._jobs = []\n\n    def push(self, name: str, urgent: bool = False) -> None:\n        if urgent:\n            self._jobs.insert(0, name)\n        else:\n            self._jobs.append(name)\n\n    def pop(self) -> str:\n        return self._jobs.pop(0)\n",
            },
        },
        "pops_from_the_back": {
            "failed_requirement": "A",
            "why": "released the most recently added ordinary job first",
            "passes_visible": False,
            "overlay": {
                "dispatch/queue.py": "class Queue:\n    def __init__(self) -> None:\n        self._urgent = []\n        self._ordinary = []\n\n    def push(self, name: str, urgent: bool = False) -> None:\n        (self._urgent if urgent else self._ordinary).append(name)\n\n    def pop(self) -> str:\n        if self._urgent:\n            return self._urgent.pop(0)\n        return self._ordinary.pop()\n",
            },
        },
    },
)


# --- T7 pathsafe: the error that must be raised -------------------------------
task(
    "pathsafe",
    title="an input that must be refused, not repaired",
    mechanism="error_behaviour",
    spec="""`resolve(name)` turns a requested file name into a path underneath the
depot directory `depot/`.

A relative name resolves to `depot/<name>`.

A name that is absolute, or that escapes the depot with `..`, must be refused by
raising `ValueError`. It must not be silently rewritten, stripped or clamped into
the depot — the caller needs to know the request was rejected.""",
    repo={
        "pathsafe/__init__.py": "",
        "pathsafe/paths.py": "DEPOT = \"depot\"\n\n\ndef resolve(name: str) -> str:\n    return f\"{DEPOT}/{name}\"\n",
        "tests/test_paths.py": "from pathsafe.paths import resolve\n\n\ndef test_relative_name_lands_in_the_depot():\n    assert resolve(\"parts.csv\") == \"depot/parts.csv\"\n",
        "README.md": "# pathsafe\n\nDepot path helpers.\n",
    },
    requirements={
        "A": "a relative name resolves to depot/<name>",
        "B": "an absolute name or one containing .. raises ValueError",
    },
    verifier="""from pathsafe.paths import resolve

assert resolve("parts.csv") == "depot/parts.csv", f"A: {resolve('parts.csv')}"

for bad in ("/etc/passwd", "../secrets", "a/../../b"):
    try:
        result = resolve(bad)
    except ValueError:
        continue
    raise AssertionError(f"B: resolve({bad!r}) -> {result!r}, expected ValueError")
print("VERIFIER OK")
""",
    positives={
        "explicit_checks": {
            "pathsafe/paths.py": "DEPOT = \"depot\"\n\n\ndef resolve(name: str) -> str:\n    if name.startswith(\"/\"):\n        raise ValueError(\"absolute names are not allowed\")\n    if \"..\" in name.split(\"/\"):\n        raise ValueError(\"names may not escape the depot\")\n    return f\"{DEPOT}/{name}\"\n",
        },
        "single_guard": {
            "pathsafe/paths.py": "DEPOT = \"depot\"\n\n\ndef _is_refused(name: str) -> bool:\n    return name.startswith(\"/\") or \"..\" in name.split(\"/\")\n\n\ndef resolve(name: str) -> str:\n    if _is_refused(name):\n        raise ValueError(f\"refused: {name}\")\n    return f\"{DEPOT}/{name}\"\n",
        },
    },
    wrongs={
        "silently_repaired": {
            "failed_requirement": "B",
            "why": "stripped the leading slash and dot segments instead of refusing the request",
            "passes_visible": True,
            "overlay": {
                "pathsafe/paths.py": "DEPOT = \"depot\"\n\n\ndef resolve(name: str) -> str:\n    cleaned = name.lstrip(\"/\").replace(\"../\", \"\")\n    return f\"{DEPOT}/{cleaned}\"\n",
            },
        },
        "absolute_only": {
            "failed_requirement": "B",
            "why": "refused absolute names but let .. escape the depot",
            "passes_visible": True,
            "overlay": {
                "pathsafe/paths.py": "DEPOT = \"depot\"\n\n\ndef resolve(name: str) -> str:\n    if name.startswith(\"/\"):\n        raise ValueError(\"absolute names are not allowed\")\n    return f\"{DEPOT}/{name}\"\n",
            },
        },
        "refuses_everything": {
            "failed_requirement": "A",
            "why": "raised for any name containing a dot, which rejects ordinary files",
            "passes_visible": False,
            "overlay": {
                "pathsafe/paths.py": "DEPOT = \"depot\"\n\n\ndef resolve(name: str) -> str:\n    if \".\" in name or name.startswith(\"/\"):\n        raise ValueError(f\"refused: {name}\")\n    return f\"{DEPOT}/{name}\"\n",
            },
        },
    },
)


# --- T8 thermo: the default nobody tested -------------------------------------
# The rounding-mode clause from the first draft was removed: it depended on a
# float midpoint that cannot be represented, which made the negatives untestable.
# What remains is purely the untested default.
task(
    "thermo",
    title="a default that the shipped tests never exercise",
    mechanism="default_argument",
    spec="""`to_fahrenheit(celsius, places=1)` converts a temperature and rounds the
result to a number of decimal places.

The `places` argument says how many decimal places to keep. When the caller does
not supply it, the result is rounded to ONE decimal place.

Rounding is ordinary nearest-value rounding; no midpoint case arises in this task.""",
    repo={
        "thermo/__init__.py": "",
        "thermo/convert.py": "def to_fahrenheit(celsius: float, places: int = 2) -> float:\n    return round(celsius * 9 / 5 + 32, places)\n",
        "tests/test_convert.py": "from thermo.convert import to_fahrenheit\n\n\ndef test_conversion_with_explicit_places():\n    assert to_fahrenheit(100, places=2) == 212.0\n    assert to_fahrenheit(36.6, places=2) == 97.88\n",
        "README.md": "# thermo\n\nTemperature conversion.\n",
    },
    requirements={
        "A": "conversion is correct and honours an explicit places argument",
        "B": "the default keeps one decimal place",
    },
    verifier="""from thermo.convert import to_fahrenheit

assert to_fahrenheit(100, places=2) == 212.0, f"A: {to_fahrenheit(100, places=2)}"
assert to_fahrenheit(36.6, places=2) == 97.88, f"A: {to_fahrenheit(36.6, places=2)}"
assert to_fahrenheit(36.6) == 97.9, f"B: default places -> {to_fahrenheit(36.6)}, expected 97.9"
assert to_fahrenheit(0) == 32.0, f"B: default places -> {to_fahrenheit(0)}, expected 32.0"
print("VERIFIER OK")
""",
    positives={
        "default_changed": {
            "thermo/convert.py": "def to_fahrenheit(celsius: float, places: int = 1) -> float:\n    return round(celsius * 9 / 5 + 32, places)\n",
        },
        "named_constant": {
            "thermo/convert.py": "DEFAULT_PLACES = 1\n\n\ndef _fahrenheit(celsius: float) -> float:\n    return celsius * 9 / 5 + 32\n\n\ndef to_fahrenheit(celsius: float, places: int = DEFAULT_PLACES) -> float:\n    return round(_fahrenheit(celsius), places)\n",
        },
    },
    wrongs={
        "default_left_at_two": {
            "failed_requirement": "B",
            "why": "kept the shipped default of two places, which the shipped tests never exercise",
            "passes_visible": True,
            "overlay": {},
        },
        "default_truncates": {
            "failed_requirement": "B",
            "why": "made the default one place but cut the digit off instead of rounding",
            "passes_visible": True,
            "overlay": {
                "thermo/convert.py": "import math\n\n\ndef to_fahrenheit(celsius: float, places: int = 1) -> float:\n    scale = 10 ** places\n    return math.floor((celsius * 9 / 5 + 32) * scale) / scale\n",
            },
        },
        "conversion_inverted": {
            "failed_requirement": "A",
            "why": "converted Fahrenheit to Celsius instead",
            "passes_visible": False,
            "overlay": {
                "thermo/convert.py": "def to_fahrenheit(celsius: float, places: int = 1) -> float:\n    return round((celsius - 32) * 5 / 9, places)\n",
            },
        },
    },
)
