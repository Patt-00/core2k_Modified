# Core2k Modified

Core2k Modified documents a Fedora Anki project that added custom Japanese vocabulary explanations to an existing **Core 2000** deck while protecting the learner's review progress.

The completed dataset contains **1,198 AI-generated explanations** in six sections: kanji breakdown, Nuance, Logic, Meaning, Difference, and Filipino. They were installed into existing notes through AnkiConnect. A later linguistic audit led to **17 section-level corrections across 10 notes**. The final Phase 8D checks passed without changing card scheduling or any non-target note.

## Current configuration and result

| Item | Value |
|---|---|
| Platform | Fedora Linux, Anki Desktop |
| Deck / note type | `Core 2000` / `Core 2000` |
| Vocabulary fields | `Vocabulary-Kanji`, `Vocabulary-Kana` |
| Japanese example field | `Expression` |
| Updated field | `Sentence-English` |
| Managed explanations | 1,198 |
| Phase 8D corrections | 17 replacements across 10 existing notes |
| Scheduling verification | Passed; 5,335 cards unchanged |
| Final device sync | Left to the user; this project did not initiate it after Phase 8D |

## Repository contents

- [`data/generated_explanations.json`](data/generated_explanations.json) contains the 1,198 vocabulary explanations, with the Phase 8D corrections reflected.
- [`docs/PROJECT_HISTORY.md`](docs/PROJECT_HISTORY.md) records the project from inspection through installation and correction.
- [`docs/ARCHITECTURE_AND_SAFETY.md`](docs/ARCHITECTURE_AND_SAFETY.md) explains matching, AnkiConnect boundaries, backup, and verification.
- [`docs/QUALITY_AUDIT.md`](docs/QUALITY_AUDIT.md) summarizes Phase 4 and Phase 8 quality work and its limits.
- [`docs/PHASE8D_CORRECTIONS.md`](docs/PHASE8D_CORRECTIONS.md) shows the 17 exact section replacements without personal Anki identifiers or original card sentences.
- [`scripts/audit_core2k_readonly.py`](scripts/audit_core2k_readonly.py) is the project's standard-library, read-only AnkiConnect audit tool.
- [`scripts/validate_public_dataset.py`](scripts/validate_public_dataset.py) checks the public dataset's structure and record count.

Run the public-data check with:

```bash
python scripts/validate_public_dataset.py
```

The read-only audit script contacts AnkiConnect at `127.0.0.1:8765`. Its generated local reports contain live collection data and should remain private; report directories are ignored by Git.

## Quality and use

The explanations are AI-generated learning aids. The project includes batch-level AI semantic reviews, a full structural audit, targeted dictionary checks, and a seeded false-negative sample. **The entire set has not been independently verified by a human native speaker.** See [the quality audit](docs/QUALITY_AUDIT.md) for the exact counts and limitations.

The public dataset intentionally omits Anki note/card IDs, original card sentence fields, live collection snapshots, scheduling values, rollback logs, and collection backup packages. Raw ChatGPT conversation exports were not used.
