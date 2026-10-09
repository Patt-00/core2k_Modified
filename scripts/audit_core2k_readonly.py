#!/usr/bin/env python3
"""Read-only Core 2000 audit. Standard library only; no collection write actions.

Only local report files are written. This is not the vocabulary updater.
"""

import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import re
import unicodedata
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ENDPOINT = "http://127.0.0.1:8765"
DECK = MODEL = "Core 2000"
EXPRESSION = "Vocabulary-Kanji"
READING = "Vocabulary-Kana"
JAPANESE = "Expression"
ENGLISH = "Sentence-English"
START = "<!-- CUSTOM-VOCAB-NOTE-START -->"
END = "<!-- CUSTOM-VOCAB-NOTE-END -->"
READ_ACTIONS = frozenset({
    "version", "deckNames", "findNotes", "notesInfo", "cardsInfo", "modelFieldNames"
})
HEADINGS = re.compile(
    r"(?<!\w)(Nuance|Logic|Meaning|Difference|Filipino|Kanji(?:\s+breakdown)?|My\s+sentence)\s*[:：]",
    re.IGNORECASE,
)
JAPANESE_CHARS = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
SIMPLE_TAGS = {"br", "div", "p", "b", "strong", "i", "em", "u", "span"}
BLOCK_TAGS = {"br", "div", "p", "li", "tr", "pre", "section", "h1", "h2", "h3"}


class AuditError(RuntimeError):
    pass


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise AuditError("HTTP redirect refused; this audit only contacts local loopback")


def anki_request(action, **params):
    """Fail closed before sending any action outside the read-only allowlist."""
    if action not in READ_ACTIONS:
        raise AuditError("Action is not on the read-only allowlist")
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), NoRedirects()
    )
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with opener.open(req, timeout=20) as response:
            result = json.load(response)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        raise AuditError(f"Local AnkiConnect request {action} failed: {exc}") from exc
    if not isinstance(result, dict) or "error" not in result or "result" not in result:
        raise AuditError("Unexpected AnkiConnect response; no audit will be finalized")
    if result["error"] is not None:
        raise AuditError(f"AnkiConnect {action}: {result['error']}")
    return result["result"]


class FieldText(HTMLParser):
    """Interpret HTML for analysis without rewriting the stored field value."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.tags = set()
        self.suspicious_markup = False
        self.open_tags = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
        if attrs:
            # Styled/custom HTML is not automatically evidence of a clean field.
            self.suspicious_markup = True
        if tag in BLOCK_TAGS:
            self.parts.append("\n")
        if tag not in {"br", "img", "hr", "input", "meta", "link", "wbr"}:
            self.open_tags.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in {"br", "img", "hr", "input", "meta", "link", "wbr"}:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.open_tags and self.open_tags[-1] == tag:
            self.open_tags.pop()
        else:
            self.suspicious_markup = True
        if tag in BLOCK_TAGS - {"br"}:
            self.parts.append("\n")

    def handle_comment(self, data):
        self.suspicious_markup = True

    def handle_decl(self, decl):
        self.suspicious_markup = True

    def handle_pi(self, data):
        self.suspicious_markup = True


def parse_field(raw):
    parser = FieldText()
    parser.feed(raw)
    parser.close()
    if parser.open_tags:
        parser.suspicious_markup = True
    return "".join(parser.parts).replace("\xa0", " ").strip(), parser


def normalize_for_matching(raw):
    text, _ = parse_field(raw)
    # No NFKC, kana conversion, pronunciation guessing, or internal-space removal.
    return unicodedata.normalize("NFC", text.strip())


def classify_english(raw):
    text, parser = parse_field(raw)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    headings = sorted({m.group(1).lower() for m in HEADINGS.finditer(text)})
    evidence = {"headings": headings, "nonempty_line_count": len(lines)}
    start_count, end_count = raw.count(START), raw.count(END)
    if "CUSTOM-VOCAB-NOTE" in raw:
        if start_count == end_count == 1 and raw.index(START) < raw.index(END):
            prefix = raw[:raw.index(START)]
            suffix = raw[raw.index(END) + len(END):]
            prefix_class, _, _ = classify_english(prefix)
            if suffix.strip() or prefix_class != "CLEAN":
                return "UNCERTAIN", "Markers exist but prefix/suffix needs manual inspection", evidence
            return "MANAGED", "Exactly one ordered marker pair with a clean sentence prefix", evidence
        return "UNCERTAIN", "Missing, duplicate, reversed, or noncanonical automation markers", evidence
    if not lines:
        return "UNCERTAIN", "Empty English field", evidence
    # Recognize strong manual structure even inside unusual block markup.
    core_headings = set(headings) - {"my sentence", "kanji", "kanji breakdown"}
    if len(core_headings) >= 2 or "my sentence" in headings or "kanji breakdown" in headings:
        return "EXISTING", "Recognized manual explanation/example headings", evidence
    if headings:
        return "UNCERTAIN", "Only one explanation heading; preserve for manual inspection", evidence
    # Unlabeled but explicit Japanese definitions/breakdowns are also existing content.
    definitions = [line for line in lines[1:] if "=" in line and JAPANESE_CHARS.search(line)]
    if len(definitions) >= 2:
        return "EXISTING", "Multiple appended Japanese definition/breakdown lines", evidence
    if len(lines) != 1:
        return "UNCERTAIN", "Unlabeled additional nonempty lines", evidence
    if parser.tags - SIMPLE_TAGS or parser.suspicious_markup:
        return "UNCERTAIN", "Unfamiliar HTML, attributes, or comments", evidence
    # CLEAN is a conservative structural observation, not proof against the original deck.
    if len(text) > 200 or not re.search(r"[A-Za-z]", text):
        return "UNCERTAIN", "Not a short recognizable English sentence", evidence
    if JAPANESE_CHARS.search(text) or re.search(r"[=→←⇒:：<>\[\]{}|]", text):
        return "UNCERTAIN", "Single-line text contains annotation-like content", evidence
    if any(unicodedata.category(char).startswith("C") for char in text):
        return "UNCERTAIN", "Control or invisible formatting characters", evidence
    if not re.search(r"[.!?][\"'’”)]?$", text):
        return "UNCERTAIN", "Sentence boundary is not clear", evidence
    return "CLEAN", "One short English sentence line, with no annotation evidence", evidence


def chunks(values, size=250):
    for start in range(0, len(values), size):
        yield values[start:start + size]


def field(note, name):
    entry = note.get("fields", {}).get(name)
    if not isinstance(entry, dict) or not isinstance(entry.get("value"), str):
        raise AuditError(f"Note {note.get('noteId')} lacks valid field {name}")
    return entry["value"]


def collect():
    version = anki_request("version")
    if not isinstance(version, int) or version < 6:
        raise AuditError("AnkiConnect API version 6 or newer is required")
    decks = anki_request("deckNames")
    if DECK not in decks:
        raise AuditError(f"Expected deck {DECK!r} is missing; available decks: {decks}")
    ids = sorted(anki_request("findNotes", query=f'deck:"{DECK}"'))
    if not ids or len(ids) != len(set(ids)):
        raise AuditError("Empty or invalid deck note query")
    notes = []
    for batch in chunks(ids):
        received = anki_request("notesInfo", notes=batch)
        if sorted(n.get("noteId", -1) for n in received) != batch:
            raise AuditError("Incomplete notesInfo response; collection may have changed during audit")
        notes.extend(received)
    models = sorted({n["modelName"] for n in notes})
    model_fields = {model: anki_request("modelFieldNames", modelName=model) for model in models}
    required = {EXPRESSION, READING, JAPANESE, ENGLISH}
    if not required.issubset(model_fields.get(MODEL, [])):
        raise AuditError("Confirmed Core note type/field structure is no longer present")
    card_ids = sorted({c for n in notes for c in n.get("cards", [])})
    cards = {}
    for batch in chunks(card_ids):
        received = anki_request("cardsInfo", cards=batch)
        if sorted(c.get("cardId", -1) for c in received) != batch:
            raise AuditError("Incomplete cardsInfo response")
        cards.update({c["cardId"]: c for c in received})
    return version, decks, notes, model_fields, cards


def collect_full_collection():
    """Read every existing note and card through AnkiConnect for integrity checks.

    The empty Anki search query returns the current collection inventory. No
    collection database files are opened, and all actions remain on the
    read-only allowlist.
    """
    ids = sorted(anki_request("findNotes", query=""))
    if not ids or len(ids) != len(set(ids)):
        raise AuditError("Empty or invalid full-collection note query")
    notes = []
    for batch in chunks(ids):
        received = anki_request("notesInfo", notes=batch)
        if sorted(n.get("noteId", -1) for n in received) != batch:
            raise AuditError("Incomplete full-collection notesInfo response")
        notes.extend(received)
    card_ids = sorted({card_id for note in notes for card_id in note.get("cards", [])})
    cards = {}
    for batch in chunks(card_ids):
        received = anki_request("cardsInfo", cards=batch)
        if sorted(c.get("cardId", -1) for c in received) != batch:
            raise AuditError("Incomplete full-collection cardsInfo response")
        cards.update({c["cardId"]: c for c in received})
    return None, None, notes, None, cards


def build_report(version, decks, notes, model_fields, cards):
    rows, excluded = [], []
    for note in notes:
        if note["modelName"] != MODEL:
            excluded.append({"note_id": note["noteId"], "model_name": note["modelName"],
                             "field_names": list(note["fields"]), "reason": "Outside Core 2000 note type"})
            continue
        raw_english = field(note, ENGLISH)
        classification, reason, evidence = classify_english(raw_english)
        raw_expression, raw_reading = field(note, EXPRESSION), field(note, READING)
        expression, reading = normalize_for_matching(raw_expression), normalize_for_matching(raw_reading)
        blockers = []
        for name, value in (("expression", expression), ("reading", reading)):
            if not value or re.search(r"\s", value) or not re.fullmatch(r"[\u3040-\u30ff\u3400-\u9fff々〆ヶー]+", value):
                blockers.append(f"Noncanonical {name}; do not infer or trim annotations")
        card_decks = sorted({cards[c]["deckName"] for c in note["cards"]})
        if not any(d == DECK or d.startswith(DECK + "::") for d in card_decks):
            blockers.append("No card in confirmed deck")
        rows.append({
            "note_id": note["noteId"], "card_ids": note["cards"], "card_decks": card_decks,
            "profile": note.get("profile"), "model_name": MODEL,
            "expression": expression, "reading": reading,
            "expression_html": raw_expression, "reading_html": raw_reading,
            "classification": classification, "classification_reason": reason,
            "evidence": evidence, "english_field_name": ENGLISH,
            "english_html": raw_english, "english_text": parse_field(raw_english)[0],
            "english_sha256": hashlib.sha256(raw_english.encode("utf-8")).hexdigest(),
            "japanese_sentence_html": field(note, JAPANESE),
            "japanese_sentence_text": normalize_for_matching(field(note, JAPANESE)),
            "notes_field": field(note, "Notes"), "core_index": field(note, "Core-Index"),
            "tags": note.get("tags", []), "note_mod": note.get("mod"),
            "matching_blockers": blockers,
        })
    by_pair, by_expression = collections.defaultdict(list), collections.defaultdict(list)
    for row in rows:
        by_pair[(row["expression"], row["reading"])].append(row)
        by_expression[row["expression"]].append(row)
    for group in by_pair.values():
        if len(group) > 1:
            for row in group:
                row["matching_blockers"].append("Duplicate expression + reading pair")
    for row in rows:
        row["eligible_by_classification"] = row["classification"] in {"CLEAN", "MANAGED"}
        row["eligible_without_extra_identity"] = row["eligible_by_classification"] and not row["matching_blockers"]
    duplicates = [{"expression": expr, "readings": sorted({r["reading"] for r in group}),
                   "note_ids": [r["note_id"] for r in group]}
                  for expr, group in sorted(by_expression.items()) if len(group) > 1]
    duplicate_pairs = [{"expression": pair[0], "reading": pair[1],
                        "note_ids": [r["note_id"] for r in group]}
                       for pair, group in sorted(by_pair.items()) if len(group) > 1]
    counts = dict.fromkeys(("CLEAN", "EXISTING", "MANAGED", "UNCERTAIN"), 0)
    counts.update(collections.Counter(r["classification"] for r in rows))
    return {
        "audit_schema_version": 1, "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "read_only": True, "endpoint": ENDPOINT, "anki_connect_api_version": version,
        "deck_name": DECK, "note_type": MODEL, "available_decks": decks,
        "field_mapping": {"expression": EXPRESSION, "reading": READING,
                          "japanese_sentence": JAPANESE, "english_sentence": ENGLISH},
        "model_fields": model_fields,
        "classification_limit": "CLEAN means conservative sentence-only structure; no original-import baseline was supplied.",
        "summary": {"total_notes_in_deck": len(notes), "audited_core_notes": len(rows),
                    "excluded_other_models": len(excluded), "classifications": counts,
                    "duplicate_expression_groups": len(duplicates),
                    "multiple_reading_expression_groups": sum(len(g["readings"]) > 1 for g in duplicates),
                    "duplicate_expression_reading_groups": len(duplicate_pairs),
                    "notes_with_matching_blockers": sum(bool(r["matching_blockers"]) for r in rows),
                    "eligible_without_extra_identity": sum(r["eligible_without_extra_identity"] for r in rows)},
        "duplicate_expressions": duplicates,
        "multiple_readings": [g for g in duplicates if len(g["readings"]) > 1],
        "duplicate_expression_reading_pairs": duplicate_pairs,
        "excluded_notes": excluded, "notes": rows,
    }


def write_reports(report, output_dir):
    # Exclusive creation prevents replacing earlier audits or source data.
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = "core2k_audit_" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    json_path, csv_path = output_dir / (stem + ".json"), output_dir / (stem + ".csv")
    with json_path.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    columns = ["note_id", "expression", "reading", "classification", "classification_reason",
               "model_name", "card_decks", "card_ids", "tags", "matching_blockers",
               "eligible_by_classification", "eligible_without_extra_identity", "english_field_name",
               "english_sha256", "english_html", "english_text", "japanese_sentence_html",
               "core_index", "notes_field", "expression_html", "reading_html"]
    with csv_path.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in report["notes"]:
            flat = {key: row[key] for key in columns}
            for key in ("card_decks", "card_ids", "tags", "matching_blockers"):
                flat[key] = json.dumps(flat[key], ensure_ascii=False)
            # Exact text is retained; view the CSV as data, without evaluating formulas.
            writer.writerow(flat)
    return json_path, csv_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "reports")
    args = parser.parse_args()
    try:
        report = build_report(*collect())
        paths = write_reports(report, args.output_dir)
    except (AuditError, OSError, KeyError, TypeError, ValueError) as exc:
        parser.exit(1, f"AUDIT ERROR: {exc}\nNo Anki write action was performed.\n")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    for path in paths:
        print(path)
    print("Read-only audit complete. No vocabulary updater is implemented.")


if __name__ == "__main__":
    main()
