#!/bin/bash

# Build the OS itself (this checkout, expected to be the rebranded main branch)
# into packages, using upstream's own package recipes. Publishing these in our
# repository is what keeps a system update from replacing DecentralOS with
# stock Omarchy. Usage: build-os-packages.sh <output-dir>

set -euo pipefail

out=$(realpath -m "$1")
src=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

git clone -q --depth 1 https://github.com/omacom/omarchy-pkgs "$work/pkgs"

# Same version as upstream's recipe, with a release number that only ever grows.
rel=$(date -u +%Y%m%d%H%M)
for pkg in omarchy-settings-dev omarchy-dev; do
  cd "$work/pkgs/pkgbuilds/$pkg"
  sed -i "s/^pkgrel=.*/pkgrel=$rel/" PKGBUILD
  OMARCHY_SRC="$src" PKGDEST="$out" makepkg --noconfirm --skippgpcheck --skipchecksums --nodeps -f
done
