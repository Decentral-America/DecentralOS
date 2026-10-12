#!/bin/bash

# Build the DecentralOS pacman repository: the packages in this folder plus the
# DecentralOS builds of the OS packages. Run on Arch (CI does this on every
# push to main). Usage: decentralos/pkg/build-repo.sh [output-dir]

set -euo pipefail
cd "$(dirname "$0")"

out=$(realpath -m "${1:-repo}")
base=https://github.com/Decentral-America/DecentralOS/releases/download/packages
mkdir -p "$out"

for pkg in */PKGBUILD; do
  dir=$(dirname "$pkg")
  file=$(cd "$dir" && basename "$(makepkg --packagelist)")
  # A version that is already published is reused, so only a bumped pkgver or
  # pkgrel triggers the slow node build.
  if curl -fsSL -o "$out/$file" "$base/$file"; then
    echo "Reusing published $file"
  else
    rm -f "$out/$file"
    (cd "$dir" && PKGDEST="$out" makepkg --syncdeps --clean --force --noconfirm)
  fi
done

# Devices must always find our OS packages ahead of upstream's, so when a build
# fails keep serving the last published ones rather than dropping them.
if ! ./build-os-packages.sh "$out"; then
  echo "::warning::OS package build failed; keeping the previously published OS packages"
  rm -f "$out"/omarchy-*.pkg.tar.zst
  gh release download packages -R Decentral-America/DecentralOS -p 'omarchy-*.pkg.tar.zst' -D "$out" || true
fi

repo-add --remove "$out/decentralos.db.tar.zst" "$out"/*.pkg.tar.zst
echo "Repository ready in $out"
