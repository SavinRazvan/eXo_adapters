<!--
File: exo_adapters_pypi_handoff.md
Path: exo_adapters_pypi_handoff.md
Role: Consumer handoff for wiring `eXo-brain` to install runtime adapters from PyPI (no local adapter workspace).
Used By:
 - Maintainer updating `SavinRazvan/eXo-brain` to consume published adapter packages
Depends On:
 - eXo-brain: `requirements.txt` (or equivalent dependency surface)
 - eXo-brain: `src/runtime/adapter_factory.py`
 - eXo-brain: `scripts/architecture/scan_forbidden_imports.py`
 - eXo-brain: CI workflow triggers (typically `.github/workflows/architecture-fitness.yml`)
Notes:
 - This file intentionally omits the publishing workflow; publishing belongs in the adapters repo (`eXo_adapters`), not the control plane.
-->

# Handoff: wire **eXo-brain** to consume **eXo_adapters** from PyPI

## Mission (what you are responsible for)

Update **[eXo-brain](https://github.com/SavinRazvan/eXo-brain)** (`SavinRazvan/eXo-brain`) so that:

- It installs adapter ecosystem packages from **PyPI** (no local `packages/eXo_adapters/...` workspace assumptions).
- Provider SDK imports remain **behind adapter boundaries** (adapter wall).
- CI gates still validate “no provider SDK imports” in the control plane.

## Adapter ecosystem distributions (PyPI)

The adapter ecosystem publishes these **four** packages (distribution names must remain exactly these):

- `exo-brain-core-contracts`
- `exo-brain-adapter-sdk`
- `exo-adapter-echo`
- `exo-adapter-openai`

## Acceptance criteria (definition of done)

### A. Dependency surface

- `eXo-brain` installs from PyPI: no `-e ./packages/eXo_adapters/...` lines required for normal usage.
- Adapter packages are optional (recommended) so the control plane can install without provider dependencies by default.

### B. Adapter loading

- `src/runtime/adapter_factory.py` successfully resolves adapter class refs that point to published modules:
  - `exo_adapter_openai.runtime.OpenAIAgentsRuntimeAdapter`
  - `exo_adapter_echo.runtime.EchoRuntimeAdapter`

### C. CI coverage for dependency-only PRs

- Changes to the dependency surface (typically `requirements.txt`) trigger the CI suite that includes architecture checks (at minimum `scan_forbidden_imports.py`, ideally pytest as well).

## Guardrails (do not violate)

- **No provider SDK imports outside adapters**: the control plane must not import `openai`, etc. This is enforced by `scripts/architecture/scan_forbidden_imports.py` in eXo-brain.
## Implementation steps (in `eXo-brain`)

### 1) Replace local adapter-workspace requirements with PyPI deps

In eXo-brain, update `requirements.txt`:

- Replace local editable lines (example):
  - `-e ./packages/eXo_adapters/packages/exo-brain-core-contracts`
- With PyPI pins/ranges:
  - `exo-brain-core-contracts==X.Y.Z` (or `>=X.Y.Z`)

Then decide how to surface adapters:

- **Recommended**: make adapters optional extras (so the control plane installs without provider deps):
  - base requirements: control plane + contracts
  - optional: `exo-adapter-openai`, `exo-adapter-echo`

If eXo-brain today expects OpenAI adapter by default, you can either:
- keep a “default adapter” extra, or
- keep in-tree fallback adapter until PyPI path is proven stable, then remove the fallback.

### 2) Ensure CI runs for dependency-only changes

Today, `architecture-fitness.yml` runs on `src/**`, `tests/**`, `packages/**`, etc.

To avoid dependency PRs slipping through with only CodeQL checks, update eXo-brain CI so that:
- `requirements.txt` changes trigger the full suite (or at least pytest + architecture scans).

Concretely:
- add `requirements.txt` to `.github/workflows/architecture-fitness.yml` `paths:` trigger.

### 3) Decide what to do with `tests/packages/*` conformance tests

Those tests currently skip unless a local adapter workspace exists.

After moving adapters out, eXo-brain has three sensible choices:

- **Choice A (recommended):** convert `tests/packages/*` into “installed package” tests
  - install `exo-adapter-echo` and `exo-adapter-openai` in CI (via extras)
  - run conformance tests against installed packages
- **Choice B:** keep them as optional local-only tests (documented)
  - fine if you don’t want provider deps in CI
- **Choice C:** move them entirely to eXo_adapters and delete from eXo-brain
  - then keep only a minimal integration smoke in eXo-brain

Pick one and update docs accordingly.

## How eXo-brain loads adapters (what must remain true)

The control plane loads adapters by dotted class reference. The published adapters must expose stable import paths, e.g.:

- `exo_adapter_openai.runtime.OpenAIAgentsRuntimeAdapter`
- `exo_adapter_echo.runtime.EchoRuntimeAdapter`

The load path is resolved in:
- `src/runtime/adapter_factory.py`

The adapter wall rule is enforced by:
- `scripts/architecture/scan_forbidden_imports.py`

## Checklist (copy/paste for the implementing agent in `eXo-brain`)

Complete these in **[SavinRazvan/eXo-brain](https://github.com/SavinRazvan/eXo-brain)** — not in this adapters repo:

- [ ] Replace any local adapter-workspace `-e ./packages/eXo_adapters/...` requirements with PyPI dependencies.
- [ ] Decide whether adapters are default deps or optional extras (e.g. separate `requirements-adapters.txt`).
- [ ] Update CI triggers so dependency-surface changes run architecture scans and pytest.
- [ ] Decide fate of `tests/packages/*` (installed-package tests vs optional local-only vs move to adapters repo).

## Notes on why `packages/eXo_adapters/**` is ignored in eXo-brain

In eXo-brain, `packages/eXo_adapters/` may exist as a local sibling clone for development, but it must not be accidentally committed/published as part of the control-plane repo. Only the small `exo-brain-core-contracts` subset was temporarily vendored for CI. Once PyPI publishing is in place, eXo-brain should stop vendoring this subtree entirely.

