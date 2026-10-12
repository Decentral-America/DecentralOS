#!/bin/bash

# Regenerate the rebranded `main` branch from `decentralos-src`.
#
# decentralos-src = upstream Omarchy + our additions, un-rebranded (merges cleanly)
# main            = decentralos-src with rebrand.sh applied (what devices install)
#
# Each release is a merge commit whose tree is computed, never hand-resolved, so
# the branch always fast-forwards and upstream changes can't conflict with the rebrand.

set -euo pipefail
cd "$(dirname "$0")/.."

src=decentralos-src
out=main

if [[ -n $(git status --porcelain) ]]; then
  echo "Working tree is dirty; commit or stash first." >&2
  exit 1
fi

git checkout -q "$out" 2>/dev/null || git checkout -q -b "$out" "$src"
git merge -q -s ours --no-ff --no-commit "$src" 2>/dev/null || true
git read-tree -u --reset "$src"
decentralos/rebrand.sh
git add -A
git commit -q -m "DecentralOS release from $src@$(git rev-parse --short "$src")" || echo "Nothing new to release."
git checkout -q "$src"
echo "Branch $out is at $(git rev-parse --short "$out")"
