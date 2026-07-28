---
name: github-go
summary: GitHub Actions test and lint jobs for Go, as reusable workflows
provides: [ci-job:test-go, ci-job:lint-go]
after: [github, go]
depends_on: [github]
---

Renders three files.

| Path | What it is |
|---|---|
| `.github/actions/setup-go/action.yml` | Installs Go and downloads modules |
| `.github/workflows/wc-test-go.yml` | Callable test job |
| `.github/workflows/wc-lint-go.yml` | Callable lint job, golangci-lint plus gofmt |

## Questions, in order

1. `go_version` -- take it from the `go` directive in the project's `go.mod`
   rather than asking. Confirm the value with the user.
2. `go_race` -- whether tests run with `-race`. Leave true for a service; the race
   detector roughly doubles test time, which matters only for a large suite.
3. `go_coverage` -- whether the test job writes a coverage profile. The workflow
   writes `coverage.out` and uploads nothing. Say that, because a user who asks
   for coverage usually wants it reported somewhere.
4. `ci_cache` -- leave true. `setup-go` caches modules and build output.
5. `ci_os_matrix` -- ask only when the project targets more than Linux.
6. `ci_version_matrix` -- ask only for a library supporting several Go versions.

## Pinned versions

`golangci-lint` is pinned to `v2.12.2` in the lint workflow. A floating `latest`
turns an upstream release into a build failure on an unrelated commit.

## After rendering

Tell the user the repo needs a `.golangci.yml`. Without one, `golangci-lint` runs
its default linter set, which is narrower than most projects want. The `go`
language package renders one when it is selected.
