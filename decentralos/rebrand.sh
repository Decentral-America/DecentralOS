#!/bin/bash

# Apply the user-visible DecentralOS rebrand to an Omarchy tree. Idempotent.
# Internals (omarchy-* commands, paths, env vars) are deliberately left alone
# so upstream merges stay clean; only the display name and artwork change.

set -euo pipefail
cd "$(dirname "$0")/.."

git ls-files -z -- . ':!decentralos' ':!.github' |
  xargs -0 grep -lIZ -e 'Omarchy' -e 'OMARCHY INSTALL LOG' -e 'Linux by DHH' |
  xargs -0 -r perl -pi -e '
    s/(?<![A-Za-z0-9])Omarchy(?![A-Za-z0-9])/DecentralOS/g;
    s/TARGET OMARCHY INSTALL LOG/TARGET DECENTRALOS INSTALL LOG/;
    s/(Beautiful, Fun & Agentic Linux) by DHH/$1/;
  '

# Artwork and hand-written files that replace upstream's wholesale.
cp -r decentralos/overlay/. .
