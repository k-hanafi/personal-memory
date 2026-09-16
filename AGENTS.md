# AGENTS.md

Instructions for AI coding agents. Read before making changes.

## Project overview

Personal Memory is a hosted personal brain for coding agents. v1 runs as a
URL plus a key (Railway + Postgres). Markdown in a git folder is the Layer 1
eval corpus, not how someone runs the product. Answers must carry an evidence
card (path, line range, `status`, `as_of`, `confidence`). Vector search is
optional and must not be required to install or to answer correctly.

Canonical plan: `docs/v1-spec.md`. If implementation drifts, update the spec
in the same change or stop and say so.

**Status (2026-09-16):** hosted v1 locked. `check` validates frontmatter.
`remember` returns evidence cards (keyword + exact id/title, one wikilink hop
from the claim line, current-only unless `--historical`). `revisit` fetches one
note by id or path with frontmatter intact. Layer 1 evals are complete: 109-note
corpus, five fixture families, `personal-memory eval run`, a committed baseline
at `evals/baselines/main.json` (family totals in `README.md`), and an `eval-gate` CI
job that fails on any gold regression. The write path exists: `draft`, `pending`,
`file`, `note`, and `inbox` (spec: Write section). Notes may carry a dated
`## Log` section. Hosted MCP: `personal-memory serve` (URL plus key; folder store
is a stub until Postgres). Stdio MCP: `personal-memory mcp --brain` for tests
and CI. Personal Memory does not call an LLM API in v1.

Do not put Khaled's real vault notes in this repo.

## Tech stack

- Python 3.11+
- Packaging: `pyproject.toml`, pip, a local `.venv`
- Tests: pytest
- MCP: official Python SDK. Hosted path is Streamable HTTP plus a bearer key
  (`personal-memory serve`). Stdio (`personal-memory mcp --brain`) is tests/CI.
- v1 live store is Postgres (not built in this slice; folder is the stub).
- Not in v1: Convex, required embeddings, Telegram, OpenClaw, marketplace
  plugins, OAuth MCP

## Repository layout

Exists:

- `docs/v1-spec.md`: product plan
- `docs/evals-spec.md`: eval architecture (three layers, fixture families, CI gate)
- `docs/eval-corpus-plan.md`: persona, note inventory, and why notes exist in `evals/brain/`
- `docs/sources.md`: every outside source a design choice traces to
- `examples/demo-brain/`: fake notes with the v1 frontmatter contract
- `src/personal_memory/`: frontmatter parse, `check`, `recall.py` (search library), `get.py`, `notes.py` (shared loader), `notelog.py` (Log section), `filing.py` (`draft`, `pending`, `file`, `note`; library `submit`, `apply`, `note`), `unfiled.py` (`inbox`), `mcp.py` (stdio server), `http.py` (hosted MCP, URL plus key), and `evals/` (fixture loader, adapters, checks)
- `tests/`: checker, remember/revisit CLI, Log, filing, inbox, stdio MCP, and HTTP MCP tests against the demo brain (write tests copy it to a temp folder)
- `evals/brain/`: fictional eval corpus (Alex Rivera persona), `evals/deny-list.txt`: name guard list
- `evals/fixtures/`: TOML fixture files, one per family (supersession, abstention, named-thing, contradiction, citation)
- `evals/baselines/main.json`: committed scores on `main`; `scripts/eval-gate.sh`: the CI regression gate
- `.cursor/environment.json`: Cloud Agent install script (venv + `.[dev]`)

Planned (do not invent extra layers before these):

- Postgres live store, hosted recall/write, Railway host, zip-export (spec remaining)
- Layer 2 vault replay and Layer 3 agent-in-the-loop evals (spec: `docs/evals-spec.md`)
- Optional vector recall arm (fail-open)

## Development commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
personal-memory check examples/demo-brain
personal-memory remember examples/demo-brain teaching load
personal-memory revisit examples/demo-brain alex-rivera
personal-memory draft examples/demo-brain
personal-memory pending examples/demo-brain
personal-memory file examples/demo-brain
personal-memory note examples/demo-brain "One fact." --provenance "user, 2026-09-10" --target alex-rivera
personal-memory inbox examples/demo-brain
personal-memory serve --key KEY --brain examples/demo-brain
personal-memory mcp --brain examples/demo-brain
personal-memory eval run
bash scripts/eval-gate.sh
```

v1 clients paste a URL and a key (README). `serve` is that hosted door. `--brain`
is the folder stub until Postgres. `mcp --brain` is stdio for tests and CI, not
the product install. `examples/demo-brain` has no `sources/` dumps, so `inbox`
is empty. The demo has no queued filings. `draft` reads a JSON proposal from
stdin, or from a file you write. Do not commit a config that points at a real
vault.

`python3 -m venv .venv` creates a local install folder. `source .venv/bin/activate`
uses it in this terminal. `python -m pip install -e ".[dev]"` installs the CLI and
the test runner.

## Cursor Cloud specific instructions

Cloud agents run on an Ubuntu VM. They do not have this laptop, `/Users/k/vault`,
User Rules, or `~/.cursor/skills`. After a Build, `.venv` already exists from
`.cursor/environment.json`. Use the same commands as Development commands, with
`.venv/bin/` in front of each binary (`.venv/bin/pytest`,
`.venv/bin/personal-memory ...`). For the eval gate, put that folder on `PATH`
so the script can find the CLI:

```bash
PATH=".venv/bin:$PATH" bash scripts/eval-gate.sh
```

If `.venv` is missing, run the `install` command in `.cursor/environment.json`.
Use `examples/demo-brain/` and `evals/brain/` only. Never copy real vault
notes into this repo. Layer 1 evals need no product API keys. HTTP MCP tests
mint their own throwaway key.

## Where to work

| Task | Start here |
|------|-----------|
| Product rules, scope, v1 vs later | `docs/v1-spec.md` |
| Evals, fixtures, baseline gate | `docs/evals-spec.md` |
| Eval corpus inventory and why notes exist | `docs/eval-corpus-plan.md` |
| Eval corpus notes | `evals/brain/`, `docs/eval-corpus-plan.md` |
| Eval loader, adapters, checks | `src/personal_memory/evals/` |
| Why a design choice was made, what we read | `docs/sources.md` |
| Frontmatter / `personal-memory check` | `src/personal_memory/frontmatter.py`, `src/personal_memory/check.py` |
| Search / evidence cards | `src/personal_memory/recall.py` (`remember` CLI and MCP) |
| Open one note | `src/personal_memory/get.py` (`revisit`) |
| Writes: draft, pending, file, note | `src/personal_memory/filing.py`, spec Write section |
| Hosted MCP (URL plus key) | `src/personal_memory/http.py` (`personal-memory serve`) |
| MCP stdio (tests/CI) | `src/personal_memory/mcp.py` |
| Log section (dated facts inside a note) | `src/personal_memory/notelog.py` |
| Inbox (unfiled sources) | `src/personal_memory/unfiled.py` |
| Fake corpus | `examples/demo-brain/` |
| Tests | `tests/` |
| Cloud VM install | `.cursor/environment.json` |

## Maintaining this file

Update this file in the same change when structure, architecture, commands,
or milestones change. Keep the cloud section accurate if install steps move.
