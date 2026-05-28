#!/usr/bin/env bash
# Remove local wheel/sdist and setuptools artifacts under packages/ (safe pre-release clean).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

for pkg in packages/exo-brain-core-contracts packages/exo-brain-adapter-sdk packages/exo-adapter-echo packages/exo-adapter-openai; do
  rm -rf "${pkg}/dist" "${pkg}/build"
  find "${pkg}/src" -type d -name '*.egg-info' -prune -exec rm -rf {} + 2>/dev/null || true
done

echo "Cleaned package build artifacts under packages/*/dist, build, *.egg-info"
