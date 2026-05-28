#!/usr/bin/env bash
# Build wheels and sdists for all four lockstep distributions (install order).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACKAGES=(
  exo-brain-core-contracts
  exo-brain-adapter-sdk
  exo-adapter-echo
  exo-adapter-openai
)

for pkg in "${PACKAGES[@]}"; do
  echo "==> building packages/${pkg}"
  python -m build "packages/${pkg}"
done

echo "==> artifacts:"
find packages -path '*/dist/*' -type f | sort
