#!/usr/bin/env python3
"""Independent, local-only gate for S13-2.

The receipt is a human-readable audit, with a heading for each mechanism.
No particular receipt filename is required. Use --root for another repository.

Findings are printed as FINDING[S13-2:NAME]. Normal checks and selftests return
0 on success and 1 on failure, including input and argument errors.

This checker was specified from the queue text, not from an existing receipt.
"""
import argparse
import contextlib
import copy
import io
import json
import re
import sys
import tempfile
from pathlib import Path

TARGET = Path("team/S13-STATEUPD-AUDIT")
BASE = ("agentmemory", "Hindsight", "Mem0", "MemPalace")
PRIOR = {
    "S11": Path("team/S11-LAYER-HIST/verdict.json"),
    "S7": Path("team/S7-STATELAYER/verdict.json"),
    "S10": Path("team/S10-PI-LCM-HIST/verdict.json"),
}
ALIASES = {
    "agentmemory": ("agentmemory", "agent memory"),
    "Hindsight": ("hindsight",),
    "Mem0": ("mem0", "mem 0"),
    "MemPalace": ("mempalace", "mem palace"),
}
TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".rst"}
GENERIC = {
    "external", "card", "cards", "memory", "mechanism", "mechanisms",
    "state", "update", "updates", "supersession", "audit", "evidence",
    "availability", "licence", "license", "licensing", "summary", "sources",
    "references", "comparison", "comparisons", "candidates", "candidate",
    "notes", "limitations", "conclusion", "conclusions", "disposition",
    "fleet", "measurements", "measurement", "model", "models", "overview",
    "background", "research", "protection", "experiments", "experiment",
    "status", "decision", "design", "scope", "links", "source", "prior",
    "existing", "local", "read", "reads", "and", "of", "the", "for",
    "before", "after", "what", "how", "not", "unknown", "product", "project",
    "system", "systems", "tool", "tools", "graph", "bitemporal", "temporal",
    "open", "closed", "available", "access", "introduction", "findings",
    "takeaways", "name", "cost", "result", "results", "limitations",
}
ACRONYMS = {
    "API", "APIs", "LLM", "LLMs", "MIT", "BSD", "GPL", "AGPL", "LGPL",
    "MPL", "JSON", "SQL", "HTTP", "HTTPS", "URL", "URLs", "README",
    "TODO", "NOTE", "G2", "Q4", "RAG", "SDK", "CRUD", "ADD", "UPDATE",
    "DELETE", "NONE", "NOOP", "DOI", "CPU", "GPU", "RAM", "UTC",
}


class InputError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError(message)


def normalized(text):
    text = text.replace("\u2019", "'").replace("\u2011", "-")
    text = re.sub(r"[*_`]", "", text)
    return re.sub(r"(\d)\s*/\s*(\d)", r"\1/\2", text)


def has(pattern, text):
    return re.search(pattern, normalized(text), re.I | re.S) is not None


def names_pattern(name):
    variants = ALIASES.get(name, (name,))
    return r"(?<![\w])(?:" + "|".join(
        re.escape(v).replace(r"\ ", r"[\s_-]*") for v in variants
    ) + r")(?![\w])"


def mentions(name, text):
    return has(names_pattern(name), text)


def read_text(path):
    if not path.is_file():
        raise InputError("not a regular file: " + str(path))
    if path.stat().st_size > 4_000_000:
        raise InputError("text input exceeds 4 MB: " + str(path))
    return path.read_text(encoding="utf-8")


def strip_inert(text):
    """Examples, HTML comments, and quoted material are not audit assertions."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            if fence is None:
                fence = match.group(1)[0]
            elif match.group(1)[0] == fence:
                fence = None
            continue
        if fence or re.match(r"^\s*>", line):
            continue
        lines.append(line)
    return "\n".join(lines)


def headings(text):
    lines = text.splitlines()
    result = []
    for i, line in enumerate(lines):
        match = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            result.append((i, len(match.group(1)), normalized(match.group(2))))
        elif (i + 1 < len(lines) and line.strip()
              and re.fullmatch(r"\s*(?:={3,}|-{3,})\s*", lines[i + 1])):
            result.append((i, 1 if "=" in lines[i + 1] else 2,
                           normalized(line.strip())))
    sections = []
    for index, (start, level, title) in enumerate(result):
        end = len(lines)
        for next_start, next_level, _ in result[index + 1:]:
            if next_level <= level:
                end = next_start
                break
        sections.append((title, "\n".join(lines[start + 1:end]), level))
    return sections


def candidate_label(value):
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = normalized(value).strip(" #:-|")
    value = re.sub(
        r"^(?:external\s+)?(?:candidate|mechanism|project|product|system)"
        r"(?:\s+name)?\s*:\s*", "", value, flags=re.I)
    value = re.sub(r"^\d+[.)]\s*", "", value)
    value = re.split(r"\s+[—–|]\s*|\s+-\s+|:\s+|\s+\(", value)[0]
    value = re.sub(r"\s+(?:card|audit|overview)$", "", value, flags=re.I)
    for name in BASE:
        if mentions(name, value):
            return name
    words = re.findall(r"[A-Za-z][A-Za-z0-9_.+-]*", value)
    if not words or len(words) > 4:
        return None
    if all(w.lower() in GENERIC or w in ACRONYMS for w in words):
        return None
    if any(w.lower() in {
        "is", "are", "was", "were", "has", "have", "should", "must",
        "testing", "tested", "why", "does", "can", "could",
    } for w in words):
        return None
    if any(w.lower() in GENERIC for w in words) and len(words) > 1:
        return None
    return " ".join(words)


def discover_candidates(cards):
    """Read card identities, named product headings, lists, and name columns.

    Ordinary CamelCase product mentions also count. A card that exposes no
    identity is not silently ignored: the caller reports CARD_INVENTORY.
    """
    inventory = {name: set() for name in BASE}
    unresolved = []
    for path, text in cards:
        found = set()
        for name in BASE:
            if mentions(name, text + " " + path.stem):
                found.add(name)
        stem = re.sub(r"^EXTERNAL-", "", path.stem, flags=re.I)
        label = candidate_label(stem.replace("_", " "))
        if label:
            found.add(label)
        for title, _, level in headings(text):
            if level <= 3:
                label = candidate_label(title)
                if label:
                    found.add(label)
        for line in text.splitlines():
            match = re.match(
                r"^\s*(?:[-+*]\s*)?(?:candidate|mechanism|project|product|system)"
                r"(?:\s+name)?\s*:\s*(.+)", normalized(line), re.I)
            if not match:
                match = re.match(r"^\s*[-+*]\s+\*\*([^*]+)\*\*\s*[:—–-]", line)
            if match:
                label = candidate_label(match.group(1))
                if label:
                    found.add(label)

        table_column = None
        for line in text.splitlines():
            if "|" not in line:
                table_column = None
                continue
            cells = [normalized(c).strip() for c in line.strip().strip("|").split("|")]
            indexes = [
                i for i, c in enumerate(cells)
                if c.lower() in {"candidate", "mechanism", "project", "product", "name"}
            ]
            if indexes:
                table_column = indexes[0]
            elif table_column is not None and table_column < len(cells):
                label = candidate_label(cells[table_column])
                if label:
                    found.add(label)

        # CamelCase catches additional products mentioned in prose, rather than
        # assuming that each card discusses only its title product.
        prose = re.sub(r"https?://\S+", "", text)
        for word in re.findall(r"\b[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]*)+\b", prose):
            if word not in ACRONYMS:
                label = candidate_label(word)
                if label:
                    found.add(label)
        if not found:
            unresolved.append(path.name)
        for name in found:
            canonical = next(
                (n for n in inventory if n.casefold() == name.casefold()), name)
            inventory.setdefault(canonical, set()).add(path.name)
    return inventory, unresolved


def paragraphs(text):
    return [normalized(p).strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def evidence_block(text, run):
    token = rf"\b{run}(?:-|/|\b)"
    blocks = []
    for paragraph in paragraphs(text):
        if not has(token, paragraph):
            continue
        other_runs = [
            other for other in PRIOR if other != run
            and has(rf"\b{other}(?:-|/|\b)", paragraph)
        ]
        if other_runs:
            blocks.extend(line for line in paragraph.splitlines() if has(token, line))
        else:
            blocks.append(paragraph)
    for title, body, _ in headings(text):
        if has(token, title) and not any(
            has(rf"\b{other}(?:-|/|\b)", body) for other in PRIOR if other != run
        ):
            blocks.append(title + "\n" + body)
    return "\n".join(blocks)


def numeric_role(text, label, ratio):
    # A role's first subsequent ratio must be the required one. This rejects
    # reversed native/layer assignments despite all numbers being present.
    for match in re.finditer(label, normalized(text), re.I):
        tail = normalized(text)[match.end():match.end() + 100]
        tail = re.split(r"[;\n]", tail)[0]
        first = re.search(r"\b\d+/\d+\b", tail)
        if first and first.group() == ratio:
            return True
    return has(r"\b" + re.escape(ratio) + r"\b\s*(?:\([^)]{0,12})?"
               + r"\s*" + label, text)


def select_receipt(root, explicit, add):
    folder = root / TARGET
    if not folder.is_dir():
        add("RECEIPT_MISSING", str(TARGET) + " does not exist")
        return None
    documents = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            documents.append((path, strip_inert(read_text(path))))
    substantive = [
        (path, text) for path, text in documents
        if sum(mentions(name, text) for name in BASE) >= 2
        or has(r"\bdisposition\b", text)
    ]
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = root / path
        path = path.resolve()
        if path.parent != folder.resolve():
            add("RECEIPT_LOCATION", "receipt must be in " + str(TARGET))
            return None
        if not path.is_file():
            add("RECEIPT_MISSING", str(path))
            return None
        if any(p.resolve() != path for p, _ in substantive):
            add("RECEIPT_MULTIPLE", "more than one substantive audit receipt")
        return strip_inert(read_text(path))
    choices = substantive if substantive else documents
    if not choices:
        add("RECEIPT_MISSING", "expected one readable audit receipt in " + str(TARGET))
        return None
    if len(choices) != 1:
        add("RECEIPT_MULTIPLE", "cannot identify one receipt: "
            + ", ".join(p.name for p, _ in choices))
        return None
    return choices[0][1]


def audit(root, receipt=None):
    findings = []

    def add(name, detail):
        item = (name, detail)
        if item not in findings:
            findings.append(item)

    text = select_receipt(root, receipt, add)
    cards = []
    for path in sorted((root / "team").glob("EXTERNAL-*.md")):
        cards.append((path, strip_inert(read_text(path))))
    if not cards:
        add("EXTERNAL_CARDS_MISSING", "no team/EXTERNAL-*.md cards found")
    inventory, unresolved = discover_candidates(cards)
    for card in unresolved:
        add("CARD_INVENTORY", "cannot establish candidate identities from " + card)

    for run, relative in PRIOR.items():
        path = root / relative
        if not path.is_file():
            add("PRIOR_SOURCE_MISSING", str(relative))
            continue
        try:
            value = json.loads(read_text(path))
            if not isinstance(value, (dict, list)) or not value:
                add("PRIOR_SOURCE_INVALID", str(relative) + " is not a nonempty record")
        except (ValueError, UnicodeError):
            add("PRIOR_SOURCE_INVALID", str(relative) + " is not valid UTF-8 JSON")

    if text is None:
        return findings
    text = normalized(text)
    if len(re.findall(r"\w+", text)) < 100:
        add("RECEIPT_SUBSTANCE", "receipt is too short to establish the required audit")

    for path, _ in cards:
        if path.name.casefold() not in text.casefold():
            add("CARD_COVERAGE", "receipt does not identify reviewed card " + path.name)

    sections = headings(text)
    mechanism_sections = {}
    for name in sorted(inventory, key=str.casefold):
        matches = [
            (title, body) for title, body, _ in sections
            if mentions(name, title)
            and not has(r"\b(?:disposition|decision|recommendation|bibliography|sources)\b",
                        title)
        ]
        if not matches:
            add("CANDIDATE_SECTION", "missing mechanism section: " + name)
            continue
        # Nested explanatory headings mentioning the same product are permitted.
        title, body = max(matches, key=lambda pair: len(pair[1]))
        if any(mentions(other, title) for other in inventory if other != name):
            add("CANDIDATE_SECTION", "shared rather than per-mechanism section: " + title)
        mechanism_sections[name] = body

        model_blocks = [
            p for p in paragraphs(body)
            if has(r"\b(?:update|updat\w+|supersed\w*|supersession|replacement|"
                   r"mutation|consolidat\w*)\b", p)
            and not has(r"^(?:fleet|licen[cs]e|availability)\s*:", p)
        ]
        model = "\n".join(model_blocks)
        explanatory = (
            len(re.findall(r"\w+", model)) >= 12
            and has(r"\b(?:replac\w*|overwrit\w*|append\w*|retain\w*|"
                    r"delet\w*|invalidat\w*|version\w*|merg\w*|correct\w*|"
                    r"upsert\w*|expire\w*|retract\w*|old|previous|prior|"
                    r"unknown|undocumented|unverified|not established)\b", model)
        )
        if not explanatory:
            add("UPDATE_MODEL", name + ": no explained update/supersession model")
        if name == "MemPalace" and not (
            has(r"\bbitemporal\b", model) and has(r"\bgraph\b", model)
        ):
            add("BITEMPORAL_GRAPH", "MemPalace must be audited as a bitemporal graph")

        availability = [
            p for p in paragraphs(body)
            if has(r"\b(?:availability|available|access|install\w*|hosted|"
                   r"self-host\w*|download\w*|repository|source code|service|SDK)\b", p)
        ]
        if not any(
            has(r"\b(?:public|open.source|local|hosted|self.host\w*|"
                r"commercial|restricted|private|unavailable|available|"
                r"unknown|unverified|not established|repository|SDK)\b", p)
            and len(re.findall(r"\w+", p)) >= 5 for p in availability
        ):
            add("AVAILABILITY", name + ": availability/access is not characterized")

        license_blocks = [
            p for p in paragraphs(body)
            if has(r"\blicen[cs](?:e|ed|ing)\b", p)
        ]
        if not any(has(
            r"\b(?:MIT|Apache|BSD|[AL]?GPL|MPL|ISC|proprietary|commercial|"
            r"source.available|public.domain|unknown|unverified|unspecified|"
            r"unconfirmed|unclear|not established|not stated|not found|"
            r"not documented|no licen[cs]e)\b", p) for p in license_blocks):
            add("LICENCE", name + ": licence or explicit licence uncertainty is missing")

        fleet_blocks = [
            p for p in paragraphs(body)
            if has(r"\b(?:fleet|our|local|team/|S\d+-)\b", p)
            and has(r"\b(?:measur\w*|evaluat\w*|test\w*|benchmark\w*|evidence|"
                    r"run|results|unmeasured)\b", p)
        ]
        no_direct = any(has(
            r"\b(?:no|without)\b[^.!?\n]{0,90}"
            r"\b(?:fleet|local|direct|mechanism.specific)\b[^.!?\n]{0,60}"
            r"\b(?:measurement|measurements|test|tests|evaluation|evidence|run)\b"
            r"|\b(?:not|never)\s+(?:yet\s+|been\s+|directly\s+)*"
            r"(?:measured|tested|evaluated|benchmarked)\b"
            r"|\b(?:unmeasured|no direct measurement|none measured)\b",
            p) for p in fleet_blocks)
        measured = any(
            has(r"\b\d+(?:/\d+|(?:\.\d+)?%)", p)
            and has(r"team/[A-Za-z0-9_./-]+", p)
            and has(r"\b(?:measured|observed|evaluated|tested|benchmark)\b", p)
            for p in fleet_blocks
        )
        if not fleet_blocks or not (no_direct or measured):
            add("FLEET_EVIDENCE", name + ": distinguish fleet measurements from "
                "external claims, or explicitly say none exist")

        if measured and not no_direct:
            cited_paths = re.findall(
                r"team/[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+\.(?:json|md|txt|csv)",
                "\n".join(fleet_blocks))
            other_sources = [
                p for p in cited_paths
                if p not in {str(v) for v in PRIOR.values()}
            ]
            if not other_sources:
                add("EVIDENCE_ATTRIBUTION", name + ": the three prior native/layer "
                    "runs do not establish an external mechanism's performance")
            for relative in other_sources:
                source = (root / relative).resolve()
                if not source.is_relative_to(root.resolve()) or not source.is_file():
                    add("EVIDENCE_SOURCE", name + ": missing local measurement " + relative)

        if inventory[name] and not any(
            card.casefold() in body.casefold() for card in inventory[name]
        ):
            add("MECHANISM_SOURCE", name + ": section does not identify a relevant card")

    # These are source facts supplied by the queue, not inferred from a builder.
    s11 = evidence_block(text, "S11")
    s7 = evidence_block(text, "S7")
    s10 = evidence_block(text, "S10")
    for run, block in (("S11", s11), ("S7", s7), ("S10", s10)):
        if str(PRIOR[run]).casefold() not in text.casefold():
            add("PRIOR_CITATION", "missing exact local source " + str(PRIOR[run]))
        if not block:
            add("PRIOR_" + run, "missing prior measurement account")
    if not (
        numeric_role(s11, r"\bnative\b", "22/33")
        and numeric_role(s11, r"\b(?:tested\s+)?layer\b", "33/33")
        and has(r"\b0/13\b.{0,35}\bmiss\w*|\bmiss\w*.{0,35}\b0/13\b", s11)
        and has(r"\bfalse\s+(?:replacement|replacements|replace\w*)\b", s11)
        and has(r"\b(?:worsen\w*|harm\w*|worse|degrad\w*|increas\w*)\b", s11)
    ):
        add("PRIOR_S11", "must explain native 22/33 -> layer 33/33 false replacement, "
            "0/13 missed, and worsening")
    if not (
        has(r"\bcontrolled\b", s7) and has(r"\b0/32\b", s7)
        and (has(r"\bboth\s+(?:arms|conditions)\b", s7)
             or len(re.findall(r"\b0/32\b", s7)) >= 2)
    ):
        add("PRIOR_S7", "must report controlled 0/32 in both arms")
    if not (
        numeric_role(s10, r"\bnative\b", "22/33")
        and has(r"\b0/13\b.{0,35}\bmiss\w*|\bmiss\w*.{0,35}\b0/13\b", s10)
    ):
        add("PRIOR_S10", "must report native 22/33 and 0/13 missed")

    retirement = has(
        r"\b(?:retire[ds]?|reject(?:ed)?|abandon(?:ed)?)\b[^.!?\n]{0,100}"
        r"\bkey[- ]equality\b|\bkey[- ]equality\b[^.!?\n]{0,100}"
        r"\b(?:retire[ds]?|reject(?:ed)?|abandon(?:ed)?|closed)\b", text)
    contrary_retirement = has(
        r"\b(?:not|never)\s+(?:be\s+|been\s+)?(?:retire[ds]?|reject(?:ed)?)"
        r"[^.!?\n]{0,80}\bkey[- ]equality\b|"
        r"\bkey[- ]equality\b[^.!?\n]{0,60}\bnot\s+retired\b|"
        r"\b(?:keep|retain|continue)\b[^.!?\n]{0,50}\bkey[- ]equality\b"
        r"[^.!?\n]{0,40}\b(?:protection|layer|active)\b", text)
    if not retirement or contrary_retirement:
        add("KEY_EQUALITY_RETIREMENT", "explicitly retire the tested key-equality protection")

    if not (
        has(r"\b(?:design|audit)[- /]*(?:only)\b", text)
        and has(r"\b(?:no|without)\s+(?:new\s+|experimental\s+)?"
                r"(?:runs?|execution|experiments?)\b|"
                r"\b(?:did not|have not|has not)\s+(?:run|execute)\b", text)
        and has(r"\bno\s+composite\s+build\b|\b(?:did not|have not)\s+"
                r"(?:build|construct)\s+(?:a\s+)?composite\b", text)
    ):
        add("DESIGN_ONLY", "state audit/design only, no run, and no composite build")
    if not (has(r"\$\s*0(?:\.00)?\b|\bzero\s+(?:cost|spend)\b", text)
            and has(r"\blocal[- ]reads?\b|\bread\s+(?:only\s+)?local\b", text)):
        add("ZERO_COST_LOCAL", "state $0 and local reads")

    for sentence in re.split(r"(?<=[.!?])\s+|\n", text):
        historical = has(r"\bS(?:7|10|11)(?:-|\b)", sentence)
        negated = has(r"\b(?:no|not|never|without)\b", sentence)
        prospective = has(r"\b(?:would|could|future|proposed|hypothetical|if approved)\b",
                          sentence)
        action = has(
            r"\b(?:we|this audit|this work|this receipt|I)\s+"
            r"(?:also\s+|have\s+)?(?:ran|executed|launched|benchmarked|"
            r"deployed|trained|built|constructed|spent|paid)\b|"
            r"\b(?:experiment|benchmark|composite|protection run)\s+"
            r"(?:was|has been)\s+(?:run|executed|built|launched|completed)\b",
            sentence)
        if action and not negated and not prospective and not historical:
            add("EXECUTION_CLAIM", "receipt claims execution/build/spend: " + sentence[:180])
        for amount in re.findall(r"\$\s*(\d[\d,]*(?:\.\d+)?)", sentence):
            if float(amount.replace(",", "")) > 0 and has(
                r"\b(?:spent|paid|cost|spend|charged|incurred)\b", sentence
            ) and not prospective and not historical and not negated:
                add("NONZERO_COST", "nonzero expenditure: " + sentence[:180])

    if not (
        has(r"\b(?:no|not|first)\b[^.!?\n]{0,100}\b(?:prior|previous|earlier|existing)"
            r"\b[^.!?\n]{0,100}\b(?:external|state.update)\b[^.!?\n]{0,70}\baudit\b"
            r"|\bno\b[^.!?\n]{0,70}\baudit\b[^.!?\n]{0,70}\b"
            r"(?:existed|previously|before|prior)\b", text)
        and has(r"\b(?:no new|not new|no fresh)\s+(?:empirical\s+)?"
                r"(?:measurements?|results?|runs?|evidence)\b|"
                r"\bprior measurements?\s+(?:only|are reused)\b", text)
    ):
        add("REMEASUREMENT_BOUNDARY", "identify the previously unaudited external "
            "mechanisms and distinguish this audit from new measurement")

    if not (
        has(r"\bQ4\b", text) and has(r"\bG2\b", text)
        and has(r"\bsupersession\b", text)
        and has(r"\b(?:R-PF\s+)?Decision\s+Gate\s+F\b", text)
        and has(r"\bexternal\s+state[- ]update\s+mechanisms?\b", text)
    ):
        add("DECISION_CONTEXT", "connect Q4's external state-update audit to "
            "G2 supersession and Decision Gate F")

    decisions = [
        (title, body, level) for title, body, level in sections
        if has(r"\b(?:disposition|final decision|decision gate outcome)\b", title)
    ]
    if len(decisions) != 1:
        add("ONE_DISPOSITION", "expected exactly one final disposition section")
        return findings
    title, decision, level = decisions[0]
    decision_text = title + "\n" + decision
    position = next(i for i, section in enumerate(sections) if section == decisions[0])
    if any(
        other_level <= level
        and not has(r"\b(?:references|sources|bibliography)\b", other_title)
        for other_title, _, other_level in sections[position + 1:]
    ):
        add("FINAL_DISPOSITION", "disposition must finish the substantive audit")

    none = has(
        r"\bnone\b[^.!?\n]{0,100}\b(?:yet|worth|warrant\w*|qualif\w*|ready)\b|"
        r"\bno\s+(?:single\s+)?mechanism\b[^.!?\n]{0,70}"
        r"\b(?:worth|warrant\w*|ready|qualif\w*)\b", decision_text)
    closed = has(r"\bclass\b[^.!?\n]{0,45}\b(?:stays|remains|is|keep\w*)\s+closed\b",
                 decision_text)
    prereg = has(r"\bpre[- ]?register(?:ed|ing|ation)?\b", decision_text)
    selected = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n", decision_text):
        if has(r"\b(?:not worth|not selected|not recommended|not yet|"
               r"do not recommend|none|no mechanism)\b", sentence):
            continue
        if has(r"\b(?:select(?:ed)?|recommend(?:ed)?|worth|choose|chosen|"
               r"warrants?|qualifies)\b", sentence):
            selected.extend(n for n in inventory if mentions(n, sentence))
    selected = sorted(set(selected))
    if none:
        if not closed or selected:
            add("ONE_DISPOSITION", "none-yet disposition must keep the class closed "
                "and must not also select a mechanism")
        if not has(r"\b(?:because|insufficient|lack\w*|uncertain\w*|unverified|"
                   r"unmeasured|gap|cannot|does not establish)\b", decision_text):
            add("DISPOSITION_REASON", "explain why no mechanism yet warrants an experiment")
    elif len(selected) != 1 or not prereg or not has(
        r"\bprotection\s+experiment\b", decision_text
    ):
        add("ONE_DISPOSITION", "select exactly one named mechanism as worth a "
            "pre-registered protection experiment, or explicitly choose none yet")
    else:
        selected_name = selected[0]
        rationale = decision_text + "\n" + mechanism_sections.get(selected_name, "")
        if not (
            has(r"\bkey[- ]equality\b", rationale)
            and has(r"\b(?:different|unlike|instead|rather than|distinct|beyond)\b", rationale)
            and has(r"\b(?:update|supersession|supersed\w*|version\w*|"
                    r"invalidat\w*|temporal|conflict|retract\w*)\b", decision_text)
            and has(r"\b(?:would|could|hypothes\w*|test whether|test if|prospective)\b",
                    decision_text)
        ):
            add("SUBSTANTIVELY_DIFFERENT", "selected mechanism needs a prospective "
                "protection test rationale distinct from tested key equality")
        if has(r"\b(?:same|identical|unchanged)\b[^.!?\n]{0,60}"
               r"\bkey[- ]equality\b", decision_text):
            add("SUBSTANTIVELY_DIFFERENT", "renaming the same key-equality test is not "
                "a substantively different experiment")

    return findings


def report(root, receipt=None, stream=None):
    if stream is None:
        stream = sys.stdout
    try:
        findings = audit(Path(root).resolve(), receipt)
    except (OSError, UnicodeError, InputError, ValueError) as exc:
        findings = [("INPUT_ERROR", str(exc))]
    except Exception as exc:
        findings = [("INTERNAL_ERROR", type(exc).__name__ + ": " + str(exc))]
    if findings:
        for name, detail in findings:
            detail = " ".join(str(detail).split())
            print("FINDING[S13-2:" + name + "] " + detail, file=stream)
        return 1
    print("PASS[S13-2]", file=stream)
    return 0


def fixture():
    files = {}
    for path in PRIOR.values():
        files[str(path)] = json.dumps({"source": str(path), "fixture": True})
    files[str(PRIOR["S11"])] = json.dumps({
        "native_false_replacement": "22/33",
        "layer_false_replacement": "33/33", "missed": "0/13",
    })
    files[str(PRIOR["S7"])] = json.dumps({"control": "0/32", "layer": "0/32"})
    files[str(PRIOR["S10"])] = json.dumps({
        "native_false_replacement": "22/33", "missed": "0/13",
    })
    models = {
        "agentmemory": "Update model: Records can be replaced or retained; the card "
                       "does not establish how a conflicting new fact supersedes "
                       "an old record.",
        "Hindsight": "Update model: Retained facts can be consolidated; whether a "
                     "correction invalidates the old fact is not established "
                     "by the available card.",
        "Mem0": "Update model: An update may replace an existing memory record; "
                "the card leaves conflict resolution and retention of previous "
                "values unverified.",
        "MemPalace": "Update model: The bitemporal graph retains versions of old "
                     "and new facts; valid time and recorded time distinguish "
                     "when a fact holds from when it was recorded.",
    }
    parts = [
        "# External state-update audit",
        "Scope: DESIGN/AUDIT ONLY. No run. No composite build. "
        "Cost: $0, local reads only.",
        "ANSWER Q4's named next step is to audit external state-update mechanisms "
        "and existing evidence before proposing a substantively different "
        "protection experiment. This advances G2 supersession and "
        "R-PF Decision Gate F.",
        "No prior external state-update mechanism audit existed. "
        "This receipt adds no new measurements.",
        "The tested key-equality protection is retired because its measured "
        "effect worsens false replacement.",
        "## Prior measurement",
        "team/S11-LAYER-HIST/verdict.json: native 22/33 false replacement; "
        "tested layer 33/33 false replacement; 0/13 missed. The layer worsens it.",
        "team/S7-STATELAYER/verdict.json: controlled 0/32 in both arms.",
        "team/S10-PI-LCM-HIST/verdict.json: native 22/33 false replacement; "
        "0/13 missed.",
    ]
    for name in BASE:
        card = "EXTERNAL-" + name + ".md"
        files["team/" + card] = (
            "# " + name + "\n\n" + models[name] + "\n\n"
            "Availability: public repository; local source access is possible.\n\n"
            "Licence: unknown; the card does not establish redistribution terms.\n\n"
            "Fleet evidence: no direct fleet measurements of this mechanism.\n"
        )
        parts.extend([
            "## " + name,
            "Source: team/" + card + ".",
            models[name],
            "Availability: public repository; local source access is possible.",
            "Licence: unknown; terms require verification before any experiment.",
            "Fleet evidence: no direct fleet measurements of this mechanism. "
            "The prior native/layer runs above are not evaluations of this product; "
            "external descriptions are not fleet results.",
        ])
    parts.extend([
        "## Disposition",
        "None yet is worth a pre-registered protection experiment. "
        "The class stays closed because direct mechanism-specific fleet "
        "evidence is insufficient and conflict-handling guarantees are unverified.",
    ])
    files[str(TARGET / "receipt.md")] = "\n\n".join(parts) + "\n"
    return files


def selftest():
    receipt_key = str(TARGET / "receipt.md")
    good = fixture()
    cases = []

    def changed(label, old, new, finding):
        data = copy.deepcopy(good)
        if old not in data[receipt_key]:
            raise InputError("selftest mutation not applied: " + label)
        data[receipt_key] = data[receipt_key].replace(old, new, 1)
        cases.append((label, data, finding))

    missing = copy.deepcopy(good)
    del missing[receipt_key]
    cases.append(("missing receipt", missing, "RECEIPT_MISSING"))

    missing = copy.deepcopy(good)
    del missing[str(PRIOR["S10"])]
    cases.append(("missing declared evidence", missing, "PRIOR_SOURCE_MISSING"))

    text = good[receipt_key]
    start = text.index("## Hindsight")
    end = text.index("## Mem0", start)
    missing = copy.deepcopy(good)
    missing[receipt_key] = text[:start] + text[end:]
    cases.append(("missing candidate", missing, "CANDIDATE_SECTION"))

    extra = copy.deepcopy(good)
    extra["team/EXTERNAL-ChronicleStore.md"] = (
        "# ChronicleStore\n\nUpdate model: append versions and invalidate old facts.\n"
    )
    cases.append(("additional card candidate", extra, "CANDIDATE_SECTION"))

    inline = copy.deepcopy(good)
    inline["team/EXTERNAL-Mem0.md"] += (
        "\nChronicleStore also appends state updates and retains old versions.\n"
    )
    cases.append(("additional inline candidate", inline, "CANDIDATE_SECTION"))

    changed("model missing",
            "Update model: Records can be replaced or retained; the card "
            "does not establish how a conflicting new fact supersedes "
            "an old record.",
            "Description: a memory package.", "UPDATE_MODEL")
    changed("availability missing",
            "Availability: public repository; local source access is possible.",
            "Distribution details omitted.", "AVAILABILITY")
    changed("licence missing",
            "Licence: unknown; terms require verification before any experiment.",
            "Legal details omitted.", "LICENCE")
    changed("fleet evidence missing",
            "Fleet evidence: no direct fleet measurements of this mechanism. "
            "The prior native/layer runs above are not evaluations of this product; "
            "external descriptions are not fleet results.",
            "Upstream users like this product.", "FLEET_EVIDENCE")
    changed("borrowed fleet result",
            "Fleet evidence: no direct fleet measurements of this mechanism. "
            "The prior native/layer runs above are not evaluations of this product; "
            "external descriptions are not fleet results.",
            "Fleet measured this mechanism at 33/33 in "
            "team/S11-LAYER-HIST/verdict.json.", "EVIDENCE_ATTRIBUTION")
    changed("graph distinction absent",
            "The bitemporal graph retains versions of old "
            "and new facts; valid time and recorded time distinguish "
            "when a fact holds from when it was recorded.",
            "The store replaces the old fact with a new fact during an update.",
            "BITEMPORAL_GRAPH")
    changed("wrong harmful result", "tested layer 33/33", "tested layer 22/33",
            "PRIOR_S11")
    changed("reversed roles",
            "native 22/33 false replacement; tested layer 33/33",
            "native 33/33 false replacement; tested layer 22/33", "PRIOR_S11")
    changed("wrong controlled result", "controlled 0/32", "controlled 1/32", "PRIOR_S7")
    changed("wrong native result",
            "team/S10-PI-LCM-HIST/verdict.json: native 22/33",
            "team/S10-PI-LCM-HIST/verdict.json: native 33/33", "PRIOR_S10")
    changed("retirement negated",
            "The tested key-equality protection is retired",
            "The tested key-equality protection is not retired",
            "KEY_EQUALITY_RETIREMENT")
    changed("prior boundary missing",
            "No prior external state-update mechanism audit existed.",
            "The prior audit situation is omitted.", "REMEASUREMENT_BOUNDARY")
    changed("local budget absent", "Cost: $0, local reads only.",
            "The budget is unspecified.", "ZERO_COST_LOCAL")
    changed("execution despite disclaimer", "No composite build.",
            "No composite build. We ran a protection experiment.",
            "EXECUTION_CLAIM")
    changed("composite despite disclaimer", "No composite build.",
            "No composite build. We built a composite protection layer.",
            "EXECUTION_CLAIM")
    changed("nonzero expenditure", "Cost: $0, local reads only.",
            "Cost: $0, local reads only. Actual cost: $9.", "NONZERO_COST")
    changed("none but reopened", "The class stays closed", "The class reopens",
            "ONE_DISPOSITION")
    changed("multiple selected mechanisms",
            "None yet is worth a pre-registered protection experiment. "
            "The class stays closed because direct mechanism-specific fleet "
            "evidence is insufficient and conflict-handling guarantees are unverified.",
            "Select Hindsight and Mem0 as worth a pre-registered protection "
            "experiment because they could test update conflicts.",
            "ONE_DISPOSITION")
    changed("renamed key equality",
            "None yet is worth a pre-registered protection experiment. "
            "The class stays closed because direct mechanism-specific fleet "
            "evidence is insufficient and conflict-handling guarantees are unverified.",
            "Select Mem0 as worth a pre-registered protection experiment. "
            "It would test the same key-equality protection with unchanged updates.",
            "SUBSTANTIVELY_DIFFERENT")

    duplicate = copy.deepcopy(good)
    duplicate[receipt_key] += "\n## Disposition\nSelect Mem0.\n"
    cases.append(("two dispositions", duplicate, "ONE_DISPOSITION"))

    duplicate = copy.deepcopy(good)
    duplicate[str(TARGET / "another.md")] = duplicate[receipt_key]
    cases.append(("two receipts", duplicate, "RECEIPT_MULTIPLE"))

    inert = copy.deepcopy(good)
    inert[receipt_key] = "<!--\n" + inert[receipt_key] + "\n-->\n# Empty audit\n"
    cases.append(("comment-only compliance", inert, "CANDIDATE_SECTION"))

    selected_good = copy.deepcopy(good)
    selected_good[receipt_key] = selected_good[receipt_key].replace(
        "None yet is worth a pre-registered protection experiment. "
        "The class stays closed because direct mechanism-specific fleet "
        "evidence is insufficient and conflict-handling guarantees are unverified.",
        "Select MemPalace as the single mechanism worth a pre-registered "
        "protection experiment. Unlike the retired key-equality layer, the "
        "prospective test would ask whether temporal invalidation preserves "
        "the correct current fact after conflicting updates. This is a "
        "hypothesis, not measured protection; licence verification and "
        "pre-registration would precede any future run."
    )

    tests = [
        ("minimal conforming, none yet", good, None),
        ("conforming, one prospective mechanism", selected_good, None),
    ] + cases
    failures = []
    for label, files, expected in tests:
        with tempfile.TemporaryDirectory(prefix="s13-2-gate-selftest-") as temporary:
            root = Path(temporary)
            for relative, content in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            output = io.StringIO()
            code = report(root, stream=output)
            emitted = output.getvalue()
            if expected is None:
                correct = code == 0 and "FINDING[" not in emitted
            else:
                correct = (code == 1
                           and "FINDING[S13-2:" + expected + "]" in emitted
                           and "Traceback" not in emitted)
            if not correct:
                failures.append(label + ": expected "
                                + (expected or "clean acceptance")
                                + "; got " + emitted.strip())
    if failures:
        for failure in failures:
            print("FINDING[S13-2:SELFTEST] " + " ".join(failure.split()))
        return 1
    print("PASS[S13-2:SELFTEST] accepted both conforming fixtures; rejected "
          + str(len(cases)) + " independent non-conforming fixtures "
          "with their expected named findings")
    return 0


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[2],
                        help="repository root (default: inferred from check.py)")
    parser.add_argument("--receipt", help="receipt path, relative to repository root")
    parser.add_argument("--selftest", action="store_true",
                        help="use temporary synthetic fixtures only")
    try:
        args = parser.parse_args(argv)
        if args.selftest:
            return selftest()
        return report(args.root, args.receipt)
    except InputError as exc:
        print("FINDING[S13-2:ARGUMENT_OR_SELFTEST] " + " ".join(str(exc).split()))
        return 1
    except (OSError, UnicodeError, ValueError) as exc:
        print("FINDING[S13-2:INPUT_ERROR] " + " ".join(str(exc).split()))
        return 1
    except Exception as exc:
        print("FINDING[S13-2:INTERNAL_ERROR] "
              + type(exc).__name__ + ": " + " ".join(str(exc).split()))
        return 1


if __name__ == "__main__":
    sys.exit(main())