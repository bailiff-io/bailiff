# workspace

Local development ergonomics: the task runner, and the container developers work
in.

| Axis | How many | Packages |
|---|---|---|
| `workspace:tasks` | At most one | justfile |
| `workspace:container` | At most one | devcontainer |

Monorepo mechanics live in `../repo/index.md`: `moon` and `package-add`.

## justfile

Renders a `justfile` whose recipes wrap the project's real commands.

Its `hook_manager` answer takes `pre-commit`, `prek`, `lefthook`, or `none`, and it must
match what the user picked in `../hooks/index.md`. A contradicting value renders
a lint recipe naming a tool the repo does not install, and `just lint` then fails
with command-not-found.

The recipes name commands the hook manager and the language packages installed,
which is what its `after:` encodes.

## devcontainer

Renders `.devcontainer/`. Offer it when the user says contributors need a
reproducible environment or the project has system dependencies beyond the
language toolchain. A project whose setup is one `mise install` does not need it.
