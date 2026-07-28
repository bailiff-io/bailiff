---
name: apm
summary: apm.yml declaring the project's APM package dependencies, then apm install
provides: [agentic:packages]
after: [base]
requires_bin: [uvx]
---

## Renders

`apm.yml`, holding `name`, `version`, `description`, `target`, `includes: auto`,
and one `dependencies.apm` entry per locator.

The task then runs `apm install` through `uvx`, pinned to `apm_cli_version`. That
resolves the locators, writes `apm.lock.yaml`, and installs the packages under
`apm_modules/`. Commit the lock file.

## Ask in this order

1. `apm_packages` -- the locator list. Each entry is
   `owner/repo/packages/name#constraint`. An empty list fails the validator and
   aborts the render before any file is written, because the package has no
   purpose without one. Drop the package from the selection instead.
2. `apm_target` -- the harnesses `apm install` deploys to, comma-separated.
   Default `claude,codex`. When `agentic` is in the same selection, set this from
   its `agentic_targets` answer so the two agree.
3. `project_name` and `description` -- copy from `base` when `base` is in the same
   selection.
4. `apm_cli_version` -- keep the default unless the user names a version.

## Scope

Offer this package when the user describes authoring or consuming APM packages:
skills, agents, or steering distributed across repos. A repo that merely runs an
agent needs `agentic`, not this.

## After rendering

- The install needs `uvx`. `render.py` exits 3 when it is missing.
- APM reads any registry token from the environment. The user supplies it out of
  band; no token enters an answers file.
- Adding a package later means editing `apm.yml` and re-running `apm install`.
- `apm install` adds `apm_modules/` to `.gitignore` and installs each package's
  harness assets under `.claude/` and `.codex/`, following the `apm_target`
  answer. Read those paths when `agentic` also rendered them.
- Pin every locator with `#tag` or `#sha`. `apm install` warns on an unpinned
  entry and resolves it to whatever the default branch holds.
