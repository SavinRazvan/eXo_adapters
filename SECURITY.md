# Security Policy

## Supported Versions

eXo_adapters is a single-maintainer open-source adapter ecosystem. There are no
commercial support tiers or SLA. Security fixes target the current `main` branch
first.

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

Do **not** open a public issue for suspected vulnerabilities.

Report privately via GitHub's private vulnerability reporting (if enabled) or
through the maintainer contact on `@SavinRazvan`.

Include:

- Description and impact
- Reproduction steps or minimal proof of concept
- Affected package(s) and version(s)

## Response Expectations

Best-effort targets:

- Acknowledgement: within 7 days
- Triage: within 14 days when enough information is available

No bug bounty program is offered.

## Scope

This repository ships **runtime adapter packages** only (`exo-brain-core-contracts`,
`exo-brain-adapter-sdk`, `exo-adapter-*`). The governed control plane (policy,
ingress, audit, tenancy) lives in
[eXo-brain](https://github.com/SavinRazvan/eXo-brain). Report control-plane issues
there when they are not limited to adapter package code.

Adapter isolation and portability guarantees: [docs/SECURITY_AND_ISOLATION.md](docs/SECURITY_AND_ISOLATION.md).
