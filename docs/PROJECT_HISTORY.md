# Project history

This timeline records the major decisions and completed stages from the first inspection request through Phase 8D. Counts and outcomes are taken from the saved project reports and successful live AnkiConnect checks.

## Phase 1 — Read-only inspection

The target environment was clarified as Fedora Linux with Anki Desktop. The collection was inspected through AnkiConnect on `127.0.0.1:8765`; the SQLite collection was not edited. The confirmed deck and note type are both `Core 2000`. The vocabulary, reading, Japanese sentence, and English sentence fields are `Vocabulary-Kanji`, `Vocabulary-Kana`, `Expression`, and `Sentence-English`.

## Phase 2 — Vocabulary audit

The initial Core 2000 audit classified 1,221 notes as CLEAN, 771 as EXISTING (manual explanations), 15 as UNCERTAIN, and excluded 19 notes with a different Basic model. The matching rule used deck/model context and vocabulary identity; ambiguous or uncertain records were not treated as clean.

## Phases 3–4 — Generate and reconcile new explanations

The first plan was to recover older ChatGPT explanations from a conversation export. That plan was replaced: no conversation export was supplied or used, and new explanations were generated in reviewable batches of 25. Each explanation follows the six-section format and uses the vocabulary reading and example context to select the intended sense.

Phase 4 reconciled **48 batches and 1,198 unique records**. All 1,198 received a batch-level AI review, 32 corrections were recorded in the progress history, and the final reconciliation reported zero unresolved semantic issues. The resumable workflow retained batch checkpoints and source hashes. This review history is not equivalent to independent human-native-speaker verification.

## Phase 5 — Installation preparation

The installation design required a full Anki collection package backup with scheduling and media, a fresh live preflight, exact field snapshots, an opt-in dry run, a five-note test, and field-level rollback values. Existing unmarked manual explanations remained protected.

## Phase 6 — Controlled test and first 100

Five existing notes were updated as a technical test, followed by the authorized first 100 remaining notes. The process used `updateNoteFields` only for `Sentence-English`, verified each field after writing, and compared card scheduling. Those 105 explanations were excluded from the next phase.

## Phase 7 — Remaining generated explanations

The remaining 1,093 eligible explanations were installed in batches of at most 100 after sync confirmation, a fresh full collection package, and live eligibility checks. Batch checkpoints and rollback values were saved. Together with the test and first 100, the final installed set was **1,198 explanations**.

## Phase 8 — Linguistic quality audit

The audit covered all 1,198 installed explanations, including a structural check of the live fields and a word-centered Nuance screen. The screen flagged 340 candidates for review; the flag was treated as a heuristic, not proof of error. Phase 8B classified 334 as KEEP, 6 as IMPROVE, 0 as CORRECT, and 0 as UNCERTAIN. A reproducible sample of 90 unflagged explanations found no confirmed missed defect. Ten corrections were reconciled for final review: six accepted as written and four revised with exact replacement text.

## Phase 8D — Authorized corrections applied

After both devices were confirmed synced and a new full collection package was verified, exactly **17 approved section replacements across 10 existing notes** were applied. Only `Sentence-English` was sent to AnkiConnect. The original English prefixes, other fields, note/card IDs, and available scheduling properties were checked. Full-collection verification passed for 3,935 notes and 5,335 cards. The other 1,188 managed explanations remained unchanged. No final AnkiWeb sync was initiated; the user handles device synchronization.

## Completion state

- 1,198 generated explanations are installed in existing Core 2000 notes.
- 10 notes received the 17 Phase 8D text corrections.
- The other 1,188 managed explanations and all non-target notes remained unchanged during Phase 8D.
- No note or card was recreated, deleted, rescheduled, or directly edited in SQLite.
- Rollback values and the full Phase 8D verification snapshot are retained locally, not published here.
