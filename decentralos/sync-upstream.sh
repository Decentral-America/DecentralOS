#!/bin/bash

# Pull the latest upstream Omarchy into decentralos-src, then regenerate the
# rebranded decentralos branch. Usage: decentralos/sync-upstream.sh [upstream-branch]

set -euo pipefail
cd "$(dirname "$0")/.."

git fetch upstream
git checkout -q decentralos-src
git merge --no-edit "upstream/${1:-quattro}"
decentralos/release.sh
