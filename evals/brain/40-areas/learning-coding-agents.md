---
id: learning-coding-agents
type: area
as_of: 2026-08-05
status: current
confidence: high
---

# Learning coding agents

Alex is learning Claude Code for research scripts and Codex
for local edits, after [[rosalind-tembe]] walked through a
first session.

What works is a short prompt that names the file and the
change, then reading the diff before keeping anything, then
repeating that loop on one file at a time rather than asking
for a whole folder rewrite in one shot.

Do not let a model invent numbers for a table. Check each
figure against the source file.
