# Eval brain

This folder is the fictional Layer 1 eval corpus: one persona, Alex Rivera, and nobody real. See `docs/eval-corpus-plan.md` for the inventory and why each note exists.

Read the table as predicted vs observed. Predictions live in the Today column of `docs/eval-corpus-plan.md`. Observed was recorded on 2026-09-09 against the engine at commit 28c4c22.

| # | Problem | Query | Family | Observed today |
|---|---|---|---|---|
| 1 | Three-note supersession chain | `teaching load` | supersession | Top is teaching-load-2026-09; the two old load notes are dropped; teaching-load-committee also returns and contradicted_by fires between the two current notes. |
| 2 | Chain under `--historical` | `teaching load` (historical) | supersession | Both old load notes appear labeled superseded; 2026-09 is first; committee is current with contradicted_by; extra superseded hit: decline-summer-teaching. |
| 3 | Reversed decision | `summer teaching` | supersession | Only accept-summer-teaching; the superseded decline note is absent. |
| 4 | Title substring trap | `teaching load` | named-thing | teaching-load-2026-09 first, then teaching-load-committee; contradicted_by fires on the pair (any two current hits). |
| 5 | Exact id vs exact title diverge | `assessment-policy` and `Curve and grading policy` | named-thing | Both queries return only assessment-policy.md as an exact match. |
| 6 | Single alias | `Sam` | named-thing | Only samir-okonkwo. |
| 7 | Multi-alias | `PN` | named-thing | Returns priya-natarajan (keyword score on the alias string, not an exact alias match). |
| 8 | Near-duplicate names | `Marcus Bell` | named-thing | Only marcus-bell; Bellamy is suppressed. |
| 9 | Near-duplicate names, ambiguous | `Marcus` | contradiction (negative) | Both marcus-bell and marcus-bellamy return; contradicted_by fires even though they do not disagree. |
| 10 | Generic-to-named | `who is the department chair` | named-thing | Three cards: department-service first, then dana-whitfield, then drop-evening-section; all three marked as contradicting. |
| 11 | Buried fact in a long note | `final exam weight` | citation | Only econometrics-fall-2026, claim line 63 (the buried weight). |
| 12 | Planted contradiction | `research budget` | contradiction | lab-budget and research-account both return and list each other; daily 2026-09-02 is a third current hit so contradicted_by is a triple. |
| 13 | Daily log mentions the same number | `research budget` | contradiction | Daily 2026-09-02 also matches and is listed as a third contradicting note. |
| 14 | Source dump vs filed note | `econometrics syllabus` | named-thing | econometrics-fall-2026 first; notion-export dump second with confidence low; contradicted_by fires between them. |
| 15 | File with no frontmatter | `chair email` | all | pasted-email-chair.md has no frontmatter and is skipped; zero cards. |
| 16 | State note vs daily mention | `office hours` | named-thing | Only office-hours.md; daily mentions do not outrank it. |
| 17 | Clean abstention | `parking permit` | abstention | Zero cards. |
| 18 | Near-miss abstention | `evening elective enrollment` | abstention | Returns drop-evening-section (mentions the topic, gives no number). |
| 19 | Near-miss abstention, low confidence | `sabbatical start date` | abstention | Returns sabbatical-plan with confidence low. |
| 20 | Open `type` string | `econometrics` | check | check reports 38 notes, 0 errors; type: course is accepted. |
