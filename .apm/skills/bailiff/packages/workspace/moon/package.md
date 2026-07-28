---
name: moon
summary: moon workspace config for cross-language task orchestration
provides: [workspace:monorepo]
after: [base]
---

## Renders

| Path | Contents |
|---|---|
| `.moon/workspace.yml` | the project map and the vcs block |
| `.mise/conf.d/moon.toml` | pins `moon = "latest"` for mise |
| `.copier-answers.moon.yml` | the answers |

The mise fragment means `mise install` in the destination brings moon in. This
package runs no task and needs no binary.

## Ask

In this order:

1. `layout` (`monorepo` or `single`, default `monorepo`) -- `monorepo` writes a
   multi-project map, `single` writes `root: '.'`. Pass the layout the user
   already described rather than asking again.
2. `monorepo_packages` (yaml list, default `[]`) -- explicit package paths, for
   example `['packages/api', 'apps/web']`. Each path's last segment becomes the
   moon project name. An empty list falls back to globs over `apps/*`,
   `packages/*`, `services/*`, and `libs/*`. Skip this question when
   `layout: single`.
3. `default_branch` (default `main`) -- the branch moon diffs against for
   affected-target detection.

## moon on a single-package repo

`layout: single` renders a valid one-project workspace. moon works as a task
runner there, and the affected-target detection that motivates it has one
project to compare. Say so before rendering it into a single-package repo.

## After rendering

`.moon/tasks.yml` and each project's `moon.yml` hold the task definitions. This
package writes neither. Author them against the project's real commands, or run
`moon init` in the destination for moon's own starting point.
