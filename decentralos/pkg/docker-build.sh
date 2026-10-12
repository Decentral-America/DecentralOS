#!/bin/bash

# Build the DecentralOS package repository inside an Arch Linux container, for
# machines that aren't running Arch. Needs Docker. Output lands in ./repo.
# Usage: decentralos/pkg/docker-build.sh [git-branch]

set -euo pipefail
cd "$(dirname "$0")"

mkdir -p repo
MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd -W 2>/dev/null || pwd)/repo:/out" archlinux:latest bash -euc '
  pacman -Syu --noconfirm --needed base-devel git sudo
  useradd -m build
  echo "build ALL=(ALL) NOPASSWD: ALL" >/etc/sudoers.d/build
  sudo -u build git clone --depth 1 -b "'"${1:-decentralos-src}"'" https://github.com/Decentral-America/DecentralOS.git /home/build/os
  sudo -u build bash /home/build/os/decentralos/pkg/build-repo.sh /home/build/repo
  cp /home/build/repo/* /out/
'
