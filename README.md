# Personal Memory

This GitHub repo is **private** until v1 is something a stranger can install.

Personal Memory is a personal brain for coding agents (Claude Code, Codex, Cursor).
v1 is hosted: paste a URL and a key. The engine answers with citations,
freshness, and confidence. Vector search is optional and off unless you turn
it on later. A git folder of markdown is the Layer 1 eval corpus, not how you
run the product.

The plan lives in [docs/v1-spec.md](docs/v1-spec.md). Read that before writing
code.

## Status

2026-09-16: hosted v1 locked. `check` validates frontmatter. `remember` searches
and returns evidence cards. `revisit` fetches one note by id or path.
Layer 1 evals are complete (`personal-memory eval run`, committed baseline,
`eval-gate` CI). The write path exists (`draft`, `pending`, `file`, `note`,
`inbox`). Hosted MCP exists (`personal-memory serve`): URL plus key, same seven
verbs. The folder behind `serve` is a stub until Postgres. Stdio MCP stays for
tests and CI. The engine holds no model: the coding agent decides what to file,
the engine validates and writes. See the Write section of `docs/v1-spec.md`.

## Connect (this is how v1 runs)

The editor calls a URL. Auth is a long random key, sent as
`Authorization: Bearer`. Not OAuth. Replace `URL` with the `/mcp` address and
`KEY` with that secret.

**Cursor.** Add this to `.cursor/mcp.json` (or Cursor Settings, MCP):

```json
{
  "mcpServers": {
    "personal-memory": {
      "url": "URL",
      "headers": {
        "Authorization": "Bearer KEY"
      }
    }
  }
}
```

**Claude Code.** From a terminal:

```bash
claude mcp add --transport http personal-memory URL --header "Authorization: Bearer KEY"
```

**Codex.** Add this to `~/.codex/config.toml`. Put the key in an env var, not
in the file:

```toml
[mcp_servers.personal-memory]
url = "URL"
bearer_token_env_var = "PERSONAL_MEMORY_API_KEY"
```

The seven tools are the same words as the engine: `remember`, `revisit`,
`inbox`, `draft`, `pending`, `file`, `note`.

Until Railway and Postgres land, you can boot that door on one machine with
`PERSONAL_MEMORY_API_KEY` set (or `--key`). `--brain` is the folder stub, not
the product:

```bash
personal-memory serve --key KEY --brain examples/demo-brain
```

That prints a `listening:` URL. Paste that URL and the key into the snippets
above. An empty stub (no `--brain`) is enough to prove the door opens. It is
not a hosted brain.

## Evals

Retrieval is measured by fixed questions against a fictional corpus. `recall` is our
engine. `grep` is a plain text search run on the same questions, so a reader can see
what searching the folder already gets you.

| family | recall | grep |
|---|---|---|
| abstention | 1/3 | 1/3 |
| citation | 4/6 | 0/6 |
| contradiction | 4/4 | 1/4 |
| named-thing | 9/10 | 2/10 |
| supersession | 7/8 | 2/8 |

These numbers are for the fictional corpus in `evals/brain/` and match the committed
baseline in `evals/baselines/main.json` (recall 25/31, grep 6/31). Cases that fail
today are capability targets, not bugs in the fixtures. How scoring and the CI gate
work is in [docs/evals-spec.md](docs/evals-spec.md).

```bash
personal-memory eval run
personal-memory eval run --update-baseline
bash scripts/eval-gate.sh
```

`eval run` prints the table and writes a receipt to `evals/runs/`. `--update-baseline`
rewrites `evals/baselines/main.json` from that run. `scripts/eval-gate.sh` compares a
fresh run to the baseline on `origin/main` and exits 1 if a passing `recall` case broke.

## Contributors

This is how you change the engine. It is not how a person runs v1.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
personal-memory check examples/demo-brain
personal-memory remember examples/demo-brain teaching load
personal-memory revisit examples/demo-brain alex-rivera
personal-memory eval run
bash scripts/eval-gate.sh
```

`python3 -m venv .venv` creates a project-local install folder so Personal Memory
does not land in your system Python. `source .venv/bin/activate` makes that folder
the active Python for this terminal. `python -m pip install -e ".[dev]"` installs
the CLI plus test tools. The `-e` means edits to `src/` show up without reinstalling.

Folder CLI verbs (`note`, `draft`, `pending`, `file`, `inbox`) and stdio
(`personal-memory mcp --brain`) still exist so tests and Layer 1 evals stay
hermetic. Do not commit a config that points at a real personal vault.

## Layout

| Path | What it is |
|---|---|
| `docs/v1-spec.md` | Product plan. Wins over code until we change it. |
| `docs/evals-spec.md` | Eval architecture, fixtures, and the CI gate. |
| `examples/demo-brain/` | Fake notes for tests and evals |
| `evals/brain/` | Fictional Layer 1 eval corpus |
| `src/personal_memory/` | Engine: `check`, `remember`, `revisit`, filing (`draft`, `pending`, `file`, `note`), `inbox`, hosted MCP, stdio MCP, and `eval` |
