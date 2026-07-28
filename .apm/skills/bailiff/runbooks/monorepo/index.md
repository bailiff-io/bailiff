# Runbook: monorepo

A repo holding several packages that share one history and one set of
conventions. Setting one up and adding to one take different runbooks.

| The user wants | Runbook |
|---|---|
| Set up a monorepo, root and its first packages | `setup/index.md` |
| Add one package to a monorepo that already exists | `add-package/index.md` |

Ask which when the request is ambiguous. "Set up my monorepo" against a directory
that already holds `moon.yml` and four packages usually means the second.

## What both share

**The destination differs by package.** Some render at the repo root, others into a
package directory. Getting this wrong puts a `pyproject.toml` at the root of a repo
whose packages each need their own.

| Renders at the root | Renders per package |
|---|---|
| base, editorconfig, moon, justfile, devcontainer | the language packages |
| the hook manager | readme (once at root, once per package) |
| ci host and ci jobs | |
| repo host, release tool, dep-updates | |
| agentic, apm, agent-hooks, beads | |

The hook manager, CI, and the release tool are root-level because git has one
`.git/hooks/`, one `.github/workflows/`, and one tag namespace.

**Per-package answers files.** A language package rendered into
`packages/api/` writes `packages/api/.copier-answers.python.yml`. Each package
directory carries its own, and they do not conflict.

**The language question is per package.** Ask which language each package uses.
Do not assume the repo has one language, and do not assume every package shares
the root's.

## Workspace marker

Confirm which workspace mechanism the repo uses or will use, because it decides
where package directories live and how they resolve each other.

| Marker | Mechanism |
|---|---|
| `moon.yml` | moon |
| `pnpm-workspace.yaml` | pnpm workspaces |
| `[tool.uv.workspace]` in `pyproject.toml` | uv workspaces |
| `[workspace]` in `Cargo.toml` | Cargo workspaces |
| `go.work` | Go workspaces |

A repo carries both a language-native workspace and `moon`. The language workspace
resolves dependencies; `moon` orchestrates tasks across them. See
`tools/workspace/index.md`.
