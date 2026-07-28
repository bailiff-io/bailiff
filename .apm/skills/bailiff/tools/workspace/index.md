# workspace

Task running, monorepo orchestration, and the container developers work in.

| Axis | How many | Packages |
|---|---|---|
| `workspace:monorepo` | At most one, monorepos only | moon |
| `workspace:tasks` | At most one | justfile |
| `workspace:container` | At most one | devcontainer |
| `workspace:add` | Repeatable, monorepos only | package-add |

## moon

Renders `moon.yml` and the workspace configuration that makes a monorepo's
packages addressable as build targets. Offer it only for a monorepo.

A monorepo runs without `moon`: the language toolchain's own workspace support
(uv workspaces, pnpm workspaces, Cargo workspaces) covers dependency resolution.
`moon` adds task orchestration and affected-target detection across languages.
Offer it when the monorepo spans more than one language, and ask otherwise.

## justfile

Renders a `justfile` with recipes wrapping the project's real commands. Its
`hook_manager` answer takes `pre-commit`, `lefthook`, or `none`, and it must match
what the user picked in `hooks/`. Passing a different value produces a lint recipe
naming a tool the repo does not install.

## devcontainer

Renders `.devcontainer/`. Offer it when the user says contributors need a
reproducible environment or the project has system dependencies beyond the
language toolchain. A project whose setup is one `mise install` does not need it.

## package-add

Adds one package to an existing monorepo. Unlike everything else in the catalog,
this runs against a repo that is already set up, and it runs once per package the
user adds. `runbooks/monorepo/add-package/index.md` drives it.

Its destination is the new package's directory, not the repo root.

## Order

Render `moon` before `package-add`, because the new package registers with the
workspace. Render `justfile` after the hook manager and after the language
packages, because its recipes name their commands.
