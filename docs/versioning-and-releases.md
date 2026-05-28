<!--
File: versioning-and-releases.md
Path: docs/versioning-and-releases.md
Role: Semver and release order for contracts, SDK, and adapters.
Depends On:
 - strategy-synthesis.md §15
 - eXo-brain `adapter-compatibility-matrix.md` (pinned link)
-->

# Versioning and releases

**Summary table:** [strategy-synthesis.md §15](strategy-synthesis.md#15-versioning-quick-reference).

**Canonical (in `eXo-brain`, pin to your control-plane release tag):**

- `https://github.com/SavinRazvan/eXo-brain/blob/v0.1.0/docs/strategy/adapter-compatibility-matrix.md`

## Current state in this repository (lockstep)

All four distributions in `packages/*/pyproject.toml` are **`0.1.1`** today:

- `exo-brain-core-contracts==0.1.1`
- `exo-brain-adapter-sdk==0.1.1`
- `exo-adapter-echo==0.1.1`
- `exo-adapter-openai==0.1.1`

Adapter packages declare `exo-brain-core-contracts>=0.1.1,<0.2`. Treat this line as
**one compatible set** until independent versioning is adopted.

**Inventory:** [packages-reference.md](packages-reference.md).

## Compatibility matrix (tested combination)

| Adapter ecosystem (lockstep) | Minimum eXo-brain tag | Notes |
|------------------------------|----------------------|--------|
| **0.1.1** (all four wheels) | **v0.1.0** | First PyPI line; pin both sides in production |
| Future 0.1.x | TBD | Bump this table when either repo releases |

eXo-brain should pin exact versions in `requirements.txt` / optional
`requirements-adapters.txt`, for example:

```text
exo-brain-core-contracts==0.1.1
exo-brain-adapter-sdk==0.1.1
exo-adapter-echo==0.1.1
exo-adapter-openai==0.1.1
```

## Distributions

Publishable wheels from this repo:

- `exo-brain-core-contracts`
- `exo-brain-adapter-sdk`
- `exo-adapter-openai`, `exo-adapter-echo`, and future `exo-adapter-*`

## Semver expectations (target policy)

- **Major** bump on `exo-brain-core-contracts` when `RuntimeAdapter` or public type shapes break compatibility for existing adapters or the control plane.
- **Future:** adapters should declare a compatible range on core-contracts, e.g. `exo-brain-core-contracts>=0.1,<0.2` (not enforced in `pyproject.toml` at `0.1.1`).
- **SDK** releases track core-contracts for API used in conformance helpers.

When moving off lockstep, bump **contracts → SDK → each adapter** in that order and refresh eXo-brain pins together.

Canonical policy narrative: eXo-brain `docs/strategy/adapter-compatibility-matrix.md` (link from this repo’s README when publishing).

## Release order

When core-contracts breaks in a major way:

1. Ship new **core-contracts** major.
2. Update **adapter-sdk** to match and release.
3. Update and release each **adapter** with new declared ranges.

## Pinning from eXo-brain

The control plane should pin:

```text
exo-brain-core-contracts==x.y.z
exo-adapter-openai==a.b.c
```

(or `pip install git+https://...@tag` until PyPI is live).

Keep **Dockerfile** and `requirements.txt` in eXo-brain aligned with tested combinations; record the matrix in `adapter-compatibility-matrix.md`.

## Changelog

Maintain per-package `CHANGELOG.md` or GitHub Releases notes when you publish — especially for **breaking** contract changes.
