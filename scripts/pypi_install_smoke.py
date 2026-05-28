"""
File: pypi_install_smoke.py
Path: scripts/pypi_install_smoke.py
Role: Verify adapter ecosystem installs from PyPI (or TestPyPI) in a clean venv.
Used By:
 - Manual post-publish release verification
Depends On:
 - PyPI distributions at EXO_ADAPTER_VERSION (default 0.1.1)
Notes:
 - Set EXO_PYPI_INDEX_URL for TestPyPI, e.g. https://test.pypi.org/simple/
 - Reuses assertion logic from external_install_smoke.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from external_install_smoke import ASSERTION_SCRIPT  # noqa: E402
DEFAULT_VERSION = "0.1.1"


def _distribution_pins(version: str) -> list[str]:
    return [
        f"exo-brain-core-contracts=={version}",
        f"exo-brain-adapter-sdk=={version}",
        f"exo-adapter-echo=={version}",
        f"exo-adapter-openai=={version}",
    ]


def _run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def main() -> int:
    version = os.environ.get("EXO_ADAPTER_VERSION", DEFAULT_VERSION).strip()
    index_url = os.environ.get("EXO_PYPI_INDEX_URL", "").strip()
    extra_index = os.environ.get("EXO_PYPI_EXTRA_INDEX_URL", "").strip()

    venv_dir = Path(tempfile.mkdtemp(prefix="exo_pypi_smoke_"))
    try:
        print(f"[pypi-smoke] version={version} venv={venv_dir}")
        _run([sys.executable, "-m", "venv", str(venv_dir)])

        pip = str(venv_dir / "bin" / "pip")
        python = str(venv_dir / "bin" / "python3")

        install_cmd = [pip, "install", "-q"]
        if index_url:
            install_cmd.extend(["--index-url", index_url])
        if extra_index:
            install_cmd.extend(["--extra-index-url", extra_index])
        install_cmd.extend(_distribution_pins(version))

        print(f"[pypi-smoke] pip install {' '.join(_distribution_pins(version))}")
        result = _run(install_cmd, check=False)
        if result.returncode != 0:
            print("[pypi-smoke] FAIL: pip install from index")
            print(result.stderr)
            return 1

        print("[pypi-smoke] Running assertion script ...")
        result = _run([python, "-c", ASSERTION_SCRIPT], check=False)
        print(result.stdout)
        if result.returncode != 0:
            print("[pypi-smoke] FAIL: assertion checks")
            if result.stderr:
                print(result.stderr)
            return 1

        print("[pypi-smoke] PASS")
        return 0
    finally:
        shutil.rmtree(venv_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
