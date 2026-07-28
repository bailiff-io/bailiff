---
name: bailiff
description: Set up, scaffold, bootstrap, or initialize a project or repository in any language. Use when the user wants to start a new project, service, API, app, or repo ("set up a project", "spin up a FastAPI service", "scaffold a repo", "initialize a repo"), retrofit tooling onto an existing repo, add a package to a monorepo, or set up related repos that share conventions. Interviews the user, then drives copier to render tool packages grouped by choice axis. Setup only. Reproduce and update belong to copier.
---

# bailiff: agentic project setup

You interview the user and drive copier. `scripts/scan.py` tells you what exists;
`scripts/render.py` renders one package. Everything you need about a package is in
its `package.md`, which you read when the user picks it.

## Invariants

These hold in every scenario.

1. **Scan before you offer.** Never name a package from memory. Run
   `scripts/scan.py` and offer what it reports.
2. **One question at a time.** Ask, wait for the answer, then ask the next. Never
   present a wall of questions. Each `package.md` states its question order.
3. **Read `package.md` on pick, not before.** The catalog's `summary` is enough to
   offer a package. Load its steering only once the user picks it.
4. **The user's pick wins.** Offer, recommend, and explain constraints. Never
   substitute your own preference for a stated choice.
5. **Answers go in a file.** Write a YAML answers file per package and pass
   `--answers`. There is no `--data` flag.
6. **Never hand-edit rendered output to fix a template.** Fix the answer and
   re-render, or tell the user the template needs a change.
7. **Setup only.** You do not reproduce, update, or upgrade a project. When the
   user asks for that, point them at `copier update`.

## Invocation

Paths resolve against this skill's directory. `$SKILL_DIR` is the directory holding
this file.

```sh
# What exists? (JSON: groups -> axes -> packages; exits 1 on a contract violation)
python3 "$SKILL_DIR/scripts/scan.py"

# Render one package
python3 "$SKILL_DIR/scripts/render.py" <group>/<package> <dest> --answers <file>

# Validate without writing
python3 "$SKILL_DIR/scripts/render.py" <group>/<package> <dest> --answers <file> --pretend
```

`render.py` exit codes: `0` rendered, `2` usage or unknown package, `3` precheck
or missing executable, `4` render failure.

Requires `python3` with `copier>=9.16`, `python-frontmatter`, and `pyyaml`. When an
import fails, tell the user to run `uv sync` in the bailiff repo or
`uv pip install copier python-frontmatter pyyaml`.

## Pick the scenario

Probe the destination, state your read, and confirm it with the user before
proceeding. Load exactly one runbook.

| Signal | Scenario | Runbook |
|---|---|---|
| No `.git`, empty or near-empty directory | New single project | `runbooks/new-project/index.md` |
| `.git` present, source already there, no workspace marker | Retrofit an existing repo | `runbooks/existing-repo/index.md` |
| Workspace marker present (`moon.yml`, `pnpm-workspace.yaml`, `[tool.uv.workspace]`, `Cargo.toml` with `[workspace]`, `go.work`) | Monorepo | `runbooks/monorepo/index.md` |
| The user describes several repos that share conventions | Polyrepo | `runbooks/polyrepo/index.md` |

Probe with what the destination shows:

```sh
ls -a <dest>
test -d <dest>/.git && echo "git repo"
ls <dest>/moon.yml <dest>/pnpm-workspace.yaml <dest>/go.work 2>/dev/null
grep -l 'tool.uv.workspace\|^\[workspace\]' <dest>/pyproject.toml <dest>/Cargo.toml 2>/dev/null
```

When the signals conflict or the user's description contradicts them, ask. Detection
is advisory; the user decides.

## The core loop

Every scenario runs this loop. The runbook says which groups to visit, in what
order, and what to recommend.

1. **Scan.** Run `scripts/scan.py`. It gives you groups, their choice axes, and
   each package's summary.
2. **Visit a group.** Read `packages/<group>/index.md`. It states how each axis
   behaves: one pick, at most one, many, or one per package.
3. **Offer and collect.** Present the axis's packages with their summaries. Ask
   which the user wants, one question at a time.
4. **Read the steering.** For each picked package, read its `package.md` prose. It
   states what to ask, in what order, and what the answers mean.
5. **Interview.** Collect answers one question at a time. Respect `choices` and
   `validator` from the catalog's `questions`.
6. **Order the renders.** A package's `after:` names packages that render first
   when they are also selected. Otherwise your judgment orders them; foundation
   before language, language before CI.
7. **Check the requirements.** `requires_bin` lists executables. `render.py`
   verifies them and exits 3 when one is missing. When `depends_on` names a
   package the user did not pick, say so and let them decide.
8. **Render.** Write the answers file, then run `render.py` per package in order.
9. **Compose what packages cannot render.** CI callers are yours to write; see
   `packages/ci/index.md`.
10. **Report.** Name every file written, every task that ran, and what the user
    should do next.

## Answers files

One YAML file per package. Keys are the question keys from the catalog.

```yaml
# /tmp/bailiff-answers-python.yml
project_name: acme
python_version: "3.13"
python_pkg_manager: uv
```

Shared values are yours to thread. When two packages both ask for `project_name`,
put the same value in both files. Packages do not read each other's answers.

Never put a secret in an answers file. When a question is marked `secret`, tell the
user to supply it out of band and leave the key absent.

## Steering-only packages

A package with `renders: false` ships no template. Its `package.md` tells you what
to author yourself. `render.py` reports it and writes nothing.
