---
name: github
summary: GitHub Actions host setup plus a reusable required-status gate
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
