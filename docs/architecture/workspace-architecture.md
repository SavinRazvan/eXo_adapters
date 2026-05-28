<!--
File: workspace-architecture.md
Path: docs/architecture/workspace-architecture.md
Role: Durable description of this repository’s scope and boundaries (adapter ecosystem only).
Used By:
 - .local/index-and-planning/current/architecture.md
 - Maintainers and agents onboarding to eXo_adapters
Depends On:
 - README.md
 - docs/conformance-testing.md
Notes:
 - Control-plane application code lives in the eXo-brain monorepo, not here.
-->

# Workspace architecture (eXo_adapters)

## Scope

This repository holds **published-style Python packages** for the eXo-brain **provider runtime adapter** surface:

| Path | Role |
|------|------|
| `packages/exo-brain-core-contracts` | `RuntimeAdapter` ABC, events, tool I/O, capability types — **no** vendor SDKs |
| `packages/exo-brain-adapter-sdk` | Conformance helpers for adapter authors |
| `packages/exo-adapter-echo` | Deterministic reference adapter (no network) |
| `packages/exo-adapter-openai` | Reference OpenAI Agents–style adapter |

**Not in this repo:** orchestration, HTTP API, policies, deterministic tool executor, or monorepo `src/**`. Adapters must not import `src.*` (see `scripts/check_no_control_plane_imports.py`).

## Integration

The **eXo-brain control plane** installs these distributions (PyPI, private index, or `git+https`) into its runtime environment and loads concrete adapters via **dotted import path**.

Operator/control-plane integration docs live in `eXo-brain` and should be referenced by pinned tags.

Adapter authoring docs live in this repo under:

- `docs/adapter-authoring/`

## Quality gates (this tree)

- `pip install -r requirements-ci.txt` then `pytest -q`
- `python scripts/check_no_control_plane_imports.py`
- `python scripts/architecture/validate_adapter_packages.py`
- `python scripts/architecture/scan_forbidden_imports.py`
- `python scripts/external_install_smoke.py`
- CI: `.github/workflows/ci.yml` (same gates + pytest)

## Strategy source of truth

Long-form strategy and extraction checklists remain in the **eXo-brain** repository. This repo keeps only the minimum strategy context needed for adapter authors under `docs/strategy-synthesis.md`, plus implementation guides.
