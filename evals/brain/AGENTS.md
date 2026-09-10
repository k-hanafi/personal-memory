# Demo brain protocol

This folder is a tiny fake brain. When you answer a question from it:

1. Search the notes. Do not answer from memory.
2. Every fact needs a file path and line range.
3. If two `current` notes disagree, report both. Do not pick a winner.
4. Prefer `status: current` unless the question is about the past.
5. If nothing matches, say the brain does not have this.
