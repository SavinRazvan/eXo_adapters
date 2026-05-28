<!--
File: README.md
Path: docs/adapter-authoring/README.md
Role: Entry point for adapter authors; defines the required artifacts, constraints, and validation loop.
Used By:
 - Adapter authors implementing new `exo-adapter-*` packages
Depends On:
 - new-provider-adapter.md
 - checklist.md
 - ../implementing-a-runtime-adapter.md
 - ../conformance-testing.md
 - ../versioning-and-releases.md
Notes:
 - Operator/control-plane docs live in `eXo-brain`; this folder is strictly adapter-author focused.
-->

# Adapter authoring

This folder describes how to implement and maintain **provider runtime adapters** (`exo-adapter-*`) for eXo-brain.

## Start here

1. **[new-provider-adapter.md](new-provider-adapter.md)** — end-to-end steps to add a new adapter package.
2. **[checklist.md](checklist.md)** — PR/release checklist (tests, smoke, portability, versioning).

## Related docs

- [../packages-reference.md](../packages-reference.md) — **code inventory** for this repo (versions, refs, tests).
- [../implementing-a-runtime-adapter.md](../implementing-a-runtime-adapter.md) — contract surface and recommended patterns.
- [../conformance-testing.md](../conformance-testing.md) — test and smoke commands used as gates.
- [../versioning-and-releases.md](../versioning-and-releases.md) — semver and release order.

