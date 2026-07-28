---
name: ts
summary: TypeScript overlay -- bun/pnpm/npm, biome or eslint+prettier, vitest, playwright
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
| `eslint.config.mjs`, `.prettierrc.json` | only when `ts_linter` is eslint-prettier |
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
4. `ts_linter` -- biome renders one config; eslint-prettier renders two.
5. `test_runner` -- decides which of `vitest.config.ts` and
   `playwright.config.ts` render. `bun-test` renders neither; bun's runner reads its settings from
   `package.json`.
6. `node_version` -- pinned in the mise fragment.
7. `ts_framework` -- recorded only. See "Framework scaffolds" below.
8. `vite_template` -- asked only when `ts_framework` is vite. Recorded only.
9. `ui_kit` -- recorded only.

## Framework scaffolds

The render runs no framework scaffold. `create-vite`, `nuxi init`, and `sst init`
all refuse a directory that already holds files, and this render writes
`tsconfig.json` before any task could run. Run the scaffold in the destination
first, then render this package over it:

| Framework | Command |
|---|---|
| vite | `pnpm dlx create-vite@9 . --template <vite_template>` |
| nuxt | `pnpm dlx nuxi@3 init . --template minimal --packageManager <js_pkg_manager>` |
| sst | `npx sst@4 init` (answers an interactive prompt) |

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
- Install the linter and test runner as dev dependencies. The render writes the
  config files but no `package.json` entries.
- `eslint.config.mjs` needs `eslint`, `typescript-eslint`, `@eslint/js`, and
  `eslint-config-prettier`. ESLint 10 dropped `.eslintrc` support, so the flat
  config is the only format that works.
- `ui_kit: shadcn` runs no scaffold. Run `shadcn init` after the framework
  scaffold exists.
- The `.pre-commit.d/` fragment stays inert until a `hooks` group package folds it
  into a config.
