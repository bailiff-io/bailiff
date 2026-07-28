---
name: github-security
summary: Callable CodeQL, Trivy, and gitleaks workflows for GitHub Actions
provides: [ci-job:security]
after: [github]
depends_on: [github]
---

Renders up to three reusable workflows, one per scanner the user turns on. A
scanner set to false renders no file at all.

| Path | Answer that renders it |
|---|---|
| `.github/workflows/wc-security-codeql.yml` | `sec_codeql` |
| `.github/workflows/wc-security-trivy.yml` | `sec_trivy` |
| `.github/workflows/wc-security-gitleaks.yml` | `sec_gitleaks` |

## Questions, in order

1. `sec_codeql` -- ask whether the repo is public. CodeQL is free on public
   repos. On a private repo it needs GitHub Advanced Security, which is a paid
   add-on, and the workflow fails with a permissions error without it.
2. `sec_codeql_languages` -- do not ask this open. Read the languages off the
   repo, map them to CodeQL identifiers, and confirm the list. TypeScript and
   JavaScript are one identifier, `javascript-typescript`. Add `actions` when the
   repo has workflows worth scanning, which it does by the time this package
   renders.
3. `sec_trivy` -- leave true. It covers dependency vulnerabilities and IaC
   misconfiguration in one pass, so it is the one scanner worth having even in a
   repo with no other security setup.
4. `sec_gitleaks` -- leave true. It reads the full history, so `fetch-depth: 0`
   makes this the slowest of the three on an old repo.

## Trivy runs twice

The first Trivy step writes SARIF with `exit-code: 0` so the upload always
happens; the second re-scans with `exit-code: 1` to fail the job. Reversing the
order means a failing scan uploads nothing and the Security tab stays empty.
Findings reach GitHub either way.

## Permissions

CodeQL and Trivy need `security-events: write` to upload SARIF. The workflows
declare it themselves, so the caller does not have to -- but a caller that sets a
narrower `permissions` block at the workflow level overrides them. Tell the user
that when they write `ci.yml`.
