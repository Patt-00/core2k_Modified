# Architecture and safety

## Data flow

```text
reviewed batch source
        ↓
Phase 4 reconciliation and checkpointing
        ↓
read-only live identity and field audit
        ↓
dry-run field construction
        ↓
user-authorized AnkiConnect updateNoteFields
        ↓
immediate field readback and full-collection verification
```

The public vocabulary JSON is a sanitized release of the generated text. It contains expression, reading, explanation sections, generation batch, and Phase 8D section names. It does not serve as a replacement Anki collection or as an import package.

## Matching and field behavior

The live target was identified by the confirmed Core 2000 deck/model and the combination of vocabulary expression, reading, and Japanese example. A note ID was used only after that identity and the saved field snapshot were verified. Missing or ambiguous identities were skipped in the wider workflow.

The managed explanation is delimited by:

```html
<!-- CUSTOM-VOCAB-NOTE-START -->
...
<!-- CUSTOM-VOCAB-NOTE-END -->
```

These markers support idempotent replacement of the generated section. Manual explanations without markers are not treated as managed content. For Phase 8D, the approved section text was reconstructed and compared byte-for-byte with the reconciled simulated final HTML before any write.

## Anki operation boundary

- Collection communication is local AnkiConnect traffic to `127.0.0.1:8765`.
- Auditing uses read-only actions such as `version`, `deckNames`, `findNotes`, `notesInfo`, and `cardsInfo`.
- The only write action used for installation and correction is `updateNoteFields`.
- The only field submitted is `Sentence-English` on an already-existing note.
- No SQLite collection file is edited directly. No notes/cards are added, deleted, recreated, repositioned, forgotten, or rescheduled.
- No template, deck assignment, other note field, review history, or scheduling property is intentionally changed.

## Backup, logging, and verification

Before an authorized write, the user syncs the devices and exports a new full `.colpkg` with scheduling and media. The package is checked for existence, archive readability/CRC, collection entries, media index, timestamp, size, and SHA-256.

Before and after writes, AnkiConnect snapshots are used to compare note and card identities and available scheduling values. Each target field is read back immediately. Original English prefixes and non-target notes are compared exactly. Original full field values and a pre-write collection snapshot are saved in a private local rollback directory. Rollback must restore only a field that still exactly matches the logged post-write value; later user edits must not be overwritten.

Phase 8D used the local backup `Core2000-phase8d-before-corrections.colpkg` and recorded its checksum and verification result in the local run log. The backup and rollback files are intentionally absent from this public repository.

## Final Phase 8D verification

- 10 of 10 target notes read back exactly as approved.
- 17 approved text sections changed; no other target field changed.
- Every target retained one managed marker pair and its original English sentence prefix.
- All 1,188 non-target managed explanations remained unchanged.
- All non-target notes remained unchanged.
- Note/card identities and all available card scheduling values remained unchanged across 3,935 notes and 5,335 cards.
- No post-install sync was initiated by the project.
