---
name: justfile
summary: justfile with default, test, lint, build, dev, and clean recipes
provides: [workspace:tasks]
after: [base, python, ts, go, rust, lefthook, precommit]
---

## Renders

| Path | Contents |
|---|---|
| `justfile` | six recipes: `default`, `test`, `lint`, `build`, `dev`, `clean`. Skipped when a `justfile` already exists |
| `.mise/conf.d/justfile.toml` | pins `just = "latest"` for mise |
| `.copier-answers.justfile.yml` | the answers |

## Ask

In this order:

1. `language` (`python`, `ts`, `go`, `rust`, or empty; default empty) -- selects
   the recipe bodies. Empty renders stubs that print a message and exit 1, so a
   maintainer hits the gap rather than a silent no-op. Pass the language package
   the user selected.
2. `js_pkg_manager` (`bun`, `pnpm`, `npm`; default `bun`) -- named by the `test`,
   `build`, and `dev` recipes. Ask only when `language: ts`.
3. `hook_manager` (`pre-commit`, `lefthook`, `none`; default `none`) -- see below.

## hook_manager must match the hooks group

The answer has to be the package the user picked from `hooks/`: `lefthook` for
`hooks/lefthook`, `pre-commit` for `hooks/precommit`, `none` when the user
selected neither. It decides the `lint` recipe body:

| Answer | `lint` runs |
|---|---|
| `pre-commit` | `pre-commit run --all-files` |
| `lefthook` | `lefthook run pre-commit` |
| `none` | the language's own linter, for example `uv run ruff check .` |

Passing a value the hooks group contradicts renders a `lint` recipe naming a tool
the repository does not install, and `just lint` then fails with a
command-not-found.

## After rendering

The recipe bodies are per-language defaults. Read the rendered `justfile` against
the project's real commands and correct any recipe that names a script the
project does not define. A second render leaves the file alone.
