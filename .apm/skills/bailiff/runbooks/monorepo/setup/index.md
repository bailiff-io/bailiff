# Runbook: monorepo setup

Set up the root and the first packages. Read `../index.md` first for the
root-versus-package split and the workspace markers.

## Interview order

1. **What does this monorepo hold?** Get the list of packages and what each does,
   before any tooling question. Everything downstream depends on this list.
2. **Name and owner.** `project_name` and `org` for the root.
3. **Package directories.** Where do packages live: `packages/`, `apps/`, `libs/`,
   or a mix. Get the actual paths.
4. **Language per package.** Walk the list from step 1, one package at a time.
5. **Workspace mechanism.** From the table in `../index.md`. Ask whether they want
   `moon` on top; recommend it when the packages span more than one language.
6. **Root tooling.** Hook manager, CI host, release tool, dep-updates. One answer
   each, applying to the whole repo.
7. **Optional groups.** `docs/`, `iac/`, `agentic/`, `workspace/devcontainer`.

Answer `layout: monorepo` in the `base` answers file.

## Render order

Root first, packages second, root-level integration last.

```
1. foundation/base                       dest = root, layout: monorepo
2. workspace/moon                        dest = root   (when picked)
3. foundation/editorconfig               dest = root
4. foundation/readme                     dest = root
5. per package, in the order the user named them:
     languages/<pick>                    dest = <package dir>
     foundation/readme                   dest = <package dir>
6. hooks/<pick>                          dest = root
7. workspace/justfile                    dest = root
8. repo/<host>                           dest = root
9. ci/<host>, then each ci/<job>         dest = root
10. repo/<release tool>                  dest = root
11. repo/dep-updates                     dest = root
12. docs/*, iac/*, agentic/*             dest = root
```

Step 6 comes after step 5 because the hook manager reads the `.pre-commit.d/` and
`.hooks.d/` fragments the language packages wrote. Each language package writes its
fragment into its own package directory, so tell the hook manager where the
packages are.

Step 10 comes after step 5 because a monorepo release config names the package
directories. Pass them in `monorepo_packages`.

## Threading shared answers

Each package's answers file needs its own `project_name`: the package's name, not
the repo's. `org`, `description`, and `default_branch` stay the root's values.

Write one answers file per render, named for what it renders:

```
/tmp/bailiff-answers-base.yml
/tmp/bailiff-answers-python-api.yml
/tmp/bailiff-answers-ts-web.yml
```

Reusing one file across packages puts the wrong `project_name` in a manifest.

## CI in a monorepo

Path filtering is the decision that matters here. A push touching one package
should run that package's jobs and no others. `tools/ci/index.md` covers the
patterns; the caller you write needs one filter per package directory.

## After rendering

```sh
git -C <dest> status --short
```

Report the tree you produced, grouped by package, and name the workspace install
command. Then say what the user does next per package: install, test, lint.

Verify the workspace resolves before calling it done. The command depends on the
mechanism: `uv sync`, `pnpm install`, `cargo check`, `go work sync`, or
`moon check --all`. Run it and report what it says.
