<!--
File: strategy-synthesis.md
Path: docs/strategy-synthesis.md
Role: Condensed strategy from eXo-brain `docs/strategy/*` for adapter authors; not a fork — canonical text stays in the monorepo.
Used By:
 - docs/README.md
 - Adapter implementers before publishing
Depends On:
 - eXo-brain canonical strategy docs (linked below; pin to tag)
Notes:
 - Replace `v0.1.0` with the eXo-brain release tag you are pinning.
 - This file is a strategy *excerpt* only — not an inventory of this repo. For code truth, see packages-reference.md.
-->

# Strategy synthesis (adapters + boundaries)

> **Not a repo inventory.** This page summarizes eXo-brain strategy for adapter authors (terminology, boundaries, certification bar, roadmap lanes). For **what exists in this repository today** (files, versions, `adapter_class_ref`, tests), use **[packages-reference.md](packages-reference.md)**.

**Canonical** policy and tables remain in the **`eXo-brain`** repository (pinned links below).

| Document | Monorepo path (from repo root) |
|----------|--------------------------------|
| Adapter strategy (full) | `docs/strategy/adapter-strategy.md` |
| Versions, semver, M0/M1, certification rows | `docs/strategy/adapter-compatibility-matrix.md` |
| Product vocabulary + repository boundary | `docs/strategy/governed-execution-positioning.md` |
| Control plane API vs customer bridge vs adapters | `docs/strategy/interface-strategy.md` |
| Control plane product alignment (phases L1–L4) | `docs/plans/control-plane-product-alignment-plan.md` |
| Extraction checklist | `docs/plans/adapter-packages-extraction-handoff.md` |

## Canonical sources (pinned links)

Use the `eXo-brain` tag that matches your control plane release (example uses `v0.1.0`, the latest tag on [SavinRazvan/eXo-brain](https://github.com/SavinRazvan/eXo-brain)):

- `https://github.com/SavinRazvan/eXo-brain/blob/v0.1.0/docs/strategy/adapter-strategy.md`
- `https://github.com/SavinRazvan/eXo-brain/blob/v0.1.0/docs/strategy/adapter-compatibility-matrix.md`
- `https://github.com/SavinRazvan/eXo-brain/blob/v0.1.0/docs/strategy/governed-execution-positioning.md`
- `https://github.com/SavinRazvan/eXo-brain/blob/v0.1.0/docs/strategy/interface-strategy.md`
- `https://github.com/SavinRazvan/eXo-brain/blob/v0.1.0/docs/plans/control-plane-product-alignment-plan.md`
- `https://github.com/SavinRazvan/eXo-brain/blob/v0.1.0/docs/plans/adapter-packages-extraction-handoff.md`

---

## PyPI distribution — how customers attach to core

**Target delivery:** each package under `packages/` is a **separate PyPI-named distribution** (public or private index). **Operators** install compatible pins **into the same environment as the eXo-brain API process**, then **register** providers via the control plane API using **`adapter_class_ref`** (dotted import path). Core loads the class at runtime with `importlib`; no second copy of orchestration runs in the customer app.

**This is not** the **customer bridge:** apps that *call* eXo-brain use **HTTP/SSE/WS** (and optional `/v1`); they do not need `exo-adapter-*` in the app’s venv unless the app process **is** the control plane host. Operator flow lives in `eXo-brain` docs.

---

## 1. Non‑negotiable rule

- **Adapters:** provider transport, streaming translation, capability/health, provider SDK usage.
- **Core (control plane):** deterministic safety, policy gates, tenancy, audit, orchestration.

Adapters **must not** create side-effect paths that skip policy pre/post checks, deterministic tool execution when required, or audit instrumentation.

---

## 2. Terminology: two different “adapters”

| Term | Meaning | Typical artifact |
|------|---------|------------------|
| **Provider runtime adapter** | **Outbound** from eXo-brain’s runtime to a **model/provider** | `exo-adapter-openai`, future `exo-adapter-*` |
| **Customer bridge** | How **customer apps** call **into** the control plane (governance in the loop) | REST/SSE/WS, optional `POST /v1/chat/completions`, **planned** thin SDK |

**Do not confuse them.** RFPs and marketing break when “adapter” mixes inbound product integration with outbound provider drivers.

Details: see the pinned `eXo-brain` links in the “Canonical sources” section above.

### 2a) `ToolExecutionAdapter` vs `RuntimeAdapter` (control plane only)

The control plane also defines **`ToolExecutionAdapter`** (in `eXo-brain`) — a **provider-neutral** contract for **deterministic tool execution backends** (sandbox, process runner, etc.) used by the deterministic tool executor.

| Contract | Lives in | Purpose |
|----------|----------|---------|
| **`RuntimeAdapter`** | `exo-brain-core-contracts` + `exo-adapter-*` | **LLM / agent runtime** — talk to OpenAI, Anthropic, … |
| **`ToolExecutionAdapter`** | **Control plane only** (`src/tools/*`) | **Tool backends** — run registered tools under policy |

**Adapter-repo authors:** you implement **`RuntimeAdapter`** for providers. You do **not** ship `ToolExecutionAdapter` implementations in `exo-adapter-*` unless you have a **very unusual** integration explicitly designed with the core team (default: **no**).

This keeps **“plugin in/out”** clear: **provider adapters** plug in via **pip + `adapter_class_ref`**; **tool execution** plugins are a **different** extension point inside the monorepo.

---

## 3. Repository boundary

- **eXo-brain:** control plane only (`src/api`, `src/core`, `src/policies`, `src/tools`, `src/runtime` factory, etc.).
- **This repo (`eXo_adapters`):** **`exo-brain-core-contracts`**, **`exo-brain-adapter-sdk`**, **`exo-adapter-*`** — **no** imports from `src.*` / eXo-brain app packages.

Strategic narrative and repository boundary are defined in the pinned `eXo-brain` strategy docs (see “Canonical sources” above).

---

## 4. Core vs adapter responsibilities

| Core owns | Adapter owns |
|-----------|--------------|
| Policy decisions, risk gates, deterministic mode | Provider SDK integration |
| Tenancy, quota, fairness, admission | Request/response / stream mapping to contract envelopes |
| Audit chain and verification | `ProviderCapabilityMap`, health probing |
| Fallback **policy** (orchestration) | Retries/timeouts **within** contract constraints |

If ownership is unclear, default to **core** (see the pinned strategy doc).

---

## 5. Standard layout per adapter package

**In this repo today:** reference packages use a **minimal** layout (see [packages-reference.md](packages-reference.md)):

- **Echo:** `runtime.py` + `__init__.py` (`load_adapter` in `runtime.py`).
- **OpenAI:** `runtime.py`, `tool_wiring.py`, `__init__.py`.

**Target / expanded layout** (from eXo-brain strategy; adopt as providers grow):

```text
src/exo_adapter_<provider>/
  __init__.py
  runtime.py
  tool_wiring.py      # optional; provider tool-call mapping
  # optional splits: capabilities.py, sessions.py, turns.py, errors.py, settings.py
```

`load_adapter()` may live in `runtime.py` (as in reference adapters) or a dedicated module. Optional `agents.py`, `workflows.py`, `completions.py` must **not** bypass the runtime contract or governance path.

---

## 6. Runtime contract surface (v1)

Must implement on `RuntimeAdapter`:

- `start_session`
- `run_turn` (async iterator of `RuntimeEvent`)
- `submit_tool_results`
- `get_capabilities`
- `healthcheck`

All outputs normalize to **`RuntimeEvent`**, **`ToolResult`**, and shared error envelopes (see the pinned `eXo-brain` strategy docs).

**Execution mode** in core is **capability + policy**, not provider-name switches — declare capabilities honestly ([`implementing-a-runtime-adapter.md`](implementing-a-runtime-adapter.md)).

---

## 7. Three-lane expansion model (portfolio)

Provider work is grouped into **lanes** (see the pinned `eXo-brain` strategy docs):

| Lane | Purpose | Examples |
|------|---------|----------|
| **A** — Universal OpenAI‑compatible | Fast onboarding for compatible HTTP APIs | Mistral, DeepSeek, Qwen, etc. (see matrix in strategy) |
| **B** — Native provider adapter | Full-fidelity provider-specific integrations | Hugging Face (hybrid A→B), Aleph Alpha, … |
| **C** — Service via **tools** | Non-LLM / specialized APIs as governed tools | DeepL and similar |

Lane **A** universal **package** (`exo-adapter-universal` or equivalent) is a **separate milestone (M1)** from registration `api_type` work (**M0** — largely **done** in control plane). See the pinned compatibility matrix.

---

## 8. Baseline provider set (naming)

Strategic **baseline five** package names (see the pinned `eXo-brain` strategy docs):

- `exo-adapter-openai`
- `exo-adapter-google-gemini`
- `exo-adapter-anthropic`
- `exo-adapter-xai`
- `exo-adapter-meta-llama`

**Expansion v2** and P0/P1 ordering live in the pinned strategy doc.

---

## 9. Customer configuration (API-first)

Customers configure providers, fallbacks, policy overlays, and quotas **through control plane APIs**, not by patching your adapter code. Adapter-specific options belong in **schema-bound** provider metadata.

---

## 10. Fallback invariants

Fallback is **policy- and capability-aware** (see pinned strategy docs):

1. Apply policy (deny / escalate / deterministic enforce).
2. Check adapter health + capability map.
3. Primary → ordered fallback list.
4. Preserve **correlation** and **audit** across transitions.
5. **No safety downgrade** on failover (deterministic requirements survive).

---

## 11. Security and governance (hard rules)

1. No provider SDK imports in core layers (eXo-brain enforces layer scans).
2. No direct risky tool side effects from the adapter path.
3. No secrets in logs; structured redaction.
4. Side-effect paths emit policy + audit evidence (core orchestrates; adapter cooperates with envelopes).
5. Every adapter version passes conformance + safety gates before release (see pinned strategy docs).

---

## 12. Certification pipeline (release bar)

Before publishing a **new** adapter version, satisfy at minimum (see pinned `adapter-strategy.md` + compatibility matrix):

1. `RuntimeAdapter` contract conformance (async, methods).
2. Capability map validity.
3. Event shape / streaming translation tests.
4. Deterministic path **non-bypass** (where applicable).
5. Policy hook cooperation (as exercised from control plane tests).
6. Provider error → standard envelope normalization.
7. Retry / timeout / cancellation behavior.
8. Secret handling and safe logging.
9. Performance smoke (latency / timeout ratios).
10. Declared compatibility vs **`exo-brain-core-contracts`** / **adapter-sdk** ranges (see pinned compatibility matrix).

**Block release** on any P0 safety or contract failure.

Practical commands in this repo: [conformance-testing.md](conformance-testing.md).

---

## 13. Implementation sequencing (strategy slices)

High-level order for baseline five (see pinned strategy docs):

| Slice | Focus |
|-------|--------|
| **A** | Contract freeze, packaging baseline, template layout |
| **B** | OpenAI reference adapter extraction + clean external install |
| **C** | Google Gemini + Anthropic |
| **D** | xAI + Meta |
| **E** | Certification automation + matrix releases |

---

## 14. Pre-merge alignment (adapter changes)

Before merging adapter PRs, answer **yes** to (see pinned strategy docs):

- Preserves provider-neutral **core** boundaries (no `src.*` in packages).
- Policy / deterministic / audit remain non-bypassable.
- Customer-controllable via API/settings schemas where relevant.
- Portability improved or unchanged.
- Strengthens monetizable **governance** story (connectors enable adoption; premium is governance).
- Monorepo **`traceability-matrix.md`** updated when strategy claims change (maintainer task).

---

## 15. Versioning quick reference

| Artifact | Semver meaning (summary) |
|----------|---------------------------|
| `exo-brain-core-contracts` | Major = breaking `RuntimeAdapter` / envelope shapes |
| `exo-brain-adapter-sdk` | Tracks compatible contracts range |
| `exo-adapter-*` | Major = new min contracts/SDK or behavior visible through core |

Full table: see the pinned compatibility matrix.

---

## 16. Migration / portability (current bar)

From the pinned `adapter-strategy.md`:

- Remove monorepo-only `src.*` imports from packages.
- Depend only on published contracts + SDK + provider SDKs **inside** the adapter.
- `pip install exo-adapter-<provider>` works outside eXo-brain; conformance passes without path hacks.

---

*This file is a **synthesis**. On conflict, the dated monorepo strategy documents win.*
