---
name: github-ts
summary: GitHub Actions test and lint jobs for TypeScript, as reusable workflows
provides: [ci-job:test-ts, ci-job:lint-ts]
after: [github, ts]
depends_on: [github]
---

Renders three files. The setup action holds the install steps that test and lint
both need.

| Path | What it is |
|---|---|
| `.github/actions/setup-ts/action.yml` | Installs Node, the package manager, and the dependencies |
| `.github/workflows/wc-test-ts.yml` | Callable test job |
| `.github/workflows/wc-lint-ts.yml` | Callable lint job |

## Questions, in order

1. `node_version` -- take it from the `ts` language package's answer.
2. `ts_pkg_manager` -- also from the language package. `pnpm`, `bun`, or `npm`.
   A mismatch fails on a missing lockfile: the install uses `--frozen-lockfile`
   against a lockfile the chosen tool did not write.
3. `ts_test_command` -- the package script name. Default `test`, so the job runs
   `pnpm run test`.
4. `ts_linter` -- `biome`, `eslint`, or `none`. `biome` covers lint and format in
   one step; `eslint` needs prettier alongside it, and the lint job runs both.
5. `ts_typecheck` -- whether the lint job runs `tsc --noEmit`.
6. `ci_cache` -- leave true. With `pnpm` and `npm` this uses the setup-node cache.
7. `ci_os_matrix` -- ask only when the project targets more than Linux.
8. `ci_version_matrix` -- ask only for a library supporting several Node versions.

## Both workflows take a working-directory input

Default `.`. In a monorepo the caller passes the package's directory:

```yaml
  test-web:
    uses: ./.github/workflows/wc-test-ts.yml
    with:
      working-directory: apps/web
```

Render this package once per repository. One pair of workflows serves every
TypeScript package, called once each with a different `working-directory`.

## After rendering

The test command must exist as a script in the package's `package.json`. Check
that it does and say so when it does not; a workflow calling a missing script
fails on the first run.
