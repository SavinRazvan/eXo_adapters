# Contributing

Thank you for your interest in eXo_adapters.

## Scope

Contributions should stay within the **adapter ecosystem boundary**:

- `exo-brain-core-contracts`, `exo-brain-adapter-sdk`, `exo-adapter-*`
- Tests, docs, and CI for those packages

Do **not** add control-plane code (API, policy, orchestration, tenancy) to this
repository.

## Before opening a PR

```bash
pip install -r requirements-ci.txt
python scripts/check_no_control_plane_imports.py
python scripts/architecture/validate_adapter_packages.py
python scripts/architecture/scan_forbidden_imports.py
python -m pytest -q
python scripts/external_install_smoke.py
```

## Adapter wall

- No `from src.` / `import src.` in any package under `packages/`.
- Provider SDK imports only inside `packages/exo-adapter-*/`.

## Commits

End the commit message body with:

```text
Author: Savin I. Razvan
GitHub-User: @SavinRazvan
```

## Releases

Maintainers use lockstep tags (e.g. `v0.1.1`) and [`.github/workflows/release.yml`](.github/workflows/release.yml).
Follow [RELEASE.md](RELEASE.md) (`pip install -r requirements-release.txt`, build, `twine check`).
Version policy: [docs/versioning-and-releases.md](docs/versioning-and-releases.md).
