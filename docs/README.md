<!--
File: README.md
Path: docs/README.md
Role: Index for adapter-repo documentation (adapter authors + maintainers).
Depends On:
 - adapter-authoring/new-provider-adapter.md
 - implementing-a-runtime-adapter.md
 - conformance-testing.md
 - versioning-and-releases.md
-->

# Adapter ecosystem documentation

Start here after reading the root [README.md](../README.md).

## Code inventory (what exists today)

0. **[packages-reference.md](packages-reference.md)** — Per-package files, exports, canonical `adapter_class_ref`, tests, gate mapping.

## Adapter authoring (provider runtime adapters)

1. **[adapter-authoring/new-provider-adapter.md](adapter-authoring/new-provider-adapter.md)** — Step-by-step: add `packages/exo-adapter-<provider>` and ship it safely.
2. **[implementing-a-runtime-adapter.md](implementing-a-runtime-adapter.md)** — Contract surface, packaging rules, `load_adapter` pattern, capability map.
3. **[conformance-testing.md](conformance-testing.md)** — Full CI gate list, smoke script, architecture scans.

4. **[strategy-synthesis.md](strategy-synthesis.md)** — Strategy excerpt from eXo-brain (**not** a repo inventory).

## Maintainer operations

5. **[versioning-and-releases.md](versioning-and-releases.md)** — Lockstep `0.1.1` today; semver and release order.
6. **[SECURITY_AND_ISOLATION.md](SECURITY_AND_ISOLATION.md)** — Security posture for adapter packages (secrets, logging, isolation).
7. **[github-repo-layout.md](github-repo-layout.md)** — Commit vs ignore; folder map for GitHub/PyPI.
8. **[pypi-trusted-publishing.md](pypi-trusted-publishing.md)** — PyPI Trusted Publisher form values (×4 packages).

## Control-plane and operator documentation

This repository does **not** duplicate operator docs (deploying `eXo-brain`, installing wheels into the control plane environment, registering providers via API, etc.). Those docs live in **[SavinRazvan/eXo-brain](https://github.com/SavinRazvan/eXo-brain)** and should be referenced by **pinned release tags** to avoid drift (example tag in this repo: `v0.1.0`).

Consumer handoff (eXo-brain maintainers): [`exo_adapters_pypi_handoff.md`](../exo_adapters_pypi_handoff.md) at repo root.
