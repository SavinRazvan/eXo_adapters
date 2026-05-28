<!--
File: checklist.md
Path: docs/adapter-authoring/checklist.md
Role: Release/PR checklist for adapter authors and maintainers.
Used By:
 - Maintainers reviewing adapter PRs
 - Adapter authors before release
Depends On:
 - ../conformance-testing.md
 - ../SECURITY_AND_ISOLATION.md
 - ../versioning-and-releases.md
Notes:
 - Keep this checklist short, auditable, and aligned with actual repository gates.
-->

# Adapter author checklist (PR + release)

## Package structure and boundaries

- [ ] New adapter lives under `packages/exo-adapter-<provider>/`.
- [ ] Python package name is `exo_adapter_<provider>` under `src/`.
- [ ] No control-plane imports: no `from src.` / `import src.` anywhere under `packages/**/src`.
- [ ] Provider SDK dependencies are declared **only** in the adapter package (never in contracts/SDK).

## Contract conformance

- [ ] Adapter implements all `RuntimeAdapter` abstract methods with correct async signatures.
- [ ] `get_capabilities()` returns accurate `ProviderCapabilityMap` values.
- [ ] `run_turn(...)` emits a stable event stream and terminates in `run_complete` or `error`.

## Security and operational safety

- [ ] No secrets in source, tests, or logs.
- [ ] Errors are normalized and do not leak credentials or raw provider responses unnecessarily.
- [ ] Any logging is tenant-safe and redacted (see `docs/SECURITY_AND_ISOLATION.md`).

## Tests and gates (must pass — matches CI)

- [ ] `pip install -r requirements-ci.txt`
- [ ] `python scripts/check_no_control_plane_imports.py`
- [ ] `python scripts/architecture/validate_adapter_packages.py`
- [ ] `python scripts/architecture/scan_forbidden_imports.py`
- [ ] `python -m pytest -q`
- [ ] `python scripts/external_install_smoke.py` (smoke script lists updated if new package added)
- [ ] `pip check`

## Versioning and release hygiene

- [ ] Version bump is intentional and consistent with `docs/versioning-and-releases.md`.
- [ ] Dependency ranges on `exo-brain-core-contracts` are accurate for the intended compatibility window.
- [ ] Release notes (or changelog entry) clearly state breaking changes and migration steps.

