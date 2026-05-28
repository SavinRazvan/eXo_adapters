# eXo adapter ecosystem

This repository contains **publishable Python packages** for the eXo-brain **provider runtime adapter** ecosystem:

- `exo-brain-core-contracts`
- `exo-brain-adapter-sdk`
- `exo-adapter-*` (provider-specific runtime adapters)

## Boundary (what this repo is / is not)

- **This repo** (`SavinRazvan/eXo_adapters`): the **only** publishable source for adapter
  wheels. Provider runtime adapters + portable contract types live here.
- **[eXo-brain](https://github.com/SavinRazvan/eXo-brain)** (`SavinRazvan/eXo-brain`): the governed control plane (policy, deterministic tools, tenancy, audit, orchestration) that **loads** adapters at runtime.
- A local `packages/eXo_adapters/` tree inside an eXo-brain checkout (if present) is
  **dev-only** and must not be treated as the publishing source of truth.

Operator documentation (deploying the control plane, installing wheels into the control plane environment, registering providers via APIs) lives in the control-plane repo. This repo focuses on **adapter authoring and maintenance**.

**Pinned strategy links** in this repo’s docs use the latest published eXo-brain tag (`v0.1.0` today). Adapter **package** versions in `packages/*/pyproject.toml` are independent (currently `0.1.1` lockstep).

## Packages (PyPI distribution names)

| Directory | Distribution | Role |
|-----------|--------------|------|
| `packages/exo-brain-core-contracts` | `exo-brain-core-contracts` | `RuntimeAdapter` ABC, events, tool I/O, capability map — **no provider SDKs** |
| `packages/exo-brain-adapter-sdk` | `exo-brain-adapter-sdk` | Conformance helpers for adapter authors |
| `packages/exo-adapter-openai` | `exo-adapter-openai` | Reference OpenAI Agents–style adapter |
| `packages/exo-adapter-echo` | `exo-adapter-echo` | Second adapter (no network) for tests and parity |

## Adapter authoring (start here)

- `docs/adapter-authoring/new-provider-adapter.md`
- `docs/implementing-a-runtime-adapter.md`
- `docs/conformance-testing.md`

## Local install order

Install **in this order** (dependencies between local paths):

1. `exo-brain-core-contracts`
2. `exo-brain-adapter-sdk`
3. `exo-adapter-echo`
4. `exo-adapter-openai`

```bash
cd /path/to/this-repo-root
pip install -e packages/exo-brain-core-contracts
pip install -e packages/exo-brain-adapter-sdk
pip install -e packages/exo-adapter-echo
pip install -e packages/exo-adapter-openai
```

**One-shot local / CI install (editable packages + pytest):**

```bash
pip install -r requirements-ci.txt
```

**Production-style install (after publish):**

```bash
pip install "exo-brain-core-contracts==…" "exo-adapter-openai==…"
```

Pin versions per [`docs/versioning-and-releases.md`](docs/versioning-and-releases.md). For the control-plane compatibility matrix and operator guidance, see `eXo-brain` docs.

## Quality gates in this repo

Install [`requirements-ci.txt`](requirements-ci.txt) before running tests (pulls in `openai-agents` and other adapter dependencies).

- **Unit / conformance tests:** `pytest -q` (from this root)
- **Package source coverage (100% gate):** same paths as CI — `packages/*/src` only:
  ```bash
  python -m pytest -q \
    --cov=packages/exo-brain-core-contracts/src \
    --cov=packages/exo-brain-adapter-sdk/src \
    --cov=packages/exo-adapter-echo/src \
    --cov=packages/exo-adapter-openai/src \
    --cov-report=term-missing \
    --cov-fail-under=100
  ```
- **Standalone install certification:** `python scripts/external_install_smoke.py` (isolated venv, editable installs all four packages)
- **Portability guard:** `python scripts/check_no_control_plane_imports.py` (adapter sources must not import `src.*`)
- **Package layout + adapter wall:** `python scripts/architecture/validate_adapter_packages.py` and `python scripts/architecture/scan_forbidden_imports.py`

Same gates run in [.github/workflows/ci.yml](.github/workflows/ci.yml) (including the coverage gate above and advisory `pip-audit`).

**Maintainer release:** [RELEASE.md](RELEASE.md) — `requirements-release.txt`, `scripts/build_all_packages.sh`, `./scripts/verify_pypi_project_names.sh` (wheel names vs PyPI Trusted Publishers), [docs/pypi-trusted-publishing.md](docs/pypi-trusted-publishing.md), tag → [`.github/workflows/release.yml`](.github/workflows/release.yml) (GitHub environment `pypi`).

**Local OpenAI adapter (optional):** set `OPENAI_API_KEY` in a gitignored `.env` and `source .env` before manual runs; CI and unit tests mock the SDK and do not need a real key. See [docs/SECURITY_AND_ISOLATION.md](docs/SECURITY_AND_ISOLATION.md).

## Repository files

| File | Purpose |
|------|---------|
| [LICENSE](LICENSE) / [NOTICE](NOTICE) | Apache-2.0 |
| [CHANGELOG.md](CHANGELOG.md) | Lockstep package release notes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contributor gates and scope |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting |
| [RELEASE.md](RELEASE.md) | Publish checklist (PyPI / tags) |
| [docs/pypi-trusted-publishing.md](docs/pypi-trusted-publishing.md) | PyPI Trusted Publisher names (four distributions) |
| [exo_adapters_pypi_handoff.md](exo_adapters_pypi_handoff.md) | **eXo-brain** consumer wiring (PyPI pins) |
| [AGENTS.md](AGENTS.md) | Agent/orchestrator entry (optional; IDE rules are gitignored) |

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/github-repo-layout.md](docs/github-repo-layout.md) | **What to commit vs ignore** (GitHub/PyPI layout) |
| [docs/packages-reference.md](docs/packages-reference.md) | **Code inventory** — packages, exports, `adapter_class_ref`, tests |
| [docs/architecture/workspace-architecture.md](docs/architecture/workspace-architecture.md) | **This repo’s scope** (packages only; no control-plane `src/`) |
| [docs/README.md](docs/README.md) | Index (implementation + **strategy-synthesis**) |
| [docs/adapter-authoring/new-provider-adapter.md](docs/adapter-authoring/new-provider-adapter.md) | **How to add a new provider adapter** (`exo-adapter-<provider>`) |
| [docs/implementing-a-runtime-adapter.md](docs/implementing-a-runtime-adapter.md) | How to implement a new `RuntimeAdapter` |
| [docs/conformance-testing.md](docs/conformance-testing.md) | SDK checks, smoke script, CI |
| [docs/versioning-and-releases.md](docs/versioning-and-releases.md) | Semver and compatibility with the control plane |
| [docs/SECURITY_AND_ISOLATION.md](docs/SECURITY_AND_ISOLATION.md) | Isolation guarantees, what is / is not leaked, operational security notes |

## Relationship to eXo-brain

The **control plane** lives in the `eXo-brain` repository. It consumes **this** repo via **`pip`** from **PyPI**, a **private index**, or **`git+https://…@tag`** and loads adapters by **dotted class path**.

For operator-facing integration and deployment docs, use `eXo-brain` documentation (pinned to the same release/tag used by your control plane).
