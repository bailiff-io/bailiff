# Runbook: monorepo

A repo holding several packages that share one history and one set of conventions.

| The user wants | Runbook |
|---|---|
| Set up a monorepo, root and its first packages | `setup/index.md` |
| Add one package to a monorepo that already exists | `add-package/index.md` |

`probe.py` reports `package_dirs`; a populated one means the second. Ask when the
request is still ambiguous.

## Rules for both

1. **The destination differs by package.** Getting this wrong puts a
   `pyproject.toml` at the root of a repo whose packages each need their own.
2. **The language question is per package.** Do not assume the repo has one
   language, and do not assume a package shares the root's.
3. **One answers file per render.** A language package rendered into
   `packages/api/` writes `packages/api/.copier-answers.python.yml`. Reusing one
   file across packages puts the wrong `project_name` in a manifest.
4. **`project_name` in a package's answers file is the package's name.** `org`,
   `description`, and `default_branch` stay the root's values.

| Renders at the root | Renders per package |
|---|---|
| base, editorconfig, moon, justfile, devcontainer | the language packages |
| the hook manager | readme (once at root, once per package) |
| ci host and ci jobs | |
| repo host, release tool, dep-updates | |
| agentic, apm, agent-hooks, beads | |

The hook manager, CI, and the release tool are root-level because git has one
`.git/hooks/`, one `.github/workflows/`, and one tag namespace.

## Workspace marker

`probe.py` reports `workspace` with the marker and its mechanism, covering moon,
pnpm, uv, cargo, and go. Confirm which mechanism the repo uses or will use: it
decides where package directories live and how they resolve each other.

A repo carries both a language-native workspace and `moon`. The language
workspace resolves dependencies; `moon` orchestrates tasks across them. See
`../../packages/workspace/index.md`.
