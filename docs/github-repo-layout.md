<!--
File: github-repo-layout.md
Path: docs/github-repo-layout.md
Role: What belongs in the public GitHub repo vs local-only paths.
Used By:
 - Maintainers preparing first push or cleaning the working tree
Depends On:
 - .gitignore
 - README.md
-->

# GitHub repository layout

Lean public repo: **packages + tests + docs + four certification scripts + CI**.

## Commit to GitHub

| Path | Purpose |
|------|---------|
| `packages/` | Four PyPI distributions — `pyproject.toml` + `src/**/*.py` only |
| `tests/` | Conformance and portability tests |
| `scripts/` | Certification, build, and optional PyPI smoke (see below) |
| `docs/` | Adapter-author and maintainer documentation (start with `packages-reference.md`) |
| `.github/workflows/ci.yml` | CI |
| `README.md`, `AGENTS.md` | Entry points |
| `LICENSE`, `NOTICE`, `CHANGELOG.md` | Legal and release notes |
| `CONTRIBUTING.md`, `SECURITY.md` | Community and security |
| `requirements-ci.txt`, `requirements-dev.txt`, `requirements-release.txt`, `pytest.ini` | Install, test, and release tooling |
| `exo_adapters_pypi_handoff.md` | eXo-brain consumer handoff (PyPI wiring) |
| `RELEASE.md` | Maintainer release checklist |

### `scripts/` (entire tree)

```text
scripts/
  check_no_control_plane_imports.py
  external_install_smoke.py
  pypi_install_smoke.py          # optional; manual post-publish verification
  build_all_packages.sh
  architecture/
    validate_adapter_packages.py
    scan_forbidden_imports.py
```

## Do not commit (gitignored)

| Path | Why |
|------|-----|
| `.venv/`, `venv/` | Local virtualenv |
| `.cursor/`, `.agents/` | IDE/agent workflow (local maintainer tooling) |
| `.local/` | Planning trackers, workflow artifacts |
| `**/*.egg-info/`, `__pycache__/`, `.pytest_cache/` | Generated caches |
| `.coverage`, `.exo_data/`, `.exo_env*` | Local runtime / coverage |
| `*Zone.Identifier` | WSL/Windows stream copies |

## After clone

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-ci.txt
python scripts/check_no_control_plane_imports.py
python scripts/architecture/validate_adapter_packages.py
python scripts/architecture/scan_forbidden_imports.py
python -m pytest -q
python scripts/external_install_smoke.py
```

## Canonical publishing source

This repository (**`SavinRazvan/eXo_adapters`**) is the **only** canonical tree used
to build and publish PyPI wheels. A sibling clone at `packages/eXo_adapters/` inside
an eXo-brain working copy is **dev-only**; do not publish from there unless it is a
verified mirror of this repo.

## Operator docs

Control-plane deployment and `adapter_class_ref` registration live in **eXo-brain**, not this repo.
