#!/bin/bash

# Build the DecentralOS packages into a pacman repository directory that can be
# served over HTTP(S) or bundled into the ISO. Run on Arch (or DecentralOS).
# Usage: decentralos/pkg/build-repo.sh [output-dir]

set -euo pipefail
cd "$(dirname "$0")"

out=$(realpath -m "${1:-repo}")
mkdir -p "$out"

for pkg in */PKGBUILD; do
  (cd "$(dirname "$pkg")" && PKGDEST="$out" makepkg --syncdeps --clean --force --noconfirm)
done

repo-add --remove "$out/decentralos.db.tar.zst" "$out"/*.pkg.tar.zst
echo "Repository ready in $out. Serve it and add to pacman.conf:"
echo "  [decentralos]"
echo "  Server = <url-of-$out>"
