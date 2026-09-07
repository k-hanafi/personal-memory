# Pith

Working name. This GitHub repo is **private** until v1 is something a stranger
can install.

Pith is a personal brain for coding agents (Claude Code, Codex, Cursor). The
brain is a git folder of markdown. The engine answers with citations,
freshness, and confidence. Vector search is optional and off unless you turn
it on later.

The plan lives in [docs/v1-spec.md](docs/v1-spec.md). Read that before writing
code.

## Status

2026-09-06: spec plus a schema checker. No MCP server yet. Filing loop
is specified in `docs/v1-spec.md` (sources dump, agent proposes, pith
applies, human reviews low confidence).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pith check examples/demo-brain
pytest
```

`python3 -m venv .venv` creates a project-local install folder so pith does not
land in your system Python. `source .venv/bin/activate` makes that folder the
active Python for this terminal. `python -m pip install -e ".[dev]"` installs
pith plus test tools. The `-e` means edits to `src/` show up without reinstalling.

## Layout

| Path | What it is |
|---|---|
| `docs/v1-spec.md` | Product plan. Wins over code until we change it. |
| `examples/demo-brain/` | Fake notes for tests and a future install walkthrough |
| `src/pith/` | Engine (today: frontmatter check only) |
