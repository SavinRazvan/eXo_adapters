#!/usr/bin/env bash
# Upload all four lockstep distributions to PyPI in dependency order (requires twine + API token).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -z "${TWINE_USERNAME:-}" || -z "${TWINE_PASSWORD:-}" ]]; then
  echo "Set PyPI credentials first:" >&2
  echo "  export TWINE_USERNAME=__token__" >&2
  echo "  export TWINE_PASSWORD='pypi-...'   # full token from pypi.org/manage/account/token/" >&2
  exit 1
fi

if [[ "${#TWINE_PASSWORD}" -lt 50 ]]; then
  echo "TWINE_PASSWORD looks too short (len=${#TWINE_PASSWORD}). Use the full pypi- token." >&2
  exit 1
fi

PACKAGES=(
  exo-brain-core-contracts
  exo-brain-adapter-sdk
  exo-adapter-echo
  exo-adapter-openai
)

for pkg in "${PACKAGES[@]}"; do
  if ! compgen -G "packages/${pkg}/dist/*" >/dev/null; then
    echo "Missing dist for packages/${pkg}. Run: ./scripts/build_all_packages.sh" >&2
    exit 1
  fi
done

./scripts/verify_pypi_project_names.sh
twine check packages/*/dist/*

for pkg in "${PACKAGES[@]}"; do
  echo "==> uploading packages/${pkg}"
  twine upload "packages/${pkg}/dist/"*
  sleep 2
done

echo "==> verify on PyPI:"
pip index versions exo-brain-core-contracts
