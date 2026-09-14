# Eval corpus plan

What is in `evals/brain/`, the fictional brain the Layer 1 evals run against,
and why each note exists.

Written 2026-09-09. The spec says what the corpus is for. The corpus is
frozen for the rest of v1. Live scores are in `evals/baselines/main.json`.

## Decision: whose brain this is

The corpus is the brain of **Alex Rivera**, the fictional economics lecturer
already in `examples/demo-brain/`. One persona, grown from 7 notes to 109
indexed notes.

Why one persona and why this one:

- A brain belongs to one person. Supersession chains, contradictions, and
  wikilinks only read as real inside one life. Mixing personas breaks that.
- Alex is shaped like the v1 user in `docs/v1-spec.md` (knowledge worker,
  daily coding-agent user, not an infrastructure person) without being any
  real person. Khaled's own brain is covered by Layer 2 (dogfood replay on
  `~/vault`). Layer 1 is the only place that shape gets tested, so the
  fictional corpus is where it lives.
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
   lists, so `aliases: Sam` is one string. Multi-alias notes are a comma
   string for the same reason.
4. One `current` note per changing fact, except the planted contradiction.
5. People are one file each in `50-people/`. Other notes link with
   `[[id]]` and never restate who the person is. A note may state the
   person's role in relation to that note ("TA: [[marcus-bell]]", "chair
   [[dana-whitfield]] agreed"); biography (background, preferences,
   history) stays in the person note.
6. `as_of` is when the claim was true. All dates fall between 2025-09-01
   and 2026-09-05.
7. Hand-written. No model-generated notes until hand-written notes stop
   covering the families.
8. Short by default, 8 to 25 lines. Six notes are deliberately long (60 or
   more lines) for dilution and source-swamp cases.

## Inventory

109 indexed notes. Demo-brain seeds are marked (exists). Folder counts in
the first tables are the original set; later tables add the rest of the
frozen corpus.

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
| `samir-okonkwo.md` (exists, add `aliases: Sam`) | current | Single alias. |
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
| `switch-econometrics-textbook.md` | current | Links the long course note. Wikilink-hop target. |

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

### Rest of the corpus

Later notes in the frozen set. Letters in the why-column are leftover
enrichment tags: a ranking, b hops, c revisit, d tokens, g dumps,
h paraphrase, i false contradiction, j abstention, k noise, l multi-line,
m temporal, n multi-entity, o timeline, p linked life notes.

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
| `grant-application.md`, id `research-grant-2026` | current | Grant application. Path differs from id (c). Links [[grant-oyelaran]] and [[lab-budget]] (b). Says the amount is not settled; must not use the phrase "research budget" so the budget contradiction stays a pair plus one daily. |
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

`office-hours-2026-01.md` is deliberately not edited: it stays without a
`supersedes` line so the break in that chain is real from both sides.
`sources/pasted-email-chair.md` is also left alone: it confirms a Thursday
seminar room that no current note mentions, but a raw dump being slightly
wrong is realistic and the file is not indexed.

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
word-boundary hit in any file under `evals/brain/`. Pytest already runs in CI,
so there is no new CI step.

## Layer 3 question bank

This table is the source for the Layer 3 set (`docs/evals-spec.md`, Layer 3).
The MCP server exists. The Layer 3 runner does not. Twenty questions, each
answerable with `remember` and `revisit` alone. "title line" means the gold
card is the exact-match title card.

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

## Freeze rule

The corpus is frozen for the rest of v1.

- A note changes only to fix a defect that a fixture found (wrong gold,
  dangling link, a rule violation). Never to make a fixture pass.
- New coverage is added as fixtures, not notes. If a family cannot be
  expressed against the frozen corpus, that is a new corpus proposal with
  its own inventory table, not an edit.
- The content hash in the eval receipt is the enforcement: a changed hash
  is a review event.

## Open

- **Daily notes and contradiction.** A `type: daily` entry that mentions a
  number can be counted as a contradicting state note. The vault's own rule
  is that daily entries are timeline, not state. The engine has no such
  rule yet.
- **Course titles vs codes.** Real courses have codes and users will search
  by them. Fictional codes risk colliding with real ones. Current choice is
  titles only. Revisit if a Layer 2 failure shows code-style queries matter.
- **`revisit` fixtures.** The fixture format only describes `remember` /
  `recall`-adapter queries. Either add a `revisit` field to a case or give
  `revisit` its own fixture file.
- **`expect_as_of`.** Some temporal questions need to assert the card's
  `as_of`. The fixture format has no such field. `expect_confidence` is
  already in the spec and used in fixtures.
- **Links hide names from keyword search.** `_keyword_score` strips
  `[[priya-natarajan]]` before scoring, so a daily that links Priya has no
  "priya" token in its body. Timeline questions about people fail
  regardless of corpus. Engine finding, not a corpus gap.
- **Claim text keeps link markup.** The card `claim` is the raw line, so it
  shows `[[dana-whitfield]]` while scoring saw the stripped line. Decide
  whether cards render links or strip them.
- **Diacritic tokenization.** TOKEN_RE `[a-z0-9]+` splits `Søren` into `s`
  and `ren`, drops `s` as too short, and `ren` substring-matches many ids
  and bodies. Non-ASCII normalization is an engine gap the corpus exposes.
