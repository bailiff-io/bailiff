---
name: go
summary: Go overlay -- go.mod, golangci-lint config, mise pin, cmd/ stub
provides: [language:go]
after: [base]
requires_bin: [go]
---

## Renders

| Path | Contents |
|---|---|
| `.golangci.yml` | golangci-lint v2 config with errcheck, govet, ineffassign, staticcheck, unused |
| `.mise/conf.d/go.toml` | go version, plus gotestsum when `test_runner` is gotestsum |
| `.pre-commit.d/go.yaml` | golangci-lint hook at `golangci_hook_rev`; empty when that answer is empty |
| `.gitignore.d/go` | build outputs, plus `vendor/` when `use_vendor_mode` is true |
| `cmd/<project_name>/main.go` | stub entry point; omitted when `app_kind` is library |
| `go.mod` | written by `go mod init` after the render |

`.golangci.yml`, `go.mod`, `go.sum`, and the `main.go` stub carry
`_skip_if_exists`.

## Question order

1. `project_name` -- becomes the module path passed to `go mod init` and the
   `cmd/<name>/` directory, lowercased with spaces and underscores turned into
   hyphens. Thread the value the user gave `base`.
2. `description` -- recorded in the answers file.
3. `go_version` -- pinned in the mise fragment.
4. `app_kind` -- library excludes the whole `cmd/` directory.
5. `test_runner` -- gotestsum adds the tool to the mise fragment. Test commands
   run `gotestsum --` instead of `go test`.
6. `use_vendor_mode` -- true adds `vendor/` to the gitignore fragment.
7. `golangci_hook_rev` -- rev for the golangci-lint hook. The default tracks a
   released tag; raise it if a newer one exists. An empty answer renders an empty
   fragment.

## Prerequisites

`go` must be on PATH. Install it from https://go.dev/doc/install, or via
`mise use go`.

## After rendering

- The task runs `go mod init` only when `go.mod` is absent. The module path it
  writes is a bare name. Rewrite the `module` line to a full path such as
  `github.com/owner/repo` before publishing.
- Add dependencies with `go get`. The render writes none.
- The `.pre-commit.d/` fragment stays inert until a `hooks` group package folds it
  into a config.

## Go needs fewer extra tools than the other languages

`golangci-lint` bundles roughly 50 analyzers, so most concerns are answers that
enable a bundled linter rather than a new dependency.

| Concern | Covered by | Note |
|---|---|---|
| Security | `gosec`, inside golangci | Ships with the runner; the standard set leaves it off |
| Dead code | `unused`, inside golangci | Already enabled |
| Duplication, complexity | `dupl`, `gocyclo` | Available in the runner, off by default |
| Coverage | `go test -cover` | Builtin to the toolchain |
| Unused deps | `go mod tidy -diff` | Builtin; no cargo-machete equivalent needed |
| Vulnerabilities | `govulncheck` | The one genuine addition |

`govulncheck` is worth having over a generic scanner because it reports
vulnerabilities on a code path the module actually reaches, rather than every
advisory touching the dependency tree.

## The config schema is golangci-lint v2

Settings nest under `linters.settings`. A top-level `linters-settings` key, which
is the v1 shape, is rejected outright:

```
jsonschema: "" does not validate with "/additionalProperties":
additional properties 'linters-settings' not allowed
```

Verify a change with `golangci-lint config verify` before committing it.

## revive is narrowed to one rule

Naming `exported` under `linters.settings.revive.rules` replaces revive's default
rule set with that rule alone. This is deliberate: the default set includes
`package-comments` and other opinions that fire on ordinary code. Adding a rule
means adding it to that list.

Verified against a rendered project: `exported` reports an undocumented exported
function, and `gosec` reports G501, G401, and G306 on a file using md5 and a
world-writable `WriteFile`.

## What runs when

| Hook | Stage | Why |
|---|---|---|
| `gofmt` | pre-commit | fast, fixes in place |
| `golangci-lint run ./...` | pre-commit | package-scoped, so no staged-file list |
| `go mod tidy -diff` | pre-commit | reports rather than rewrites, so a stale go.mod fails |
| `govulncheck ./...` | pre-push | queries the vulnerability database |

`go mod tidy -diff` matters over plain `go mod tidy`: the plain form rewrites the
files mid-commit, which fixes the symptom without the author noticing.
