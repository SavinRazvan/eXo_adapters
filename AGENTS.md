# AGENTS.md

## Project intent

**eXo_adapters** publishes provider-neutral runtime adapter packages for **eXo-brain** (`exo-brain-core-contracts`, `exo-brain-adapter-sdk`, `exo-adapter-*`). The control plane (policy, API, orchestration) lives in [SavinRazvan/eXo-brain](https://github.com/SavinRazvan/eXo-brain).

## First reads

1. [README.md](README.md) — packages, local install, quality gates  
2. [docs/packages-reference.md](docs/packages-reference.md) — **code inventory** (versions, exports, `adapter_class_ref`)  
3. [docs/adapter-authoring/new-provider-adapter.md](docs/adapter-authoring/new-provider-adapter.md) — add a new provider adapter  
4. [docs/conformance-testing.md](docs/conformance-testing.md) — tests and smoke  
5. [docs/github-repo-layout.md](docs/github-repo-layout.md) — what is committed vs local-only  
6. [RELEASE.md](RELEASE.md) — PyPI publish checklist (`requirements-release.txt`)

Maintainer IDE workflow (`.cursor/`, `.agents/`, `.local/`) is **gitignored** — keep locally or copy from eXo-brain when needed.

## Quality gates (run before merge)

Install deps first: `pip install -r requirements-ci.txt`

```bash
python scripts/check_no_control_plane_imports.py
python scripts/architecture/validate_adapter_packages.py
python scripts/architecture/scan_forbidden_imports.py
python -m pytest -q
python scripts/external_install_smoke.py
```

CI runs the same steps (see [.github/workflows/ci.yml](.github/workflows/ci.yml)).

## Adapter wall (non-negotiable)

- Provider SDKs only inside `packages/exo-adapter-*/`.
- No `from src.` / `import src.` in any package under `packages/`.
- Adapters implement `exo_brain_core_contracts.runtime_adapter.RuntimeAdapter` only.

## Commits

End message body with:

- `Author: Savin I. Razvan`
- `GitHub-User: @SavinRazvan`

## Branching

Use `feature/`, `fix/`, or `chore/` branches. PR workflow and release automation live in **eXo-brain**, not this repo.
