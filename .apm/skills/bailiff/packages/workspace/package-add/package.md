---
name: package-add
summary: One new package in a monorepo, initialised by its language's own tool
provides: [workspace:add]
after: [base, moon]
precheck: precheck.py
---

## The destination is the package directory

Every other package in the catalog renders into the repository root. This one
renders into the new package's own directory, so the destination passed to
`render.py` is `<repo>/<parent-dir>/<name>`, for example
`/repo/packages/api-client`. The directory need not exist; `render.py` creates it.

Passing the repository root instead initialises the new package on top of the
repository's own manifest.

## Renders

| Path, relative to the destination | Contents |
|---|---|
| `package.json`, `pyproject.toml`, `go.mod`, or `Cargo.toml` | written by the language's own init command, not by a template |
| `.copier-answers.package-add.yml` | the answers |

The template holds only the answers file. `_tasks` runs the native init in the
destination: `bun init -y`, `pnpm init`, `npm init`, `uv init`, `pdm init -n`,
`go mod init`, or `cargo init`. Each is guarded by a `test -f` on its manifest, so
a second render over a populated directory changes nothing.

## Ask

In this order:

1. `name` -- the package name, also the directory basename. `precheck.py` rejects
   any value that is not alphanumeric plus dot, dash, and underscore, because the
   value reaches a shell command.
2. `lang` (`ts`, `python`, `go`, `rust`) -- selects which init command runs.
3. `python_pkg_manager` (`uv` or `pdm`, default `uv`) -- ask only when
   `lang: python`.
4. `js_pkg_manager` (`bun`, `pnpm`, `npm`, default `bun`) -- ask only when
   `lang: ts`. Match the manager the monorepo already uses.
5. `rust_edition` (`2024` or `2021`, default `2024`) -- ask only when
   `lang: rust`.

The parent directory is not a question. It is part of the destination path the
agent constructs. `packages/` is the usual choice.

## precheck

`precheck.py` validates `name` and checks that the one binary the chosen language
and manager need is on PATH. `render.py` runs it before copier, so a missing
binary leaves the destination untouched. `requires_bin` cannot express this
because the binary depends on the answers.

## After rendering

Register the new package with the workspace, from the repository root, not from
the destination:

| Stack | Command |
|---|---|
| uv workspace | `uv add --workspace <dir>/<name>` |
| pnpm | add the path to `pnpm-workspace.yaml` `packages:` |
| bun | add the path to the root `package.json` `workspaces` |
| Cargo | add the path to the root `Cargo.toml` `[workspace] members` |
| go | `go work use <dir>/<name>` when `go.work` exists |
| moon | add the project to `.moon/workspace.yml` `projects`, unless it already matches a glob |

`runbooks/monorepo/add-package/index.md` drives the whole sequence.
