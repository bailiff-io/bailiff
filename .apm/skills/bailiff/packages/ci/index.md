# ci

CI packages render deterministic units. You write the workflow that calls them.

| Axis | How many | Packages |
|---|---|---|
| `ci:host` | Exactly one, or none | github |
| `ci-job:*` | One or more, matched to the languages present | github-python, github-ts, github-go, github-rust, github-security |

## What renders and what you write

| Artifact | Author | Path |
|---|---|---|
| Composite action | package render | `.github/actions/<name>/action.yml` |
| Reusable workflow | package render | `.github/workflows/wc-<name>.yml` |
| Caller workflow | you | `.github/workflows/ci.yml` |

No package renders `ci.yml`. The reason is that the caller encodes decisions
specific to the project: which jobs run on which paths, what depends on what, and
which matrix dimensions are worth the runner minutes. A template that tried to
cover those decisions would need a conditional per combination.

## Pick the jobs

Render one language package per language the project has. Each one provides both
a test job and a lint job, as two reusable workflows sharing one composite setup
action. Take the language list from what you rendered in `languages/`, and confirm
it with the user rather than inferring it from files on disk.

Every workflow takes a `working-directory` input defaulting to `.`. One render of
`github-python` therefore serves every Python package in a monorepo; the caller
passes a different directory per job. Do not render a language package twice.

`github-security` is language-independent. Offer it once.

## Compose the caller

Apply these patterns. Which ones fit depends on the project the user described,
so ask when the answer is not evident.

**Path filtering.** In a monorepo, gate each package's jobs on that package's
paths with `dorny/paths-filter` or `on.push.paths`. A push touching one package
should not run every other package's tests.

**Matrix.** Put the language runtime versions the user named on the matrix axis.
Add operating systems only when the user says the project targets more than
Linux; each extra axis value multiplies runner minutes.

**Parallel lint and test.** Lint and test have no ordering relationship. Give
them separate jobs with no `needs` between them so both start immediately.

**needs graph.** A build or publish job takes `needs: [test, lint]`. Nothing else
should.

**Concurrency.** Every caller workflow gets:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

A superseded push should stop consuming runners.

**OIDC over stored secrets.** When a job authenticates to a cloud, use
`permissions: id-token: write` with the provider's OIDC action. Ask the user to
add a stored credential only when the provider has no OIDC path.

**Pin actions by SHA.** Third-party actions take a full commit SHA, with the
version in a trailing comment. Actions under `actions/` may take a tag.

**Least privilege.** Declare `permissions:` at the workflow level with the
narrowest set, and widen per job where a job needs more.

## Order

Render the host package before the job packages. Render every job package before
you write the caller, so the caller references files that exist.
