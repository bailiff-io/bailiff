---
name: github
summary: GitHub Actions -- gate, path filter, and per-language test, lint, and security jobs
provides: [ci:host]
after: [base]
requires_bin: []
---

Renders the host-level pieces every GitHub Actions caller needs, and nothing
language-specific.

| Path | What it is |
|---|---|
| `.github/actions/ci-gate/action.yml` | Composite action that fails when any `needs` job failed |
| `.github/workflows/wc-gate.yml` | Reusable workflow wrapping the gate as a callable job |
| `.github/workflows/wc-changes.yml` | Reusable path filter, wrapping `dorny/paths-filter` |
| `.github/actions/setup-<lang>/action.yml` | One composite setup action per selected language |
| `.github/workflows/wc-test-<lang>.yml` | One test workflow per selected language, when `test` is in `ci_jobs` |
| `.github/workflows/wc-lint-<lang>.yml` | One lint workflow per selected language, when `lint` is in `ci_jobs` |
| `.github/workflows/wc-security-*.yml` | codeql, trivy, secrets, and osv, when `security` is in `ci_jobs` |
| `.github/workflows/wc-quality.yml` | the slow repo-wide checks, when `quality` is in `ci_jobs` |

## Questions, in order

1. `default_branch` -- the branch the caller triggers on, and the one to protect.
   Thread it from `base`.
2. `merge_queue` -- whether the caller gets a `merge_group` trigger. Requires a
   GitHub organization or Enterprise Cloud. Confirm the repo has one before
   answering yes: the workflow stays valid either way, and on a personal repo the
   trigger never fires, so a wrong answer here has no visible symptom.
3. `job_timeout_minutes` (default 15) -- the gate's own timeout.

`default_branch` and `merge_queue` reach the caller workflow, which you write.
Neither appears in a rendered file, so carry both answers forward yourself.

## The gate

A required-status gate is one job that depends on every other job and fails when
any of them failed. Branch protection then needs one required check instead of
one per job, so adding a job later does not mean editing branch protection.

`if: always()` on the gate job is what makes it run after a failure rather than
being skipped with its dependencies.

## After rendering

Render the per-language CI packages, then write `.github/workflows/ci.yml`
yourself. `../index.md` holds the composition patterns. The caller references the
gate as:

```yaml
  gate:
    needs: [test-python, lint-python]
    if: always()
    uses: ./.github/workflows/wc-gate.yml
```

## Triggers for the caller

```yaml
on:
  push:
    branches: [<default_branch>]
    # Skip CI for changes that cannot break a build.
    paths-ignore: ['**.md', 'docs/**', 'LICENSE']
  pull_request:
  <merge_group: when merge_queue is true>

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  # Never cancel on the default branch: a superseded run there may be the one a
  # release or a deployment is waiting on.
  cancel-in-progress: ${{ github.ref != 'refs/heads/<default_branch>' }}
```

With a merge queue, the gate has to run on `merge_group` as well as
`pull_request`. A required check that never runs in the queue blocks every merge.

## Branch protection

Tell the user to set the gate as the required check on `default_branch`. Nothing
rendered here configures branch protection, and `gh api` can do it:

```sh
gh api -X PUT repos/<owner>/<repo>/branches/<branch>/protection \
  --input protection.json
```

Offer to run it, and say that it needs admin on the repository.

## Language answers must match the language packages

Each language question here names a tool the job invokes. The job does not install
it; the language package does. A mismatch renders a job that fails on a missing
binary rather than on a real finding.

| Answer here | Must equal |
|---|---|
| `python_type_checker` | `languages/python`'s `python_type_checker` |
| `python_version`, `python_pkg_manager` | the same answers in `languages/python` |
| `ts_linter`, `ts_pkg_manager`, `node_version` | the same answers in `languages/ts` |
| `go_version`, `go_vulncheck` | the same answers in `languages/go` |
| `rust_toolchain`, `rust_deny` | the same answers in `languages/rust` |

## The security jobs are the second layer

`hooks/baseline` scans the staged index on every commit. These scan what a
`--no-verify` push skipped, and what predates the hooks.

| Workflow | Covers |
|---|---|
| `wc-security-secrets.yml` | full history, with trufflehog verifying a credential against its API |
| `wc-security-osv.yml` | every lockfile against the OSV database, one binary per ecosystem |
| `wc-security-trivy.yml` | IaC misconfiguration and vulnerable dependencies |
| `wc-security-codeql.yml` | dataflow analysis; free on public repos, needs Advanced Security on private |

`sec_codeql_languages` defaults to `ci_languages` with `ts` rewritten to
`javascript-typescript`, which is CodeQL's name for it. Override it only to add a
language the catalog does not scaffold.

## Filenames carry no quote character

The conditional filenames use derived booleans (`job_py_test`, `setup_go`,
`job_security`) rather than `{% if "python" in ci_languages %}`. jinja compiles a
template with its filename embedded in the generated Python, so a quote in the
path breaks that string literal and raises a `SyntaxError` pointing at an
unrelated body line. The flags carry `when: false`, so they never reach the
interview.

## The quality job holds what a commit hook cannot

`hooks/baseline` runs what is fast enough against staged files. These are the rest,
measured on a 212-file repo:

| Check | Why not a hook |
|---|---|
| `pinact run --check` | 1.4s, and it resolves every action tag over the GitHub API |
| `yamllint` | 1.1s |
| `markdownlint-cli2` | 1.2s |
| `cspell` | 1.7s |
| `lychee` without `--offline` | reaches the network; the hook only resolves relative links |
| `lizard` whole-repo | 3.1s against 212 files, where 12 staged files take 208ms |
| `jscpd` | duplication is invisible from a staged set, so it has no hook form |

`yamllint` runs with the relaxed profile and line-length disabled when the repo
pins no `.yamllint`. Its defaults flag 80-column lines and a missing document
start, and a GitHub workflow routinely exceeds 80 columns, so the defaults would
report findings that are not project rules.

`lizard` and `jscpd` default off. Both report on a codebase rather than on a
change, so they suit a repo that has agreed a threshold.
