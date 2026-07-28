---
title: bailiff v2 architecture
status: Accepted
date: 2026-07-28
supersedes: bailiff v1 (archived at bailiff-io/bailiff-v1, tag archive/v1)
---

# bailiff v2 architecture

bailiff sets up projects. An agent interviews the user, then picks tool packages
from a grouped catalog and drives copier to render them. Setup is the whole scope.

## Scope

| In | Out |
|---|---|
| Scaffolding a new project | Reproducing a project from committed answers |
| Retrofitting tools onto an existing repo | Upgrading a project to a newer template version |
| Adding a package to a monorepo | Deploying or releasing |
| Composing CI from deterministic units | Guaranteeing byte-identical re-renders |

Copier writes `.copier-answers.<package>.yml` into every project it touches.
bailiff builds nothing on those files. A user who wants `copier update` runs it
directly.

## Repository layout

bailiff is a single-skill APM package. Assets live at the repository root.

```
apm.yml
.apm/skills/bailiff/
  SKILL.md                      # trigger, scenario dispatch, invariants
  runbooks/
    new-project/index.md
    existing-repo/index.md
    polyrepo/index.md
    monorepo/index.md           # dispatches to the two below
    monorepo/setup/index.md
    monorepo/add-package/index.md
  scripts/
    scan.py                     # emits the catalog as JSON
    render.py                   # precheck, then copier.run_copy
  tools/
    <group>/
      index.md                  # selection semantics per axis
      <package>/
        package.md              # frontmatter contract + steering prose
        copier.yml              # optional; questions may be empty
        template/               # optional
        tasks/                  # optional; scripts referenced from _tasks
        precheck                # optional executable
```

Every directory that discloses progressively carries an `index.md`, so a scenario
or group grows sub-levels without a restructure.

## Progressive disclosure

The agent loads one file per level and never the whole tree.

| Level | File | Loaded when |
|---|---|---|
| Scenario | `runbooks/<scenario>/index.md` | The agent identifies the repo shape |
| Group | `tools/<group>/index.md` | The agent considers that group's axis |
| Package | `tools/<group>/<package>/package.md` | The user picks that package |

`SKILL.md` carries the dispatch table and the invariants. It does not carry
procedure detail for any scenario.

## Tool package contract

`package.md` frontmatter is the machine-readable manifest. Prose below the
frontmatter is steering the agent reads on pick.

```yaml
---
name: python                    # MUST equal the directory name
summary: Python overlay -- uv/pdm, ruff, mise, pytest
provides: [language:python]     # key:value tags; the namespace is the choice axis
after: [base]                   # soft ordering; applies only if also selected
depends_on: []                  # hard requirement; scan warns when unmet
requires_bin: [uv]              # executables checked before render
precheck: null                  # script path for checks beyond binaries
---
```

Acceptance criteria:

- Given a package whose `name` differs from its directory name, `scan.py` lists it under `lint` and exits non-zero.
- Given an `after:` or `depends_on:` entry naming a package that does not exist, `scan.py` lists it under `lint` and exits non-zero.
- Given a package directory with no `package.md`, `scan.py` lists it under `lint` and exits non-zero.
- `scan.py` sets `renders: true` for a package with a `copier.yml` and `renders: false` for a package without one.
- Given an unmet `depends_on`, `render.py` prints a warning and renders.

### Package shapes

| Shape | Contents | Example |
|---|---|---|
| Rendering | `copier.yml` + `template/` | `editorconfig` |
| Rendering, no questions | `copier.yml` with only `_subdirectory` | `ci/github-test-python` |
| Steering only | `package.md` alone | a package whose output the agent authors |

Copier renders a template whose `copier.yml` declares zero questions. Multiple
packages render into one destination without collision when each passes its own
`answers_file`.

## Groups and axes

A package lives in exactly one group directory. Its `provides:` tag namespace
names the choice axis. The group's `index.md` states what to do with each axis.

| Group | Axes | Packages |
|---|---|---|
| `foundation/` | `scaffold:*` | base, readme, editorconfig |
| `languages/` | `language:*` | python, ts, go, rust, api |
| `hooks/` | `hooks:manager` | lefthook, precommit |
| `ci/` | `ci:*`, `ci-job:*` | github, github-python, github-ts, github-go, github-rust, github-security |
| `repo/` | `repo:*`, `release:*`, `deps:*` | github-repo, gitlab-repo, cocogitto, release-please, dep-updates |
| `docs/` | `docs:*` | mkdocs, decision-records |
| `iac/` | `iac:*` | terraform, cdk, cloudformation |
| `agentic/` | `agentic:*`, `tracker:*` | apm, agentic, agent-hooks, beads |
| `workspace/` | `workspace:*` | moon, justfile, devcontainer, package-add |

A group holds as many axes as its members need. `repo/` holds three axes: the
repo host allows one pick, the release tool allows at most one, and dep-updates
is independent of both.

Exclusivity is prose in the group's `index.md`. Prose states "pick exactly one",
"pick one or more, and one per package in a monorepo", and the constraints
attached to each. A boolean field states only the first.

## CI composition

CI packages render deterministic units. The agent composes the caller.

| Artifact | Author | Path |
|---|---|---|
| Composite action | package render | `.github/actions/<name>/action.yml` |
| Reusable workflow | package render | `.github/workflows/wc-<name>.yml` |
| Caller workflow | agent | `.github/workflows/ci.yml` |

`ci/index.md` carries the per-language commands and the composition patterns:
job matrices, path-filtered jobs, parallel lint and test, needs graphs,
concurrency cancellation, OIDC over stored secrets, actions pinned by SHA. The
agent selects among them against the project the user described.

Acceptance criteria:

- Each CI package renders one composite action or one reusable workflow.
- No CI package renders `ci.yml`.
- A rendered reusable workflow declares `on: workflow_call`.

## Scripts

### scan.py

Reads every `package.md` frontmatter and every `copier.yml`, emits one JSON
document, and exits non-zero when the catalog violates the contract.

Output structure: groups, then axes, then packages. Each package carries `name`,
`summary`, `provides`, `after`, `depends_on`, `requires_bin`, `renders`, and the
`questions` that `scan.py` reads from its `copier.yml`. A `lint` block lists
contract violations.

Acceptance criteria:

- Rerunning `scan.py` over an unchanged tree produces byte-identical output.
- `scan.py` writes and reads no cache file.
- `scan.py` omits `questions` for a package that declares none.

### render.py

Renders one package into one destination.

```sh
python scripts/render.py <group>/<package> <dest> --answers <file>
```

Steps: run the package's `precheck` if present, then call
`copier.run_copy(package_dir, dest, data=answers, answers_file=".copier-answers.<package>.yml", unsafe=True, defaults=True)`.

Acceptance criteria:

- Given a `precheck` that exits non-zero, `render.py` writes no file to the destination.
- `render.py` accepts answers as a YAML or JSON file. It exposes no `--data key=value` flag.
- `render.py` passes `unsafe=True` on every invocation.
- Given a `_tasks` entry that exits non-zero, copier removes the rendered files (`cleanup_on_error`).

## Tasks

Each package's `_tasks` list in `copier.yml` names scripts under its `tasks/`
directory. Copier executes the list in written order and renders each command
with the answer context. Task commands read answers as jinja values or as
environment variables.

Copier runs every task after rendering. A check that must precede rendering goes
in the package's `precheck` script, which `render.py` runs first.

## Trust

`render.py` passes `unsafe=True`. Tool packages ship inside the bailiff package;
installing bailiff is the consent. Copier's `settings.yml` trust list stays
untouched.

## Interview behavior

The agent asks one question at a time and waits for the answer. `package.md`
steering states what to ask and in what order.

Acceptance criterion: every `package.md` that declares questions states an order
for them.

## v1 removals

| Removed | Replacement |
|---|---|
| `_external_data` cross-package reads | The agent passes shared values in the answers file |
| `depends_on` as hidden `when:false` answers | `depends_on` in `package.md` frontmatter |
| Catalog of remote template repos | Packages ship in the bailiff package |
| Trust CLI and consent recording | Install-time consent, `unsafe=True` |
| Ordering engine | `after:` metadata plus agent judgment |
| Reproduce and update commands | Copier's own `recopy` and `update` |
| 679-line `ci.yml` template | Deterministic units plus an agent-composed caller |

The `.gitignore.d/`, `.pre-commit.d/`, `.mise/conf.d/`, and `.hooks.d/` fragment
conventions carry over: each package writes one namespaced file rather than
editing a shared one, so two packages never contend for the same lines.

Only two of the four are read natively. mise reads `.mise/conf.d/`, and lefthook
reads `.hooks.d/` because `lefthook.yml` carries `extends: [.hooks.d/*.yaml]`.
The other two need a task, because neither consumer has an include directive:

| Directory | Merged by | Owner |
|---|---|---|
| `.mise/conf.d/` | mise, natively | -- |
| `.hooks.d/` | lefthook, via `extends` | -- |
| `.pre-commit.d/` | `tasks/merge_precommit.py` | `hooks/precommit` |
| `.gitignore.d/` | `tasks/fold_gitignore.py` | every contributing package |

A fragment is written in its consumer's own schema; the conventions share a
directory shape, not a format. lefthook reports `hooks: Value is array but
should be object` and then runs nothing when handed a pre-commit-shaped
fragment, so a fragment that lints clean as YAML can still be inert.

`fold_gitignore.py` ships as a byte-identical copy in each package that writes a
`.gitignore.d/` fragment, because a copier template cannot reference a sibling
package's files. It is idempotent and rewrites its own delimited block, so
render order does not matter and a re-render converges.
