# Runbook: retrofit an existing repo

A repo with `.git` and source already in it. The project's shape is a fact you
read, not a decision you make. Your job is adding the tooling that is missing
without overwriting what works.

## Read before you ask

Establish the shape from the repo, and ask only what the repo cannot tell you.

```sh
git -C <dest> status --short
git -C <dest> log --oneline -5
ls -a <dest>
ls <dest>/.copier-answers.*.yml 2>/dev/null
```

| Question | Where the answer is |
|---|---|
| Languages present | manifests: `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml` |
| Package manager | lockfile: `uv.lock`, `pnpm-lock.yaml`, `poetry.lock` |
| Runtime version | `.python-version`, `engines` in `package.json`, `go.mod`, `rust-toolchain.toml` |
| Hook manager | `.pre-commit-config.yaml`, `lefthook.yml` |
| CI host | `.github/workflows/`, `.gitlab-ci.yml` |
| Default branch | `git symbolic-ref refs/remotes/origin/HEAD` |
| Bailiff already ran | `.copier-answers.*.yml` files |

State what you found and ask the user to confirm it. Detection is evidence, not
truth: a `pyproject.toml` in a repo whose real work is TypeScript proves nothing.

## The uncommitted-work check

Run this first, before any render:

```sh
git -C <dest> status --porcelain
```

Non-empty output means uncommitted changes. Say what is uncommitted and ask the
user to commit or stash before you render. Rendering over a dirty tree leaves them
no diff to review and no way to undo one package's output.

## Do not overwrite

`render.py` passes `overwrite=True`, so copier writes over an existing file
without asking.

Before rendering a package, list the files it would write:

```sh
python3 "$SKILL_DIR/scripts/render.py" <group>/<package> <dest> --answers <file> --pretend
```

For every path that already exists in the repo, say so and ask before proceeding.
Name the specific file. "This would replace your `.pre-commit-config.yaml`" is
actionable; "this may overwrite files" is not.

When the user wants to keep the existing file, skip that package. Do not render it
and then restore the file from git.

## What to offer

Offer the gaps. A repo with `.pre-commit-config.yaml` already has a hook manager,
so `hooks/` has nothing to add unless the user wants to switch.

Answer language questions from what the repo already uses. When the repo runs
Python 3.11, put `3.11` in the answers file. Do not offer to upgrade it as part of
setup; that is a separate change with its own testing.

## Render order

Same as a new project, minus what already exists. When you skip `base`, take
`project_name`, `org`, and `description` from the repo (its README, its manifest,
its remote URL) and confirm them with the user before threading them onward.

## After rendering

```sh
git -C <dest> status --short
git -C <dest> diff --stat
```

Report every path written and every path changed. Then run the repo's own checks,
because new hook and lint configuration can fail against existing code:

- The hook manager's run-all command, when you rendered one.
- The lint command the language package names.

When a check fails on pre-existing code, say so and give the user the choice: fix
the code, or loosen the rendered config. Do not silently loosen it.
