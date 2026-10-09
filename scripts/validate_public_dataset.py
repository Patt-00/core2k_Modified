#!/usr/bin/env python3
"""Validate the sanitized, public Core2k Modified explanation dataset."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

DATA = Path(__file__).resolve().parents[1] / "data/generated_explanations.json"
REQUIRED = {
    "generation_batch", "expression", "reading", "kanji_breakdown", "nuance",
    "logic", "meaning", "difference", "filipino", "phase8d_updated_sections",
}
FORBIDDEN_KEYS = {"note_id", "card_id", "japanese_sentence", "english_sentence", "english_html", "scheduling"}
NOTE_ID_PATTERN = re.compile(r"\b1\d{12}\b")


def main() -> int:
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    records = doc.get("records")
    if not isinstance(records, list) or len(records) != 1198 or doc.get("record_count") != 1198:
        raise SystemExit("Expected exactly 1,198 records")
    if set(doc.get("record_fields", [])) != REQUIRED:
        raise SystemExit("Dataset schema declaration is unexpected")
    seen: set[tuple[str, str]] = set()
    updated_records = updated_sections = 0
    serialized = DATA.read_text(encoding="utf-8")
    if NOTE_ID_PATTERN.search(serialized):
        raise SystemExit("Anki note-ID-shaped number found in public dataset")
    for index, row in enumerate(records, start=1):
        if set(row) != REQUIRED:
            raise SystemExit(f"Unexpected fields in record {index}")
        pair = (row["expression"], row["reading"])
        if not all(isinstance(x, str) and x for x in pair) or pair in seen:
            raise SystemExit(f"Invalid or duplicate vocabulary identity at record {index}")
        seen.add(pair)
        for key in REQUIRED - {"phase8d_updated_sections", "generation_batch"}:
            if not isinstance(row[key], str):
                raise SystemExit(f"Non-text {key} in record {index}")
        changed = row["phase8d_updated_sections"]
        if not isinstance(changed, list) or any(x not in {"nuance", "logic", "meaning", "difference", "filipino"} for x in changed):
            raise SystemExit(f"Invalid Phase 8D section list in record {index}")
        if changed:
            updated_records += 1
            updated_sections += len(changed)
        if FORBIDDEN_KEYS.intersection(row):
            raise SystemExit(f"Private Anki fields present in record {index}")
    if updated_records != 10 or updated_sections != 17:
        raise SystemExit(f"Expected 10 Phase 8D records / 17 sections, got {updated_records} / {updated_sections}")
    print(json.dumps({
        "status": "passed", "records": len(records), "unique_expression_reading_pairs": len(seen),
        "phase8d_records": updated_records, "phase8d_sections": updated_sections,
        "note_ids_or_original_sentence_fields": "not included",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
