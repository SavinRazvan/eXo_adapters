"""
File: check_no_control_plane_imports.py
Path: scripts/check_no_control_plane_imports.py
Role: Fail if adapter/SDK sources import monorepo control-plane paths (src.*).
Used By:
 - CI for adapter ecosystem repo
Depends On:
 - packages/exo-brain-core-contracts/src, packages/exo-brain-adapter-sdk/src, packages/exo-adapter-*/src
Notes:
 - Complements eXo-brain ``scan_forbidden_imports.py`` when packages live only here.
 - Core-contracts must stay provider-neutral and must never import the control plane.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SCAN_ROOTS = [
    REPO_ROOT / "packages" / "exo-brain-core-contracts" / "src",
    REPO_ROOT / "packages" / "exo-brain-adapter-sdk" / "src",
    REPO_ROOT / "packages" / "exo-adapter-openai" / "src",
    REPO_ROOT / "packages" / "exo-adapter-echo" / "src",
]


def main() -> int:
    failures: list[str] = []
    for root in SCAN_ROOTS:
        if not root.is_dir():
            failures.append(f"Missing scan root: {root}")
            continue
        for path in root.rglob("*.py"):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("from src.") or stripped.startswith("import src."):
                    failures.append(f"{path.relative_to(REPO_ROOT)}:{lineno}: {stripped}")
    if failures:
        print("Forbidden control-plane import(s) detected:\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("Adapter import guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
