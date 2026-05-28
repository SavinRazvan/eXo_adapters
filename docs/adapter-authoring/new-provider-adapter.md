<!--
File: new-provider-adapter.md
Path: docs/adapter-authoring/new-provider-adapter.md
Role: Enterprise-grade guide for creating a new `exo-adapter-<provider>` distribution.
Used By:
 - Adapter authors adding new providers
Depends On:
 - ../implementing-a-runtime-adapter.md
 - ../conformance-testing.md
 - ../../packages/exo-brain-core-contracts/src/exo_brain_core_contracts/runtime_adapter.py
 - ../../packages/exo-brain-adapter-sdk/src/exo_brain_adapter_sdk/conformance/runtime_adapter_contract.py
Notes:
 - This guide is intentionally control-plane agnostic: it explains how to ship an importable adapter package.
-->

# Add a new provider adapter (`exo-adapter-<provider>`)

This guide walks you through creating a **new** provider runtime adapter package under `packages/` and shipping it as a standalone distribution.

## Outcomes (definition of done)

- A new folder exists: `packages/exo-adapter-<provider>/` with `pyproject.toml` and `src/` layout.
- The adapter exposes a stable class ref: `exo_adapter_<provider>.runtime.<Provider>RuntimeAdapter`.
- The adapter exports `load_adapter(...)` from `exo_adapter_<provider>.__init__`.
- The package passes repo gates (same as CI — see [conformance-testing.md](../conformance-testing.md)):
  - `python scripts/check_no_control_plane_imports.py`
  - `python scripts/architecture/validate_adapter_packages.py`
  - `python scripts/architecture/scan_forbidden_imports.py`
  - `python -m pytest -q`
  - `python scripts/external_install_smoke.py` (after updating install order in that script)

## 1) Create the package skeleton

Create:

```text
packages/exo-adapter-<provider>/
  pyproject.toml
  src/exo_adapter_<provider>/
    __init__.py
    runtime.py
```

### Naming rules

- **Distribution name (PyPI)**: `exo-adapter-<provider>` (dash-separated).
- **Import package name (Python)**: `exo_adapter_<provider>` (underscore-separated).
- **Canonical class path**: `exo_adapter_<provider>.runtime.<Provider>RuntimeAdapter`

## 2) Write `pyproject.toml`

Copy the pattern used by existing adapters in:

- `packages/exo-adapter-openai/pyproject.toml`
- `packages/exo-adapter-echo/pyproject.toml`

Required points:

- `name = "exo-adapter-<provider>"`
- `requires-python = ">=3.11"`
- `dependencies` must include **only**:
  - `exo-brain-core-contracts` (compatible range recommended; see `docs/versioning-and-releases.md`)
  - provider SDK dependencies (only for this adapter)

Never add provider SDK deps to `exo-brain-core-contracts` or `exo-brain-adapter-sdk`.

## 3) Implement `RuntimeAdapter` in `runtime.py`

The source of truth for the contract is:

- `packages/exo-brain-core-contracts/src/exo_brain_core_contracts/runtime_adapter.py`

Your adapter must implement:

- `start_session(session_id, metadata=None) -> SessionHandle`
- `run_turn(session_id, user_input, context) -> AsyncIterator[RuntimeEvent]`
- `submit_tool_results(session_id, run_id, tool_results) -> AsyncIterator[RuntimeEvent]`
- `get_capabilities() -> ProviderCapabilityMap`
- `healthcheck() -> HealthStatus`

### Event stream expectations (portable minimum)

For a minimal `run_turn`, your adapter should emit:

- at least one `RuntimeEventType.OUTPUT_DELTA` (or equivalent output-bearing event), and
- a terminal `RuntimeEventType.RUN_COMPLETE`, or `RuntimeEventType.ERROR`.

Keep emitted payloads schema-bound and stable. Do not leak secrets into event payloads or logs.

## 4) Add `load_adapter(...)` factory + exports

In `runtime.py`, provide:

- `def load_adapter(provider_id: str = "<provider>", **kwargs) -> <Provider>RuntimeAdapter`

Then, in `__init__.py`, export:

- the concrete adapter class
- `load_adapter`

Follow the pattern used in:

- `packages/exo-adapter-openai/src/exo_adapter_openai/__init__.py`
- `packages/exo-adapter-echo/src/exo_adapter_echo/__init__.py`

## 5) Add conformance tests

Add a new test file under `tests/`:

- `tests/test_<provider>_adapter_conformance.py`

Minimum coverage:

- Instantiate the adapter and run `assert_runtime_adapter_contract(adapter)` from `exo-brain-adapter-sdk`.
- Run a minimal async `run_turn` and assert it yields expected event types (`output_delta`, `run_complete`).
- Ensure **no** `from src.` / `import src.` appear in your adapter source files.

Use existing tests as templates:

- `tests/test_openai_adapter_conformance.py`
- `tests/test_echo_adapter_conformance.py`

## 6) Run gates locally (full CI parity)

From repo root:

```bash
pip install -r requirements-ci.txt
python scripts/check_no_control_plane_imports.py
python scripts/architecture/validate_adapter_packages.py
python scripts/architecture/scan_forbidden_imports.py
python -m pytest -q
python scripts/external_install_smoke.py
```

If you add a new adapter package:

1. Add its directory to `EXPECTED_PACKAGES` in `scripts/architecture/validate_adapter_packages.py`.
2. Add its `src` root to `SCAN_ROOTS` in `scripts/check_no_control_plane_imports.py`.
3. Append its path to `PACKAGES_INSTALL_ORDER` in `scripts/external_install_smoke.py` (after contracts and SDK, before or after other adapters as dependencies require).

See [packages-reference.md](../packages-reference.md) for the current four-package inventory.

## 7) Release readiness (high-level)

- Align versions per `docs/versioning-and-releases.md`.
- Ensure the adapter’s declared dependency ranges are accurate.
- Cut a release only after all gates are green.

