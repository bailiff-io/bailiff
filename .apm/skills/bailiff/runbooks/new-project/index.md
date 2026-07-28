# Runbook: new single project

One project, in an empty or near-empty directory. The user decides the project's
shape; there is no repo to read it from.

## Before the interview

`probe.py` cannot tell this scenario from a fresh monorepo, so confirm the shape
before spending questions on it.

| The user says | Go to |
|---|---|
| Several packages sharing one repo and one history | `../monorepo/index.md` |
| Several repos sharing conventions | `../polyrepo/index.md` |
| One project | continue here |

A second package arriving later is not this runbook's problem. Rendering a single
project and converting it to a workspace afterwards costs less than setting up a
workspace nobody needs.

## Interview order

Each answer narrows what you offer next.

| # | Ask | Why here |
|---|---|---|
| 1 | What is this project, in one sentence | Becomes `description`, and tells you which groups are worth offering |
| 2 | `project_name` and `org` | Every other package takes them from `base` |
| 3 | Language, from what `scan.py` reports under `languages` | Decides which CI job packages exist |
| 4 | The language package's own questions | Version and package manager, `choices` verbatim |
| 5 | Repo host, and whether the remote is created now | `visibility: public` publishes on render |
| 6 | Whether the project needs CI at all | A no here skips the whole `ci` group |
| 7 | Each remaining group in `scan.py` order | State what it gives them, accept a no |

Step 7 takes the group list from the scan, not from a list here. A group added to
the catalog is offered without editing this file.

## Render order

`scan.py --order <picks>` gives it. Do not sort by hand.

A framework scaffold is the one exception. `create-vite` and `nuxi init` refuse a
directory that holds files, so they run before `foundation/base` rather than in
the derived order: scaffold into the empty destination, then render `base` and the
language package over the result. `packages/languages/ts/package.md` carries the
commands and their non-interactive flags. `ts_framework: sst` has no
non-interactive path; tell the user to run `npx sst@4 init` and continue once they
have.

## What to recommend

| Group | Recommend for a new project |
|---|---|
| `foundation` | base, readme, editorconfig |
| `hooks` | lefthook |
| `ci` | The host they chose, plus test and lint for their language |
| `repo` | The host, and dep-updates with renovate |
| `agentic` | agentic, when they say they use coding agents |
| `iac`, `docs` | Nothing unprompted |

A new project has no infrastructure to describe and no audience to document for.

## Closing

Beyond the core loop's verify-and-report: the rendered tree holds no commit. Say
so, and leave the first commit to the user unless they ask you to make it.
