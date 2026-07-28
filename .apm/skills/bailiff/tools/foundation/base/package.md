---
name: base
summary: Project identity -- AGENTS.md, docs/tests/scripts skeleton, .gitignore, LICENSE, git init
provides: [scaffold:identity]
requires_bin: [git]
---

`base` holds the identity answers every other package reuses. Render it first,
then pass `project_name`, `org`, `description`, `layout`, and `default_branch`
into each later answers file unchanged.

## What it renders

| Path | Contents |
|---|---|
| `AGENTS.md` | Heading, description, path map, repo line. Not overwritten when it exists. |
| `docs/.gitkeep` | Always. |
| `docs/architecture/`, `docs/decisions/`, `docs/runbooks/` | When `docs_subdirs` is true. |
| `tests/.gitkeep`, `scripts/.gitkeep` | Always. |
| `<dir>/.gitkeep` per `extra_dirs` entry | Created by a task, not by the template. |
| `.gitignore` | Written by a task through `gitnr`. Left alone when it exists. |
| `LICENSE` | Written by a task through `gh api`. Left alone when it exists. |
| `.copier-answers.base.yml` | The answers, for later reference. |

## Question order

Ask in this order. Each answer feeds the ones below it.

1. `project_name` -- the AGENTS.md heading and the repo line. In a monorepo
   package directory, answer the package name.
2. `org` -- owner. Becomes the `copyright_name` default.
3. `description` -- one line under the heading. An empty answer leaves a
   placeholder comment for you to fill after the interview.
4. `layout` -- `single` or `monorepo`. `monorepo` renders a Packages table in
   AGENTS.md instead of a path map.
5. `default_branch` -- passed to `git init --initial-branch`, and reused by the
   CI and repo-host packages.
6. `license` -- SPDX id from the choice list, or `none` to write no LICENSE.
7. `copyright_name` -- accept the `org` default unless the legal holder differs.
8. `branch_strategy` -- one guidance line in AGENTS.md.
9. `docs_subdirs` -- the three `docs/` subdirectories.
10. `extra_dirs` -- a YAML list of directories to create with a `.gitkeep`. In a
    monorepo, answer the package roots the user named in the interview, for
    example `[packages, apps]`. The monorepo runbook collects those paths; use
    them here rather than a fixed set.
11. `run_git_init` -- answer false for a destination that is already a git repo.

## Tasks

Copier runs these after the render, in this order.

| Task | Requires | On failure |
|---|---|---|
| `tasks/gitignore.sh` | `gitnr` on PATH | Exits 0 with a stderr note; no `.gitignore`. |
| `tasks/license.sh` | `gh` on PATH and authenticated | Exits 0 with a stderr note; no `LICENSE`. |
| `git init --initial-branch <default_branch>` | `git` | Aborts the render. |
| `mkdir` per `extra_dirs` entry | none | Aborts the render. |

`gitnr` and `gh` are best-effort by design. Copier's `cleanup_on_error` deletes
every rendered file when a task exits non-zero, so a missing binary or an offline
`gh api` call must not fail the task. Both scripts exit 0 and report on stderr.
Read that stderr after the render: when it says no `.gitignore` or no `LICENSE`
was written, tell the user and offer to write the file yourself.

`git` is the one mandatory binary, so `requires_bin` names it and `render.py`
exits 3 when it is absent.

## After rendering

- Fill the `AGENTS GUIDANCE`, `ARCHITECTURE`, and `BUILD COMMANDS` placeholder
  comments in `AGENTS.md` once the language and CI packages have rendered and
  their commands are known.
- In a monorepo, fill the Packages table as each package lands.
- Check whether `.gitignore` and `LICENSE` exist.
