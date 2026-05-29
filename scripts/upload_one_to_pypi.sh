#!/usr/bin/env bash
# Upload a single lockstep distribution to PyPI (rate-limit friendly).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PKG="${1:-}"
if [[ -z "$PKG" ]]; then
  echo "Usage: $0 <package-dir-name>" >&2
  echo "  e.g. $0 exo-brain-core-contracts" >&2
  echo "Order: exo-brain-core-contracts → exo-brain-adapter-sdk → exo-adapter-echo → exo-adapter-openai" >&2
  exit 1
fi

if [[ -z "${TWINE_USERNAME:-}" || -z "${TWINE_PASSWORD:-}" ]]; then
  echo "Set PyPI credentials first:" >&2
  echo "  export TWINE_USERNAME=__token__" >&2
  echo "  export TWINE_PASSWORD='pypi-...'" >&2
  exit 1
fi

if [[ "${#TWINE_PASSWORD}" -lt 50 ]]; then
  echo "TWINE_PASSWORD looks too short (len=${#TWINE_PASSWORD}). Use the full pypi- token." >&2
  exit 1
fi

if ! compgen -G "packages/${PKG}/dist/*" >/dev/null; then
  echo "Missing dist for packages/${PKG}. Run: ./scripts/build_all_packages.sh" >&2
  exit 1
fi

./scripts/verify_pypi_project_names.sh "$PKG"
twine check "packages/${PKG}/dist/"*

echo "==> uploading packages/${PKG}"
twine upload --verbose "packages/${PKG}/dist/"*

echo "==> verify:"
pip index versions "${PKG//_/-}" 2>/dev/null || pip index versions "$PKG"
