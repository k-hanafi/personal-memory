# AGENTS.md

Instructions for AI coding agents. Read before making changes.

## Project overview

Personal Memory is a git-native personal brain for coding agents. Markdown in a
folder is the system of record. Answers must carry an evidence card (path, line
range, `status`, `as_of`, `confidence`). Vector search is optional and must
not be required to install or to answer correctly.

Canonical plan: `docs/v1-spec.md`. If implementation drifts, update the spec
in the same change or stop and say so.

**Status (2026-09-09):** spec locked. `check` validates frontmatter.
`recall` returns evidence cards (keyword + exact id/title, current-only
unless `--historical`). `get` fetches one note by id or path with
frontmatter intact. No wikilink hops, no MCP, no filing queue yet.
Personal Memory does not call an LLM API in v1.

Do not put Khaled's real vault notes in this repo.

## Tech stack

- Python 3.11+
- Packaging: `pyproject.toml`, pip, a local `.venv`
- Tests: pytest
- Planned: MCP Python SDK over stdio (Claude Code, Codex, Cursor)
- Not in v1: Postgres, Convex, required embeddings, Telegram, OpenClaw,
  marketplace plugins

## Repository layout

Exists:

- `docs/v1-spec.md`: product plan
- `docs/evals-spec.md`: eval architecture (three layers, fixture families, CI gate)
- `docs/sources.md`: every outside source a design choice traces to
- `examples/demo-brain/`: fake notes with the v1 frontmatter contract
- `src/personal_memory/`: frontmatter parse, `check`, `recall`, `get`
- `tests/`: checker, recall, and get tests against the demo brain

Planned (do not invent extra layers before these):

- `evals/`: fictional eval corpus, TOML fixtures, committed baseline, `personal-memory eval` (spec: `docs/evals-spec.md`)
- MCP stdio server
- Unfiled scan, proposal queue, apply (human review for low confidence)
- Optional vector recall arm (fail-open)

## Development commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
personal-memory check examples/demo-brain
personal-memory recall examples/demo-brain teaching load
personal-memory get examples/demo-brain alex-rivera
```

`python3 -m venv .venv` creates a local install folder. `source .venv/bin/activate`
uses it in this terminal. `python -m pip install -e ".[dev]"` installs the CLI and
the test runner.

## Where to work

| Task | Start here |
|------|-----------|
| Product rules, scope, v1 vs later | `docs/v1-spec.md` |
| Evals, fixtures, baseline gate | `docs/evals-spec.md` |
| Why a design choice was made, what we read | `docs/sources.md` |
| Frontmatter / `personal-memory check` | `src/personal_memory/frontmatter.py`, `src/personal_memory/check.py` |
| Recall / evidence cards | `src/personal_memory/recall.py` |
| Get by id or path | `src/personal_memory/get.py` |
| Fake corpus | `examples/demo-brain/` |
| Tests | `tests/` |

## Maintaining this file

Update this file when structure, architecture, or milestones change.
See ~/.cursor/user-rules/agents-md-maintenance.md for the full checklist.
