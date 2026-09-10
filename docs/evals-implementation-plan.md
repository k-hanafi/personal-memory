# Evals implementation plan

How `docs/evals-spec.md` gets built, one pull request at a time, by a small team of agents with one human approving merges up front.

Written 2026-09-09. The spec says what the eval system is. `docs/eval-corpus-plan.md` says what goes in the corpus. This file says who builds what, in which order, and how a change gets from a branch to `main`.

## Where things stand

`main` has `check`, `recall`, and `get` with tests. The eval corpus is being built on the `eval-corpus` branch (PR 0 below). Nothing else from the spec exists yet. There is no CI.

## The factory

Three roles. One of them is a person.

**Orchestrator.** The parent chat. Owns this plan, cuts branches, writes each builder's brief, reviews the builder's summary, runs a local review pass, opens the pull request, spawns the babysitter, merges when the babysitter reports ready, updates the status table, and kicks off the next PR. The orchestrator writes almost no code itself.

**Builder.** One subagent per PR, run as a `best-of-n-runner` so it gets its own git worktree and branch. It receives a brief (template below), implements exactly that scope, runs the acceptance checks, commits, and reports back. It does not push and does not open the PR. Keeping push and PR creation with the orchestrator keeps commit identity, PR body quality, and the pre-registration habit in one place.

**Babysitter.** One subagent per open PR, following `~/.cursor/skills-cursor/autopilot/SKILL.md`. It watches CI and Bugbot, fixes what is in scope, dismisses what is wrong with a stated reason, and escalates anything touching security, privacy, or data. It reports READY when the PR is mergeable, CI is green, and Bugbot's latest review on the latest commit has no open threads. It does not merge.

**Khaled** approves the merge policy once, here, rather than per PR. Any PR in the table below may be squash-merged by the orchestrator once its babysitter reports READY. Anything outside the table, or any babysitter escalation, waits for him.

### Why this split

The autopilot skill says the agent must never merge or enable auto-merge. That rule exists because merging is the one irreversible step and a babysitter working alone has no way to know whether the human wanted it. This plan is the human saying so in advance, for a named list of PRs, with a named acceptance condition. The orchestrator, not the babysitter, performs the merge, so the skill's rule still holds for the agent that is closest to the churn.

Bugbot is the reviewer because a second pass by a different system catches what the builder's own tests do not. It works best on diffs of a few hundred lines with one concern each. The PR split below is sized for that.

## PR sequence

Dependencies are strict where an interface is involved and loose where only data is involved.

```
PR 0 eval-corpus ─────┐
                      ├──> PR 2 loader + adapters ──> PR 3 runner + CLI ──┐
PR 1 factory-setup ───┘                          └──> PR 4 fixtures ────┼──> PR 5 baseline + gate ──> PR 6 wikilink hops
```

PR 0 and PR 1 run in parallel. PR 3 and PR 4 can run in parallel once PR 2 is merged, because the fixture schema is fixed by PR 2's loader and the TOML files are data. PR 4's final validation needs PR 3's runner, so PR 4 merges second.

### Status

| PR | Branch | Scope | Depends on | Status |
|---|---|---|---|---|
| 0 | `eval-corpus` | `evals/brain/` (109 notes), `evals/deny-list.txt`, `tests/test_eval_brain_guard.py`, `docs/eval-corpus-plan.md`, spec and AGENTS pointers | none | merged |
| 1 | `factory-setup` | `.github/workflows/test.yml` running pytest; this plan; `evals/runs/` in `.gitignore` | none | merged |
| 2 | `eval-loader-adapters` | `src/personal_memory/evals/`: `Case` and fixture loader, `Hit`, check functions, `recall` adapter, grep adapter in pure Python; unit tests | 0, 1 | merged |
| 3 | `eval-runner-cli` | runner, receipt writer, table report, `personal-memory eval run` with `--corpus --fixtures --adapter --family --out`; determinism test | 2 | merged |
| 4 | `eval-fixtures` | five TOML files (about 30 cases) from the corpus plan's planted problems; fixture validation test; `expect_confidence` added to spec | 2 (start), 3 (merge) | merged |
| 5 | `eval-baseline-gate` | fixtures hash, `--update-baseline`, `--allow-regression`, `eval compare`, gate modes, `justification`, `scripts/eval-gate.sh`, `eval-gate` CI job, first `evals/baselines/main.json`, README scoreboard, spec open items closed | 3, 4 | merged |
| 6 | `wikilink-hops` | first engine change made under the gate; pre-registered prediction in the PR body | 5 | in flight |

Update this table when a status changes. It is the only place the whole program is visible at once.

### PR 0: eval corpus

Owned by the worker already running. Scope and done-criteria are in `docs/eval-corpus-plan.md`. The orchestrator's job on this one is to open the PR when the worker reports done, run the babysitter, and merge. Nothing in this plan changes that work.

### PR 1: factory setup

Small and independent. The workflow runs `pytest` on Python 3.11 and 3.12 on every push and pull request. The eval gate job is added later in PR 5; this PR gives the babysitters something to watch from the first PR onward.

Also in this PR: this document, and `evals/runs/` added to `.gitignore` so PR 3's receipts never get committed by accident.

Acceptance: the workflow file passes `gh workflow view` parsing, and the first push shows a green check on the PR.

Orchestrator tasks alongside PR 1, not in any PR: turn on branch protection for `main` requiring the `test` check (`gh api` on the branch protection endpoint), and confirm the Bugbot GitHub app is installed on the repository. If Bugbot is configured to run on demand rather than on every push, the babysitter triggers it with a `bugbot run` comment after each push.

### PR 2: loader and adapters

The first code PR. It defines the shapes everything else uses, so it is reviewed hardest.

Files under `src/personal_memory/evals/`:

- `fixtures.py`: `Case` dataclass matching the field table in the spec plus `expect_confidence`, and `load_fixtures(path) -> list[Family]` using `tomllib`. Unknown fields raise. Missing `id` raises. Duplicate `id` across files raises.
- `adapters.py`: `Hit` dataclass (`path`, `start_line`, `end_line`, `status`, `confidence`, `contradicted_by`), the `search()` signature from the spec, a `recall` adapter that wraps `personal_memory.recall.recall`, and a `grep` adapter written in Python that tokenizes the query, counts occurrences per file, ranks by count, reads frontmatter for `status` and `confidence`, and returns the first matching line as the range.
- `checks.py`: one function per fixture field. Each returns `None` on pass or the field name on fail. `check_case(case, hits) -> str | None` runs them in a fixed order and returns the first failure.

The grep adapter is Python rather than a shell call to `rg` because `rg` is not on the PATH on a default macOS install (this machine only has the one bundled inside Cursor.app), and the spec requires the run to work on a fresh machine with no extra binaries. This PR amends the spec's adapter section to say so.

Tests: loader rejects bad input; both adapters return `Hit` lists on `evals/brain`; `check_case` returns the right field name for each kind of failure using hand-built hits.

Size: roughly 350 lines of source and 200 of tests.

### PR 3: runner and CLI

- `runner.py`: for each family and adapter, run every case, collect results into a receipt dict: commit hash, fixtures hash, adapter, per-case pass or failing field plus the top five hits, per-family counts, superseded-leak count, abstention accuracy.
- `receipt.py`: write the dict as JSON with keys sorted and floats rounded to four places. Timestamp is a separate top-level key so it can be stripped for comparison.
- `report.py`: the table from the spec. One row per family, one column per adapter. The `vs main` column is added in PR 5 and prints blank until then.
- `cli.py`: `eval` subcommand with `run`, flags `--corpus`, `--fixtures`, `--adapter`, `--family`, `--out`. Defaults point at `evals/brain`, `evals/fixtures`, both adapters, all families, `evals/runs/<timestamp>.json`.

The receipt keeps the top five hits per case. The spec left this open; storing them costs a few kilobytes at this scale and saves a re-run every time a case fails.

Tests: run the suite twice on the same tree and assert the receipts are byte-identical with timestamps removed. This is the hermetic guarantee as a test, not a claim.

Size: roughly 300 lines of source and 150 of tests.

### PR 4: fixtures

Data plus one test. Five files in `evals/fixtures/`: `supersession.toml`, `abstention.toml`, `named-thing.toml`, `contradiction.toml`, `citation.toml`. Cases come from the twenty planted problems in `docs/eval-corpus-plan.md`, expanded where a problem has more than one query.

The builder writes each case, then runs the query against the corpus and records what happened. Where the corpus plan predicted "passes today" and it does not, the fixture stays as written and the discrepancy is noted in the PR body. Fixtures describe what should happen. They do not bend to what does.

`tests/test_eval_fixtures.py`: every fixture file loads; every `expect_path` exists in the corpus; every `expect_line` is within that file's length and the line is non-empty; every `forbid_paths` entry exists (a forbid on a missing file is a typo, not a constraint).

Also in this PR: the `expect_confidence` field added to the spec's field table.

Reviewer focus is gold correctness. Bugbot should be told, in the PR body, to check line numbers against file contents.

Size: about 30 cases across five files, one test file.

### PR 5: baseline and gate

- `baseline.py`: compute the fixtures hash (sha256 over sorted file contents of `evals/fixtures/` and `evals/brain/`), write `evals/baselines/main.json` from a receipt, compare two receipts case by case, and decide the gate outcome per the spec's two modes. Regressions under a changed hash require a `justification` string in the committed baseline.
- CLI: `eval run --update-baseline`, `eval run --allow-regression "<reason>"` (records the reason, local only), `eval compare <a.json> <b.json>`.
- `report.py`: fill in the `vs main` paired column.
- `scripts/eval-gate.sh`: fetches `origin/main`, extracts the baseline with `git show origin/main:evals/baselines/main.json`, runs the suite, compares, exits 1 on regression. CI and local use the same script.
- `.github/workflows/test.yml`: add an `eval-gate` job after `test`.
- `evals/baselines/main.json`: the first committed baseline, produced by the builder from a clean run.
- `README.md`: a scoreboard table, per family, `recall` versus `grep`, with the commit hash it came from.
- `docs/evals-spec.md`: close the open items (top-five hits in receipts, Python grep baseline, `expect_confidence`).

Acceptance is a live test, done by the orchestrator on a throwaway branch after merge: change `TITLE_SCORE` in `recall.py` so a named-thing case flips, push, watch the `eval-gate` job go red naming the case, delete the branch.

Size: roughly 300 lines of source, 100 of shell and workflow, plus docs.

### PR 6: wikilink hops

Not part of the eval folder. It is the first engine change made under the gate and the first use of pre-registration, so it belongs in this plan as the closing step.

Before the builder starts, the orchestrator writes the prediction into the brief and the PR body: which named-thing cases should flip from fail to pass, and that nothing else should move. The builder implements hops in `recall`, runs the suite, and reports the actual delta. The PR body records prediction and outcome side by side. Graduated cases enter the baseline with `--update-baseline`.

If the prediction misses, the PR still merges if the delta is an improvement with no regressions, and the miss is written down. That is the habit being installed.

## Builder brief template

Every builder gets the same shape. Fill every section; an empty section is a bug in the brief.

```
PR: <number and branch>
Base: main at <commit>
Read first: docs/evals-spec.md, docs/eval-corpus-plan.md, this plan's section for this PR, AGENTS.md

Scope (do all of this):
- <file>: <what it contains>
- ...

Out of scope (do none of this, even if it looks easy):
- ...

Acceptance (run these; paste the output in your report):
- pytest
- <specific commands from the PR section>

Constraints:
- No new dependencies. Standard library only.
- No em dashes anywhere, including comments and commit messages.
- Commit author must be Khaled Hanafi <kamhhm@gmail.com>. Check with
  git log --format='%an <%ae>' before reporting. No Co-authored-by trailers.
- Commit message: one line, imperative, says why. No "Cursor" or "agent".
- Do not push. Do not open a PR. Do not edit files outside scope.
- If the spec and this brief disagree, stop and report; do not pick one.

Report back with: files changed, acceptance output, anything you could not
do and why, any place the spec was wrong or silent.
```

## Babysitter brief template

```
PR: <url>
Follow ~/.cursor/skills-cursor/autopilot/SKILL.md exactly.

Loop until READY or BLOCKED:
1. gh pr view and gh pr checks. Never act on state from a previous pass.
2. Merge conflicts first. Rebase on origin/main, never force-push.
3. Bugbot and human comments second. For each open thread: fix (smallest
   change, reply with the commit), dismiss (reply with the concrete reason),
   or ask (stop and report; anything about security, privacy, the vault,
   or data handling is always ask).
4. Failing CI third. Read the log. Fix only what this PR caused.
5. After any push, wait for CI and for Bugbot's re-review on the new commit
   (gh pr checks --watch). If Bugbot is on-demand for this repo, comment
   "bugbot run".

READY means: mergeable, all checks green, Bugbot's latest review on the
latest commit has zero open threads, all human threads resolved.
Do not merge. Do not enable auto-merge. Report READY with the final commit
hash, or BLOCKED with what you tried and what you need.
```

## Orchestrator checklist per PR

1. Confirm the dependency PRs are merged and `main` is pulled.
2. Write the builder brief from the template and the PR section above.
3. Launch the builder as a `best-of-n-runner` on a fresh branch from `main`.
4. Read the builder's report. Run the acceptance commands yourself in the worktree. If anything fails, send the builder back with the failure, do not patch it yourself.
5. Run the local Bugbot subagent on the branch diff (`~/.cursor/skills-cursor/review-bugbot/SKILL.md`). Fix or send back anything it finds. This saves a round trip with the hosted reviewer.
6. Check commit identity: `git log main..HEAD --format='%an <%ae>'` shows only Khaled.
7. Push and open the PR with `gh pr create`. Body: what and why in two paragraphs, acceptance output, and for PR 6 the pre-registered prediction. For PR 4, a line asking the reviewer to verify line numbers against files.
8. Launch the babysitter with the PR URL.
9. On READY: `gh pr merge <n> --squash --delete-branch`. On BLOCKED: read the reason, decide, and either answer the babysitter or bring it to Khaled.
10. Pull `main`. Update the status table in this file on the next PR's branch. Start the next PR.

## Outside the PRs

Some of the work is not a code change and does not get a branch.

Branch protection on `main` requiring the `test` check, and later the `eval-gate` check. Done once by the orchestrator with `gh api`.

The private deny list at `~/vault/90-meta/evals/deny-list.txt` and the vault fixture file at `~/vault/90-meta/evals/vault-fixtures.toml`. Both are vault-side, written by the orchestrator following the vault's own filing rules, committed to the vault repo, never to this one. The first replay session (spec Layer 2) happens after PR 5 merges and produces the first capability fixtures for the next fixture PR.

The throwaway-branch gate test after PR 5.

## What is not in this plan

Layer 3 (agent in the loop) waits for the MCP server. The holdout slice waits for fifty fixtures. Model-generated corpus growth waits for hand-written notes to stop covering the families. A vector adapter waits for a reason to exist. None of these have a PR number here, and none should be started because a builder finished early.

## Risks

The `contradicted_by` logic in `recall` marks any two current notes matching a query as contradicting each other. Corpus plan problems 4, 9, 10, and 13 will expose this. Those fixtures will fail or pass for the wrong reason in PR 4, and the fix is an engine change that belongs in its own PR after PR 6, pre-registered like everything else. It is listed here so nobody "fixes" it inside PR 4 to make the numbers look better.

Bugbot may comment on the corpus notes as if they were prose. The babysitter should dismiss style comments on fictional note content with a one-line reason; the corpus is test data.

Two builders touching `cli.py` (PR 3 and PR 5) in sequence is fine. Two touching it in parallel is not. PR 3 and PR 4 may overlap only because PR 4 does not touch source.
