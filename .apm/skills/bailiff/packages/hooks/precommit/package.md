---
name: precommit
summary: pre-commit as the git hook manager, with a fragment merge step
provides: [hooks:manager]
after: [base, python, ts, go, rust, cocogitto]
requires_bin: [pre-commit, git, python3]
---

## Renders

| Path | Contents |
|---|---|
| `.pre-commit.d/precommit.yaml` | baseline hooks: whitespace, EOF, yaml/toml syntax, merge conflicts, large files, gitleaks, shellcheck, and the two optional hooks below |
| `.pre-commit-hooks/check-commit-msg.py` | Conventional Commits validator, referenced as a `local` hook when `enforce_conventional_commits` is true |
| `.pre-commit-config.yaml` | written by the merge task, not by the template |
| `.copier-answers.precommit.yml` | the answers |

## The merge step is required

pre-commit reads one file, `.pre-commit-config.yaml`. It has no include or
extends directive: an `include:` key at the root produces
`[WARNING] Unexpected key(s) present at root: include` and the referenced hooks
never run. So `tasks/merge_precommit.py` runs as the first `_tasks` entry, reads
every `.pre-commit.d/*.yaml`, deduplicates repos by URL and hooks by id, and
writes `.pre-commit-config.yaml` sorted by repo URL. On a rev-pin conflict for
one repo URL the highest rev wins and the script warns on stderr. The script
writes nothing when no fragment exists.

The generated file is derived. A user who edits it loses the edit on the next
render; the edit belongs in a `.pre-commit.d/` fragment.

## Ask

In this order:

1. `enforce_conventional_commits` (bool, default true) -- adds the commit-msg
   hook running `.pre-commit-hooks/check-commit-msg.py`.
2. `enable_typo_check` (bool, default true) -- adds `crate-ci/typos`.
3. `precommit_exclude_patterns` (yaml list, default `[]`) -- regexes joined with
   `|` into the config's top-level `exclude`. Ask when the repo holds vendored or
   generated trees the hooks should skip.
4. `install_hooks` (bool, default true) -- runs `pre-commit install`. Answer
   false when the destination is not a git repository yet.

## Destination must be a git repository

`pre-commit install` fails outside a git work tree. Run `git init` first, or
answer `install_hooks: false` and tell the user to run `pre-commit install`
themselves.

## After rendering

Language packages write their own `.pre-commit.d/<package>.yaml` fragments, each
a mapping with a top-level `repos:` list. Render this package after them so the
merge picks their fragments up. Re-rendering it is how a later fragment reaches
`.pre-commit-config.yaml`.

Verify with `pre-commit run --all-files`.
