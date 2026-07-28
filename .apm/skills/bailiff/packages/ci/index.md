# ci

CI packages render deterministic units. You write the workflow that calls them.

| Axis | How many | Packages |
|---|---|---|
| `ci:host` | Exactly one, or none | github |

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

## One package, two multiselects

`github` renders every job. `ci_languages` decides which languages get a test and
a lint workflow; `ci_jobs` decides which kinds of job render at all.

Take the language list from what you rendered in `languages/`, and confirm it with
the user rather than inferring it from files on disk. Every language answer must
match the language package's: `python_type_checker`, `ts_linter`, and the version
answers all name tools the CI job invokes, and a mismatch means the job runs
something the project did not install.

Adding a language is one answer. Adding a host is one package.

Every workflow takes a `working-directory` input defaulting to `.`. One render
therefore serves every package in a monorepo; the caller passes a different
directory per job.

### Conditional filenames carry no quote character

A filename like `{% if job_py_test %}wc-test-python.yml{% endif %}.jinja` uses a
derived boolean rather than `{% if "python" in ci_languages %}`. jinja compiles
each template with its filename embedded in the generated Python, so a quote in
the path breaks that string literal. The failure is a `SyntaxError` pointing at an
unrelated line of the file body, which is why the flags exist.

## Compose the caller

Apply these patterns. Which ones fit depends on the project the user described,
so ask when the answer is not evident.

**Path filtering.** `github` renders `wc-changes.yml`, which wraps
`dorny/paths-filter`. Call it first, pass one filter key per area, and gate each
language job on the matching output:

```yaml
  changes:
    uses: ./.github/workflows/wc-changes.yml
    with:
      filters: |
        python: ['src/**', 'pyproject.toml', 'uv.lock']
        ts: ['web/**', 'package.json']
  test-python:
    needs: changes
    if: contains(fromJSON(needs.changes.outputs.changes), 'python')
    uses: ./.github/workflows/wc-test-python.yml
```

Do not reach for `on.push.paths` instead. It decides whether the whole workflow
runs rather than which jobs run, and a workflow that never starts leaves its
required checks pending forever, so a docs-only PR cannot merge. Use
`paths-ignore` only for paths that should skip CI entirely.

**Timeouts.** Every rendered job carries `timeout-minutes`. GitHub's default is
360, so a hung job burns six runner hours before it is killed.

**Do not persist credentials.** Every rendered checkout passes
`persist-credentials: false`. The default writes `GITHUB_TOKEN` into
`.git/config`, where any later step or transitive dependency can read it.

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

**Pin every action by SHA, including `actions/`.** A full commit SHA with the
version in a trailing comment. zizmor's `unpinned-uses` audit reports a tag on
`actions/checkout` as a high-confidence finding under its blanket policy, and
`hooks/baseline` runs zizmor on commit, so a tag-pinned action fails the hook
this catalog installed. `pinact run --check` verifies the whole tree.

**Least privilege.** Declare `permissions:` at the workflow level with the
narrowest set, and widen per job where a job needs more.

Write the caller last, after every job package has rendered, so it references
files that exist.
