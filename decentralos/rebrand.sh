#!/bin/bash

# Apply the user-visible DecentralOS rebrand to an Omarchy tree. Idempotent.
# Internals (omarchy-* commands, paths, env vars) are deliberately left alone
# so upstream merges stay clean; only the display name and artwork change.

set -euo pipefail
cd "$(dirname "$0")/.."

git grep -lIz -e 'Omarchy' -e 'OMARCHY INSTALL LOG' -e 'Linux by DHH' -- . ':!decentralos' ':!.github' |
  xargs -0 -r perl -pi -e '
    s/(?<![A-Za-z0-9])Omarchy(?![A-Za-z0-9])/DecentralOS/g;
    s/TARGET OMARCHY INSTALL LOG/TARGET DECENTRALOS INSTALL LOG/;
    s/(Beautiful, Fun & Agentic Linux) by DHH/$1/;
  '

# Artwork and hand-written files that replace upstream's wholesale.
cp -r decentralos/overlay/. .

# Ship the DecentralChain node: make our package repository known to pacman and
# add the node to the default package set.
for conf in $(git ls-files 'default/pacman/**pacman*.conf'); do
  grep -q '^\[decentralos\]' "$conf" || cat >>"$conf" <<'REPO'

[decentralos]
SigLevel = Optional TrustAll
Server = https://github.com/Decentral-America/DecentralOS/releases/download/packages
REPO
done
grep -qx 'decentralchain-node' install/omarchy-base.packages || echo 'decentralchain-node' >>install/omarchy-base.packages

# DecentralOS ships on appliances whose owner plugs in their own keyboard and
# mouse after install, so USB approval stays off unless they turn it on in
# Setup > Security. Left on, it locks them out of the very keyboard needed to
# approve it.
sed -i 's/^systemctl enable usbguard\.service$/systemctl disable usbguard.service/' install/config/usb-authorization.sh

# Make the DecentralOS theme the default and put the node widget on the bar.
sed -i 's/omarchy-theme-set "Tokyo Night"/omarchy-theme-set "DecentralOS"/' install/user/theme.sh
grep -q 'omarchy.decentralchain-node' config/omarchy/shell.json ||
  perl -0pi -e 's/("right": \[)(\r?\n)(\s*)\{/$1$2$3\{$2$3  "id": "omarchy.decentralchain-node"$2$3\},$2$3\{/' config/omarchy/shell.json
