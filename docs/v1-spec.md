# Personal Memory v1 spec

Name: **Personal Memory**. GitHub: `k-hanafi/personal-memory`.
Locked: 2026-09-02. Renamed from pith on 2026-09-07.

This file is the product plan. If code and this file disagree, this file wins
until we change it on purpose.

## Bet

A git folder of markdown is the brain. A coding agent (Claude Code, Codex,
Cursor) talks to it over MCP. Every answer cites a file and a line range, and
says whether the note is still current, when the claim was true, and how sure
we were.

The product works with no embedding vendor, no Postgres, and no hosted agent.
Vector search is an optional extra for large, messy brains. It is never
required to install or to get a correct answer.

## Who it is for

v1 users live in a coding agent every day. They are not expected to run
Telegram bots, Docker, or a vector database.

Primary users:

- Khaled, dogfooding on the private vault at `~/vault`
- A knowledge worker like Jan Bena: finance professor, uses Codex and Claude
  Code daily, not an infrastructure person
- Other people in the same boat who want a personal brain they own as files

v1 does **not** target OpenClaw, Hermes, Telegram, or a 24/7 hosted agent.
That can come later. Most of the value now is memory for the agent already
open in the editor.

## What this is not

Gbrain (Garry Tan) is prior art, not the product. Gbrain is a full memory
stack: git markdown as source of truth, Postgres index, hybrid search
(keyword + vectors + graph), skills, optional hosted agent. Tens of thousands
of pages, many ingestion pipes, paid embedding APIs.

Personal Memory takes the same *ownership* idea (you keep the files) and a narrower
job: coding-agent memory that stays honest when notes go stale.

Gbrain's own retrieval doc is the reason vectors are optional here. Vector
search alone underdelivers on personal-knowledge questions. Keyword-only and
vector-only scored similarly on their BrainBench table. The large precision
jump they publish came from the page graph and extract quality, not from
embeddings. Gbrain can already boot with no embedding key and fall back to
keyword search. We are making that the default path, not the fallback.

Do not clone Gbrain's connector list, Render/Telegram tutorial, or Convex as
the database. Git markdown stays the system of record. Any database is an
index you can rebuild.

## Repos

Three different things. The Gbrain tutorial says "create two repos" because
Gbrain *the product* already exists. You install it, then you create a private
brain and (if you run a hosted agent) a private workspace.

Personal Memory is the product, so the map is:

| Repo | Job | Public? | Today |
|---|---|---|---|
| **Product** (this repo) | Engine, MCP, schema, docs, demo brain | Private now. Public later. | `k-hanafi/personal-memory` |
| **Brain** | The person's notes | Never (unless they choose) | Khaled: `k-hanafi/vault`. Jan: his own folder. |
| **Agent workspace** | How a hosted agent behaves (skills copies, crons, Telegram) | Private | Not in v1 |

Boundary test: would this file still matter if you switched coding agents?
Then it belongs in the brain. Would a stranger need this file to run the
engine? Then it belongs in the product.

Khaled's vault today mixes both (`bin/` scripts next to people notes). That
was right when the "product" was three scripts. The public product cannot
live in `~/vault`. Features land here. `~/vault` stays the first customer:
point Personal Memory at that folder. Do not freeze the vault while building a
greenfield clone, and do not migrate onto a new note format at the end.

Community install uses `examples/demo-brain/` (fake people, fake courses).
Khaled's life never ships in this repo.

## Retrieval

Think of four lookup keys. They do different jobs.

| Key | Question it answers | v1 |
|---|---|---|
| Keyword | Which files contain these words? | Yes. Better than raw grep if we can (title vs body). |
| Exact / alias | Which page is *this name*? | Yes. `id`, title, optional `aliases`. |
| Graph | This page links to what? | Yes, walk existing `[[wikilinks]]`. No LLM extraction required. |
| Vector | Which pages are *about* this even if they used different words? | **Optional, v1.5+.** Fail-open: no API key means Personal Memory still works. |

Vectors help when the asker does not share vocabulary with the notes
("gaming the curve" vs a note that says "strategic sitting of exams"), and
when the corpus is large and paraphrase-heavy (meetings, email, Slack).

Vectors fail when the question is a name, an id, a number, or a *current*
fact sitting next to a semantically similar *old* fact. Naive RAG (chunk,
embed, dump top-k) strips `status` and `as_of`. That is the failure this
product exists to prevent.

If vectors land later: they only propose candidate pages. Every candidate
still has to pass frontmatter filters and return an evidence card. A cosine
score is not an answer.

v1 accepted hole: synonym misses when the agent and the notes use different
words. Document that honestly. Do not paper over it with a required embedding
vendor.

## Evidence card

Every fact shown to the user or the agent must be backed by a card before it
appears in a sentence. If there is no card, the engine says the brain does
not have it.

| Field | Meaning |
|---|---|
| Claim | One fact, one line |
| Path | File inside the brain |
| Lines | Inclusive line range |
| Status | `current` or `superseded` |
| As of | Date the claim was true (`as_of` in frontmatter, or the Log line's own date) |
| Confidence | `high` / `medium` / `low` |
| Contradicted? | Other current notes on the same fact, if any |

Two `current` notes that disagree are a **bug in the brain**, not something
to smooth over. Report both.

A `current` note and a `superseded` note disagreeing is supersession working.
Use the current one and say the older one was replaced.

"The brain doesn't have this" is a successful answer.

## Write

Decided 2026-09-10. Writes matter as much as reads: the brain compounds only
if facts stated in passing get filed. The engine does not need a model to do
this, because every write splits into two halves that want different tools.

| Half | Who does it | Why |
|---|---|---|
| Judgment: is this durable, which note is it about, new or changed, what `type`, what `as_of`, where | The coding agent in the editor | It has the whole conversation, the filing rules, and the neighborhood from `remember`. It can ask the user. An engine-side model would see one sentence and could not ask. |
| Consistency: valid frontmatter, no duplicate `id`/title/alias, supersession mechanics, `sources/` untouched, line-ranged cards | The engine, in code | This is bookkeeping. Models forget to flip a `status`; code does not. |

The engine never decides. It refuses to let a decision be recorded wrong.

### One door

Every write enters through the same validated path: `draft`, then
`file`. `note` is the one-call shortcut for a single fact the user stated
in chat, and it goes through the same validation. Nothing writes markdown
around this door. That seam is what lets a later background filer (spec step
9) be added as another caller, not as a rewrite.

### What the engine checks on every write

- Required frontmatter present and valid (`id` kebab-case, `as_of` a date,
  `status` and `confidence` from the allowed sets).
- No existing note with the same `id`, the same normalized title, or the
  proposed title in its `aliases`. If one exists, refuse to create and return
  that note as the target.
- Path is inside the brain and not under `sources/`.
- A changed fact supersedes: the old note gets `status: superseded` and
  `superseded_by: <new id>`; the new note is `current`. Never overwrite in
  place. A second current note with the same `id`, normalized title, or that
  title as an alias is refused, not merged. A Log line with the same
  normalized claim is `duplicate`. Semantic same-fact is not detected.
- Provenance recorded on the note: who proposed (`user`, `agent:<name>`,
  later `filer:<model>`) and the date. A user statement is a dated source, so
  it satisfies the "boring signal" rule for high confidence.

### What the engine returns

`file` returns `inserted`, `duplicate` (with the existing note), `superseded`
(with the old and new paths, after a `supersede` proposal), or `queued` (with
the reason). `note` only appends or creates, so its result is `inserted`,
`duplicate`, `queued`, or `blocked`. Plus, without a model, the facts it can
count: near-miss notes sharing entity tokens with the proposal, and where
notes of the same `type` and the linked notes already live.

### Placement

File next to what you link to. The agent runs `remember` on the subject, sees
where the sibling notes live, and proposes that folder. The engine's tally
confirms or disagrees. Folder is a convention; `id` is the address, so a
note in the wrong folder is still found by id, title, alias, keyword, and
wikilink. Misfiling is cheap to fix and never a retrieval error. Ambiguous
placement stays in the queue at the capped confidence and the user picks.
There is no `inbox/` folder. `inbox` is the command that lists `sources/`
files no note has named yet.

### Note shape: State and Log

Decided 2026-09-10. A note may carry a `## Log` section. Everything above it
is State: the current picture, maintained by the agent, rewritten when the
picture changes. The Log is an append-only ledger of dated facts, one per
line, oldest first:

```markdown
## Log
- 2026-09-01 | user | Dean approved the sabbatical request.
- 2026-09-10 | agent:claude-code | Start date moved to January.
```

Each entry is `- YYYY-MM-DD | provenance | claim`. `check` rejects a Log
line that does not parse. The Log is optional: a note without one is a
single-fact note and nothing changes for it. Khaled's vault opts in one note
at a time.

Why two layers: `as_of` in frontmatter is one date, and an entity or project
note accumulates facts with many dates. With a Log, frontmatter `as_of` is
when the State was last true, and every Log line carries its own date. An
evidence card whose claim line is a Log entry reports that line's date as
`as_of`. Every system that has run a brain at scale (Gbrain's compiled truth
over a timeline, Karpathy's wiki over `log.md`, Zep's facts with validity
windows) converged on this split; see `docs/sources.md`.

The engine writes only to the Log and to frontmatter. Rewriting State is
judgment, so the agent does it in the editor, and `check` catches a State
edit that breaks the schema.

### Proposals

A proposal is one JSON file under `.personal-memory/queue/`. JSON, not
markdown, because a proposal is a validated payload, not a note: it must
never be indexed by `remember`, and it needs fields with fixed meanings.
Applied proposals move to `.personal-memory/applied/` so the queue folder is
always exactly the open work. The id is the first twelve hex digits of the
SHA-256 of the proposal's content, so submitting the same proposal twice is
a no-op.

Three kinds:

| Kind | Writes | Requires |
|---|---|---|
| `create` | A new note: frontmatter, title, body | `path`, `id`, `type`, `as_of`, `confidence`, `title`; optional `body`, `aliases`, `source` |
| `append` | One Log entry on an existing note | `target` (note id), `claim`, `as_of` |
| `supersede` | A new note, and flips the old one to `superseded` | Everything `create` needs, plus `supersedes` (old note id) |

Every kind requires `provenance`. Empty provenance is refused with the reason,
the same way Gbrain's `remember` refuses it.

Validation, in order, stops at the first failure and records it as the
proposal's `blocked` reason:

1. Path is inside the brain, ends in `.md`, and is not under `sources/`.
2. Frontmatter fields pass the same parser `check` uses.
3. `create` and `supersede`: no current note already has this `id`, this
   normalized title, or this title among its `aliases`. If one does, the
   result is `duplicate` and names that note as the target to `append` to.
4. `append`: the target exists and is `current`. A Log entry with the same
   normalized claim already present is `duplicate`.
5. `supersede`: the old note exists and is `current`.

Confidence is the proposer's claim, capped by the engine. High survives only
with a boring signal: `provenance` starts with `user`, or `source` names a
file that exists under `sources/`, or the kind is `append` or `supersede`
(the target was found by exact id). Otherwise the engine records
`confidence: medium` and the proposal waits for a person.

`file` with no arguments writes every valid proposal whose effective
confidence is high. `file <id>` writes one named proposal at any
confidence: that is the person choosing. `file` for `supersede` writes the new
note and edits the old note's frontmatter in the same call, because leaving
the flip in the queue would create the exact state this spec calls a bug:
two current notes on one fact.

On `create` and `supersede` the engine stamps `provenance` into frontmatter
and, when given, `source`. On `append` the Log line carries provenance.

### `note`

`note(claim, provenance, target?, path?, type?, as_of?, title?)` saves one
fact and returns immediately. It is `draft` then `file` for that one
proposal. `title` is live on the CLI and MCP; leaving it off uses the path
stem. `note` does not supersede.

- With `target`: an `append` proposal. The fact becomes a Log line on that
  note.
- Without `target`: a `create` proposal for a stub note (frontmatter, a title
  from `title` or the path stem, and a Log with the one fact). `path` and
  `type` are required in that case; the agent knows the folder from
  `remember`.

`note` does not take a whole body. A whole page is a `create` proposal
through `draft`. One call, one fact, one shape.

Result is one of `inserted`, `duplicate`, `queued`, `blocked`, with the
paths touched and the reason when there is one. It also carries the
zero-LLM counts from the section above: candidate notes sharing tokens with
the claim, and the folders where notes of this `type` and the linked notes
already live.

### Filed marker and `inbox`

A `sources/` item counts as filed when some note names it: frontmatter
`source: <path>` on a created note, or `source:<path>` as the provenance of
a Log line. `inbox` lists every file under `sources/` that no note names.
No side file, no move, no edit under `sources/`.

### Automatic capture

"Automatic" filing is a property of the prompt side, not the engine. The
brain's `AGENTS.md` (and the user's own rules) tell the agent to call
`note` for durable facts without being asked: preferences, corrections,
decisions, commitments, relationships, project-state changes. It also
carries the skip list: anything derivable from the codebase or git, session
state, unverified conclusions, secrets. No harness hook in v1.

### Not in v1, and the trigger to revisit

Not in v1: embedding-based dedup, a model judge for contradictions, any
background sweep. `contradicted_by` on the evidence card is the zero-LLM
version: surface both, let the human pick.

Revisit when dogfood replay shows the failure a background pass would catch
(two notes on one fact that never co-retrieve) three or more times. First try
an agent-run lint over `remember` and `revisit`. Only if that is not enough, add an
overnight filer with its own key as a caller of `draft`.

## Note schema

Required YAML frontmatter on every note:

```yaml
---
id: kebab-case-slug
type: <string>
as_of: YYYY-MM-DD
status: current | superseded
confidence: high | medium | low
---
```

Rules:

- `id` is stable. Do not rename it casually. Links depend on it.
- `as_of` is when the claim was true, not when the file was edited.
- `status: superseded` notes are kept. History is part of the value.
- `type` is a string, not a closed enum in the engine. Folder layout is a
  convention, not a requirement. Khaled's type-at-top folders are the default
  *template*, not the only legal brain.
- People are one file each. Other notes link to them instead of restating
  who they are.

Optional fields the engine reads: `aliases` (other names for exact match),
`supersedes` and `superseded_by` (the id on the other end of a supersession;
`check` requires that note to exist), `provenance` (who proposed the note
and when), `source` (the `sources/` file this note files). Wikilink brackets
around an id are allowed in `supersedes` and `superseded_by`.

The engine indexes markdown files that have this frontmatter. Files without
it (README, agent protocol files) are skipped, not rejected.

## Ingest and filing

This is the onboarding loop. Dumps do not become the schema. Raw material
lands in `sources/`. Labeled notes are written elsewhere. `sources/` is
immutable: Personal Memory and the agent read it and never edit it.

### Ordered workflow

`personal-memory init` is not built. Point Personal Memory at a folder the
user already has, or copy `examples/demo-brain/`.

1. **Land raw material in `sources/`.** Drag and drop files, or later a
   connector (Notion first). Connectors are copy jobs: token in env, no
   model in the pipe. Same job as Khaled's `notion-sync`.
2. **Scan.** `personal-memory inbox` lists `sources/` items that have no filed
   note yet. No LLM. No file moves. A source is filed when a note names it
   (`source:` in frontmatter, or `source:<path>` on a Log line). The engine
   never writes under `sources/`.
3. **Draft.** The user's coding agent (Claude Code, Codex, or Cursor)
   reads each inbox item plus `remember` against notes already in the
   brain, then submits a proposal via `draft`: destination path, jar-label
   frontmatter, short claim, and a confidence. Personal Memory stores
   proposals in `.personal-memory/queue/`. The agent does not write the
   note yet.
4. **Validate.** `personal-memory file` uses the Write / `filing.py` rules
   (required fields, path not under `sources/`, no duplicate `id` / title /
   alias, no same-claim Log line, live target). Model-stated
   "high confidence" is not enough. High survives only with a boring
   signal: `provenance` starts with `user`, or `source` names a file that
   exists under `sources/`, or the kind is `append` or `supersede`.
5. **File by confidence.**
   - High, and the engine agrees: `file`. Write the note, leave `sources/`
     untouched. The note names the source; that is what `inbox` uses.
   - Medium or low, or the engine disagrees: stay in the queue. The user sees
     a short list ("this looks like a person named Samir, or a course
     note, I cannot tell") and picks with `file <id>`.
   - Blocked: the engine will not guess. Example: the path is under
     `sources/`, or a current note already has this title.
6. **Check.** `personal-memory check` must pass on the brain after a batch.

Jan's session is: drop files in `sources/`, open Cursor in the brain
folder, say "file the inbox." The agent uses Personal Memory tools. The user only
answers the low-confidence list.

### Who runs the LLM

**v1: the coding agent already in the editor. Personal Memory does not call an LLM
API and does not ask for a second key.**

Filing is judgment (`as_of`, type, which person, whether to supersede).
That is what Claude Code / Codex / Cursor are for. The user is already
paying for that session. The chat UI *is* the human-in-the-loop.

Personal Memory's job is the clerk work: list unfiled sources, accept or reject
proposals, enforce jar rules, refuse silent overwrite, leave `sources/`
alone. The split, and why the engine holds no model, is in the Write section.

Gbrain does both, on purpose:

- Interactive ingest uses **agent skills** (the OpenClaw / Claude Code
  session files pages). Same shape as Khaled's vault setup.
- Overnight extract / enrich / query expansion uses **keys inside
  gbrain** (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` in `~/.gbrain`). No
  chat session is open, so the binary has to call a model. With no chat
  key, those jobs stay off.

Personal Memory is not a 24/7 daemon in v1, so it should not collect a chat API
key. A later overnight `--model` path can copy gbrain's
daemon. Not now.

If the agent writes markdown with the editor instead of `personal-memory file`,
that is a bypass. `AGENTS.md` in the brain must say: new notes go
through Personal Memory. `personal-memory check` (and later a git hook) catch strays.

## MCP surface (v1)

Install is: point Personal Memory at a folder, add one MCP server entry in Claude Code /
Codex / Cursor. No website, no Telegram, no cloud account.

CLI and MCP share these seven words (locked 2026-09-12):

1. **remember.** Search the brain. Returns evidence cards, already filtered
   with `status` / `as_of` / `confidence` visible. Default to preferring
   `current` unless the question is historical.
2. **revisit.** Fetch one note by `id` or path, with frontmatter intact.
3. **inbox.** List `sources/` items with no filed note yet.
4. **draft.** Agent hands Personal Memory a filing. Personal Memory validates
   jar rules and queues it. Does not write the note.
5. **pending.** List filings waiting for review.
6. **file.** Write queued proposals that pass validation. High
   writes now. Low stays for the user. Never silent-overwrite a
   changing fact (supersede instead).
7. **note.** Same write path as `file`, for a single fact the user
   stated in chat rather than a `sources/` dump. Contract in the Write
   section.

Out of v1 MCP: Slack, Gmail, Calendar, a hosted HTTP MCP with OAuth, a
reranker, query-expansion LLMs, engine-owned chat API calls.

One ingestion path can follow later: Notion into `sources/`, modeled on
Khaled's existing `notion-sync`. Not a launch checklist of five
connectors.

## Tech (v1)

- Language: Python 3.11+, packaged so a non-infrastructure user can run one
  command (`uvx` or equivalent) later
- Why Python: Khaled already ships Python tooling, the vault scripts are
  Python, and Jan should not need Node + Docker + a cloud DB to start
- MCP: official Python SDK, stdio first (the coding-agent path)
- Search v1: walk markdown + frontmatter, keyword match, exact id/title,
  wikilink hop. SQLite FTS is allowed if grep gets painful. Postgres is not
  required.
- Optional later: embeddings as a second recall arm, same evidence-card
  contract

## Dogfood

Khaled keeps using `~/vault` every day. New engine features must run against
that folder the same week they land. If Personal Memory cannot serve the vault without
rewriting the notes, the engine is wrong, not the vault.

Schema changes are versioned. The vault opts in. No surprise rewrites of
historical notes.

## Out of scope until we say otherwise

- Public launch site
- OpenClaw / Hermes / Telegram
- Convex or any backend that becomes the source of truth
- Required vector search
- Slack / Google Suite ingestion
- Marketplace plugins (Claude Code / Codex / Cursor). v1 install is the
  CLI plus one MCP config snippet. A plugin can wrap that later.
- Multi-user company brain, authz beyond "this folder is yours"
- Changing Khaled's vault into a public demo

## Contract

GOAL: After v1, a coding agent connected to Personal Memory can answer a question from a
markdown brain using only remember/revisit, and every stated fact has an evidence
card. The same install works with embeddings disabled. A new user can run
`personal-memory check` on `examples/demo-brain` and get a clean pass without API keys.

CONSTRAINTS:

- Git markdown is the system of record
- No required cloud account, embedding key, or engine-owned LLM API key
- v1 clients are Claude Code, Codex, and Cursor only
- `sources/` is never rewritten by Personal Memory or the agent
- Low-confidence proposals never auto-apply
- Do not put real personal notes in this repo
- Do not treat two `current` notes on one fact as a tie to pick silently

FORMAT:

- Engine code under `src/personal_memory/`
- Fake brain under `examples/demo-brain/`
- This spec under `docs/v1-spec.md`
- Evidence cards as the recall return shape

FAILURE (any of these means v1 is not done):

- Install requires Voyage, OpenAI embeddings, or Postgres
- Recall can return a superseded note as if it were current
- Recall returns a chunk with frontmatter stripped
- An answer cites a file but no line range
- `personal-memory check examples/demo-brain` needs a network call
- Khaled's vault notes are copied into this repo
- Filing requires the user to paste an OpenAI/Anthropic key into Personal Memory
- Low-confidence dumps are written into the brain with no review
- `sources/` files are moved or edited by `file`

## Implementation order

1. Schema check (`personal-memory check`) on a folder, including the demo brain
2. Recall over markdown + frontmatter + evidence cards (library, then MCP)
3. Get-by-id (`revisit`)
3a. Eval corpus, fixtures, baseline gate (`docs/evals-spec.md`). Lands before
    wikilink hops so hops are measured, not assumed.
4. Done. MCP stdio server + install snippet for the three coding agents
5. Done. Unfiled scan (`inbox`), proposal queue (`draft` / `pending`),
   apply (`file`) with human review for low confidence, and `note`
6. Dogfood on `~/vault` (including `70-sources/` as the dump pile)
7. Optional Notion connector into `sources/`
8. Optional vectors as a second recall arm (fail-open)
9. Optional later: engine-owned model key for overnight filing with no
   editor session (gbrain autopilot path)

## Open

- Rejecting a queued proposal: today the person deletes the file; a `reject`
  command with a reason may be worth the audit trail
- Whether `check` should flag a `current` note whose State was last true
  before its newest Log line (a staleness hint, not an error)
- `personal-memory init` to write a template brain (folders, `AGENTS.md`,
  empty `sources/`). Not a live verb.

Resolved 2026-09-10 (see Write): queue format is JSON under
`.personal-memory/queue/`; notes may carry an optional State plus Log shape;
`note` saves one fact and stub-creates when there is no target; the
`supersede` kind flips the old note in the same `file` call.

Resolved 2026-09-12 (see MCP surface): CLI and MCP share
`remember`, `revisit`, `inbox`, `draft`, `pending`, `file`, `note`.
`remember` is search. `note` is the chat write.
