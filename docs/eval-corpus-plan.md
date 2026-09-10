# Eval corpus plan

How we build `evals/brain/`, the fictional brain the Layer 1 evals run against.

Written 2026-09-09. Implements step 1 of the order in `docs/evals-spec.md`.
The spec says what the corpus is for. This file says what goes in it, why
each note exists, and how we know it is done.

## Decision: whose brain this is

The corpus is the brain of **Alex Rivera**, the fictional economics lecturer
already in `examples/demo-brain/`. One persona, grown from 7 notes to about 40.

Why one persona and why this one:

- A brain belongs to one person. Supersession chains, contradictions, and
  wikilinks only read as real inside one life. Mixing personas breaks that.
- Alex is shaped like the ICP in `docs/long-term-vision.md` (domain expert,
  daily coding-agent user, not a software engineer) without being any real
  person. Khaled's own brain is covered by Layer 2 (dogfood replay on
  `~/vault`). Layer 1 is the only place the customer's shape gets tested, so
  the fictional corpus is where the ICP lives.
- Realism comes from structure and mess, not biography. What makes a fixture
  hard is an alias that differs from the title, a fact buried at line 70, a
  superseded note that shares most of its words with its replacement. Those
  are planted on purpose. The persona is the vehicle that makes them read as
  plausible notes.

A second persona brain is not planned. Add one only if a real failure shows
the engine overfits to academic vocabulary.

## Rules for every note

1. Fictional. No real person, employer, institution, or course code. The
   university is "the university." Courses have titles, not codes.
2. Nothing from `~/vault`. Not a sentence, not a name, not a date pattern.
3. Frontmatter is flat `key: value` lines. The parser does not read YAML
   lists, so `aliases: Sam` is one string. Multi-alias notes are written as
   a comma string on purpose so they fail today (see capability targets).
4. One `current` note per changing fact, except the planted contradiction.
5. People are one file each in `50-people/`. Other notes link with
   `[[id]]` and never restate who the person is. A note may state the
   person's role in relation to that note ("TA: [[marcus-bell]]", "chair
   [[dana-whitfield]] agreed"); biography (background, preferences,
   history) stays in the person note.
6. `as_of` is when the claim was true. All dates fall between 2025-09-01
   and 2026-09-05.
7. Hand-written. No model-generated notes in this phase (spec step 10 comes
   after hand-written notes stop covering the families).
8. Short by default, 8 to 25 lines. Two notes are deliberately long (60 to
   90 lines) for the dilution case.

## Inventory

About 39 notes. Existing demo notes are marked (exists) and are copied, then
edited where the table says so.

### `20-identity/` (2)

| File | Status | Why it exists |
|---|---|---|
| `alex-rivera.md` (exists) | current | Persona anchor. Exact id and exact title target. |
| `working-preferences.md` | current | Standing preferences (async comments, Codex for rubrics). Body-only keyword target. |

### `30-projects/` (7)

| File | Status | Why it exists |
|---|---|---|
| `undergrad-case-competition.md` (exists, extend) | current | Project with two people linked. Generic-to-named source ("who co-organizes the case competition"). |
| `case-competition-2025.md` | superseded | Last year's edition. Shares most words with the current one. Supersession with high lexical overlap. |
| `econometrics-fall-2026.md` | current | Long note (60 to 90 lines). One fact (final exam weight) buried past line 60. Dilution and citation. `type: course` to prove `type` is an open string. |
| `intro-micro-fall-2026.md` | current | Second course. Shares "fall 2026" and "syllabus" with the first so single-token queries are ambiguous. |
| `startup-survey-pipeline.md` | current | Research pipeline run with Claude Code. Links a research assistant. Vocabulary far from teaching notes. |
| `labor-markets-paper.md` | current | Coauthored paper. Links coauthor with a multi-alias. |
| `rubric-redesign.md` | current | Small finished project. Confirms projects with an end still stay `current` until a claim changes. |

### `40-areas/` (12)

| File | Status | Why it exists |
|---|---|---|
| `teaching-load-2025-09.md` | superseded | Oldest link in a three-note chain. |
| `teaching-load-2026-01.md` (exists) | superseded | Middle of the chain. |
| `teaching-load-2026-09.md` (exists) | current | Head of the chain. Default query must land here. |
| `teaching-load-committee.md` | current | Title contains "teaching load" as a substring. Substring trap. |
| `office-hours-2026-01.md` | superseded | Old schedule. |
| `office-hours.md` | current | New schedule. Daily logs also mention office hours in passing; this must outrank them. |
| `assessment-policy.md` | current | id is `assessment-policy`, title is "Curve and grading policy". Exact id and exact title diverge. Daily 2026-09-01 points here. |
| `advising-load.md` | current | Plain area note. Filler that shares "load" with teaching load. |
| `department-service.md` | current | Mentions the chair by link. Generic-to-named support. |
| `sabbatical-plan.md` | current, `confidence: low` | Says timing is undecided. Near-miss abstention target ("when is the sabbatical"). Carries `low` so the card must show it. |
| `lab-budget.md` | current | Says the research budget is 12,000. Half of the planted contradiction. |
| `research-account.md` | current | Says the research budget is 9,500. Other half. Both `current`, same fact, different numbers. |

### `50-people/` (6)

| File | Status | Why it exists |
|---|---|---|
| `samir-okonkwo.md` (exists, add `aliases: Sam`) | current | Single alias. Passes today. |
| `priya-natarajan.md` | current | `aliases: PN, Dr. Natarajan`. Multi-alias. Exact-alias match fails (one string), but keyword scoring finds `pn` in the alias string and scores a title hit. |
| `dana-whitfield.md` | current | Department chair. Target of "who is the department chair." |
| `marcus-bell.md` | current | Teaching assistant. |
| `marcus-bellamy.md` | current | Journal editor. Near-duplicate name with the TA. Query "Marcus Bell" must return Bell only; "Marcus" must not flag them as contradicting each other. |
| `yuki-tanaka.md` | current | Research assistant on the survey pipeline. `confidence: medium`. |

### `60-decisions/` (5)

| File | Status | Why it exists |
|---|---|---|
| `drop-evening-section.md` (exists) | current | Mentions the chair and "enrollment was already thin" with no number. Near-miss abstention source. |
| `adopt-codex-for-grading.md` | current | Tool decision. Vocabulary overlaps `working-preferences.md`. |
| `decline-summer-teaching.md` | superseded | Reversed decision. |
| `accept-summer-teaching.md` | current | The reversal. Supersession across decisions, not just areas. |
| `switch-econometrics-textbook.md` | current | Links the long course note. Wikilink-hop target for later. |

### `10-daily/` (5)

| File | Why it exists |
|---|---|
| `2026-08-20.md` | Day of the evening-section decision. Mentions it in passing. |
| `2026-08-28.md` | Mentions office hours and a coffee with Priya. Timeline-only fact ("when did Alex last meet Priya"). |
| `2026-09-01.md` (exists) | Points at the assessment note. |
| `2026-09-02.md` | Mentions the budget number from `lab-budget.md`. A third voice in the contradiction that must not be counted as a state note. |
| `2026-09-03.md` | Plain day. Filler. |

### `sources/` (2)

| File | Why it exists |
|---|---|
| `notion-export-2026-08-15.md` | Raw dump with frontmatter (`type: source`, `confidence: low`), titled by export date. Repeats much of the long course note in the body. The filed note must outrank the dump. The id and title carry no course words, otherwise id scoring puts the dump on top. |
| `pasted-email-chair.md` | No frontmatter. Loader skips it. Must never appear in results. Proves skip-not-reject. |

## Planted problems, mapped to families

Each row is one problem, the queries that will become fixtures, the family it
serves, and what today's `recall` does. "Passes today" rows become gold items
in the first baseline. "Fails today" rows are capability targets. "Passes for
the wrong reason" rows are the most valuable: they pass now and will flip when
the engine gets smarter, and the flip must be understood, not waved through.

| # | Problem | Query | Family | Today |
|---|---|---|---|---|
| 1 | Three-note supersession chain | `teaching load` | supersession | Passes. Status filter drops the old two. |
| 2 | Chain under `--historical` | `teaching load` (historical) | supersession | Passes. Both old notes appear labeled `superseded`. `decline-summer-teaching` also matches. |
| 3 | Reversed decision | `summer teaching` | supersession | Passes. Current accept note first; the superseded decline note is absent. Phase 2 dailies `2026-03-02` and `2026-04-21` and `grant-call-pdf-text` also match, so `contradicted_by` fires across four current hits. |
| 4 | Title substring trap | `teaching load` | named-thing | Passes by tie-break. Both `teaching-load-2026-09` and `teaching-load-committee` score the same; path sort puts `2` before `c`. Fragile. Good early tripwire. `contradicted_by` fires on the pair because any two current notes matching the query are marked as contradicting. |
| 5 | Exact id vs exact title diverge | `assessment-policy` and `Curve and grading policy` | named-thing | Passes. Both are exact matches. |
| 6 | Single alias | `Sam` | named-thing | Passes. |
| 7 | Multi-alias | `PN` | named-thing | Passes for the wrong reason. Exact-alias match does not fire (`aliases` is one string), but `_keyword_score` finds `pn` inside the alias string and scores a title hit. |
| 8 | Near-duplicate names | `Marcus Bell` | named-thing | Passes. Exact title suppresses the keyword hit on Bellamy. |
| 9 | Near-duplicate names, ambiguous | `Marcus` | contradiction (negative) | Passes for the wrong reason, then fails. Both notes return, and `contradicted_by` links them although they do not disagree. This is the case that shows `contradicted_by` fires on any two current hits. |
| 10 | Generic-to-named | `who is the department chair` | named-thing | Fails. Stopwords leave `department chair`; hits Dana, `department-service`, and `drop-evening-section`, and flags all three as contradicting. Capability target. |
| 11 | Buried fact in a long note | `final exam weight` | citation | Passes. Claim line is 64 (the buried 40 percent weight). A `supersedes` line added in phase 2 moved it from 63. `expect_line` guards it. |
| 12 | Planted contradiction | `research budget` | contradiction | Passes. Both notes return, each listing the other. |
| 13 | Daily log mentions the same number | `research budget` | contradiction | Passes for the wrong reason. Daily `2026-09-02` also matches and is listed as a third contradicting note. A daily entry is timeline, not state. Deciding how the engine treats `type: daily` is an open question below. |
| 14 | Source dump vs filed note | `econometrics syllabus` | named-thing | Passes. The filed note scores on id plus body; the dump scores on body only. The dump appears below it with `confidence: low`. |
| 15 | File with no frontmatter | any | all | Passes. `pasted-email-chair.md` has no frontmatter, so the loader skips it. |
| 16 | State note vs daily mention | `office hours` | named-thing | Passes. Exact title match on `office-hours.md` suppresses every keyword hit, so the daily notes never return. Title boost is not what does it; if the title were "Office hours (fall)" the dailies would appear below it. |
| 17 | Clean abstention | `parking permit` | abstention | Passes. Zero hits. |
| 18 | Near-miss abstention | `evening elective enrollment` | abstention | Fails. `drop-evening-section` returns, and daily `2026-08-19` also matches, so `contradicted_by` fires. The decision note says enrollment was thin and gives no number. Token matching cannot tell "mentions the topic" from "answers the question." Capability target. Note that adding `number` to the query would make the engine pass by accident, since `recall` requires every token to match; the query is kept to words the note contains. |
| 19 | Near-miss abstention, low confidence | `sabbatical start date` | abstention | Fails. `sabbatical-plan` matches and is returned. The card carries `confidence: low`, which is the honest part. Capability target. |
| 20 | Open `type` string | `econometrics` | check | Passes. `check` accepts `type: course`. |

Fourteen of twenty pass today. That is the right starting ratio. A corpus where
everything passes teaches nothing; one where nothing passes cannot seed a
baseline.

## Deny list and grep guard

The spec requires a CI guard that fails the build if a real name appears in
`evals/brain/`. Two lists:

- **Committed**, `evals/deny-list.txt`: names that are already public in this
  repo or its history. Khaled's name, the product's prior name, the
  university and employer names that appear in `docs/`. Short, and it is
  fine for the world to see it.
- **Private**, `~/vault/90-meta/evals/deny-list.txt`: every person, employer,
  course code, and place name from the vault. Never committed here. Run by
  the same script as part of the Layer 2 workflow.

Committing the full list would leak who Khaled knows, which is the thing the
guard exists to protect. Gbrain commits one list because its author is
public about his contacts. We are not.

The guard is a pytest test, `tests/test_eval_brain_guard.py`, that reads a
deny-list path (default the committed one, overridable by an environment
variable for the private run), lowercases both sides, and fails on any
substring hit in any file under `evals/brain/`. Pytest already runs in CI,
so there is no new CI step.

## Process

Order matters because notes link to people, and links to files that do not
exist yet are easy to leave dangling.

1. **Seed.** Copy `examples/demo-brain/` to `evals/brain/`. Write
   `evals/brain/README.md`: two paragraphs on purpose and persona, then the
   planted-problems table from this file, trimmed to problem, query, family.
   Verify: `personal-memory check evals/brain` passes.
2. **People.** Write the six person notes. Add `aliases` to Samir and
   Priya. Verify: `check` passes; `personal-memory recall evals/brain Sam`
   returns Samir.
3. **Areas.** Write the twelve area notes, including the contradiction pair
   and the three-note chain. Verify: `check` passes; `recall "teaching load"`
   returns the 2026-09 note first; `recall "research budget"` returns both
   budget notes.
4. **Projects and decisions.** Write the twelve notes. The long
   econometrics note goes last so its buried line number is fixed once and
   recorded. Verify: `check` passes; `recall "final exam weight"` reports the
   buried line.
5. **Daily and sources.** Write the five daily entries and two source files.
   Verify: `check` passes; `recall "chair email"` does not return
   `pasted-email-chair.md`.
6. **Record reality.** Run every query in the planted-problems table. Write
   what actually happened into the `Today` column of `evals/brain/README.md`.
   Where this plan's prediction was wrong, fix the table, not the note. That
   is the pre-registration habit applied to the corpus itself.
7. **Guard.** Write `evals/deny-list.txt` and the pytest guard. Verify: the
   suite passes; plant one denied word in a scratch note, watch it fail,
   remove the word.
8. **Link check.** Every `[[id]]` in `evals/brain/` must resolve to a note id
   in the corpus. `check` does not validate links yet, so run a one-off
   script from `/tmp` and do not commit it. If dangling links keep
   appearing, that is a reason to add link validation to `check` in a later
   change, with its own spec update.
9. **Docs.** Add one sentence to the Corpus section of `docs/evals-spec.md`
   pointing here. Add `evals/brain/` and this file to `AGENTS.md`.

Done means: 39 notes, `check` clean, guard green, every planted problem has a
recorded `Today` value, and the corpus has not been touched by a fixture file
yet. Fixtures are step 4 of the spec's order and start only after this.

## Not in this phase

- Fixture TOML files, the runner, adapters, baselines (spec steps 2 to 5).
- Model-generated notes (spec step 10).
- A second persona.
- Link validation inside `check`.
- Any change to `examples/demo-brain/`. The demo stays small and clean.

## Phase 2: enrichment

Written 2026-09-09, after phase 1 landed (38 notes, 2,600 words, 20 planted
problems with observed results in `evals/brain/README.md`).

### Why a second phase

After this phase the corpus is frozen for the rest of v1. Fixtures grow;
notes do not. That means the corpus has to already hold what every v1
feature will be measured against: wikilink hops, `get` by id and path, the
ripgrep baseline row, a holdout slice (needs 60 or more fixtures), the
Layer 3 question bank, the filing loop over `sources/`, and later a vector
arm. Phase 1 also barely tests ranking: 12 of the 20 planted queries return
one or two cards, so id, title, and body weights rarely decide anything.

### Targets

| Measure | After phase 1 | After phase 2 |
|---|---|---|
| Indexed notes (frontmatter present) | 38 | 109 |
| Files under `sources/` with no frontmatter | 1 | 3 |
| Words | 2,600 | 8,603 |
| People | 6 | 20 |
| Daily notes | 5 | 25 |
| Sources | 2 | 7 |
| Long notes (60 or more lines) | 1 | 6 |
| Supersession chains | 4 | 10 (2 with no current successor) |
| Superseded notes | 5 | 12 |
| Folders | 7 | 9 (`70-meetings/`, `80-reading/` added) |
| Distinct supportable queries | 22 | 87 |
| Fixture families | 5 (+ `check`) | 8 (+ `check`, `get`, `filing` rows) |

The word target cannot be met with 8 to 25 line notes alone (110 such notes
is about 7,500 words). Rule 8 is relaxed for this phase: six long notes and
five long `sources/` dumps carry roughly half the words. That is realistic;
real brains have a few dumps that dwarf the filed notes.

### New inventory

Every row names the item (a to p) from the enrichment goal it serves.
Ids are final; waves below depend on them not changing.

#### `50-people/` (14 new, 20 total)

| File | Status | Why it exists |
|---|---|---|
| `grant-oyelaran.md` | current | Program officer at the funding foundation. First name is a common noun next to the grant application project (k). `Grant` becomes a four-way id tie (a). |
| `kjaer.md`, id `soren-kjaer` | current | Title "Søren Kjær", visiting scholar. Diacritics: TOKEN_RE turns "Søren" into `ren` (k). Path stem differs from id (c). |
| `tobias-renquist.md` | current | Former student, reference letter. No note links to him; dailies name him in prose only (k). |
| `ines-castellanos.md` | current | Econometrics TA. Role lookup "TA for econometrics" and a second TA so `TA` has two golds (n, i). |
| `felix-brandvold.md` | current | Second coauthor on the labor markets paper. Multi-entity question (n). |
| `nadia-ferrante.md` | current | Curriculum group colleague. Dailies refer to her by surname only (k). |
| `mira-solberg.md` | current | Physiotherapist, linked from the health area. Daily writes "mira" lowercase (k, p). |
| `theo-lindqvist.md` | current | Property manager, linked from home admin (p). |
| `bea-okonkwo.md` | current | Data librarian. Shares a surname with Samir so `Okonkwo` is ambiguous (a). |
| `jonas-weir.md` | current | Conference discussant. Daily misspells him "Jonas Wier" (k). |
| `sam-delacroix.md` | current | Student team captain. Real first name collides with Samir's alias `Sam` (a, d). |
| `harriet-obuya.md` | current | Associate dean who signs sabbatical and release forms. Appears in minutes (a). |
| `rosalind-tembe.md` | current | Colleague who taught Alex to use coding agents. Linked from the learning area (p). |
| `kofi-amankwah.md` | current | Master's advisee. Linked from thesis supervision (n). |

#### `30-projects/` (7 new, 14 total)

| File | Status | Why it exists |
|---|---|---|
| `grant-application.md`, id `research-grant-2026` | current | Grant application. Path differs from id (c). Links [[grant-oyelaran]] and [[lab-budget]] (b). Says the amount is not settled; must not use the phrase "research budget" so problem 12 stays a pair plus one daily. |
| `conference-trip-2026-06.md` | current, `type: trip` | Two-day conference. Links [[soren-kjaer]], [[jonas-weir]]. Filed counterpart of the programme dump (g, p). |
| `intermediate-macro-fall-2025.md` | superseded, no `superseded_by` field because nothing replaced it | Course taught once. "Fact that stopped being true and was never replaced" (j). |
| `econometrics-fall-2025.md` | superseded, `superseded_by: econometrics-fall-2026` | Second long note (60 to 90 lines). Same section layout as the 2026 note; final exam weight 35 percent, not 40. Temporal query under `--historical` (m, a). |
| `reading-group-causal-inference.md` | current | Reading group. Adds "identification" and "difference in differences" pressure against the course and reading notes (a). |
| `replication-workshop-2026.md` | current | Week 13 workshop. Shares "replication" with the long course note; body-only target (a). |
| `thesis-supervision-amankwah.md` | current | Links [[kofi-amankwah]]. Says the defense date is not set: near-miss abstention (j). Milestones span a paragraph (l). |

#### `40-areas/` (10 new, 22 total)

| File | Status | Why it exists |
|---|---|---|
| `health.md` | current, `confidence: medium` | Shoulder, sleep, "running on empty by mid-afternoon". Paraphrase target for `burnout` (h, p). Links [[mira-solberg]]. |
| `home-admin.md` | current | Lease, renewal date, "lease payment" (never "rent"). Paraphrase target for `rent` (h). Carries two unknown frontmatter keys, `tags` and `source` (k). |
| `learning-coding-agents.md` | current | Alex learning Claude Code and Codex, with [[rosalind-tembe]]. Learning area (p). What-works list spans a paragraph (l). |
| `exam-integrity.md` | current | "Strategic exam sitting", deferred sittings. Paraphrase target for `gaming the curve` (h). Mentions the curve without disagreeing with `assessment-policy` (i). |
| `office-hours-2025-09.md` | superseded, **no `superseded_by`** although `office-hours-2026-01` replaced it | Fall 2025 schedule, Mondays 1 to 3. Broken chain link (k). Temporal target (m). |
| `advising-load-2025-09.md` | superseded, `superseded_by: advising-load` | Eighteen advisees. Temporal pair with the current note (m). |
| `commute.md` | superseded, no successor | Cycled to campus; stopped after a move. Second never-replaced fact (j). |
| `data-purchases.md` | current | Data line items, links [[bea-okonkwo]]. Says "data line", not "budget" (a). |
| `committee-service-2025.md` | superseded, `superseded_by: department-service` | Last year's committees. Temporal question "what committees in 2025" (m). |
| `journal-refereeing.md` | current | Refereeing load; names the Northbridge Review. Contradiction negative with [[marcus-bellamy]] (i). `review` pressure (a). |

#### `60-decisions/` (6 new, 11 total)

| File | Status | Why it exists |
|---|---|---|
| `adopt-open-textbook-intro-micro.md` | current | Rationale spans three lines (l). Shares "textbook" with the econometrics switch (a). |
| `decline-conference-panel-2027.md` | current, as_of 2026-08-14 | Declined a future panel. Date in the title is later than the as_of range on purpose; as_of is the decision date (m). |
| `move-office-hours-to-afternoon.md` | current | Long id with four query tokens. Outscores the schedule note on `afternoon office hours` (a, d). |
| `use-claude-code-for-pipeline.md` | current | Vocabulary overlaps the pipeline and the learning area (a). |
| `accept-associate-editor-role.md` | superseded, `superseded_by: decline-associate-editor-role` | Second reversed decision. "editor" pressure (a). |
| `decline-associate-editor-role.md` | current, `supersedes: accept-associate-editor-role` | The reversal. Names the Northbridge Review (i). |

#### `70-meetings/` (new folder, 6)

| File | Status | Why it exists |
|---|---|---|
| `committee-minutes-2026-05-08.md` | current, `type: meeting` | Load committee minutes. "release request" appears (i). |
| `committee-minutes-2026-09-04.md` | current, `type: meeting` | Load committee minutes. Filed counterpart of the transcript dump (g). Motion text spans three lines (l). Links [[dana-whitfield]], [[nadia-ferrante]], [[harriet-obuya]]. |
| `curriculum-group-2026-02-05.md` | current | Where the open textbook was first raised. Links the decision (b). |
| `meeting-grant-officer-2026-07-22.md` | current | Links [[grant-oyelaran]]. One-hop source for "who is the program officer" (b). |
| `meeting-chair-staffing-2026-08-19.md` | current | Day before the evening section was dropped. `chair` pressure (a, o). |
| `sponsor-call-quill-timber-2026-08-05.md` | current | Says "their marketing lead" with no name. Mentioned-but-not-named abstention (j). |

#### `80-reading/` (new folder, 5)

| File | Status | Why it exists |
|---|---|---|
| `reading-calder-markets-in-numbers.md` | current, `type: reading` | Notes on the textbook. "identification" pressure (a, p). |
| `reading-hiring-frictions-survey.md` | current | Fictional survey paper. Overlaps the labor paper (a). Saved with **CRLF line endings** in the noise pass (k). |
| `reading-agents-for-non-programmers.md` | current | Fictional essay on coding agents. Overlaps the learning area (a). |
| `reading-diff-in-diff-handbook.md` | current | Third long note (60 or more lines). Dailies 2026-09-03 and 2026-09-05 mention it (a, o). |
| `reading-strategic-exam-behavior.md` | current | The paper behind `exam-integrity`. Gives the paraphrase target a second candidate (h, a). |

#### `10-daily/` (20 new, 25 total)

| File | Why it exists |
|---|---|
| `2025-09-03.md` | First week of fall 2025; intermediate macro and the seminar in passing (o, j). |
| `2025-09-18.md` | Mentions Monday office hours; must not outrank `office-hours-2025-09` under `--historical` (m). |
| `2025-10-09.md` | Reference letter for "Tobias", prose only, no link (k). |
| `2025-11-07.md` | Night before the case competition (o). |
| `2025-11-08.md` | Case competition day (o). |
| `2025-12-12.md` | Grading the seminar; "running on empty" first appears (h). |
| `2026-01-12.md` | Office hours moved to Monday and Wednesday (m, o). |
| `2026-02-05.md` | Curriculum group; "Ferrante" surname only (k). |
| `2026-03-02.md` | Declined summer teaching, in passing (o). |
| `2026-04-21.md` | Accepted summer teaching after the chair asked again (o). |
| `2026-05-08.md` | Committee day; release requests (i). |
| `2026-06-10.md` | Conference day one; "Jonas Wier" misspelled (k). |
| `2026-06-11.md` | Conference day two; "Søren" with the diacritic in the body (k). |
| `2026-07-22.md` | Grant officer meeting; "the grant call" as a common noun (k). |
| `2026-08-05.md` | Sponsor call (o). |
| `2026-08-19.md` | Staffing meeting with the chair (o). |
| `2026-08-25.md` | Physio visit, "saw mira" lowercase (k). |
| `2026-08-31.md` | "Put off the results table again" (h). |
| `2026-09-04.md` | Pipeline "next step" line; committee vote; "Ferrante" (o, k). |
| `2026-09-05.md` | Last date in range. Closes the timeline (o). |

#### `sources/` (5 new, 7 total)

| File | Frontmatter | Why it exists |
|---|---|---|
| `transcript-committee-2026-09-04.md` | yes, `type: source`, `confidence: low` | Meeting transcript, 600 or more words. Filed counterpart: `committee-minutes-2026-09-04`. Source swamp (g, a). |
| `chat-log-yuki-pipeline-2026-09-04.md` | none | Chat log about the dedup fix. No filed counterpart; only daily 2026-09-04 mentions it (g). Loader skips it. |
| `grant-call-pdf-text.md` | yes | PDF-to-text of the call for proposals. Filed counterpart: `research-grant-2026`. Uses "award" and "costs", never "budget" (g). Fourth `grant` id hit (a). |
| `pasted-email-editor-decision.md` | none | Decision letter from the journal. No filed counterpart (g). |
| `conference-programme-2026-06.md` | yes | Programme dump with many names, including "Søren Kjær". Filed counterpart: `conference-trip-2026-06`. Its id carries both query words, so it outranks the filed note (a, g). |

#### Edits to existing notes

| File | Edit | Why |
|---|---|---|
| `30-projects/undergrad-case-competition.md` | Add `supersedes: case-competition-2025` in frontmatter and body | Fixes the one-way chain; makes the hop into a superseded note possible (b). |
| `30-projects/labor-markets-paper.md` | Add `[[felix-brandvold]]` to the coauthor line | Multi-entity question (n). |
| `30-projects/econometrics-fall-2026.md` | Add `supersedes: econometrics-fall-2025` | Temporal chain (m). Body word count for the 2026 note is unchanged since links are stripped from scoring. |
| `40-areas/advising-load.md` | Add `supersedes: advising-load-2025-09` | Temporal chain (m). |
| `40-areas/department-service.md` | Add `supersedes: committee-service-2025` | Temporal chain (m). |
| `10-daily/2026-09-01.md` | Turn "the assessment note" into `[[assessment-policy]]` | Daily-to-state hop (b). |
| `60-decisions/adopt-codex-for-grading.md` | Change `as_of` from 2026-08-12 to 2026-08-05 | Internal date consistency: the decision must precede the rubric work that used Codex (`rubric-redesign` ended 2026-08-10). Temporal family (m). |
| `evals/brain/README.md` | Append rows 21 to 85 with observed results and the commit | Wave 4. |

`office-hours-2026-01.md` is deliberately not edited: it stays without a
`supersedes` line so the break in that chain is real from both sides.
`sources/pasted-email-chair.md` is also left alone: it confirms a Thursday
seminar room that no current note mentions, but a raw dump being slightly
wrong is realistic and the file is not indexed.

### New planted problems

Numbering continues from phase 1. The letter in the Problem column is the
enrichment item. An asterisk on the query marks a ripgrep-discriminating case:
a dumb grep ranked by match count, or a grep with word boundaries, gives a
different top result than our engine. `Today` is the prediction from the
engine code; wave 4 records what happened.

| # | Problem | Query | Family | Today |
|---|---|---|---|---|
| 21 | (a) Single token, three id matches | `load` | named-thing | Passes for the wrong reason. `advising-load`, `teaching-load-2026-09`, and `teaching-load-committee` all score 10 on id; path sort puts advising first. Six more body hits join them (both minutes, the transcript, `journal-refereeing`, `bea-okonkwo`, `nadia-ferrante`), so nine cards return and `contradicted_by` fires across all nine. Gold is `also_present` for the load note, not hit@1. |
| 22 | (a) Long decision id beats the state note | `afternoon office hours`* | named-thing | Fails. `move-office-hours-to-afternoon` scores 30 on id and returns first. `office-hours` scores 0: AND matching drops it because the schedule note never says "afternoon". Extra hit: `econometrics-fall-2026`. Gold is the schedule note. Id length inflates score. rg counts more mentions in the schedule note and gets it right. |
| 23 | (a) Title and id beat eight body hits | `grading policy`* | named-thing | Passes. `assessment-policy` scores 10 (id) plus 8 (title) against a body hit in the course note. The Codex decision lacks `policy` and does not return. `contradicted_by` fires on the pair. rg ranks the long course note first. |
| 24 | (a) Shared surname | `Okonkwo` | named-thing | Fails. Both `bea-okonkwo` and `samir-okonkwo` score 10; path sort puts Bea first. Gold is both present. `contradicted_by` fires on the pair (i). |
| 25 | (a, d) Alias collides with a real first name | `Sam`* | named-thing | Fails on `also_present`. Exact alias match on Samir suppresses every keyword hit, so `sam-delacroix` (id hit) never returns. rg finds both plus "same". |
| 26 | (a) Exact title through the collision | `Sam Delacroix` | named-thing | Passes. Exact title. |
| 27 | (k) First name that is a common noun | `Grant`* | named-thing | Fails. Four ids contain `grant` (`research-grant-2026`, `grant-oyelaran`, `meeting-grant-officer-2026-07-22`, `grant-call-pdf-text`); tie at 10; path sort puts `30-projects/grant-application.md` first. Gold is the person. A case-sensitive grep on "Grant" would find only the person and the dailies that capitalize him. |
| 28 | (a) Buried date in the grant note | `grant application deadline` | citation | Passes. `research-grant-2026` scores 10 (id) plus 8 (title "application") plus 1 and wins. The dump id `grant-call-pdf-text` contains `grant`, so it scores on id, not body only, and still ranks second. Claim line is the deadline line. `contradicted_by` fires on the pair. |
| 29 | (a) `review` pressure | `journal review` | named-thing | Passes. `journal-refereeing` scores 11 on id plus body; `decline-associate-editor-role` scores 2; `marcus-bellamy` scores 1 or 0. |
| 30 | (b) One hop | `labor markets paper editor` | hop | Fails. AND matching: the paper note lacks "editor"; the editor's note only links the paper, and links are stripped from the body. Zero cards. Gold `marcus-bellamy` via the paper note's link. |
| 31 | (b) Two hops | `journal for Priya's paper` | hop | Fails. Zero cards. Gold `marcus-bellamy` via `priya-natarajan` to `labor-markets-paper` to the editor. |
| 32 | (b) Hop into a superseded note | `case competition sponsor 2025` | hop | Fails by default: daily `2025-11-08` returns (it has the tokens) rather than the current project note, which has no "2025". Passes under `--historical` by id: `case-competition-2025` first, labeled superseded, plus the daily. Gold is `case-competition-2025` labeled superseded, reached through the new `supersedes` link. |
| 33 | (b, n) Generic-to-named through a meeting | `who is the program officer for the grant` | hop | Fails. `meeting-grant-officer-2026-07-22` scores 21 and returns first with the link on its claim line; gold is `grant-oyelaran`. |
| 34 | (b, n) Identity to project to people | `Alex's coauthor on hiring frictions` | hop | Fails. Zero cards: no note carries "alex" next to "hiring frictions". Gold `priya-natarajan` and `felix-brandvold` via the paper note. |
| 35 | (c) Get by id when path differs | `get research-grant-2026` | get | Passes. Id scan finds `30-projects/grant-application.md`. |
| 36 | (c) Get by path | `get 30-projects/grant-application.md` | get | Passes. |
| 37 | (c) Shared id prefix | `get office-hours` | get | Passes. Exact id; `office-hours-2025-09` and `office-hours-2026-01` do not match. |
| 38 | (c) Filename stem is not an id | `get kjaer` | get | Passes by returning nothing. `get soren-kjaer` and `get 50-people/kjaer.md` both return the note. |
| 39 | (c, g) Get a source with no frontmatter | `get sources/chat-log-yuki-pipeline-2026-09-04.md` | get | Returns nothing: `_load` requires frontmatter even for a path lookup. Whether the filing loop needs `get` to read raw sources is open; recorded so the decision is measured. |
| 40 | (d) Stopwords | `what is the curve policy`* | named-thing | Passes. Stopwords leave `curve policy`; `assessment-policy` scores 18. rg with all five words matches almost every note. |
| 41 | (d) Lowercase name | `priya`* | named-thing | Passes. Query and notes are lowercased. rg without `-i` misses every "Priya". |
| 42 | (d, n) Two-letter token matches inside words | `TA`* | named-thing | Fails. `ta` is a substring of `natarajan`, `tanaka`, `data-purchases`, and dozens of body words ("stack", "start", "table"). Gold is `marcus-bell` and `ines-castellanos`. rg with `-w` gets both. |
| 43 | (d) Status filter on a long chain | `econometrics final exam weight`* | supersession | Passes. Only the 2026 note; the 2025 note is superseded and hidden. rg returns both, 2025 first if it has more matches. |
| 44 | (m) Old weight under `--historical` | `econometrics final exam weight 2025` (historical) | temporal | Passes. `econometrics-fall-2025` scores 23 (id has econometrics and 2025) against 0 for the 2026 note, which never says 2025. Card labeled superseded; claim line is the 35 percent line. Default returns zero cards. |
| 45 | (m) Advisee count last year | `advising load 2025` (historical) | temporal | Passes under `--historical` (id 30 vs 20). Default returns zero cards, which the fixture records as expected v1 behavior. |
| 46 | (m, k) Broken chain under history | `office hours fall 2025` (historical) | temporal | Passes. `office-hours-2025-09` scores 38. The card cannot name what replaced it because `superseded_by` is missing, and `check` does not notice. |
| 47 | (m) Winter load | `what was the teaching load in winter 2026` (historical) | temporal | Passes. `teaching-load-2026-01` scores 38 (id 30 plus title "winter"). Default: zero cards, since the fall note has no "winter". |
| 48 | (o) Where we left off | `survey pipeline next step` | temporal | Passes for the wrong reason. The state note lacks "next" and "step", so AND matching drops it and daily `2026-09-04` is the only card. Add either word to the state note and the daily loses. |
| 49 | (m) Which figure is newer | `budget August statement` | temporal | Passes. Only `research-account` has all three tokens. The fixture cannot assert `as_of: 2026-08-15` because the format has no `expect_as_of`. Add the field when fixtures land. |
| 50 | (h) Paraphrase | `gaming the curve` | paraphrase | Fails. "gaming" appears nowhere; zero cards. Gold `exam-integrity` ("strategic exam sitting"). |
| 51 | (h) Paraphrase | `burnout` | paraphrase | Fails. Zero cards. Gold `health` ("running on empty"). |
| 52 | (h, d) Paraphrase with a substring trap | `rent`* | paraphrase | Fails. `rent` is inside "current" and "different"; three cards (`labor-markets-paper`, `rubric-redesign`, `reading-diff-in-diff-handbook`) at score 1, all marked contradicting. Gold `home-admin` ("lease payment") is absent. rg with `-w` returns nothing. |
| 53 | (h) Paraphrase into a daily | `procrastinating on the paper` | paraphrase | Fails. Zero cards. Gold daily `2026-08-31` ("put off the results table again"). |
| 54 | (h) Paraphrase | `AI tools for grading` | paraphrase | Fails. `ai` matches inside "said" and "email"; no note pairs it with both other tokens except by accident. Gold `adopt-codex-for-grading`. |
| 55 | (i) Agreeing notes flagged as contradicting | `midterm week 7`* | contradiction (negative) | Fails. The digit `7` is a one-character token and is dropped. Both course notes and the Notion dump return and list each other. rg keeps the 7. |
| 56 | (i) Two meetings, same phrase | `release request` | contradiction (negative) | Fails. Five cards: daily `2026-05-08` first, then `teaching-load-committee`, both minutes notes, and the transcript dump, each listing the others. |
| 57 | (i) Same journal, three notes | `Northbridge Review` | contradiction (negative) | Fails. `marcus-bellamy`, `journal-refereeing`, and `decline-associate-editor-role` return as a contradicting triple. |
| 58 | (i, n) Two people share a trait | `who prefers async comments` | contradiction (negative) | Fails. `working-preferences` and `samir-okonkwo` return and list each other. Gold is both present, no contradiction. |
| 59 | (j) Not in corpus | `dissertation defense date` | abstention | Passes. "dissertation" appears nowhere. |
| 60 | (j) Mentioned but not named | `sponsor contact at Quill and Timber` | abstention | Fails. The sponsor call note has every token and returns, but names nobody. |
| 61 | (j) Under-specified | `the meeting` | abstention | Fails. Stopwords leave `meeting`; sixteen cards return as a contradicting set (five meeting notes, two dailies, plus people, lab-budget, the load committee, and a decline). |
| 62 | (j) Superseded, never replaced | `intermediate macro` | abstention | Passes by default (zero cards). Under `--historical` the superseded note returns labeled. No field says "never replaced"; open. |
| 63 | (j) Superseded, never replaced, area | `commute` | abstention | Same shape as 62. Passes by default. |
| 64 | (j) Near miss on a date | `thesis defense date` | abstention | Fails. `thesis-supervision-amankwah` returns; it says the date is not set. |
| 65 | (k) Misspelled name | `Jonas Wier` and `Jonas Weir` | named-thing | First query fails: daily `2026-06-10` (the typo) and the conference programme dump return; the person note scores 0 on "wier". Second passes by exact title and never finds the daily. |
| 66 | (k) Surname only | `Ferrante`* | named-thing | Passes. Person id scores 10; two dailies and the minutes score 1. rg ranks by count and puts the minutes first. |
| 67 | (k) Lowercase mention | `mira`* | named-thing | Passes. Id 10 over the lowercase daily. rg without `-i` misses the title. |
| 68 | (k) Diacritic | `Søren`, `Søren Kjær`, `Soren Kjaer` | named-thing | `Søren` passes for the wrong reason: TOKEN_RE splits it into `s` and `ren`, drops `s` as too short, and `ren` substring-matches many ids and bodies, so twenty cards return. `Søren Kjær` passes by exact title: both sides normalize to `s ren kj r`, so exact match fires and suppresses keyword hits. `Soren Kjaer` passes on id. |
| 69 | (k) Person nobody links to | `Tobias Renquist` and `reference letter` | named-thing | Both pass (exact title; body). A hop implementation must not require inbound links. |
| 70 | (k) Missing `superseded_by` | `check` | check | Passes, which is the finding: `check` validates fields, not chains. |
| 71 | (k) CRLF note | `hiring frictions survey` | citation | Passes. The frontmatter regex allows `\r?\n`, `splitlines` handles CRLF, `strip` removes the stray `\r` from the claim. Watch the claim string in wave 4. |
| 72 | (k) Unknown frontmatter keys | `lease renewal` and `get home-admin` | check | Passes. Extra keys land in `extra` and are ignored. |
| 73 | (l) Claim spans three lines | `open textbook rationale intro micro` | citation | Passes for the wrong reason. The card is the single line with the most token hits; the rationale is three lines. `expect_line` must be set to the line the engine picks until the range-overlap rule exists. |
| 74 | (l) Motion spans three lines | `committee motion release cap` | citation | Same shape as 73. |
| 75 | (n) Role lookup, course outranks person | `who is the TA for econometrics`* | named-thing | Fails. Course note scores 11 (id plus `ta` inside "stats"); `ines-castellanos` scores 2. Gold is the person. |
| 76 | (n) Role lookup, second course | `who is the TA for intro micro`* | named-thing | Fails. `intro-micro-fall-2026` scores 21; `marcus-bell` scores 3. Matches what phase 1 already showed for this query. |
| 77 | (n) Multi-entity | `labor markets paper` | named-thing | Passes for the wrong reason. Exact title on the paper suppresses every keyword hit, so the coauthor notes never return. The editor is absent because his note links rather than restates, so a full answer needs a hop. |
| 78 | (n) Multi-entity phrased | `which people are on the labor markets paper` | hop | Fails. "which" is not a stopword and appears in no note with the other tokens; zero cards. |
| 79 | (o) Timeline fact | `case competition day` (historical) | temporal | Passes for the wrong reason. Neither project note says "day", so daily `2025-11-08` ranks first; `drop-evening-section` and `meeting-chair-staffing-2026-08-19` also match and `contradicted_by` fires. |
| 80 | (o) Daily mention through a link | `last met Priya` | temporal | Fails. Daily `2026-08-28` writes `[[priya-natarajan]]`; the link is stripped before scoring, so "priya" is not in its body. Zero cards. Links hide names from keyword search. |
| 81 | (o) Meeting note vs daily | `sponsor call` | named-thing | Passes. Meeting id scores 20; daily `2026-08-05` scores 2. |
| 82 | (g) Unfiled scan | none | filing | Not runnable today. Expected list once `unfiled` exists: `chat-log-yuki-pipeline-2026-09-04.md` and `pasted-email-editor-decision.md` unfiled; the other five have counterparts. `pasted-email-chair.md` has no counterpart either. How "filed" is marked is the feature's decision. |
| 83 | (g, a) Source swamp, tie | `release request vote`* | named-thing | Passes by tie-break. Minutes and transcript both score 3; path sort puts `70-meetings/` before `sources/`. rg counts the transcript's repeats and puts the dump first. Fragile, like row 4. |
| 84 | (g, a) Source id carries the query words | `conference programme` | named-thing | Fails. The dump id scores 20; the trip note scores 11. The dump outranks the filed note with `confidence: low`. Contrast with row 14. |
| 85 | (c) Path lookup for a diacritic person | `get 50-people/kjaer.md` | get | Passes. Frontmatter intact, title keeps the diacritics. |

Predicted: 35 pass (7 for the wrong reason), 28 fail, 2 not runnable or
open (39, 82). With phase 1 that is 49 of 85 passing, which keeps the
baseline seedable while leaving hills to climb in every new family.
Observed 2026-09-09: 35 pass (7 for the wrong reason: 21, 48, 68, 73, 74,
77, 79), 28 fail (22, 24, 25, 27, 30, 31, 32, 33, 34, 42, 50, 51, 52, 53,
54, 55, 56, 57, 58, 60, 61, 64, 65, 75, 76, 78, 80, 84), 2 not runnable
(39, 82).

### Layer 3 question bank

This table is the source for the Layer 3 set when the MCP server lands
(`docs/evals-spec.md`, Layer 3). Twenty questions, each answerable with
`recall` and `get` alone. Lines for new notes are recorded in wave 4;
"title line" means the gold card is the exact-match title card.

| # | Question | Gold path | Gold line | Gold status | Abstain |
|---|---|---|---|---|---|
| L1 | What is Alex's teaching load this term? | `40-areas/teaching-load-2026-09.md` | 12 | current | no |
| L2 | What was the teaching load in winter 2026? | `40-areas/teaching-load-2026-01.md` | 13 | superseded | no |
| L3 | Who is the department chair? | `50-people/dana-whitfield.md` | 11 | current | no |
| L4 | What is the final exam weight in econometrics? | `30-projects/econometrics-fall-2026.md` | 64 | current | no |
| L5 | What is the research budget? | `40-areas/lab-budget.md` and `40-areas/research-account.md` | 11 and 11 | current, both | no; must report both |
| L6 | Who is Sam? | `50-people/samir-okonkwo.md` | title line (10) | current | no |
| L7 | When are office hours? | `40-areas/office-hours.md` | 12 | current | no |
| L8 | Does Alex have a parking permit? | none | none | none | yes, not in corpus |
| L9 | When does the sabbatical start? | `40-areas/sabbatical-plan.md` | 11 | current, confidence low | no; answer is "undecided" |
| L10 | Which journal has the labor markets paper? | `50-people/marcus-bellamy.md` | 11 | current | no |
| L11 | Who sponsored the 2025 case competition? | `30-projects/case-competition-2025.md` | 14 | superseded | no |
| L12 | Who is the program officer on the grant? | `50-people/grant-oyelaran.md` | title line | current | no |
| L13 | Who is the TA for intro micro? | `50-people/marcus-bell.md` | 11 | current | no |
| L14 | Who is the TA for econometrics? | `50-people/ines-castellanos.md` | 11 | current | no |
| L15 | What did Alex decide about summer teaching? | `60-decisions/accept-summer-teaching.md` | 12 | current | no |
| L16 | Is Alex still teaching intermediate macro? | `30-projects/intermediate-macro-fall-2025.md` | title line | superseded, no successor | no; answer is "no, and nothing replaced it" |
| L17 | Who is the sponsor's contact at Quill and Timber? | none | none | none | yes, mentioned but not named |
| L18 | Where did we leave off on the survey pipeline? | `10-daily/2026-09-04.md` | 11 | current | no |
| L19 | What did the meeting decide? | none | none | none | yes, under-specified; agent should ask which meeting |
| L20 | What were office hours in fall 2025? | `40-areas/office-hours-2025-09.md` | title line | superseded | no |

Seventeen answerable, three abstentions, one contradiction, five that need a
superseded card. Grading is code: path present, line inside the cited range,
status stated.

### Build order

Ids are assigned above, so waves 2a to 2e can run in parallel without
collisions. Links to notes in another lane are allowed; the link check in
wave 4 catches anything dangling.

1. **People.** Write the 14 person notes. Verify:
   `personal-memory check evals/brain && personal-memory recall evals/brain Okonkwo`
   returns two cards.
2. **Folders, in parallel.**
   - 2a. Projects and decisions (13 notes) plus the five frontmatter edits
     to existing project and area notes. Verify:
     `personal-memory recall evals/brain --historical "econometrics final exam weight 2025"`
     returns the 2025 note labeled superseded.
   - 2b. Areas (10). Verify: `personal-memory recall evals/brain "gaming the curve"`
     returns zero cards and `personal-memory recall evals/brain "exam sitting"`
     returns `exam-integrity` first.
   - 2c. Meetings and reading (11). Verify:
     `personal-memory recall evals/brain "release request"` returns three cards.
   - 2d. Daily (20) plus the link edit to `2026-09-01`. Verify:
     `personal-memory recall evals/brain "survey pipeline next step"` returns
     daily `2026-09-04`.
   - 2e. Sources (5). Verify: `personal-memory check evals/brain` reports 108
     notes and 5 skipped (README, AGENTS, three raw files).
3. **Noise pass.** Convert `reading-hiring-frictions-survey.md` to CRLF
   (`python -c` with `replace("\n", "\r\n")`; do not use an editor that
   normalizes). Confirm `office-hours-2025-09.md` has no `superseded_by`.
   Confirm the typo, surname-only, lowercase, and diacritic mentions are in
   the dailies named above. Add `tags` and `source` keys to `home-admin.md`.
   Verify: `python -m pytest -q` passes (guard and check), and
   `file evals/brain/80-reading/*.md` shows exactly one CRLF file.
4. **Integration.** Run every query in rows 1 to 85 (both default and
   `--historical` where a row says so). Append rows 21 to 85 to the README
   table with observed results, date, and commit. Re-record rows 1 to 20:
   new notes change several of them (row 21 now shadows row 1's tie-break;
   `grading` and `chair` pressure grew). Fill the wave 4 lines in the Layer 3
   table. Run the link check from `/tmp` (every `[[id]]` resolves). Record
   word count and note count against the Targets table. Verify:
   `python -m pytest -q && personal-memory check evals/brain` clean, README
   has 85 rows.

Done means: 108 indexed notes, 3 skipped raw files, about 15,000 words,
`check` clean, guard green, every row 1 to 85 has an observed value, every
link resolves, the Layer 3 table has no "wave 4" cells left.

### Freeze rule

After wave 4 the corpus is frozen for the rest of v1.

- A note changes only to fix a defect that a fixture found (wrong gold,
  dangling link, a rule violation). Never to make a fixture pass.
- Every such change gets a dated line in a "Changes since freeze" section at
  the bottom of `evals/brain/README.md`: file, what changed, which fixture
  found it.
- New coverage is added as fixtures, not notes. If a family cannot be
  expressed against the frozen corpus, that is a phase 3 proposal with its
  own inventory table, not an edit.
- The content hash in the eval receipt is the enforcement: a changed hash
  without a README line is a review failure.

## Open

- **Daily notes and contradiction.** Problem 13 shows a `type: daily` entry
  being counted as a contradicting state note. The vault's own rule is that
  daily entries are timeline, not state. The engine has no such rule yet.
  Options: exclude `type: daily` from `contradicted_by`, or leave it and let
  the fixture fail until a rule is chosen. Leaning toward the fixture
  failing first so the rule is measured, not assumed.
- **`expect_confidence`.** Problem 19 wants to assert that the returned card
  carries `confidence: low`. The fixture format in the spec has no such
  field. Adding it is a one-line spec change; do it when fixtures land.
- **Course titles vs codes.** Real courses have codes and users will search
  by them. Fictional codes risk colliding with real ones. Current choice is
  titles only. Revisit if a Layer 2 failure shows code-style queries matter.
- **`get` fixtures.** Rows 35 to 39 and 85 test `get`, but the fixture
  format only describes `recall` queries. Either add a `get` field to a
  case or give `get` its own fixture file. Decide when fixtures land.
- **`expect_as_of` and `expect_confidence`.** Row 49 needs to assert the
  card's `as_of`; rows 19 and 60 need to assert `confidence`. Neither field
  exists in the spec's fixture table. Both are one-line spec changes.
- **Links hide names from keyword search.** `_keyword_score` strips
  `[[priya-natarajan]]` before scoring, so a daily that links Priya has no
  "priya" token in its body (row 80). Timeline questions about people fail
  regardless of corpus. Engine finding, not a corpus gap.
- **Claim text keeps link markup.** The card `claim` is the raw line, so it
  shows `[[dana-whitfield]]` while scoring saw the stripped line (defect 12
  in the phase 2 audit). Decide whether cards render links or strip them.
- **Diacritic tokenization.** Row 68: TOKEN_RE `[a-z0-9]+` splits `Søren`
  into `s` and `ren`, drops `s` as too short, and `ren` substring-matches
  many ids and bodies, so a diacritic query returns twenty cards.
  Non-ASCII normalization is an engine gap the corpus now exposes.
