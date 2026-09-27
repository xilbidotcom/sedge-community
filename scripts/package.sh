#!/usr/bin/env bash
# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
if [[ -n $(git status --porcelain) ]]; then
  printf 'Commit the intended Community source changes before packaging.\n' >&2
  exit 1
fi
VERSION=$(tr -d '\n' < VERSION)
COMMIT=$(git rev-parse --short HEAD)
NAME="sedge-community-${VERSION}-${COMMIT}"
mkdir -p dist
if [[ -e "dist/${NAME}.tar.gz" ]]; then
  printf 'Package already exists: dist/%s.tar.gz\n' "$NAME" >&2
  exit 1
fi
git archive --format=tar.gz --prefix="${NAME}/" -o "dist/${NAME}.tar.gz" HEAD
sha256sum "dist/${NAME}.tar.gz" > "dist/${NAME}.tar.gz.sha256"
printf 'Created dist/%s.tar.gz\n' "$NAME"
