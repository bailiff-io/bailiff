---
name: cocogitto
summary: Conventional-commit releases driven by the local cog command
provides: [release:tool]
after: [base]
---

Renders:

- `cog.toml` with `tag_prefix = "v"` and `[changelog] path = "CHANGELOG.md"`
- `.mise/conf.d/cocogitto.toml` pinning `cog = "latest"`
- `.pre-commit.d/cocogitto.yaml` with a `commit-msg` hook running `cog verify --file`

The pre-commit fragment only takes effect when the `precommit` package is also
selected; it reads `.pre-commit.d/`.

## Questions, in order

1. `project_name` -- written into the `cog.toml` header comment. Thread the value you already collected for `base`.
2. `layout` -- `single` or `monorepo`. `monorepo` adds `generate_mono_repository_global_tag = false` and a `[monorepo.packages]` table.
3. `monorepo_packages` -- a YAML list of package directories relative to the repo root, such as `[packages/api, packages/web]`. Pass the directories you rendered language packages into. Leave it `[]` for a single-package repo.

Each entry becomes one `[monorepo.packages]` row with `path` and
`changelog_path` set, keyed on the directory with `/` replaced by `-`.

## What does not happen

No task runs `cog bump`, `cog changelog`, or creates a tag. Rendering touches no
network and reads no commit history.

The two `_tasks` entries check for `mise` and run `mise install` to fetch `cog`.
Both exit 0 on failure, so a missing `mise` leaves the rendered files in place.

## After rendering

The keys written here match cog 7.x. Tell the user to run `cog check` to validate
their commit history, then `cog bump --auto` when they want the first release.
