---
name: bailiff
description: Set up, scaffold, bootstrap, or initialize a project or repository in any language. Use when the user wants to start a new project, service, API, app, or repo ("set up a project", "spin up a FastAPI service", "scaffold a repo", "initialize a repo"), retrofit tooling onto an existing repo, add a package to a monorepo, or set up related repos that share conventions. Interviews the user, then drives copier to render packages grouped by choice axis. Setup only. Reproduce and update belong to copier.
---

# bailiff

Role: interviewer and render driver.

- The catalog is authoritative for what exists; never name a package from memory.
- Deterministic facts come from the scripts. Reasoning is yours: what to offer,
  what to recommend, and what the user meant.
- Setup only. Reproduce, update, and upgrade belong to `copier` itself.

## Core rules

1. **Scan before you offer.** `scripts/scan.py` reports every package, axis, and
   question. A package, group, choice, or default you did not read from it does
   not exist.
2. **Probe before you route.** `scripts/probe.py <dest>` reports what the
   destination already is. Never infer the scenario from the user's wording alone,
   and never run the filesystem reads by hand.
3. **Derive the order.** `scripts/scan.py --order <picks>` returns the render
   sequence. Never hand-sort it and never carry a sequence from a previous
   session; `after:` in each package is the only ordering source.
4. **One question at a time.** Ask, wait for the answer, ask the next. A wall of
   questions violates the contract.
5. **Read `package.md` on pick, not before.** The catalog `summary` is enough to
   offer a package. Its steering loads once the user picks it.
6. **The user's pick wins.** Offer, recommend, state constraints. Never
   substitute your preference for a stated choice, and never re-offer a rejected
   package.
7. **Answers go in a file, one per package.** `--answers <file>`. There is no
   `--data` flag. Never put a secret in one.
8. **Never hand-edit rendered output to fix a template.** Fix the answer and
   re-render, or tell the user the template needs a change.
9. **Never render over uncommitted work.** `probe.py` reports `git.dirty`. True
   means stop and ask the user to commit or stash first; copier passes
   `overwrite=True`, so there is no diff to review afterward.
10. **Report what happened, not what should have.** Name every file written,
    every task that ran, and every command that failed with its output.

## Invocation

`$SKILL_DIR` is the directory holding this file. Requires `python3` with
`copier>=9.16`, `python-frontmatter`, and `pyyaml`; on an import error tell the
user to run `uv sync` in the bailiff repo.

| Command | Answers |
|---|---|
| `python3 "$SKILL_DIR/scripts/probe.py" <dest>` | What is the destination already? |
| `python3 "$SKILL_DIR/scripts/scan.py"` | What packages exist, with what questions? |
| `python3 "$SKILL_DIR/scripts/scan.py" --order <picks>` | In what order do these render? |
| `python3 "$SKILL_DIR/scripts/render.py" <group>/<package> <dest> --answers <file>` | Render one package |
| add `--pretend` | List what would be written, writing nothing |

`render.py` exit codes: `0` rendered, `2` usage or unknown package, `3` precheck
or missing executable, `4` render failure. `scan.py --lint-only` exits 1 on a
contract violation.

## Pick the scenario

Run `probe.py`, then decide. It reports `scenario.suggested` and
`scenario.ask_intent`.

| `ask_intent` | What to do |
|---|---|
| `false` | State the suggestion, confirm it in one question, proceed |
| `true` | The markers cannot settle it. Ask the intent question below |

The intent question, asked verbatim when `ask_intent` is true:

> One project, several packages in one repo, or several separate repos?

| Answer | Runbook |
|---|---|
| One project | `runbooks/new-project/index.md` |
| Several packages, one repo | `runbooks/monorepo/index.md` |
| Several separate repos | `runbooks/polyrepo/index.md` |
| (probe says `existing-repo`) | `runbooks/existing-repo/index.md` |

An empty directory carries no marker, so a fresh monorepo and a single project
look identical to `probe.py`. Never route an empty directory to `new-project`
without asking. Load exactly one runbook; each one delegates when the answer
turns out to be a different shape.

## The core loop

Every scenario runs this. The runbook supplies the interview order, what to
recommend, and the destination per package.

1. **Probe and route.** Above.
2. **Scan.** `scan.py`. Groups, axes, packages, questions.
3. **Visit each group the runbook names.** Read `packages/<group>/index.md` for
   how its axes behave: one pick, at most one, many, or one per package.
4. **Offer and collect.** Present the axis's packages with their summaries, one
   question at a time.
5. **Read the steering of each pick.** Its `package.md` states what to ask, in
   what order, and what each answer changes.
6. **Interview.** Per "Asking questions" below.
7. **Order.** `scan.py --order <every pick>`. Act on its `notes`: an unmet
   `depends_on` is a question for the user, not something to resolve silently.
8. **Render.** Write one answers file per package, then `render.py` per package
   in the derived order. Exit 3 names a missing executable; give the user the
   install command and stop.
9. **Compose what packages cannot render.** CI callers are yours to write. See
   `packages/ci/index.md`.
10. **Verify and report.** Run `git -C <dest> status --short`. Then run the
    project's own check, whatever the language package named: the workspace
    resolve, the install, the test command, the lint. Report its real output. A tree that renders is not a project that builds.

## Asking questions

The catalog carries each question's `type`, `choices`, `default`, and `help`.
That is the question; you are presenting it, not writing it.

| Rule | Why |
|---|---|
| Offer `choices` verbatim and in catalog order | An answer outside the list fails the render with exit 4 |
| Never invent an option, and never omit one | The list is the closed set the template branches on |
| State the `default` and let the user take it | Most defaults are the recommended answer |
| Ask a `multiselect` as one question, not one per choice | It returns a list; asking per choice is the wall rule 4 forbids |
| Take an answer the repo already contains from the repo | `probe.py` reports languages, package managers, and versions |
| Read a destructive or public answer back before rendering | `visibility: public` publishes a repo the moment `gh repo create` runs |
| Skip a question whose `when:` is false for the answers so far | Asking it wastes attention on a value nothing reads |

A question with no `choices` is free-form; say what shape the value takes rather
than leaving the user to guess.

## Answers files

One YAML file per package, keyed by the catalog's question keys.

```yaml
# /tmp/bailiff-answers-python.yml
project_name: acme
python_version: "3.13"
python_pkg_manager: uv
```

Packages never read each other's answers. When two ask for `project_name`, put
the same value in both files -- threading shared values is your job. In a monorepo
`project_name` is the package's name, not the repo's.

A question marked `secret` never goes in the file. Tell the user to supply it out
of band and leave the key absent.

## Steering-only packages

A package with `renders: false` ships no template; its `package.md` states what
to author yourself. `render.py` reports it and writes nothing.
