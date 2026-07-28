# Runbook: retrofit an existing repo

A repo with `.git` and source already in it. The project's shape is a fact you
read, not a decision you make. Add what is missing without overwriting what works.

## Rules

1. **Take every answer the repo already carries from `probe.py`.** It reports
   `languages`, `package_managers`, `version_files`, `hook_managers`, `ci_hosts`,
   `git.default_branch`, and `rendered_packages`. Asking the user for one of these
   invites a wrong answer about their own repo.
2. **State what you found and have the user confirm it.** Detection is evidence.
   A `pyproject.toml` in a repo whose real work is TypeScript proves nothing.
3. **Stop on `git.dirty`.** Ask the user to commit or stash first. Copier passes
   `overwrite=True`, so a render over a dirty tree leaves no diff to undo.
4. **`--pretend` every package before rendering it.** For each path it lists that
   already exists, name that path and ask. "This would replace your
   `.pre-commit-config.yaml`" is actionable; "this may overwrite files" is not.
5. **Skip the package when the user keeps the existing file.** Do not render it and
   then restore the file from git.
6. **Offer the gaps only.** A repo with `.pre-commit-config.yaml` already has a
   hook manager, so `hooks` has nothing to add unless the user wants to switch.
7. **Never fold a version upgrade into setup.** When the repo runs Python 3.11, put
   `3.11` in the answers file. Upgrading is a separate change with its own testing.

## The pretend check

```sh
python3 "$SKILL_DIR/scripts/render.py" <group>/<package> <dest> --answers <file> --pretend
```

## Identity when you skip base

`rendered_packages` says whether `base` already ran here. When it did not and the
user does not want it, take `project_name`, `org`, and `description` from the repo
itself: its README, its manifest, and `git.remote`. Confirm all three before
threading them into other packages' answers files.

## Verification

The core loop's verification is not enough here, because rendered hook and lint
configuration runs against code that predates it. Add:

- The hook manager's run-all command, when you rendered one.
- The lint command the language package names.

A failure on pre-existing code is the user's choice to resolve: fix the code, or
loosen the rendered config. Do not loosen it on their behalf.
