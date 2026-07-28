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
