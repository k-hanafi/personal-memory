# Personal Memory evals

How we measure whether the brain answers correctly, and how we keep it from getting worse.

Written 2026-09-09. Companion to `docs/v1-spec.md`. Every source named here is listed with a one-line summary in `docs/sources.md`.

## Why this document exists

Personal Memory is a search engine over a folder of markdown. The product promise is narrow and testable: every answer cites a file and a line range, says whether the note is still current, and refuses to answer when the brain does not have it. A promise that specific can be checked by a script. This document describes that script, the data it runs on, and the rules for reading its output.

The larger reason is that retrieval quality is the product. When we add wikilink hops, or SQLite full-text search, or an optional vector arm, the only way to know whether the change helped is to ask the same questions before and after and count. Without that, every architectural decision is a guess dressed up as a decision.

There are four jobs the evals do for us:

1. Tell us whether a change to retrieval made search better, worse, or neither.
2. Catch a regression before a user does. If the current teaching-load note stops outranking the superseded one, CI fails.
3. Give future users a reproducible scoreboard instead of a claim. They can run it on their own machine.
4. Later, measure which coding agent and model use our tools best, and at what token cost.

The first three are one mechanism. The fourth is a separate, slower layer. Keeping them apart is the main design decision in this document.

## Vocabulary

These terms are used throughout. Each one is defined once here.

A **fixture** is one test case: a query, what should come back, and what must not come back. A **family** is a group of fixtures that test one ability, such as finding a note by name or preferring current facts over superseded ones. The **corpus** is the fictional brain the fixtures run against.

A **gold item** is a fixture whose expected answer a human has verified against the corpus. If a gold item passes and later fails, something changed in the engine.

**hit@1** asks whether the first result was the right file. **recall@5** asks whether the right file appeared anywhere in the top five. Together they say "did the right thing show up, and was it on top."

An **adapter** is a small function that makes some search system answer our fixtures in a common shape. Our own `recall` is one adapter. A plain grep is another. Later, a vector search is a third. The fixtures do not know or care which adapter is running.

A **baseline** is a JSON file committed to git that records how every fixture scored on `main`. The **gate** is the CI step that runs the fixtures on a pull request and compares against the baseline.

**Hermetic** means the run uses no network and no API keys. The same inputs give the same outputs every time, so a difference between two runs is a difference in the code.

## The shape of the system

Think of a driving test. The written exam is fixed questions with exact answers. Anyone can grade it, and two graders agree. The road test puts you in traffic with a human examiner, and no two runs are alike. Both tests matter. Nobody would combine them into one score.

Personal Memory's evals have the same split.

| Layer | Question it answers | Runs when | Cost | Gated in CI |
|---|---|---|---|---|
| 1. Engine evals | Does `recall` return the right card for a fixed question on a fixed corpus? | Every pull request | Seconds, no keys | Yes |
| 2. Dogfood replay | Does the engine handle the questions Khaled asks his real vault? | Weekly, by hand | Minutes, no keys | No. Private data. |
| 3. Agent in the loop | Does a coding agent using our MCP tools produce a correct, cited answer? | Before releases | Minutes, model tokens | No. Stochastic. |

Layer 1 is possible because Personal Memory calls no LLM in v1. The engine is a pure function from (corpus, query) to a list of evidence cards. Most memory products cannot say that, so their core evals are noisy by construction and they argue about the noise in public. We get a deterministic gate for free by keeping the model out of the engine.

Layer 3 is where models enter, and where the numbers become probabilities. It is also where the "which agent and which model" question from job four gets answered.

## Layer 1: engine evals

### The corpus

The eval corpus lives at `evals/brain/`. It is a fictional brain in the v1 frontmatter format, seeded by copying `examples/demo-brain/` and then adding notes that exist only to trigger failure paths. The note inventory and why each note exists are in `docs/eval-corpus-plan.md`.

It is a separate folder from the demo brain on purpose. The demo brain is what a new user sees first and it should be small and clean. The eval corpus needs planted problems: two `current` notes that disagree, a person note with an alias that differs from the title, a note whose title is a substring of another title. Those belong in a test bed, not in onboarding material.

Everything in the corpus is made up. Gbrain generated its 240-page BrainBench corpus with a model, and we may do the same to grow past what we can write by hand. A grep guard in CI fails the build if any string from a deny list of real names appears in `evals/brain/`. Khaled's vault never touches this folder.

The corpus is versioned by content hash. Any change to any file in `evals/brain/` or `evals/fixtures/` changes the hash, and the gate treats a changed hash differently from an unchanged one. That rule is explained under "The gate" below.

### Fixture format

Fixtures are TOML files, one per family, in `evals/fixtures/`. TOML because Python 3.11 reads it with the standard library (`tomllib`), and because it is easier for a person to write than JSON. The runtime depends on the MCP SDK; fixtures are not a reason to add another parser.

The suite runs on `evals/brain/`. Live cases are in `evals/fixtures/`; this is a shortened copy of `evals/fixtures/supersession.toml`:

```toml
family = "supersession"

# Current notes must outrank superseded ones on a default query.

[[case]]
id = "teaching-load-current-wins"
query = "teaching load"
expect_path = "40-areas/teaching-load-2026-09.md"
expect_status = "current"
forbid_paths = ["40-areas/teaching-load-2026-01.md", "40-areas/teaching-load-2025-09.md"]

[[case]]
id = "teaching-load-history-labels-old-notes"
query = "teaching load"
historical = true
expect_path = "40-areas/teaching-load-2026-09.md"
expect_status = "current"

[[case.also_present]]
path = "40-areas/teaching-load-2026-01.md"
status = "superseded"
```

Human asides are `#` comments, not fields. Each case carries some subset of these fields:

| Field | Meaning |
|---|---|
| `id` | Stable name. Baselines key on it, so do not rename casually. |
| `query` | The string passed to the adapter. |
| `historical` | Pass `--historical` (include superseded notes). Default false. |
| `expect_path` | The file that should be the top card. |
| `expect_line` | A line number that must fall inside the top card's `start_line..end_line`. |
| `expect_status` | The `status` the top card must report. |
| `expect_confidence` | The `confidence` the top card must report. |
| `forbid_paths` | Files that must not appear in the top five. |
| `also_present` | Files that must appear somewhere in the results, with the status they must carry. |
| `abstain` | If true, the adapter must return zero cards. |
| `contradiction` | A list of two or more current paths. All must appear, and each must list the others in `contradicted_by`. |
| `holdout` | If true, this case is scored in published runs but excluded from the CI gate. |

A case passes only if every field it declares is satisfied. There is no partial credit inside a case. Partial credit lives one level up, as the pass rate across a family.

### Fixture families

Each family is named for the ability it tests and for the source we took the idea from.

**Named thing:** find the page a query names. Gbrain's NamedThingBench splits this into sub-families that fail in different ways, and we borrow the split: exact id (`samir-okonkwo`), exact title (`Samir Okonkwo`), alias (a nickname in the `aliases` frontmatter field), title substring (`Okonkwo`), and generic-to-named (`who co-organizes the case competition`, where the answer is a person the query does not name). Exact id, exact title, alias, and substring are gold. Generic-to-named is mixed: one hop makes `who is the department chair` pass; `who co-organizes the case competition` still fails and stays a capability target.

**Supersession:** the current note outranks the superseded one on a default query. Under `--historical`, both appear and the old one is labeled `superseded`. This family takes its scoring rule from MEME's trivial-pass filter: the engine gets credit for handling a superseded note only if it can also find that note when asked. A retriever that never indexes old notes would pass a naive version of this test while failing the product promise, and the filter closes that hole.

**Abstention:** queries the corpus cannot answer must return zero cards. LongMemEval scores this as one of its five memory abilities, and most systems it tested fail it. For us it is the FAILURE line in the v1 spec: "the brain doesn't have this" is a successful answer. The family includes near misses on purpose, such as a query that shares two words with a real note but asks about something the note does not say.

**Contradiction:** two `current` notes in the eval corpus disagree about the same fact. Both must surface and each must name the other in `contradicted_by`. The spec calls this a bug in the brain that must be reported, never smoothed over. The eval corpus plants exactly this bug so we can test the report.

**Citation:** the line range in the returned card must contain the line that carries the claim. Today `recall` returns a single line. When it starts returning ranges, `expect_line` still works: the line must fall inside the range. This is the family that protects "an answer cites a file but no line range" from ever shipping.

**Baseline comparison:** a row in the results rather than a family of fixtures. Every family is also run through the grep adapter. If our engine does not beat grep on a family, the engine is not yet earning its keep on that family. Gbrain publishes exactly this row (their "grep + BM25" baseline sits at 17.1% precision against their full system's 49.1%), and it is the most useful single number for a reader deciding whether to trust a retrieval claim.

### Adapters

An adapter is a function with this signature, in plain Python:

```python
def search(corpus_root: Path, query: str, historical: bool) -> list[Hit]
```

where a `Hit` carries `path`, `start_line`, `end_line`, `status`, `confidence`, and `contradicted_by`. That is a subset of the evidence card `recall` already returns, so the first adapter is a thin wrapper.

The grep adapter is a plain text search written in Python, with no subprocess and no `rg`. It lowercases the query, splits it into alphanumeric tokens, counts every occurrence of every token in each file, ranks files by that count, reads frontmatter to fill in `status` and `confidence`, and returns the first matching line as the range. It ignores `historical` because grep does not know what `status` means. It does not shell out to ripgrep because a default machine does not have `rg`, and the eval run must work with no extra binaries. It is deliberately dumb. It exists to answer "what does a plain text search already get you," which is the question every user of a markdown brain should ask before installing anything. Two consequences follow and both are the point, not bugs. Because it ignores `status`, grep loses the supersession family by design, and on a tie in match count it may rank a superseded note first. Because its line is the first token match over the whole file, that line is usually the `id:` frontmatter line, so grep loses the citation family by design.

Adapters that need a network (embeddings, a reranker) may exist later. They are excluded from the CI gate because they are not hermetic, and their results are published as separate rows with the model name and date recorded.

The point of the adapter shape is the one gbrain-evals makes about its own system: the engine is one system under test, not the subject of the benchmark. Anyone can write an adapter for their own search and run our fixtures.

### Scoring

A run produces one JSON receipt in `evals/runs/` (gitignored). The receipt records:

- git commit, fixtures hash, adapter name, timestamp
- per case: pass or fail, and which declared field failed
- per family: passed count, total count, hit@1 rate, recall@5 rate
- superseded leak count: cases where a superseded note outranked a current one without `--historical`
- abstention accuracy: abstain cases that returned zero cards, over all abstain cases

The receipt is the unit of evidence. Receipts keep the top five hits per case. Baselines drop those hit lists along with the timestamp and the commit hash, and the floats are rounded to four places, so a baseline diff shows pass/fail flips and nothing else.

Rounding and key sorting are what make a baseline diff in a pull request readable by a human, and a readable diff is how a reviewer notices that a "small refactor" flipped three gold items.

### The gate

CI runs the fixtures on the pull request's HEAD and compares the receipt to `evals/baselines/main.json` as it exists on `main`. There are two modes, chosen by comparing the fixtures hash.

If the hash is unchanged, the pull request touched only engine code. Any gold item that passed on `main` and fails on HEAD fails the build. There is no tolerance band. Two runs of a hermetic suite produce identical numbers, so a flipped case is a behavior change, and the reviewer should know about it even if the aggregate went up.

If the hash changed, the pull request touched fixtures or the corpus. The committed baseline must then byte-match a fresh run on HEAD, so the file cannot claim a number the code does not produce. Any case that regressed against `main`'s baseline needs a `justification` string in the committed baseline. That string shows up in the diff and a human judges it. It only counts when it differs from the one on `main`, so a justification carried forward by `--update-baseline` cannot waive a later change. The count of gold items may not fall under an unchanged corpus, which stops the quiet trick of deleting a hard fixture to make the suite pass.

Only the `recall` adapter gates (`grep` is the baseline row, not the system under test), and the committed baseline must byte-match a fresh run whenever it differs from `main`'s, whatever the hash did.

Holdout cases (`holdout = true`) are excluded from the gate and scored only in published runs. This keeps a slice of the fixtures that nobody has tuned against. The holdout is empty until the fixture set passes fifty cases; below that size a 15% slice is too small to mean anything.

There is no `--allow-regression` flag. A pull request cannot approve its own regression. The only waiver is a `justification` string in the committed baseline when fixtures or the corpus changed.

### Reading a result

The CLI prints a table. One row per family, one column per adapter, plus a paired-change column against the baseline.

```
family          recall      grep       vs main
named-thing     9/12        6/12       +1 / -0
supersession    4/4         1/4        +0 / -0
abstention      5/6         2/6        +0 / -1   <- FAIL: no-such-course
contradiction   1/2         0/2        +0 / -0
citation        11/12       4/12       +0 / -0
```

The `vs main` column is a paired comparison: for each case, did it flip from fail to pass (+) or pass to fail (-). This is more informative than two averages, because a change that fixes five cases and breaks five others has the same average as one that did nothing, and the paired view shows you the churn. Gbrain reports every retrieval change this way, as "+18 / -8" rather than "95.3% vs 93.2%".

### Capability versus regression

Anthropic's eval writeup draws a line we adopt. A capability eval is one the system currently fails; its job is to give you a hill to climb, and it should start with a low pass rate. A regression eval is one the system passes; its job is to stay at 100%, and any drop is a bug.

In our fixtures the same case moves between roles over time. A fail is a capability target; a pass is gold and gates. One generic-to-named case is gold after the hop (`generic-to-named-department-chair`). The other (`generic-to-named-case-competition-co-organizer`) still fails and stays a capability target. A case never moves from gold back to capability without a justification string.

This is also how the fixture set grows without the gate becoming a wall. You can add ten cases the engine fails today and CI stays green, because the gate only cares about gold items flipping.

### Pre-registration

Before a retrieval change, write down what you expect the fixtures to do. One sentence in the pull request description is enough: "A synonym table should move named-thing from 10/11 to 11/11 and change nothing else."

Then run the evals and publish whether the prediction held. If it did not, say so in the same place.

Gbrain does this for every search-mode change and publishes the misses in release notes alongside the hits. A result you predicted is evidence about your understanding of the system. A result you observed and then explained is a story. Only the first kind tells you whether you know why the engine behaves the way it does.

## Layer 2: dogfood replay

Layer 1 runs on a fictional corpus because a fictional corpus can be published. But the questions that matter are the ones Khaled asks his real vault, and the failures that matter are the ones that show up there.

The replay uses the same fixture format and the same runner. The difference is where the file lives. A private fixture file sits inside the vault, at `~/vault/90-meta/evals/vault-fixtures.toml`, pointing at real vault paths. It is never copied into this repository. The command is:

```bash
personal-memory eval run --corpus ~/vault --fixtures ~/vault/90-meta/evals/vault-fixtures.toml
```

The workflow, once a week or after any retrieval change:

1. Run the replay and read every failure, not only the count.
2. Write down what kind of failure each one is. Wrong note on top. Right note but wrong line. Superseded note leaked. Should have abstained and did not.
3. When a kind shows up three times, it is a family gap. Write a fictional fixture that reproduces it in `evals/brain/` and add it to Layer 1 as a capability case.
4. Fix the engine. Watch the fictional case flip to pass. Re-run the replay to confirm the real one flipped too.

This is Hamel Husain's error analysis loop, and it is the part of eval practice that people skip because it is not automated. The automation in Layer 1 catches what we already know to look for. The replay is how we learn what to look for next. Gbrain has the same two-part structure under the names `eval export` and `eval replay`, which capture live queries and replay them against code changes.

The replay is not gated and its numbers are not published, because the corpus is private. Its output is fixtures for Layer 1, and those are public.

## Layer 3: agent in the loop

The MCP server exists (`personal-memory mcp --brain`). This layer's runner does not. It is specified so the earlier layers stay compatible with it.

The question is different from Layer 1. Layer 1 asks whether the `recall` adapter returns the right card. Layer 3 asks whether Claude Code, Codex, or Cursor, given our `remember` and `revisit` tools, produces an answer that cites the right file and line and says the right thing about status. The engine can be perfect and the agent can still ignore the card, cite the wrong line, or answer from memory. LongMemEval found the same gap: even with perfect retrieval, the reading step lost accuracy.

Write tools (`draft`, `pending`, `file`, `note`, `inbox`) are specified for Layer 3 and not built into any runner. Decide whether they belong in that set when the runner is built.

The set is small on purpose. Twenty questions against `evals/brain/`, each with a gold path, gold line, and gold status. Each is run three times per agent and model. The grade is code, not a model: does the agent's answer contain the gold path, does it name a line range containing the gold line, and does it report the gold status. Abstention questions pass if the agent says the brain does not have it and cites nothing.

Two numbers per (agent, model) pair:

- pass^3, the fraction of questions where all three trials passed. Anthropic's writeup argues this is the right metric for anything user-facing, because a user does not get to retry.
- mean tokens per question, read from the agent's own usage output.

Together they answer job four: which agent and model use our tools reliably, and what it costs. Mem0 reports tokens per retrieval next to accuracy for the same reason. A memory system that is 2% more accurate and 4x more expensive per query is a different product.

Layer 3 is run before a release, by hand, and costs a few dollars. It is not gated. A model judge is not used until error analysis on the transcripts shows a failure mode that code cannot grade, and even then the judge is validated against hand labels first, per ARES and per Hamel's guidance on aligning judges before trusting them.

## Primitives and where they come from

Every structural choice above is copied from somewhere. This table is the map.

| Primitive | Taken from | What we copy | What we leave out |
|---|---|---|---|
| Committed fictional corpus, publishable | Gbrain BrainBench, gbrain-evals | Fictional pages, grep guard against real names, grow with a model when hand-writing runs out | Their Postgres index. Our corpus is a folder. |
| Hermetic run, no keys, seconds | Gbrain BrainBench | Deterministic adapters so any flipped case is a real change | Their in-memory PGLite. We have no database. |
| Baseline on `main`, exact gate, byte-match when fixtures change, `justification` string | Gbrain BRAINBENCH.md gate governance | The whole mechanism | The `--live` and `--llm` stochastic modes, which we put in Layer 3 instead |
| Holdout slice | Gbrain BrainBench | 15% excluded from gate, scored in published runs | Deferred until fifty cases |
| Named-thing sub-families | Gbrain NamedThingBench | Exact, alias, substring, generic-to-named, multi-chunk dilution | Their reranker-specific rules |
| Trivial-pass filter for supersession | MEME (arXiv 2605.12477) | Credit only if the old fact is findable and labeled, not merely absent | Cascade and multi-entity propagation, which need a graph we do not have |
| Abstention as a scored ability | LongMemEval (arXiv 2410.10813) | Queries with no answer must return nothing | Their chat-session data format. Our substrate is markdown. |
| Index, retrieve, read as separate stages | LongMemEval | Layer 1 tests retrieve; Layer 3 tests read | Their long-context baselines |
| Grep baseline row | Gbrain scorecard, Letta filesystem experiment | Always report what a plain text search gets you | Nothing |
| Adapter interface, engine is one system under test | gbrain-evals README | Common `search()` shape; anyone can plug in | Their TypeScript harness |
| Paired +/- comparison | Gbrain scorecards | Per-case flips instead of two averages | Bootstrap confidence intervals, which only matter for stochastic runs |
| Pre-registration | Gbrain SEARCH_MODE_METHODOLOGY.md | Predict the number in the PR, publish the miss | Their formal hypothesis numbering |
| Capability versus regression evals | Anthropic, Demystifying evals for AI agents | Cases graduate from one to the other; gate only on regression | Their computer-use and coding agent sections |
| pass^k and tokens per question | Anthropic; Mem0 memory evaluation docs | Layer 3 metrics | pass@k, which rewards retries we do not offer |
| Error analysis before automation, binary grades, code before judge | Hamel Husain, Your AI Product Needs Evals; Evals FAQ | Layer 2 loop; no model judge without a counted failure mode | A/B testing, which needs users we do not have yet |
| Synthetic questions need a human anchor | Can we Evaluate RAGs with Synthetic Data? (arXiv 2508.11758); ARES (arXiv 2311.09476) | Hand-written cases stay in every family even after generation begins; judges validated on labels | Their fine-tuned judge models |
| Do not chase competitor numbers | Zep vs Mem0 dispute; Letta's 74% with grep | Publish our own ablation table and the corpus to reproduce it | Head-to-head claims against systems we cannot run |

## What this does not do

Personal Memory does not run LongMemEval or MEME as datasets. Both are built from chat transcripts, and converting them into frontmatter notes would test the converter more than the engine. We take their task definitions and their scoring rules, and we write our own fixtures in our own format.

There is no leaderboard against Gbrain, Sentra, Mem0, or Zep. Their published numbers come from their own corpora and protocols, and the one time two of them ran on the same benchmark it took a month of public correction to agree on the arithmetic. The claim we can make is smaller and checkable: here is the corpus, here is the commit, here is what grep scores and here is what we score, run it yourself.

No model grades anything in Layers 1 or 2. Evidence cards are paths and line numbers. Code can check those.

## Commands

All of these run from the repository root with the virtual environment active.

```bash
# Run every family against the eval corpus with our engine and with the grep baseline,
# and show flips against the committed baseline. Always exits 0.
personal-memory eval run

# Same, but only one family and one adapter.
personal-memory eval run --family supersession --adapter recall

# Rewrite the committed baseline from a fresh run. Only after a fixture or
# corpus change, and only when the PR explains why.
personal-memory eval run --update-baseline

# Compare two receipts case by case. Prints +/- flips.
personal-memory eval compare evals/runs/a.json evals/runs/b.json

# Run the suite and exit 1 if a gold recall case regressed against the given
# baseline. The script fetches origin/main's baseline and passes it in; CI runs it.
personal-memory eval gate --main-baseline <path>
bash scripts/eval-gate.sh

# Private replay against the vault. Never commits anything.
personal-memory eval run --corpus ~/vault --fixtures ~/vault/90-meta/evals/vault-fixtures.toml
```

`--update-baseline` is the one command that changes a tracked file. Everything else writes to `evals/runs/`, which git ignores.

## Failure conditions

Any of these means the eval system is not doing its job:

- A pull request merges with a gold item flipped from pass to fail and no `justification` in the diff.
- `personal-memory eval run` needs a network connection or an API key.
- Two runs of the same commit on the same corpus produce different receipts.
- The eval corpus contains a real name, a real course, or any text from `~/vault`.
- A superseded note passes a supersession case by being absent rather than by being found and labeled.
- The grep row is missing from a published scoreboard.
- A model is used to grade Layer 1 or Layer 2.
- A retrieval change ships without a written prediction and a note on whether it held.
- Vault fixtures or vault receipts appear in this repository.

## Implementation order

Evals come before the features they will measure, so that each feature is built to pass a case that already exists.

Layer 1 is shipped: corpus, fixture loader, adapters, runner, five families, baseline plus CI gate, wikilink hops.

Remaining:

1. Vault fixture file and the first replay session. Turn the first three real failures into fictional fixtures.
2. Layer 3 question set, pass^3 runner, token logging. MCP exists; the runner does not.
3. Holdout slice once fixtures pass fifty cases.
4. Model-generated corpus growth once hand-written notes stop covering the families.

## Open

- Decided 2026-09-10: the write path (`draft`, `file`, `note`) is not a fixture family. Its rules are deterministic (refuse a duplicate title, flip `status` on supersede, cap confidence without a boring signal), so they are unit tests in `tests/test_filing.py`, not gated retrieval cases. Whether the agent files the right thing is a Layer 3 question (specified, not built; decide whether write tools are in scope later).
- The contradiction family has no negative assertion. There is no way to say `contradicted_by` must be empty, so a fix that stops marking unrelated current notes as contradictions cannot be measured. A `no_contradiction` field is the likely fix.
- How to express `expect_line` once cards return multi-line ranges and a claim spans a paragraph. A range-overlap rule is the likely answer.
- Whether Layer 3 should record the agent's full transcript for later error analysis, and where that transcript is stored given that it may contain model output about the fictional corpus only.
