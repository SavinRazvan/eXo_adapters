<!--
File: conformance-testing.md
Path: docs/conformance-testing.md
Role: How to run conformance, smoke, and forbidden-import checks in the adapter repo.
Depends On:
 - strategy-synthesis.md (§12 certification pipeline — full bar)
-->

# Conformance and testing

**Release bar (strategy):** structural checks below are **necessary** but not always **sufficient** — see [strategy-synthesis.md §12](strategy-synthesis.md#12-certification-pipeline-release-bar) and the pinned `eXo-brain` `adapter-strategy.md` (example):

- `https://github.com/SavinRazvan/eXo-brain/blob/v0.1.0/docs/strategy/adapter-strategy.md`

## Structural conformance (no network)

`exo_brain_adapter_sdk.assert_runtime_adapter_contract(adapter)` checks that an instance:

- Is a concrete `RuntimeAdapter` subclass
- Exposes the required **async** methods with callable shapes
- Implements `get_capabilities()` returning a `ProviderCapabilityMap`

Use this in unit tests for every adapter.

## Repository tests

From this repo root (with packages + dev deps installed):

```bash
pip install -r requirements-ci.txt
pytest -q
```

Tests under `tests/`:

- Import from **installed** distributions (`pip install -r requirements-ci.txt` installs editable packages).
- Scan adapter source files for forbidden `from src.` / `import src.`.
- Run minimal `run_turn` async smoke for OpenAI and Echo adapters (event type strings include `output_delta` and `run_complete`).

## External install smoke

**Certifies** that a **clean virtualenv** can `pip install -e` all four packages in order and run imports + conformance + a minimal OpenAI `run_turn` loop:

```bash
python scripts/external_install_smoke.py
```

Run this in CI on every PR that touches `packages/` or dependencies.

## PyPI install smoke (post-publish)

After wheels exist on PyPI (or TestPyPI):

```bash
EXO_ADAPTER_VERSION=0.1.1 python scripts/pypi_install_smoke.py
```

For TestPyPI:

```bash
EXO_PYPI_INDEX_URL=https://test.pypi.org/simple/ \
EXO_PYPI_EXTRA_INDEX_URL=https://pypi.org/simple/ \
EXO_ADAPTER_VERSION=0.1.1 \
python scripts/pypi_install_smoke.py
```

## Portability import guard

```bash
python scripts/check_no_control_plane_imports.py
```

Fails if any Python file under these roots references the monorepo control plane (`from src.` / `import src.`):

- `packages/exo-brain-core-contracts/src`
- `packages/exo-brain-adapter-sdk/src`
- `packages/exo-adapter-echo/src`
- `packages/exo-adapter-openai/src`

(When you add a new adapter, extend `SCAN_ROOTS` in the script.)

## Package layout validation

```bash
python scripts/architecture/validate_adapter_packages.py
```

Confirms expected package directories exist and contain `pyproject.toml` + `src/` layout.

## Forbidden provider SDK placement (adapter packages)

```bash
python scripts/architecture/scan_forbidden_imports.py
```

In this repo (no monorepo `src/`), enforces **no `src.*` imports** inside `packages/exo-adapter-*/src`. Provider SDK imports belong only inside those adapter trees.

## CI

See `.github/workflows/ci.yml` — `pip install -r requirements-ci.txt`, import guard, `validate_adapter_packages.py`, `scan_forbidden_imports.py`, `pytest -q`, external install smoke.

## Parity with eXo-brain CI

The monorepo job `package_workspace_tests` runs similar tests under `tests/packages/`. After extraction, eXo-brain should either:

- Depend on this repo’s releases and run a **small** integration test, or  
- Checkout this repo in CI for cross-repo verification.
