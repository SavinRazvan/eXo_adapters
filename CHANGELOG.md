# Changelog

All notable changes to the eXo adapter ecosystem packages are documented here.
The four distributions (`exo-brain-core-contracts`, `exo-brain-adapter-sdk`,
`exo-adapter-echo`, `exo-adapter-openai`) release on a **lockstep** version line.

## [0.1.1] - 2026-05-28

### Added

- Initial publishable split of the adapter ecosystem from eXo-brain.
- `exo-brain-core-contracts`: `RuntimeAdapter` ABC, events, tool I/O, capability map.
- `exo-brain-adapter-sdk`: `assert_runtime_adapter_contract` conformance helper.
- `exo-adapter-echo`: deterministic reference adapter (`EchoRuntimeAdapter`).
- `exo-adapter-openai`: OpenAI Agents–style adapter with lightweight echo path
  and optional full Agents SDK path when `OPENAI_API_KEY` and tool wiring are
  provided.
- CI gates: portability import guard, package layout validation, forbidden-import
  scan, conformance tests, `external_install_smoke.py`, advisory coverage.
- `scripts/pypi_install_smoke.py` for post-publish verification (optional CI via
  `EXO_PYPI_SMOKE=1`).
- Root docs: `RELEASE.md`, `CONTRIBUTING.md`, `SECURITY.md`, consumer handoff
  `exo_adapters_pypi_handoff.md`.

### Notes

- Compatible with eXo-brain control plane tag **v0.1.0** or newer (see
  [docs/versioning-and-releases.md](docs/versioning-and-releases.md)).
- Canonical `adapter_class_ref` values:
  - `exo_adapter_openai.runtime.OpenAIAgentsRuntimeAdapter`
  - `exo_adapter_echo.runtime.EchoRuntimeAdapter`
