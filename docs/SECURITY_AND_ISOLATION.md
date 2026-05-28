<!--
File: SECURITY_AND_ISOLATION.md
Path: docs/SECURITY_AND_ISOLATION.md
Role: Isolation guarantees and operational security notes for adapter packages.
Depends On:
 - strategy-synthesis.md §11 (governance rules summary)
-->

# Security and isolation (adapter ecosystem repo)

**Strategy alignment:** hard rules for adapters (secrets, logging, side effects) are summarized in [strategy-synthesis.md §11](strategy-synthesis.md#11-security-and-governance-hard-rules).

Canonical policy (in `eXo-brain`, pin to your control-plane release tag), e.g.:

- `https://github.com/SavinRazvan/eXo-brain/blob/v0.1.0/docs/strategy/adapter-strategy.md`

## Is this tree isolated from the eXo-brain control plane?

**At runtime and for published wheels: yes, by design.**

- Adapter packages declare dependencies only on **`exo-brain-core-contracts`**, **provider SDKs** (e.g. `openai`, `openai-agents`), and the **stdlib**. They do **not** declare a dependency on the monorepo or on a control-plane Python distribution.
- **`pip install exo-adapter-openai`** does not install orchestration, API routes, policies, or tenant logic from eXo-brain. Nothing in the adapter repo can “pull in” private core source unless someone **manually** adds a malicious dependency or vendored code.
- The control plane **loads** adapters by **import string** (`adapter_class_ref`) **after** it has installed those packages in **its** environment. Direction of trust: **core chooses which adapter code runs**, not the other way around.

## Does package code leak core implementation?

**Shipped Python under `packages/*/src`:** Reviewed for imports. It uses only:

- `exo_brain_core_contracts.*` (this repo),
- `exo_adapter_*` (same repo),
- third-party provider libraries,
- stdlib.

There must be **no** `from src.` / `import src.` (eXo-brain layout). CI runs `scripts/check_no_control_plane_imports.py` over **core-contracts, adapter-sdk, and all `exo-adapter-*` sources**.

**Secrets:** No credentials are embedded in source. The OpenAI adapter reads **`OPENAI_API_KEY`** from the environment at runtime (normal pattern). Operators supply keys in **their** deployment; publishing this repo does not publish keys.

## What can still “show something” about core?

1. **Documentation** in this repo may name control-plane concepts and (optionally) monorepo **file paths** (e.g. `src/runtime/adapter_factory.py`) so maintainers can navigate `eXo-brain`. That is **operational documentation**, not source code. If this GitHub repo is **public** and you want to minimize footprint disclosure, rephrase to “the control plane adapter loader” without exact paths.
2. **PyPI package metadata** (`description` in `pyproject.toml`) mentions “eXo-brain” as product context — branding, not internals.
3. **Contracts package** intentionally exposes **public** types (`RuntimeEvent`, `ToolResult`, …). That is the **published boundary**, not a leak of orchestration internals.

## Will this break core code?

**No automatic breakage** from publishing or cloning this repo in isolation. Risk appears only when:

- Core **pins incompatible** `exo-brain-core-contracts` / adapter versions (fix: matrix + tests), or
- Someone **removes** monorepo `packages/` before core’s `requirements.txt` / Docker install published wheels (fix: follow `adapter-packages-extraction-handoff.md`).

## Threat model notes (short)

| Concern | Mitigation |
|--------|------------|
| Adapter imports core source | Forbidden-import CI; no `src.*` in packages |
| Malicious adapter on install | Pin **exact versions** or hashes in core; vet publishers |
| Adapter exfiltrates tenant data | Core policy/audit and tool execution boundaries remain in **core**; adapters see what you pass in `context` / APIs — design data minimization in integration |
| Supply chain (typosquat) | Use official distribution names and internal mirror if needed |

## Completeness

Isolation is **strong for code in `packages/`** plus the **import guard**. It does **not** replace:

- Core-side **reviews** of `adapter_class_ref` allowlists,
- **Secret management** in production,
- **SBOM / vulnerability scanning** on dependencies.

Keep this file updated when you add new adapter packages (ensure they are on `SCAN_ROOTS` or under `packages/exo-adapter-*/src` glob policy).
