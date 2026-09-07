# AGENTS.md

Instructions for AI coding agents. Read before making changes.

## Project overview

Pith is a git-native personal brain for coding agents. Markdown in a folder
is the system of record. Answers must carry an evidence card (path, line
range, `status`, `as_of`, `confidence`). Vector search is optional and must
not be required to install or to answer correctly.

Canonical plan: `docs/v1-spec.md`. If implementation drifts, update the spec
in the same change or stop and say so.

**Status (2026-09-06):** spec locked, `pith check` validates frontmatter,
demo brain exists. No MCP server, no recall, no filing queue yet.
Filing is specified: dumps land in `sources/`, the coding agent
proposes, pith applies high-confidence jar-valid notes, humans review
the rest. Pith does not call an LLM API in v1.

Working name: pith. Rename is allowed while the GitHub repo is private.
Do not put Khaled's real vault notes in this repo.

## Tech stack

- Python 3.11+
- Packaging: `pyproject.toml`, pip, a local `.venv`
- Tests: pytest
- Planned: MCP Python SDK over stdio (Claude Code, Codex, Cursor)
- Not in v1: Postgres, Convex, required embeddings, Telegram, OpenClaw

## Repository layout

Exists:

- `docs/v1-spec.md` — product plan
- `examples/demo-brain/` — fake notes with the v1 frontmatter contract
- `src/pith/` — frontmatter parse, `pith check`
- `tests/` — checker tests against the demo brain

Planned (do not invent extra layers before these):

- Recall returning evidence cards
- Get-by-id
- MCP stdio server
- Unfiled scan, proposal queue, apply (human review for low confidence)
- Optional vector recall arm (fail-open)

## Development commands

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
pith check examples/demo-brain
```

`python3 -m venv .venv` creates a local install folder. `source .venv/bin/activate`
uses it in this terminal. `python -m pip install -e ".[dev]"` installs pith and
the test runner.

## Where to work

| Task | Start here |
|------|-----------|
| Product rules, scope, v1 vs later | `docs/v1-spec.md` |
| Frontmatter / `pith check` | `src/pith/frontmatter.py`, `src/pith/check.py` |
| Fake corpus | `examples/demo-brain/` |
| Tests | `tests/` |

## Maintaining this file

Update this file when structure, architecture, or milestones change.
See ~/.cursor/user-rules/agents-md-maintenance.md for the full checklist.
