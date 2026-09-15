# Sources

Everything Personal Memory borrows an idea from, and what we borrowed. One line each.

This file is the answer to "where did that come from." If a design choice in `docs/v1-spec.md` or `docs/evals-spec.md` traces to something we read, it is listed here. If it is not listed, the choice is ours.

The date in each entry is when we read it. Blog posts and repos change. If a claim below stops matching the source, update the entry and say what changed.

## How to add a source

Add an entry when a document changes a decision in this repo. Do not add things we skimmed and ignored. Write what we use it for, in one sentence, in plain words. Link the exact page, not the homepage. For papers, use the arXiv abstract page and include the identifier so the entry survives a URL change.

## Prior art: products and their eval repos

**Gbrain** by Garry Tan. https://github.com/garrytan/gbrain. Read 2026-09-08.
The closest existing product. Git markdown as source of truth, Postgres index, hybrid search, agent skills. We take the ownership idea and the eval discipline, and leave the database, the connectors, and the hosted agent.

**Gbrain retrieval writeup** (README search section and `docs/eval-bench.md`). Read 2026-09-02 and 2026-09-08.
Their own numbers show keyword-only and vector-only scoring close together, with the big precision jump coming from the page graph. This is why vectors are optional in our v1.

**gbrain-evals** repository. https://github.com/garrytan/gbrain-evals. Read 2026-09-08.
Public, reproducible scorecards with the commit hash, the fictional corpus, and the numbers they are not proud of. Our Layer 1 is modeled on this repo. The line "gbrain is one system under test, not the subject of the benchmark" is where our adapter interface comes from.

**BrainBench methodology**, `docs/eval/BRAINBENCH.md` in the Gbrain repo. Read 2026-09-08.
The gate: baseline fetched from `main`, exact comparison on unchanged fixtures, byte-match plus `justification` string when fixtures change, 15% holdout, no self-approval. We copied the mechanism nearly whole.

**Search-mode methodology**, `docs/eval/SEARCH_MODE_METHODOLOGY.md` in the Gbrain repo. Read 2026-09-08.
Pre-registration: write the predicted number before the run, publish the miss. Also the paired +/- reporting style.

**Gbrain v0.40.6.0 benchmark snapshot**, in gbrain-evals `docs/benchmarks/`. Read 2026-09-08.
The ablation table (full system 49.1% P@5, no graph 19.2%, grep + BM25 17.1%, vector only 10.8%). Source of our rule that the grep row is always published.

**Gbrain system-of-record contract**, `docs/architecture/system-of-record.md` in the Gbrain repo. Read 2026-09-10.
Markdown is canonical, the database is a rebuildable index, and a CI gate fails any write that skips the markdown. Also the forget and supersede encoding: rows are struck through with a date, never deleted. Source of our "one door" rule and of never overwriting in place.

**Gbrain memory verbs protocol**, `docs/protocol/MEMORY_VERBS_v1.md` in the Gbrain repo. Read 2026-09-10.
`remember(fact, provenance, entity?, kind?)` with provenance required, returning `inserted | duplicate | superseded`, and `recall` as a zero-LLM search verb. Their write-`remember` is our `note`. Our `remember` is search and returns evidence cards. Mandatory provenance on the write comes from here. Their dedup rides embeddings and degrades without them; ours starts from exact match.

**Gbrain filing rules and ambient writeback**, `skills/_brain-filing-rules.md` and `docs/guides/ambient-writeback.md` in the Gbrain repo. Read 2026-09-10.
File by primary subject, a notability gate ("when in doubt, don't create"), source precedence when claims conflict, and automatic capture as an opt-in prompt contract with a skip list rather than a new verb. Our Write section's placement rule and automatic-capture paragraph follow this.

**Andrej Karpathy, "LLM Wiki" gist.** https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f. Read 2026-09-10.
Immutable raw sources, an LLM-maintained wiki, a small `index.md`, an append-only `log.md`, and a lint pass for contradictions, stale claims, and orphans. Source of the agent-run lint we try before any background filer, and of the "file next to what you link to" placement habit.

**Mem0, "Platform: Migrating to the New Memory Algorithm."** https://docs.mem0.ai/migration/platform-v2-to-v3. Read 2026-09-10.
They removed the in-engine LLM diff (ADD/UPDATE/DELETE) and moved to append-only with links, resolving currency at retrieval. Evidence that write-time judgment inside the engine is the part the field is walking away from.

**Zep / Graphiti bi-temporal model.** https://getzep-graphiti.mintlify.app/concepts/temporal-model. Read 2026-09-10.
Four timestamps per fact (`valid_at`, `invalid_at`, `created_at`, `expired_at`); contradictions close the old fact's window instead of deleting it. Our `as_of` plus `status: superseded` is the note-level version of `valid_at` plus `invalid_at`.

**Anthropic memory tool.** https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool. Read 2026-09-10.
Six raw file commands under `/memories`, no schema. The zero-engine floor: it shows what an agent writing files directly gets, which is what our engine's validation is there to improve on.

**Sentra**, "What is a company brain?" https://www.sentra.app/articles/what-is-a-company-brain. Read 2026-09-01.
Five requirements for a brain: gather where work happens, preserve decisions and why, stay current, respect access boundaries, one memory for people and agents. "Stay current" is the requirement our `status` and `as_of` fields serve. Sentra's benchmark numbers are vendor-stated and we do not compare against them.

**Sentra vs Zep** comparison page. https://www.sentra.app/articles/sentra-vs-zep. Read 2026-09-08.
Useful mainly as a list of which public benchmarks each memory vendor reports. Confirms that different vendors measure different things.

**Mem0 memory evaluation docs.** https://docs.mem0.ai/core-concepts/memory-evaluation. Read 2026-09-08.
They report tokens per retrieval next to accuracy. We copy that pairing for Layer 3.

**Mem0, "Building Production-Ready AI Agents with Scalable Long-Term Memory."** arXiv 2504.19413, ECAI 2025. Read 2026-09-08 (HTML version).
The first broad head-to-head of memory systems on one benchmark. Read together with the Zep rebuttal below as a lesson in how not to publish comparisons.

**Zep, "Lies, Damn Lies, and Statistics."** https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory. Read 2026-09-08.
Zep's rebuttal to the Mem0 paper, later corrected from 84% to 75.14% after an arithmetic error was found. With the GitHub issue below, this is why we do not chase competitor numbers and instead publish our own corpus and ablation.

**Mem0 response to Zep**, GitHub issue on getzep/zep-papers. https://github.com/getzep/zep-papers/issues/5. Read 2026-09-08.
The other half of the dispute. Also a reminder that SDK defaults and timestamp handling can swing a benchmark by tens of points.

**Letta, "Benchmarking AI Agent Memory: Is a Filesystem All You Need?"** https://www.letta.com/blog/benchmarking-ai-agent-memory. Read 2026-09-08.
A plain file plus `grep` scored 74% on LoCoMo, above a specialized memory product. Supports our keyword-first design and our insistence on a grep baseline row.

## Papers

**LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory.** Wu et al., ICLR 2025. arXiv 2410.10813. Read 2026-09-08.
Five abilities to test: information extraction, multi-session reasoning, temporal reasoning, knowledge updates, abstention. We adopt abstention as a scored family and the index, retrieve, read split as the line between Layer 1 and Layer 3. Their finding that a perfect retriever still loses accuracy at the reading step is why Layer 3 exists.

**MEME: Multi-entity and Evolving Memory Evaluation.** KAIST, 2026. arXiv 2605.12477. Read 2026-09-08.
Cascade, Absence, and Deletion tasks, and the trivial-pass filter: credit only if the system was right before and after the change. Our supersession family uses that filter. Six systems averaged 3% on Cascade and 1% on Absence, which tells us staleness is the unsolved part of the field and the right place to compete.

**ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems.** Saad-Falcon et al. arXiv 2311.09476. Read 2026-09-08.
Synthetic questions filtered by round-trip consistency, and judges calibrated on a small set of human labels before use. Our rule that no model judge runs without validation against hand labels comes from here.

**Can we Evaluate RAGs with Synthetic Data?** arXiv 2508.11758. Read 2026-09-08.
Synthetic benchmarks rank systems reliably only under some conditions. This is why every family keeps hand-written cases even after we start generating fixtures with a model.

## Practitioner writeups

**Anthropic, "Demystifying evals for AI agents."** https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents. Published 2026-01-09. Read 2026-09-08.
Capability evals versus regression evals, cases graduating from one to the other, pass@k versus pass^k, and "read the transcripts." Our gate only cares about regression cases, and Layer 3 reports pass^3.

**Hamel Husain, "Your AI Product Needs Evals."** https://hamel.dev/blog/posts/evals/. Read 2026-09-08.
Three levels: unit tests on every commit, human and model review on a cadence, A/B tests for mature products. Binary pass/fail over scores. Our Layer 1 is his Level 1 and our Layer 2 is his Level 2.

**Hamel Husain, "AI Evals FAQ."** https://hamel.dev/blog/posts/evals-faq. Read 2026-09-08.
Do error analysis first; build an automated judge only for a failure mode that recurs enough to justify aligning one. For agents, score end to end first and note the first upstream failure. The weekly replay in Layer 2 follows this.

## Local

**`~/vault`**, Khaled's private brain. Not in this repo.
The first customer and the source of Layer 2 replay questions. Nothing from it is copied here. Two vault notes shaped the v1 spec: the decision record on v1 shape (coding agents only, three repos, vectors optional) and the learning note on Sentra's five requirements.
