#!/usr/bin/env bash
# Print distribution names from built wheels (must match PyPI pending publisher / project names).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! compgen -G "packages/*/dist/*.whl" >/dev/null; then
  echo "No wheels found. Run: ./scripts/build_all_packages.sh"
  exit 1
fi

echo "Built distribution names (must match PyPI Trusted Publisher 'Project name' exactly):"
echo ""
for whl in packages/*/dist/*.whl; do
  name="$(unzip -p "$whl" '*.dist-info/METADATA' | awk -F': ' '/^Name: /{print $2; exit}')"
  pkg_dir="$(dirname "$(dirname "$whl")")"
  echo "  $name  <- $pkg_dir"
done
echo ""
echo "On PyPI you need FOUR pending publishers (or four projects), not one named eXo_adapters."
