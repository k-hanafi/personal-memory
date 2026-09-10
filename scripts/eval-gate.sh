#!/usr/bin/env bash
# Run the eval suite on this checkout and compare it to the baseline committed on origin/main.
# Exits 1 when a gold recall case regressed or the committed baseline does not match a fresh run.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"
git fetch origin main

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
if ! git show origin/main:evals/baselines/main.json > "$tmp" 2>/dev/null; then
  # origin/main has no baseline yet, so the gate must see none.
  rm -f "$tmp"
fi

personal-memory eval gate --main-baseline "$tmp"
