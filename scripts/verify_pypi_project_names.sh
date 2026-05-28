#!/usr/bin/env bash
# Print distribution names from built wheels (must match PyPI pending publisher / project names).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACKAGE_FILTER="${1:-}"

if [[ -n "$PACKAGE_FILTER" ]]; then
  WHEEL_GLOB="packages/${PACKAGE_FILTER}/dist/*.whl"
else
  WHEEL_GLOB="packages/*/dist/*.whl"
fi

if ! compgen -G "$WHEEL_GLOB" >/dev/null; then
  if [[ -n "$PACKAGE_FILTER" ]]; then
    echo "No wheels found for packages/${PACKAGE_FILTER}. Run: python -m build packages/${PACKAGE_FILTER}"
  else
    echo "No wheels found. Run: ./scripts/build_all_packages.sh"
  fi
  exit 1
fi

extract_distribution_name() {
  local whl="$1"
  local metadata_path name

  metadata_path="$(unzip -Z1 "$whl" 2>/dev/null | grep -E '\.dist-info/METADATA$' | head -1 || true)"
  if [[ -z "$metadata_path" ]]; then
    echo "ERROR: no METADATA entry in wheel: $whl" >&2
    return 1
  fi

  name="$(unzip -p "$whl" "$metadata_path" | awk -F': ' '/^Name: /{print $2; exit}')"
  name="${name//$'\r'/}"
  name="${name#"${name%%[![:space:]]*}"}"
  name="${name%"${name##*[![:space:]]}"}"

  if [[ -z "$name" ]]; then
    echo "ERROR: missing or empty 'Name:' in $whl ($metadata_path)" >&2
    return 1
  fi

  printf '%s' "$name"
  return 0
}

echo "Built distribution names (must match PyPI Trusted Publisher 'Project name' exactly):"
echo ""
errors=0
for whl in $WHEEL_GLOB; do
  pkg_dir="$(dirname "$(dirname "$whl")")"
  if ! name="$(extract_distribution_name "$whl")"; then
    echo "  <missing Name:>  <- $pkg_dir (wheel: $whl)" >&2
    errors=$((errors + 1))
    continue
  fi
  echo "  $name  <- $pkg_dir"
done
echo ""
echo "On PyPI you need FOUR pending publishers (or four projects), not one named eXo_adapters."

if (( errors > 0 )); then
  echo "" >&2
  echo "FAILED: $errors wheel(s) missing a valid distribution Name: field." >&2
  exit 1
fi
