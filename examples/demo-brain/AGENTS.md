# Demo brain protocol

This folder is a tiny fake brain. When you answer a question from it:

1. Search the notes. Do not answer from memory.
2. Every fact needs a file path and line range.
3. If two `current` notes disagree, report both. Do not pick a winner.
4. Prefer `status: current` unless the question is about the past.
5. If nothing matches, say the brain does not have this.

Lookups use `remember` (search) and `revisit` (open one note). Durable facts
said in chat go through `note`.

This folder has no `sources/` dumps. `inbox` lists leftovers under `sources/`,
so it is empty here. Skip filing from dumps until you add a file under
`sources/`.
