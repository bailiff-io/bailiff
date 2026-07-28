---
name: ts
summary: TypeScript overlay -- bun/pnpm/npm, biome or oxlint, tsc, vitest, knip
provides: [language:ts]
after: [base]
requires_bin: [mise]
precheck: precheck.py
---

## Renders

| Path | Contents |
|---|---|
| `tsconfig.json` | strict compiler options, `src` in, `dist` out |
| `biome.json` | Biome 2 config; only when `ts_linter` is biome |
| `.oxlintrc.json` | oxlint config; only when `ts_linter` is oxlint |
| `vitest.config.ts` | only for the vitest test runners |
| `playwright.config.ts` | only for `playwright-only` and `vitest+playwright` |
| `.mise/conf.d/ts.toml` | node version, plus bun or pnpm |
| `.pre-commit.d/ts.yaml` | hooks matching the chosen linter |
| `.gitignore.d/ts` | Node and TypeScript ignore lines |
| `package.json` | written by the chosen package manager after the render |

`package.json` and `pnpm-workspace.yaml` carry `_skip_if_exists`.

## Question order

1. `project_name` -- recorded in the answers file. Thread the value the user gave
   `base`.
2. `description` -- recorded in the answers file.
3. `js_pkg_manager` -- bun, pnpm, or npm. Decides which init task runs and which
   tool the mise fragment lists.
4. `ts_linter` -- `biome` or `oxlint`. See below.
5. `test_runner` -- decides which of `vitest.config.ts` and
   `playwright.config.ts` render. `bun-test` renders neither; bun's runner reads its settings from
   `package.json`.
6. `node_version` -- pinned in the mise fragment.
7. `ts_framework` -- recorded only. See "Framework scaffolds" below.
8. `vite_template` -- asked only when `ts_framework` is vite. Recorded only.
9. `ui_kit` -- recorded only.

## Framework scaffolds

The render runs no framework scaffold, because every scaffold refuses a directory
that already holds files and this render writes `tsconfig.json` before any task
could fire. Run the scaffold in the destination first, then render this package
over it. `ts_framework` and `vite_template` are recorded so the answers file says
which scaffold produced the tree.

| Framework | Command |
|---|---|
| vite | `pnpm dlx create-vite@9 . --template <vite_template>` |
| nuxt | `pnpm dlx nuxi@3 init . --template minimal --packageManager <js_pkg_manager> --no-install --force --gitInit=false` |
| sst | No non-interactive form. Have the user run `npx sst@4 init` themselves. |

Check that the scaffold wrote files rather than trusting its exit status. `nuxi`
exits 0 after printing a prompt it could not ask, so a missing flag reads as
success. It needs all three of `--template`, `--force`, and `--gitInit=false`: it
refuses a destination that exists at all, and treats the other two as required in
a non-interactive terminal. `--force` overwrites only the paths the template
writes.

`sst@4 init` has a `--yes` flag, but it skips the confirmation only. The provider
question still prompts, and the command exits 1 without writing.

`create-vite@9` writes the vanilla template for a `--template` name it does not
recognise rather than failing, which is why `vite_template` is an enum.

A scaffold writes its own `package.json` and `tsconfig.json`. `package.json`
carries `_skip_if_exists` so the render leaves it alone; `tsconfig.json` does not,
so this package's strict config replaces the scaffold's. Reconcile the two if the
framework needs specific compiler options.

## Prerequisites

`mise` must be on PATH. The precheck also requires whichever of `bun`, `pnpm`, or
`npm` `js_pkg_manager` names.

## After rendering

- Tasks run `mise trust --yes && mise install`, then the package manager's init
  when `package.json` is absent.
- A task installs the linter, prettier, typescript, knip, and the coverage
  provider as devDependencies, so the hooks run tools the project owns rather
  than whatever the runner fetches at hook time.
- `ui_kit: shadcn` runs no scaffold. Run `shadcn init` after the framework
  scaffold exists.
- The `.pre-commit.d/` fragment stays inert until a `hooks` group package folds it
  into a config.

## biome or oxlint

eslint is gone. Both replacements are Rust, and the difference is scope.

| | biome 2.5.6 | oxlint 1.76.0 |
|---|---|---|
| Lint | yes | yes, ~500 rules porting eslint, typescript-eslint, unicorn, react |
| Format | same binary | `oxfmt`, a second binary |
| CSS and JSON | yes | JS and TS only |
| Config | `biome.json` | `.oxlintrc.json`, eslint-compatible |

Default to `biome`: one binary covering lint and format across four languages is
less to install and less to keep in step. Offer `oxlint` when the user wants the
wider rule set and accepts a second binary for formatting.

Prettier renders either way. Neither biome nor oxlint formats markdown or YAML.

## The package manager decides the runner

Each has its own, and they are not interchangeable: bun uses `bunx`, npm uses
`npx`, pnpm uses `pnpm exec`. `bun exec` is not a command and fails with
`command not found`, so the fragments render the right one per answer.

## What the linters do not check

| Concern | Tool | Why it is separate |
|---|---|---|
| Types | `tsc --noEmit` | Neither linter type-checks; only the compiler does |
| Dead code, unused deps | `knip` | Whole-project: an export is dead only when nothing imports it |
| Coverage | `@vitest/coverage-v8` | Reports lcov for CI and text locally |

`tsc` and `knip` take no file list. Both read the whole project, and a per-file
run resolves nothing.

`ts_coverage` is asked only for a vitest runner. Playwright measures end-to-end
runs rather than units, so a coverage threshold against it means little.
