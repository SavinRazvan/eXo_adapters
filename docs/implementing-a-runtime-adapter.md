<!--
File: implementing-a-runtime-adapter.md
Path: docs/implementing-a-runtime-adapter.md
Role: Hands-on adapter implementation guide; pairs with strategy-synthesis.md.
Depends On:
 - strategy-synthesis.md
 - eXo-brain strategy docs (pinned link; see below)
-->

# Implementing a `RuntimeAdapter`

**Strategy context:** read [strategy-synthesis.md](strategy-synthesis.md) first (terminology, lanes, certification, core vs adapter).

**Canonical policy (in `eXo-brain`):** `docs/strategy/adapter-strategy.md` (use the tag for your control-plane release), e.g.:

- `https://github.com/SavinRazvan/eXo-brain/blob/v0.1.0/docs/strategy/adapter-strategy.md`

## Contract source of truth

Subclass **`exo_brain_core_contracts.runtime_adapter.RuntimeAdapter`** and implement every abstract method with matching signatures. The v1 surface is intentionally small:

| Method | Purpose |
|--------|---------|
| `start_session(session_id, metadata?)` | Create or attach provider-side session state; return `SessionHandle`. |
| `run_turn(session_id, user_input, context)` | Returns **`AsyncIterator[RuntimeEvent]`** (implement with `async def` + `yield`). |
| `submit_tool_results(session_id, run_id, tool_results)` | Same async-iterator pattern as `run_turn`. |
| `get_capabilities()` | Return **`ProviderCapabilityMap`** (provider id, feature tiers, health hints). |
| `healthcheck()` | Return **`HealthStatus`** for routing and ops. |

**Types** to use from `exo_brain_core_contracts`: `RuntimeEvent`, `RuntimeEventType`, `ToolResult`, `ToolCallContext`, `ProviderCapabilityMap`, `HealthStatus`, and related enums in `tool_io` / `events`.

Read the ABC in:

`packages/exo-brain-core-contracts/src/exo_brain_core_contracts/runtime_adapter.py`

## Canonical `adapter_class_ref` values (this repo)

eXo-brain loads adapters by dotted path. Stable refs for the reference packages:

| Package | `adapter_class_ref` |
|---------|---------------------|
| OpenAI | `exo_adapter_openai.runtime.OpenAIAgentsRuntimeAdapter` |
| Echo | `exo_adapter_echo.runtime.EchoRuntimeAdapter` |

New adapters should expose `exo_adapter_<provider>.runtime.<Provider>RuntimeAdapter` and export `load_adapter` from the package `__init__.py`. Full inventory: [packages-reference.md](packages-reference.md).

## Recommended package layout

**Minimum (matches reference code in this repo):** `runtime.py` + `__init__.py`; add `tool_wiring.py` when provider tool mapping is non-trivial (see OpenAI package).

Expanded module splits (`turns.py`, `capabilities.py`, etc.) are optional — see [strategy-synthesis.md §5](strategy-synthesis.md#5-standard-layout-per-adapter-package) for the long-term target shape.

## Packaging rules

1. **Distribution name:** prefer `exo-adapter-<provider>` (PyPI) per eXo-brain `docs/strategy/adapter-strategy.md`.
2. **Dependencies:** declare `exo-brain-core-contracts` with a **compatible version range**. Provider SDKs (`openai`, etc.) belong **only** in your adapter package, not in core-contracts.
3. **Forbidden:** `from src.` / `import src.` (eXo-brain control plane). Adapters must not import `exo_brain` app packages. Run `python scripts/check_no_control_plane_imports.py` before every PR.
4. **Module path for registration:** expose a stable dotted class path, e.g. `exo_adapter_foo.runtime.FooRuntimeAdapter`, for `adapter_class_ref` in the control plane.

## Factory helper (`load_adapter`)

Follow the pattern used by `exo-adapter-openai` and `exo-adapter-echo`:

- A module-level `load_adapter(provider_id: str, **kwargs) -> RuntimeAdapter` that constructs your adapter with the same **`RuntimeAdapter`** type the control plane expects.
- Export the concrete class and `load_adapter` from the package `__init__.py`.

## Capability map

`get_capabilities()` must return accurate **`ProviderCapabilityMap`** data so the orchestrator can choose **capability + policy** execution modes (not provider-name switches in core). Align tier flags with what your adapter actually supports; see `capability_map.py` in core-contracts.

## Event stream expectations

Reference adapters emit at least `output_delta` and `run_complete` over a minimal `run_turn` (see `conformance-testing.md`). Match event shapes expected by the control plane orchestrator for your interaction mode (chat vs agents) as that contract hardens.

## Conformance before publishing

```bash
pip install -r requirements-ci.txt
python scripts/check_no_control_plane_imports.py
python scripts/architecture/validate_adapter_packages.py
python scripts/architecture/scan_forbidden_imports.py
python -m pytest -q
python scripts/external_install_smoke.py
```

Quick contract check (after editable install of your package):

```bash
python -c "from exo_brain_adapter_sdk import assert_runtime_adapter_contract; from exo_adapter_echo import EchoRuntimeAdapter; assert_runtime_adapter_contract(EchoRuntimeAdapter(provider_id='t'))"
```

## Further reading

- [packages-reference.md](packages-reference.md) — code inventory for this repo
- [strategy-synthesis.md](strategy-synthesis.md) — strategy excerpt (not inventory)
- [conformance-testing.md](conformance-testing.md)
- [versioning-and-releases.md](versioning-and-releases.md)
