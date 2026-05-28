# Release checklist (lockstep)

Use this checklist when publishing adapter ecosystem version **X.Y.Z** to PyPI.

## Preconditions

- [ ] All changes merged on `main`
- [ ] `packages/*/pyproject.toml` versions bumped to **X.Y.Z** (all four, lockstep)
- [ ] [CHANGELOG.md](CHANGELOG.md) updated
- [ ] [docs/versioning-and-releases.md](docs/versioning-and-releases.md) compatibility matrix updated

## Local build tooling

Install build + publish tools once:

```bash
pip install -r requirements-release.txt
```

Build all four wheels/sdists:

```bash
chmod +x scripts/build_all_packages.sh
./scripts/build_all_packages.sh
twine check packages/*/dist/*
```

Manual upload (TestPyPI or PyPI) after `twine check`:

```bash
# TestPyPI (recommended first)
twine upload --repository testpypi packages/*/dist/*

# Production PyPI
twine upload packages/*/dist/*
```

Prefer **Trusted Publishing** via tag push (below) for production; use twine for first-time TestPyPI checks.

## Adapter repo gates

```bash
pip install -r requirements-ci.txt
python scripts/check_no_control_plane_imports.py
python scripts/architecture/validate_adapter_packages.py
python scripts/architecture/scan_forbidden_imports.py
python -m pytest -q
python scripts/external_install_smoke.py
```

## Publish (GitHub Actions)

1. On GitHub: **Settings → Environments → New** → name `pypi` (restrict deploy access if desired).
2. On PyPI: add a **pending trusted publisher** (×4) per distribution:
   - `exo-brain-core-contracts`, `exo-brain-adapter-sdk`, `exo-adapter-echo`, `exo-adapter-openai`
   - Owner `SavinRazvan`, repository `eXo_adapters`, workflow **`release.yml`**, environment **`pypi`**
   - Repository name is **not** a URL; PyPI project name is the **distribution** name, not `eXo_adapters`.
3. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
4. Workflow [`.github/workflows/release.yml`](.github/workflows/release.yml) builds and uploads wheels (job uses GitHub environment `pypi`).

## Post-publish verification

```bash
EXO_ADAPTER_VERSION=X.Y.Z python scripts/pypi_install_smoke.py
```

Or enable repository variable `EXO_PYPI_SMOKE=1` for CI on `main`.

## eXo-brain follow-up (separate PR)

- [ ] Pin `exo-brain-core-contracts==X.Y.Z` and optional adapters in eXo-brain `requirements.txt` / `requirements-adapters.txt`
- [ ] Update [docs/strategy/adapter-compatibility-matrix.md](https://github.com/SavinRazvan/eXo-brain/blob/main/docs/strategy/adapter-compatibility-matrix.md)
- [ ] Run eXo-brain CI with adapter packages installed from PyPI
