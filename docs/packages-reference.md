<!--
File: packages-reference.md
Path: docs/packages-reference.md
Role: Code-accurate inventory of distributions in this repo (files, exports, registration refs, tests).
Used By:
 - docs/README.md
 - docs/adapter-authoring/new-provider-adapter.md
 - docs/implementing-a-runtime-adapter.md
Depends On:
 - packages/*/pyproject.toml
 - tests/test_*_adapter_conformance.py
Notes:
 - This is the source of truth for *what exists in this repository today*, not roadmap packages.
-->

# Packages reference (this repository)

**Current release line:** all four distributions are **`0.1.1`** (lockstep). See [versioning-and-releases.md](versioning-and-releases.md).

**Python:** `requires-python >= 3.11` (CI uses 3.12).

---

## Distribution summary

| PyPI name | Import package | Role |
|-----------|----------------|------|
| `exo-brain-core-contracts` | `exo_brain_core_contracts` | `RuntimeAdapter` ABC, events, tool I/O, capability types |
| `exo-brain-adapter-sdk` | `exo_brain_adapter_sdk` | Conformance helpers for adapter authors |
| `exo-adapter-echo` | `exo_adapter_echo` | Deterministic reference adapter (no network) |
| `exo-adapter-openai` | `exo_adapter_openai` | OpenAI Agents–style reference adapter |

Install order (local or smoke script): **contracts → SDK → echo → openai**.

---

## `exo-brain-core-contracts`

**Path:** `packages/exo-brain-core-contracts/`

| File | Role |
|------|------|
| `src/exo_brain_core_contracts/runtime_adapter.py` | `RuntimeAdapter` ABC, `SessionHandle` |
| `src/exo_brain_core_contracts/events.py` | `RuntimeEvent`, `RuntimeEventType` |
| `src/exo_brain_core_contracts/tool_io.py` | `ToolCallContext`, `ToolResult`, policy/risk types |
| `src/exo_brain_core_contracts/capability_map.py` | `ProviderCapabilityMap`, `HealthStatus`, `SecurityTier` |
| `src/exo_brain_core_contracts/__init__.py` | Stable public re-exports |

**Public exports (from `__init__.py`):** `RuntimeAdapter`, `SessionHandle`, `RuntimeEvent`, `RuntimeEventType`, `ToolCallContext`, `ToolResult`, `ProviderCapabilityMap`, `HealthStatus`, `HealthState`, `SecurityTier`, `RiskTier`, `blocked_result`, and related policy/tool types.

**Dependencies:** stdlib only (no provider SDKs).

**Tests:** `tests/test_core_contracts_imports.py`

---

## `exo-brain-adapter-sdk`

**Path:** `packages/exo-brain-adapter-sdk/`

| File | Role |
|------|------|
| `src/exo_brain_adapter_sdk/conformance/runtime_adapter_contract.py` | `assert_runtime_adapter_contract` |
| `src/exo_brain_adapter_sdk/execution_adapter.py` | `AdapterToolDescriptor`, `ToolExecutionAdapterContract` (SDK typing helpers; not control-plane tool backends) |
| `src/exo_brain_adapter_sdk/__init__.py` | Public exports |

**Public exports:** `assert_runtime_adapter_contract`, `AdapterToolDescriptor`, `ToolExecutionAdapterContract`

**Dependencies:** `exo-brain-core-contracts`

**Tests:** Used by adapter conformance tests (no dedicated test file).

---

## `exo-adapter-echo`

**Path:** `packages/exo-adapter-echo/`

| File | Role |
|------|------|
| `src/exo_adapter_echo/runtime.py` | `EchoRuntimeAdapter`, `load_adapter` |
| `src/exo_adapter_echo/__init__.py` | Re-exports class + factory |

**Canonical `adapter_class_ref` (eXo-brain):**

```text
exo_adapter_echo.runtime.EchoRuntimeAdapter
```

**Behavior:** Deterministic `run_turn` — emits `output_delta` then `run_complete`; no external API calls.

**Dependencies:** `exo-brain-core-contracts`

**Tests:** `tests/test_echo_adapter_conformance.py`

---

## `exo-adapter-openai`

**Path:** `packages/exo-adapter-openai/`

| File | Role |
|------|------|
| `src/exo_adapter_openai/runtime.py` | `OpenAIAgentsRuntimeAdapter`, `load_adapter` |
| `src/exo_adapter_openai/tool_wiring.py` | `build_agent_tools` (Agents SDK tool wiring when registry + executor provided) |
| `src/exo_adapter_openai/__init__.py` | Re-exports `OpenAIAgentsRuntimeAdapter`, `load_adapter`, `build_agent_tools` |

**Canonical `adapter_class_ref` (eXo-brain):**

```text
exo_adapter_openai.runtime.OpenAIAgentsRuntimeAdapter
```

**Behavior notes (no code changes required to document):**

- **Smoke / no API key:** `run_turn` can run in a lightweight echo-style path (still emits `output_delta` + `run_complete`).
- **Full Agents path:** when `OPENAI_API_KEY` is set and `tool_registry` + `tool_executor` are passed to the constructor, uses `openai-agents` streaming.
- **Planned tool call:** `context["planned_tool_call"]` yields a `tool_intent` event without calling the provider.
- **`submit_tool_results`:** when `OPENAI_API_KEY` and tool registry/executor are set, formats orchestrator `ToolResult` values and runs a **continuation** (`Runner.run`) so the user gets a final answer. Without a key, returns a text summary + `run_complete`. Agents stream tool calls use **delegating** `FunctionTool` bodies (no duplicate `TOOL_INTENT` when wired).

**Dependencies:** `exo-brain-core-contracts`, `openai`, `openai-agents`

**Tests:** `tests/test_openai_adapter_conformance.py`, `tests/test_openai_adapter_depth.py`

---

## `RuntimeAdapter` contract (v1)

Implementations must provide:

| Method | Notes |
|--------|--------|
| `async def start_session(...)` | Returns `SessionHandle` |
| `def run_turn(...) -> AsyncIterator[RuntimeEvent]` | Abstract signature; use `async def` + `yield` in subclasses |
| `def submit_tool_results(...) -> AsyncIterator[RuntimeEvent]` | Same pattern as `run_turn` |
| `def get_capabilities()` | Returns `ProviderCapabilityMap` |
| `async def healthcheck()` | Returns `HealthStatus` |

Minimum portable `run_turn` event types (conformance): **`output_delta`**, **`run_complete`** (or **`error`**).

---

## Quality gates (map to packages)

| Gate | What it validates |
|------|-------------------|
| `scripts/check_no_control_plane_imports.py` | No `src.*` imports in contracts, SDK, echo, openai sources |
| `scripts/architecture/validate_adapter_packages.py` | Expected four package dirs + layout |
| `scripts/architecture/scan_forbidden_imports.py` | No `src.*` inside `packages/exo-adapter-*/src` |
| `pytest -q` | Conformance + contracts import tests |
| `scripts/external_install_smoke.py` | Clean venv editable install of all four packages |

---

## Operator integration (eXo-brain)

Registration, deployment, and control-plane factory behavior are documented in **`SavinRazvan/eXo-brain`**, not this repo. Pin published wheels using [RELEASE.md](../RELEASE.md) and [versioning-and-releases.md](versioning-and-releases.md).
