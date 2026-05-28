<!--
File: exo_adapters_pypi_handoff.md
Path: exo_adapters_pypi_handoff.md
Role: Consumer handoff for wiring `eXo-brain` to install runtime adapters from PyPI (no local adapter workspace).
Used By:
 - Maintainer updating `SavinRazvan/eXo-brain` to consume published adapter packages
Depends On:
 - eXo-brain: `requirements.txt`, `requirements-adapters.txt`
 - eXo-brain: `src/runtime/adapter_factory.py`
 - eXo-brain: `scripts/dev/install_adapter_dependencies.sh`
 - eXo-brain: `scripts/architecture/scan_forbidden_imports.py`
 - eXo-brain: CI workflow triggers (`.github/workflows/architecture-fitness.yml`)
Notes:
 - Publishing workflow lives in this repo (`RELEASE.md`, `.github/workflows/release.yml`).
 - Status reviewed: 2026-05-28 against local `eXo_adapters` + `eXo-brain` trees.
-->

# Handoff: wire **eXo-brain** to consume **eXo_adapters** from PyPI

## Status snapshot (2026-05-28)

| Track | Overall |
|-------|---------|
| **eXo_adapters** (publish) | **Ready to tag** — packages, CI, smoke green locally; **PyPI upload not done yet** |
| **eXo-brain** (consume) | **Wired for PyPI pins** — requirements + CI + factory E2E; **full PyPI-only CI blocked until wheels exist on PyPI** |

**Blocker for “100% done”:** publish all four distributions to PyPI (`v0.1.1`), then run `EXO_ADAPTER_VERSION=0.1.1 python scripts/pypi_install_smoke.py` and confirm eXo-brain CI installs without `packages/repo_for_pipy` fallback.

---

## Mission

**eXo-brain** ([SavinRazvan/eXo-brain](https://github.com/SavinRazvan/eXo-brain)) should:

- Install adapter ecosystem packages from **PyPI** (no `-e ./packages/eXo_adapters/...` in normal `requirements.txt`).
- Keep provider SDKs **behind adapter boundaries** (adapter wall).
- Keep architecture CI on dependency changes.

**eXo_adapters** ([SavinRazvan/eXo_adapters](https://github.com/SavinRazvan/eXo_adapters)) publishes:

- `exo-brain-core-contracts`
- `exo-brain-adapter-sdk`
- `exo-adapter-echo`
- `exo-adapter-openai`

(lockstep **0.1.1** today)

---

## Acceptance criteria

### A. Dependency surface

| Criterion | Status |
|-----------|--------|
| eXo-brain `requirements.txt` uses PyPI pin for contracts (no `-e ./packages/eXo_adapters/...`) | **Done** — `exo-brain-core-contracts==0.1.1` |
| Adapters optional (control plane can install without provider wheels) | **Done** — `requirements-adapters.txt` + `install_adapter_dependencies.sh` |
| Wheels actually on PyPI | **Not done** — `pip index` still reports no distribution (publish pending) |

### B. Adapter loading

| Criterion | Status |
|-----------|--------|
| `adapter_factory` resolves `exo_adapter_openai.runtime.OpenAIAgentsRuntimeAdapter` | **Done** (code + `tests/modules/runtime/test_packaged_adapter_e2e.py`) |
| `adapter_factory` resolves `exo_adapter_echo.runtime.EchoRuntimeAdapter` | **Done** (same) |

### C. CI coverage for dependency-only PRs

| Criterion | Status |
|-----------|--------|
| `requirements.txt` / `requirements-adapters.txt` in CI `paths:` | **Done** (`architecture-fitness.yml`) |
| Architecture scans + pytest on those PRs | **Done** |
| CI uses PyPI-only installs (no local mirror) | **Partial** — CI runs `install_adapter_dependencies.sh` (PyPI first, **`packages/repo_for_pipy` fallback** until PyPI exists) |

---

## Checklist — **eXo_adapters** (this repository)

Publisher / certification work:

- [x] Four packages under `packages/` with lockstep `0.1.1` in `pyproject.toml`
- [x] Stable `adapter_class_ref` import paths documented
- [x] No `src.*` in adapter packages; CI import guard + `scan_forbidden_imports.py`
- [x] Conformance tests + `external_install_smoke.py` (local gates green: 16 pytest, smoke PASS)
- [x] `.github/workflows/ci.yml`
- [x] `.github/workflows/release.yml` (tag `v*` → build/upload)
- [x] `RELEASE.md`, `requirements-release.txt`, `scripts/build_all_packages.sh`
- [x] Root legal/docs: `LICENSE`, `NOTICE`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`
- [ ] **Public GitHub repo** pushed (`SavinRazvan/eXo_adapters`)
- [ ] **PyPI Trusted Publishing** configured per distribution (four projects; workflow `release.yml`, environment `pypi`)
- [ ] **Publish** `v0.1.1` to PyPI (tag push or `twine upload`)
- [ ] **Post-publish:** `python scripts/pypi_install_smoke.py` (or CI `EXO_PYPI_SMOKE=1`)

---

## Checklist — **eXo-brain** (control plane)

Consumer wiring (implement in eXo-brain, not here):

- [x] Replace `-e ./packages/eXo_adapters/...` in `requirements.txt` with PyPI pin (`exo-brain-core-contracts==0.1.1`)
- [x] Optional adapters in `requirements-adapters.txt` (SDK + echo + openai)
- [x] `scripts/dev/install_adapter_dependencies.sh` (PyPI first, local `packages/repo_for_pipy` fallback)
- [x] CI `paths:` include `requirements.txt`, `requirements-adapters.txt`, `requirements-adapters-local.txt`
- [x] CI installs adapters before `tests/packages` / runtime jobs (`install_adapter_dependencies.sh`)
- [x] Factory E2E for installed wheels: `tests/modules/runtime/test_packaged_adapter_e2e.py`
- [~] **`tests/packages/*`:** **Choice A + legacy fallback** — runs in CI when packages are installed; still supports local `repo_for_pipy` / sibling clone via `tests/adapter_package_paths.py`. Primary conformance suite lives in **eXo_adapters** (`tests/test_*_adapter_*.py`).
- [ ] **PyPI-only CI** (no `repo_for_pipy` fallback) — after PyPI publish, verify CI without mirror
- [ ] Pin / matrix updated in eXo-brain `docs/strategy/adapter-compatibility-matrix.md` for **0.1.1**
- [ ] Remove or shrink `packages/repo_for_pipy/` mirror once PyPI path is proven (optional cleanup)

---

## Implementation reference (eXo-brain)

### 1) Requirements (done in tree)

- `requirements.txt` — `exo-brain-core-contracts==0.1.1` (no provider SDKs in base file)
- `requirements-adapters.txt` — optional adapter line
- `requirements-adapters-local.txt` — editable fallback for pre-publish dev only

### 2) CI triggers (done)

`architecture-fitness.yml` includes `requirements.txt`, `requirements-adapters.txt`, and related paths.

### 3) `tests/packages/*` (hybrid)

- **eXo_adapters:** full conformance + smoke (canonical for adapter authors).
- **eXo-brain:** `package_workspace_tests` job + `test_packaged_adapter_e2e` for control-plane integration.

### How eXo-brain loads adapters

- Dotted refs: `exo_adapter_openai.runtime.OpenAIAgentsRuntimeAdapter`, `exo_adapter_echo.runtime.EchoRuntimeAdapter`
- Loader: `src/runtime/adapter_factory.py`
- Adapter wall: `scripts/architecture/scan_forbidden_imports.py` (eXo-brain)

---

## Notes on `packages/eXo_adapters/**` and `packages/repo_for_pipy/**` in eXo-brain

- `packages/eXo_adapters/` — sibling clone for dev; gitignored.
- `packages/repo_for_pipy/` — **temporary mirror** of this repo for CI/dev until PyPI wheels exist; do not treat as the publishing source of truth.
- **Canonical publish source:** [SavinRazvan/eXo_adapters](https://github.com/SavinRazvan/eXo_adapters).

---

## After PyPI publish (both repos)

1. GitHub **Settings → Environments → `pypi`**; PyPI pending publishers: Owner `SavinRazvan`, repo `eXo_adapters`, workflow `release.yml`, environment `pypi` (×4 distribution names).
2. Tag **`v0.1.1`** in eXo_adapters → release workflow uploads four wheels.
3. Run `EXO_ADAPTER_VERSION=0.1.1 python scripts/pypi_install_smoke.py`.
4. Re-run eXo-brain CI; confirm `install_adapter_dependencies.sh` logs **“Installed … from PyPI”** with no fallback.
5. Check off remaining boxes above.
