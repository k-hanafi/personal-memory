# Eval brain

This folder is the fictional Layer 1 eval corpus: one persona, Alex Rivera, and nobody real. See `docs/eval-corpus-plan.md` for the inventory and why each note exists.

Read the table as predicted vs observed. Predictions live in the Today column of `docs/eval-corpus-plan.md`. Observed values were recorded on 2026-09-09 against commit `eae9e61` plus the phase 2 notes. `70-meetings/` and `80-reading/` exist to test that folder layout is convention.

| # | Problem | Query | Family | Observed today |
|---|---|---|---|---|
| 1 | Three-note supersession chain | `teaching load` | supersession | Top teaching-load-2026-09.md:10; extra teaching-load-committee.md:9; contradicted_by fired. Old load notes dropped. |
| 2 | Chain under `--historical` | `teaching load` (historical) | supersession | Top teaching-load-2026-09.md:10; extras committee:9, teaching-load-2025-09.md:10, teaching-load-2026-01.md:11, decline-summer-teaching.md:10; old load notes labeled superseded; contradicted_by fired on the two current hits. |
| 3 | Reversed decision | `summer teaching` | supersession | Top accept-summer-teaching.md:10; extras daily 2026-03-02.md:11, daily 2026-04-21.md:11, grant-call-pdf-text.md:22; contradicted_by fired. Decline note absent. |
| 4 | Title substring trap | `teaching load` | named-thing | Top teaching-load-2026-09.md:10, then teaching-load-committee.md:9; contradicted_by fired on the pair. |
| 5 | Exact id vs exact title diverge | `assessment-policy` and `Curve and grading policy` | named-thing | Both queries return only assessment-policy.md:9 as an exact match. |
| 6 | Single alias | `Sam` | named-thing | Only samir-okonkwo.md:10. |
| 7 | Multi-alias | `PN` | named-thing | Only priya-natarajan.md:10 (keyword score on the alias string, not an exact alias match). |
| 8 | Near-duplicate names | `Marcus Bell` | named-thing | Only marcus-bell.md:9; Bellamy suppressed. |
| 9 | Near-duplicate names, ambiguous | `Marcus` | contradiction (negative) | marcus-bell.md:9 and marcus-bellamy.md:9; contradicted_by fired. |
| 10 | Generic-to-named | `who is the department chair` | named-thing | Top department-service.md:16; extras dana-whitfield.md:11, drop-evening-section.md:13; contradicted_by fired on all three. |
| 11 | Buried fact in a long note | `final exam weight` | citation | Only econometrics-fall-2026.md:64 (the buried weight). |
| 12 | Planted contradiction | `research budget` | contradiction | Top lab-budget.md:11; extras research-account.md:11, daily 2026-09-02.md:11; contradicted_by fired on the triple. |
| 13 | Daily log mentions the same number | `research budget` | contradiction | Same triple as row 12; daily 2026-09-02.md:11 is a third contradicting note. |
| 14 | Source dump vs filed note | `econometrics syllabus` | named-thing | Top econometrics-fall-2026.md:10; extra notion-export-2026-08-15.md:17 with confidence low; contradicted_by fired. |
| 15 | File with no frontmatter | `chair email` | all | pasted-email-chair.md is skipped; zero cards. |
| 16 | State note vs daily mention | `office hours` | named-thing | Only office-hours.md:10; exact title suppresses daily mentions. |
| 17 | Clean abstention | `parking permit` | abstention | Zero cards. |
| 18 | Near-miss abstention | `evening elective enrollment` | abstention | Top drop-evening-section.md:9; extra daily 2026-08-19.md:12; contradicted_by fired. |
| 19 | Near-miss abstention, low confidence | `sabbatical start date` | abstention | Only sabbatical-plan.md:11 with confidence low. |
| 20 | Open `type` string | `econometrics` | check | check reports 109 notes, 5 skipped, 0 errors; type: course is accepted. |
| 21 | (a) Single token, three id matches | `load` | named-thing | Top advising-load.md:10; extras teaching-load-2026-09.md:10, teaching-load-committee.md:9, committee-minutes-2026-05-08.md:9, committee-minutes-2026-09-04.md:9, transcript-committee-2026-09-04.md:9, journal-refereeing.md:15, bea-okonkwo.md:15, nadia-ferrante.md:14; nine cards; contradicted_by fired. |
| 22 | (a) Long decision id beats the state note | `afternoon office hours` | named-thing | Top move-office-hours-to-afternoon.md:9; extra econometrics-fall-2026.md:21; contradicted_by fired. office-hours.md absent (no token afternoon). |
| 23 | (a) Title and id beat eight body hits | `grading policy` | named-thing | Top assessment-policy.md:9; extra econometrics-fall-2026.md:55; contradicted_by fired. |
| 24 | (a) Shared surname | `Okonkwo` | named-thing | Top bea-okonkwo.md:9; extras samir-okonkwo.md:10, conference-programme-2026-06.md:53; contradicted_by fired. |
| 25 | (a, d) Alias collides with a real first name | `Sam` | named-thing | Only samir-okonkwo.md:10; sam-delacroix suppressed by exact alias match. |
| 26 | (a) Exact title through the collision | `Sam Delacroix` | named-thing | Only sam-delacroix.md:9 (exact title). |
| 27 | (k) First name that is a common noun | `Grant` | named-thing | Top grant-application.md:14; extras grant-oyelaran.md:9, meeting-grant-officer-2026-07-22.md:9, grant-call-pdf-text.md:9, daily 2026-07-22.md:11; five cards; contradicted_by fired. |
| 28 | (a) Buried date in the grant note | `grant application deadline` | citation | Top grant-application.md:14; extra grant-call-pdf-text.md:66; contradicted_by fired. Filed note wins. |
| 29 | (a) `review` pressure | `journal review` | named-thing | Top journal-refereeing.md:9; extra decline-associate-editor-role.md:12; contradicted_by fired. |
| 30 | (b) One hop | `labor markets paper editor` | hop | Zero cards. |
| 31 | (b) Two hops | `journal for Priya's paper` | hop | Zero cards. |
| 32 | (b) Hop into a superseded note | `case competition sponsor 2025` | hop | Default: only daily 2025-11-08.md:11. Historical: top case-competition-2025.md:10 labeled superseded; extra daily 2025-11-08.md:11; contradicted_by no. |
| 33 | (b, n) Generic-to-named through a meeting | `who is the program officer for the grant` | hop | Top meeting-grant-officer-2026-07-22.md:11; extras grant-application.md:11, grant-oyelaran.md:11, grant-call-pdf-text.md:94; contradicted_by fired. |
| 34 | (b, n) Identity to project to people | `Alex's coauthor on hiring frictions` | hop | Zero cards. |
| 35 | (c) Get by id when path differs | `get research-grant-2026` | get | Returns 30-projects/grant-application.md. |
| 36 | (c) Get by path | `get 30-projects/grant-application.md` | get | Returns 30-projects/grant-application.md. |
| 37 | (c) Shared id prefix | `get office-hours` | get | Returns 40-areas/office-hours.md. Prefix ids do not match. |
| 38 | (c) Filename stem is not an id | `get kjaer` | get | get kjaer returns nothing. get soren-kjaer and get 50-people/kjaer.md return the note. |
| 39 | (c, g) Get a source with no frontmatter | `get sources/chat-log-yuki-pipeline-2026-09-04.md` | get | Nothing: _load requires frontmatter. |
| 40 | (d) Stopwords | `what is the curve policy` | named-thing | Only assessment-policy.md:9. |
| 41 | (d) Lowercase name | `priya` | named-thing | Only priya-natarajan.md:10. |
| 42 | (d, n) Two-letter token matches inside words | `TA` | named-thing | Top startup-survey-pipeline.md:9; 61 cards; contradicted_by fired. |
| 43 | (d) Status filter on a long chain | `econometrics final exam weight` | supersession | Only econometrics-fall-2026.md:64. |
| 44 | (m) Old weight under `--historical` | `econometrics final exam weight 2025` (historical) | temporal | Historical: only econometrics-fall-2025.md:64 labeled superseded (35 percent). Default: zero cards. |
| 45 | (m) Advisee count last year | `advising load 2025` (historical) | temporal | Historical: only advising-load-2025-09.md:10 labeled superseded. Default: zero cards. |
| 46 | (m, k) Broken chain under history | `office hours fall 2025` (historical) | temporal | Only office-hours-2025-09.md:9 labeled superseded. Card has no successor. |
| 47 | (m) Winter load | `what was the teaching load in winter 2026` (historical) | temporal | Historical: only teaching-load-2026-01.md:11 labeled superseded. Default: zero cards. |
| 48 | (o) Where we left off | `survey pipeline next step` | temporal | Only daily 2026-09-04.md:11. |
| 49 | (m) Which figure is newer | `budget August statement` | temporal | Only research-account.md:12. |
| 50 | (h) Paraphrase | `gaming the curve` | paraphrase | Zero cards. |
| 51 | (h) Paraphrase | `burnout` | paraphrase | Zero cards. |
| 52 | (h, d) Paraphrase with a substring trap | `rent` | paraphrase | Top labor-markets-paper.md:17; extras rubric-redesign.md:17, reading-diff-in-diff-handbook.md:48; contradicted_by fired. home-admin absent. |
| 53 | (h) Paraphrase into a daily | `procrastinating on the paper` | paraphrase | Zero cards. |
| 54 | (h) Paraphrase | `AI tools for grading` | paraphrase | Zero cards. |
| 55 | (i) Agreeing notes flagged as contradicting | `midterm week 7` | contradiction (negative) | Top econometrics-fall-2026.md:32; extras intro-micro-fall-2026.md:17, notion-export-2026-08-15.md:20; contradicted_by fired. |
| 56 | (i) Two meetings, same phrase | `release request` | contradiction (negative) | Top daily 2026-05-08.md:11; extras teaching-load-committee.md:15, committee-minutes-2026-05-08.md:13, committee-minutes-2026-09-04.md:19, transcript-committee-2026-09-04.md:24; five cards; contradicted_by fired. |
| 57 | (i) Same journal, three notes | `Northbridge Review` | contradiction (negative) | Top journal-refereeing.md:11; extras marcus-bellamy.md:11, decline-associate-editor-role.md:13; contradicted_by fired. |
| 58 | (i, n) Two people share a trait | `who prefers async comments` | contradiction (negative) | Top working-preferences.md:11; extra samir-okonkwo.md:13; contradicted_by fired. |
| 59 | (j) Not in corpus | `dissertation defense date` | abstention | Zero cards. |
| 60 | (j) Mentioned but not named | `sponsor contact at Quill and Timber` | abstention | Only sponsor-call-quill-timber-2026-08-05.md:9. |
| 61 | (j) Under-specified | `the meeting` | abstention | Top meeting-chair-staffing-2026-08-19.md:9; 16 cards; contradicted_by fired. |
| 62 | (j) Superseded, never replaced | `intermediate macro` | abstention | Default: zero cards. Historical: top intermediate-macro-fall-2025.md:9 labeled superseded; extra teaching-load-2025-09.md:12. |
| 63 | (j) Superseded, never replaced, area | `commute` | abstention | Default: zero cards. Historical: only commute.md:9 labeled superseded. |
| 64 | (j) Near miss on a date | `thesis defense date` | abstention | Top thesis-supervision-amankwah.md:17; extra conference-programme-2026-06.md:101; contradicted_by fired. |
| 65 | (k) Misspelled name | `Jonas Wier` and `Jonas Weir` | named-thing | `Jonas Wier`: top daily 2026-06-10.md:14; extra conference-programme-2026-06.md:111; contradicted_by fired. `Jonas Weir`: only jonas-weir.md:9. |
| 66 | (k) Surname only | `Ferrante` | named-thing | Top nadia-ferrante.md:9; extras daily 2026-02-05.md:11, daily 2026-09-04.md:14, committee-minutes-2026-09-04.md:11, conference-programme-2026-06.md:74, transcript-committee-2026-09-04.md:28; contradicted_by fired. |
| 67 | (k) Lowercase mention | `mira` | named-thing | Top mira-solberg.md:9; extra daily 2026-08-25.md:11; contradicted_by fired. |
| 68 | (k) Diacritic | `Søren`, `Søren Kjær`, `Soren Kjaer` | named-thing | `Søren`: top working-preferences.md:9; 20 cards; contradicted_by fired. `Søren Kjær`: only kjaer.md:9 (exact title). `Soren Kjaer`: only kjaer.md:9. |
| 69 | (k) Person nobody links to | `Tobias Renquist` and `reference letter` | named-thing | `Tobias Renquist`: only tobias-renquist.md:9. `reference letter`: top daily 2025-10-09.md:11; extra tobias-renquist.md:11; contradicted_by fired. |
| 70 | (k) Missing `superseded_by` | `check` | check | check reports 109 notes, 0 errors. office-hours-2025-09 has no superseded_by and is not flagged. |
| 71 | (k) CRLF note | `hiring frictions survey` | citation | Only reading-hiring-frictions-survey.md:9; claim `Notes on a hiring frictions survey`. |
| 72 | (k) Unknown frontmatter keys | `lease renewal` and `get home-admin` | check | `lease renewal`: top home-admin.md:13; extra theo-lindqvist.md:11; contradicted_by fired. get home-admin returns 40-areas/home-admin.md. |
| 73 | (l) Claim spans three lines | `open textbook rationale intro micro` | citation | Only adopt-open-textbook-intro-micro.md:13. |
| 74 | (l) Motion spans three lines | `committee motion release cap` | citation | Top committee-minutes-2026-09-04.md:15; extra transcript-committee-2026-09-04.md:71; contradicted_by fired. |
| 75 | (n) Role lookup, course outranks person | `who is the TA for econometrics` | named-thing | Top econometrics-fall-2026.md:10; extras ines-castellanos.md:11, notion-export-2026-08-15.md:17; contradicted_by fired. |
| 76 | (n) Role lookup, second course | `who is the TA for intro micro` | named-thing | Top intro-micro-fall-2026.md:9; extra marcus-bell.md:11; contradicted_by fired. |
| 77 | (n) Multi-entity | `labor markets paper` | named-thing | Only labor-markets-paper.md:9 (exact title suppresses coauthor hits). |
| 78 | (n) Multi-entity phrased | `which people are on the labor markets paper` | hop | Zero cards. |
| 79 | (o) Timeline fact | `case competition day` (historical) | temporal | Top daily 2025-11-08.md:11; extras drop-evening-section.md:12, meeting-chair-staffing-2026-08-19.md:15; contradicted_by fired. |
| 80 | (o) Daily mention through a link | `last met Priya` | temporal | Zero cards. |
| 81 | (o) Meeting note vs daily | `sponsor call` | named-thing | Top sponsor-call-quill-timber-2026-08-05.md:9; extra daily 2026-08-05.md:11; contradicted_by fired. |
| 82 | (g) Unfiled scan | none | filing | Not runnable: unfiled does not exist yet. |
| 83 | (g, a) Source swamp, tie | `release request vote` | named-thing | Top committee-minutes-2026-09-04.md:19; extra transcript-committee-2026-09-04.md:24; contradicted_by fired. |
| 84 | (g, a) Source id carries the query words | `conference programme` | named-thing | Top conference-programme-2026-06.md:14 with confidence low; extra conference-trip-2026-06.md:9; contradicted_by fired. |
| 85 | (c) Path lookup for a diacritic person | `get 50-people/kjaer.md` | get | Returns 50-people/kjaer.md; title keeps the diacritics. |
