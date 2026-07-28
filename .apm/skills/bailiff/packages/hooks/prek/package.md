---
name: prek
summary: prek as the git hook manager, reading the pre-commit config format
provides: [hooks:manager]
after: [base, python, ts, go, rust, cocogitto]
requires_bin: [prek, git, python3]
---

## Renders

| Path | Contents |
|---|---|
| `.pre-commit.d/prek.yaml` | baseline hooks: whitespace, EOF, yaml/toml syntax, merge conflicts, large files, gitleaks, shellcheck, and the two optional hooks below |
| `.pre-commit-hooks/check-commit-msg.py` | Conventional Commits validator, referenced as a `local` hook when `enforce_conventional_commits` is true |
| `.mise/conf.d/prek.toml` | pins `prek = "latest"` for mise, which resolves it through `aqua:j178/prek` |
| `.pre-commit-config.yaml` | written by the merge task, not by the template |
| `.copier-answers.prek.yml` | the answers |

## prek reads pre-commit's config format

`prek` is a Rust reimplementation of `pre-commit` and reads the same
`.pre-commit-config.yaml`, so every `.pre-commit.d/` fragment in the catalog
works unchanged.

It has no include directive either, so `tasks/merge_precommit.py` runs first and
writes `.pre-commit-config.yaml` from the fragments, exactly as it does for the
`precommit` package.

Verify the merged file with `prek validate-config`.

## Ask

In this order:

1. `enforce_conventional_commits` (bool, default true) -- adds the commit-msg
   hook running `.pre-commit-hooks/check-commit-msg.py`.
2. `enable_typo_check` (bool, default true) -- adds `crate-ci/typos`.
3. `precommit_exclude_patterns` (yaml list, default `[]`) -- regexes joined with
   `|` into the config's top-level `exclude`. Ask when the repo holds vendored or
   generated trees the hooks should skip.
4. `install_hooks` (bool, default true) -- runs `prek install`, which writes the
   git shims. Answer false when the destination is not a git repository yet.

## Destination must be a git repository

`prek install` writes into Git's effective hooks directory and fails outside a
work tree. Run `git init` first, or answer `install_hooks: false` and tell the
user to run `prek install` themselves.

## After rendering

Language packages write their own `.pre-commit.d/<package>.yaml` fragments, each
a mapping with a top-level `repos:` list. Render this package after them so the
merge picks their fragments up. Re-rendering it is how a later fragment reaches
`.pre-commit-config.yaml`.

Verify with `prek run --all-files`.
