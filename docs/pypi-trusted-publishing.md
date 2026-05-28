<!--
File: pypi-trusted-publishing.md
Path: docs/pypi-trusted-publishing.md
Role: Exact PyPI Trusted Publisher settings for all four adapter distributions.
Used By:
 - RELEASE.md
 - First-time publish checklist
-->

# PyPI Trusted Publishing (four packages)

Configure this **before** pushing tag `v0.1.1` (or your release version).

## GitHub

Workflow file must be **`release.yml`** (see `.github/workflows/release.yml`). No GitHub **Environment** is required.

## PyPI (four times)

Account → **Publishing** → **Add a new pending publisher** → **GitHub**

Repeat for **each row** (do not use repo name `eXo_adapters` as the PyPI project name):

| PyPI project name (required) | Owner | Repository name | Workflow name | Environment |
|------------------------------|--------|-----------------|---------------|-------------|
| `exo-brain-core-contracts` | `SavinRazvan` | `eXo_adapters` | `release.yml` | *(blank)* |
| `exo-brain-adapter-sdk` | `SavinRazvan` | `eXo_adapters` | `release.yml` | *(blank)* |
| `exo-adapter-echo` | `SavinRazvan` | `eXo_adapters` | `release.yml` | *(blank)* |
| `exo-adapter-openai` | `SavinRazvan` | `eXo_adapters` | `release.yml` | *(blank)* |

**Remove** any pending publisher whose project name is `eXo_adapters`, `hydra-logger`, or anything other than the four names above. If you previously set Environment to `pypi`, edit each publisher to leave Environment blank (or re-add publishers to match this table).

## Verify names match your wheels

After `./scripts/build_all_packages.sh`:

```bash
./scripts/verify_pypi_project_names.sh
```

Each line must have a **matching** pending publisher on PyPI with the same **PyPI project name**.

## Publish

```bash
git tag v0.1.1
git push origin v0.1.1
```

Or re-run failed jobs in **Actions → release** after fixing PyPI (no new tag needed).

Watch **Actions → release** (four green jobs). Then:

```bash
pip index versions exo-brain-core-contracts
```

## If it fails again

See [RELEASE.md](../RELEASE.md) § Troubleshooting (`400 Non-user identities cannot create new projects`).
