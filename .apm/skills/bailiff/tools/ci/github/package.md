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

## Questions, in order

1. `default_branch` -- the branch the caller triggers on. Take it from `base`.
2. `merge_queue` -- whether the caller adds a `merge_group` trigger. Requires a
   GitHub organization or GitHub Enterprise Cloud subscription. Ask the user to
   confirm the repo has one before answering yes; a `merge_group` trigger on a
   personal repo never fires.

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

Tell the user to set the gate as the required check in branch protection. Nothing
rendered here configures branch protection.
