# Linguistic quality audit

## Phase 4 batch review

The 1,198 source records span 48 batches. The Phase 4 reconciliation reports 1,198 unique records reviewed, 32 corrected entries recorded in the progress history, and zero unresolved semantic issues. Review dimensions included reading and context alignment, meaning, nuance, kanji logic, grammar, comparisons, and Filipino wording.

## Phase 8 comprehensive audit

The full audit reconciled all 1,198 installed marker pairs to the latest Phase 4 source set and checked identity fields, Japanese examples, original English prefixes, marker boundaries, and managed explanation bodies through AnkiConnect. It reported:

| Status | Count |
|---|---:|
| PASS | 1,194 |
| MINOR | 2 |
| MODERATE | 2 |
| MAJOR | 0 |
| NEEDS HUMAN REVIEW | 0 |

Those counts describe the audit process and are not a claim that every lexical judgment was independently checked in dictionaries or by a human speaker.

## Word-centered Nuance screen and adjudication

The Nuance criterion asks explanations to teach how a word behaves across contexts, with the deck sentence serving only as a brief application. The exhaustive screen grouped the entries as follows:

| Screening group | Count |
|---|---:|
| Word-centered, no sentence reference | 270 |
| Word-centered with helpful context | 438 |
| Context secondary | 150 |
| Sentence-dominant candidates for review | 340 |

The 340 were reviewed individually. Outcomes were **334 KEEP, 6 IMPROVE, 0 CORRECT, 0 UNCERTAIN**. A seeded stratified false-negative sample (seed `20261009`) reviewed 30 records from each of the other three groups, 90 total; it found zero confirmed missed defects. That sample does not prove every unflagged explanation is error-free.

The audit paid special attention to `行く` (habitual versus planned reading), `細かい` (word meaning versus the full phrase), `姪` (number neutrality), `歌` (song/singing and literary poetry), and the word-level scope of entries such as `高い`, `交渉`, `パチンコ`, and `留学`.

## Phase 8C–8D corrections

Ten corrections were reconciled. Six prior proposals were retained as written and four were revised for consistency. The final 17 replacements were applied in Phase 8D: 9 Nuance, 4 Logic, 2 Meaning, 1 Difference, and 1 Filipino section. The exact text changes are in [PHASE8D_CORRECTIONS.md](PHASE8D_CORRECTIONS.md).

## Reliability and references

The audit combined structural and hash checks, model-led semantic review, source reconciliation, targeted lexical references, and a seeded sample. It did **not** establish native-speaker certification for every explanation or every Filipino translation. Short/simple vocabulary was not given invented nuance merely to make sections longer.

Lexical references consulted for disputed points include:

- [Digital Daijisen: 高い](https://dictionary.goo.ne.jp/word/%E9%AB%98%E3%81%84/)
- [Shogakukan Thesaurus: 交渉](https://dictionary.goo.ne.jp/thsrs/11016/meaning/m0u/)
- [Digital Daijisen: 歌](https://dictionary.goo.ne.jp/word/%E6%AD%8C_%28%E3%81%86%E3%81%9F%29/)
- [Digital Daijisen: ぱちんこ](https://dictionary.goo.ne.jp/word/%E3%81%B1%E3%81%A1%E3%82%93%E3%81%93/)
- [Digital Daijisen: 留学](https://dictionary.goo.ne.jp/srch/all/%E3%82%8A%E3%82%85/m0u/)
- [Tokyo University of Foreign Studies: polite nonpast Vます](https://www.coelang.tufs.ac.jp/mt/ja/gmod/courses/c02/lesson13/step1/explanation/023.html)
- [Japan Kanji Aptitude Testing Foundation: 姪](https://dictionary.goo.ne.jp/word/kanji/%E5%A7%AA/)
- [Digital Daijisen: 細かい](https://dictionary.goo.ne.jp/word/%E7%B4%B0%E3%81%8B%E3%81%84/)
- [Digital Daijisen: 両替](https://dictionary.goo.ne.jp/word/%E4%B8%A1%E6%9B%BF/)
