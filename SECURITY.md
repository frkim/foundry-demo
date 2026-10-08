# Security policy

## Supported versions

Only the latest commit on the `main` branch is supported. The demo environment is non-production and handles
public data only.

## Reporting a vulnerability

**Do not open a public issue for security problems.**

Report vulnerabilities privately through
[GitHub private vulnerability reporting](https://github.com/frkim/foundry-demo/security/advisories/new)
(**Security → Report a vulnerability**). Include:

- a description of the issue and its impact,
- steps to reproduce or a proof of concept,
- affected files, commits, or deployed endpoints.

You can expect an acknowledgement within five working days. Confirmed issues are fixed according to severity
(critical within 7 days, high within 30 days) and disclosed through a GitHub security advisory.

If the issue concerns a Microsoft product or service rather than this repository, report it to the
[Microsoft Security Response Center (MSRC)](https://msrc.microsoft.com/create-report).

## Security practices in this repository

- Keyless Azure access: the app uses a user-assigned managed identity; the Foundry resource disables local
  (key-based) authentication.
- No secrets in the repository. A temporary, time-boxed exception for the deployment credential is documented in
  [ADR-0003](docs/adr/0003-github-actions-azure-auth-exception.md).
- Packages are installed only from the Microsoft-protected package feeds; lock files are committed.
- GitHub Actions are pinned to full commit SHAs with least-privilege `permissions`.
- Dependabot, secret scanning with push protection, and CodeQL are expected to be enabled on the repository.

If a secret is ever leaked: rotate it immediately, revoke the old value, audit its usage, then remove it from
history.
