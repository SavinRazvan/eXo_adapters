"""
File: validate_adapter_packages.py
Path: scripts/architecture/validate_adapter_packages.py
Role: Adapter-ecosystem layout and monorepo-import guard (no control-plane src.* in packages).
Used By:
 - .github/workflows/ci.yml
Depends On:
 - pathlib
Notes:
 - Use this gate when the repo root has no monorepo ``src/`` tree (adapter-only repository).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_PACKAGES = (
    "exo-brain-core-contracts",
    "exo-brain-adapter-sdk",
    "exo-adapter-echo",
    "exo-adapter-openai",
)


def _scan_roots() -> list[Path]:
    roots: list[Path] = []
    for name in EXPECTED_PACKAGES:
        roots.append(REPO_ROOT / "packages" / name / "src")
    return roots


def main() -> int:
    failures: list[str] = []

    packages_dir = REPO_ROOT / "packages"
    if not packages_dir.is_dir():
        print("Adapter package validation failed: missing packages/ directory.", file=sys.stderr)
        return 1

    for name in EXPECTED_PACKAGES:
        pkg_dir = packages_dir / name
        pyproject = pkg_dir / "pyproject.toml"
        if not pyproject.is_file():
            failures.append(f"Missing pyproject.toml: {pyproject.relative_to(REPO_ROOT)}")
            continue
        src_dir = pkg_dir / "src"
        if not src_dir.is_dir():
            failures.append(f"Missing src/ for package {name}")
            continue
        py_files = list(src_dir.rglob("*.py"))
        if not py_files:
            failures.append(f"No Python sources under {src_dir.relative_to(REPO_ROOT)}")

    for root in _scan_roots():
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("from src.") or stripped.startswith("import src."):
                    rel = path.relative_to(REPO_ROOT)
                    failures.append(f"{rel}:{lineno}: {stripped}")

    if failures:
        print("Adapter package validation failed:", file=sys.stderr)
        for item in failures:
            print(f"  {item}", file=sys.stderr)
        return 1

    print("Adapter package validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
