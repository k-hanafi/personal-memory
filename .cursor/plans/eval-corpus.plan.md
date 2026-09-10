# Eval corpus build (orchestrator SoT)

Spec: `docs/eval-corpus-plan.md` (inventory, planted problems, process).
Branch: `eval-corpus` (off `main`, 2026-09-09). Nothing committed yet.
Workers: `cursor-grok-4.6-xhigh-fast`, generalPurpose.

## STATUS

State: PHASE 2 COMPLETE AND COMMITTED (a5e6888 on `eval-corpus`; phase 1
is eae9e61). Corpus is FROZEN per the freeze rule. 109 notes, 5 raw files,
8,603 words (target was 15k; not padded, see report), 87 distinct queries,
85 planted rows: 49 pass (14/20 phase 1, 28+7 wrong-reason of 65 phase 2),
28 fail, 2 not runnable. `docs/evals-implementation-plan.md` disappeared
from the tree on its own (user action), never committed.

PR #2 open: https://github.com/k-hanafi/personal-memory/pull/2. Local
Bugbot: no findings. GitHub Bugbot check: SUCCESS. Merge state CLEAN, zero
review comments. Awaiting user merge (never merge myself).

Next: spec step 2, fixture loader + Hit shape + recall/rg adapters, on a
new branch off eval-corpus after merge. Engine bugs the corpus exposed, in
priority order: wikilink stripping hides names (row 80), contradicted_by
fires on any two current hits (rows 4, 9, 13, 14, 55 to 58), non-ASCII
tokenization (row 68), aliases matched as one string (row 7).

Phase 1 state (superseded by the above): 38 notes + 1
no-frontmatter .md, check ok (3 skipped), 19 tests pass, no dangling links.
Observed table in `evals/brain/README.md`. 14/20 planted problems pass
(3 for the wrong reason: rows 7, 9, 13), 3 fail (rows 10, 18, 19).

Env note: `.venv/bin/pytest` shebang points at the old pith venv path; use
`python -m pytest` or recreate the venv.

Phase 2 (enrichment) PLANNED, not built: `docs/eval-corpus-plan.md`
section "Phase 2: enrichment" (audit worker 721935f8). 73 new notes + 6
edits, rows 21 to 85, Layer 3 bank, 4-wave build order, freeze rule.
Targets: 108 notes, ~15k words, 20 people, 25 daily, 7 sources, ~90 queries.
Audit found 12 defects in phase 1 notes; fixes scheduled in the Edits table
except defect 10 (left on purpose). Engine findings added to Open.

Phase 1 committed: eae9e61. Untracked and NOT mine: docs/evals-implementation-plan.md
(left alone; ask user).

Phase 2 RUNNING. Wave 1 people done (330738de): 52 notes. Finding: `Søren`
returns 10 cards, tokenizer splits on non-ASCII and `ren` substring-matches.
Wave 2 lanes in background: 2a projects/decisions/edits (47af5c47),
2b areas (dc196bd3), 2c meetings/reading (4538ff3e), 2d daily (3bae61ce),
2e sources (d708bce2).
Then wave 3 noise pass + wave 4 integration (single worker), then commit.
All five lanes done: 109 notes, 5 skipped. Prediction misses to record:
row 11 line 63 to 64, row 28 dump id contains `grant`, row 56 five cards,
row 68 `Søren` tokenizer finding, row 80 wikilink stripping confirmed.
Waves 3+4 running (03307c22): CRLF, noise confirm, 85-row README,
plan cell fixes, Layer 3 gold lines, Targets actuals, link check, AGENTS.
After it reports: commit phase 2 on eval-corpus. Then spec step 2 (fixture loader, Hit shape,
recall + rg adapters). Contradiction family needs negative cases (rows 4, 9,
14 show `contradicted_by` fires on any two current hits).

Deferred (vault-side, not a worker job): private deny list at
`~/vault/90-meta/evals/deny-list.txt` built from vault people/employer names.
Ask user before touching the vault.

Findings so far:
- Plan row 7 (multi-alias `PN`) is wrong: `_keyword_score` substring-matches
  tokens against the normalized aliases string, so `PN` returns Priya via
  keyword scoring even though the exact-alias arm never fires. Reclassify as
  "passes for the wrong reason" in wave 3. Correct the plan doc too.
- Areas done (a684b4a2): 23 notes, check ok. Row 4 tie-break holds, but
  `teaching load` also lists teaching-load-committee in `contradicted_by`
  of the current note. Same root cause as row 9. Record in README.
- advising-load does not say "teaching" (worker chose to avoid a third hit).
- Daily+sources done (1b3428b3): 28 notes. Row 15 is weak: loader globs
  `*.md` only, so the .txt is never read. Wave 3: rename to
  `pasted-email-chair.md` with no frontmatter (tests the real skip path),
  fix plan inventory + row 15.

Waves:
1. Seed `evals/brain/` from demo brain; identity (2) + people (6). Foreground.
2. Parallel, background: areas (12) | projects (7) + decisions (5) | daily (5) + sources (2).
3. Integration: `evals/brain/README.md` with recorded reality (step 6), deny list + pytest guard (step 7), link check (step 8), spec/AGENTS pointers (step 9), full `check` + `pytest`.

Decisions:
- One persona (Alex Rivera). Ids equal filename stems, fixed by the plan, so waves can run in parallel without coordinating ids.
- Two deny lists: short committed, full private in vault. Guard is a pytest test.
- No commits until user asks. No fixtures in this build.

Open (carry to fixtures phase):
- `type: daily` and `contradicted_by`.
- `expect_confidence` fixture field.

Next: after wave 3, report pass/fail table vs plan predictions; ask user about committing.
