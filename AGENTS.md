# AGENTS.md

Instructions for AI coding agents. Read before making changes.

## Project overview

Personal Memory is a git-native personal brain for coding agents. Markdown in a
folder is the system of record. Answers must carry an evidence card (path, line
range, `status`, `as_of`, `confidence`). Vector search is optional and must
not be required to install or to answer correctly.

Canonical plan: `docs/v1-spec.md`. If implementation drifts, update the spec
in the same change or stop and say so.

**Status (2026-09-10):** spec locked. `check` validates frontmatter.
`recall` returns evidence cards (keyword + exact id/title, one wikilink hop
from the claim line, current-only unless `--historical`). `get` fetches one
note by id or path with frontmatter intact. Layer 1 evals are complete: 109-note
corpus, 36 fixture cases in five families, `personal-memory eval run`, a
committed baseline, and an `eval-gate` CI job that fails on any gold regression
(recall 28/36, grep 7/36). No MCP, no filing queue yet. Personal Memory does not
call an LLM API in v1.

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
- `docs/eval-corpus-plan.md`: persona, note inventory, planted problems, build order for `evals/brain/`
- `docs/sources.md`: every outside source a design choice traces to
- `examples/demo-brain/`: fake notes with the v1 frontmatter contract
- `src/personal_memory/`: frontmatter parse, `check`, `recall`, `get`, and `evals/` (fixture loader, adapters, checks)
- `tests/`: checker, recall, and get tests against the demo brain
- `evals/brain/`: fictional eval corpus (Alex Rivera persona), `evals/deny-list.txt`: name guard list
- `evals/fixtures/`: TOML fixture files, one per family (supersession, abstention, named-thing, contradiction, citation)
- `evals/baselines/main.json`: committed scores on `main`; `scripts/eval-gate.sh`: the CI regression gate
- `.cursor/environment.json`: Cloud Agent install script (venv + `.[dev]`)

Planned (do not invent extra layers before these):

- Layer 2 vault replay and Layer 3 agent-in-the-loop evals (spec: `docs/evals-spec.md`)
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
personal-memory eval run
bash scripts/eval-gate.sh
```

`python3 -m venv .venv` creates a local install folder. `source .venv/bin/activate`
uses it in this terminal. `python -m pip install -e ".[dev]"` installs the CLI and
the test runner.

## Cursor Cloud specific instructions

Cloud agents run on an Ubuntu VM. They do not have this laptop, `/Users/k/vault`,
User Rules, or `~/.cursor/skills`. After a Build, `.venv` already exists from
`.cursor/environment.json`. Use those binaries:

```bash
.venv/bin/pytest
.venv/bin/personal-memory check examples/demo-brain
.venv/bin/personal-memory recall examples/demo-brain teaching load
.venv/bin/personal-memory get examples/demo-brain alex-rivera
.venv/bin/personal-memory eval run
bash scripts/eval-gate.sh
```

If `.venv` is missing, run the `install` command in `.cursor/environment.json`.
Use `examples/demo-brain/` (and later `evals/brain/`) only. Never copy real vault
notes into this repo. No product API keys are required.

## Where to work

| Task | Start here |
|------|-----------|
| Product rules, scope, v1 vs later | `docs/v1-spec.md` |
| Evals, fixtures, baseline gate | `docs/evals-spec.md` |
| Eval corpus contents and build order | `docs/eval-corpus-plan.md` |
| Eval corpus notes | `evals/brain/`, `docs/eval-corpus-plan.md` |
| Eval loader, adapters, checks | `src/personal_memory/evals/` |
| Why a design choice was made, what we read | `docs/sources.md` |
| Frontmatter / `personal-memory check` | `src/personal_memory/frontmatter.py`, `src/personal_memory/check.py` |
| Recall / evidence cards | `src/personal_memory/recall.py` |
| Get by id or path | `src/personal_memory/get.py` |
| Fake corpus | `examples/demo-brain/` |
| Tests | `tests/` |
| Cloud VM install | `.cursor/environment.json` |

## Maintaining this file

Update this file in the same change when structure, architecture, commands,
or milestones change. Keep the cloud section accurate if install steps move.
