---
name: github-python
summary: GitHub Actions test and lint jobs for Python, as reusable workflows
provides: [ci-job:test-python, ci-job:lint-python]
after: [github, python]
depends_on: [github]
---

Renders three files. The setup action holds the install steps that test and lint
both need, so a change to the install path happens once.

| Path | What it is |
|---|---|
| `.github/actions/setup-python/action.yml` | Installs Python and the dependencies |
| `.github/workflows/wc-test-python.yml` | Callable test job |
| `.github/workflows/wc-lint-python.yml` | Callable lint job |

## Questions, in order

1. `python_version` -- take it from the `python` language package's answer rather
   than asking again.
2. `python_pkg_manager` -- also from the language package. A mismatch installs
   dependencies with a tool the project does not use, and the job fails on a
   missing lockfile.
3. `python_test_command` -- what the test job runs. Default `pytest`.
4. `python_type_checker` -- `none`, `mypy`, `pyright`, or `ty`. Ask whether the
   project type checks in CI; answer `none` when it does not.
5. `ci_cache` -- leave true.
6. `ci_os_matrix` -- ask only when the user says the project targets more than
   Linux. Each entry multiplies runner minutes by one.
7. `ci_version_matrix` -- ask only for a library that supports several Python
   versions. An application pins one version and needs no matrix.

## Both workflows take a working-directory input

Default `.`. In a monorepo, the caller passes the package's directory:

```yaml
  test-api:
    uses: ./.github/workflows/wc-test-python.yml
    with:
      working-directory: packages/api
```

Render this package once per repository, not once per package. One pair of
workflows serves every Python package in a monorepo, called once each with a
different `working-directory`.

## After rendering

Write the caller yourself. Give test and lint separate jobs with no `needs`
between them so both start at once. `../index.md` holds the rest of the patterns.
