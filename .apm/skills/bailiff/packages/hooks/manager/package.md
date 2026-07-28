---
name: manager
summary: The git hook manager, one of lefthook, pre-commit, or prek
provides: [hooks:manager]
after: [base, baseline, python, ts, go, rust, cocogitto]
requires_bin: [git]
---

## Renders

| Path | Contents |
|---|---|
| `lefthook.yml` | `extends: [.hooks.d/*.yaml]` and nothing else. Only when `hook_manager: lefthook` |
| `.pre-commit-config.yaml` | written by the merge task from `.pre-commit.d/`. Only when `hook_manager` is `pre-commit` or `prek` |
| `.copier-answers.manager.yml` | the answers |

It renders no hook definitions. Those come from `../baseline/package.md` and from
the language packages, in both schemas, so the manager choice does not change
what the hooks check.

## The choice is a question, not three packages

Each manager writes `.git/hooks/`, so whichever installs last wins. A single
`hook_manager` answer makes that exclusive by construction. A package per manager
made it exclusive by convention, and nothing enforced the convention.

## Ask

In this order:

1. `hook_manager` (`prek`, `lefthook`, `pre-commit`; default `prek`).
2. `install_hooks` (bool, default true) -- runs the manager's install command.
   Answer false when the destination is not a git repository yet.

| Answer | Reads | Install command | Needs |
|---|---|---|---|
| `prek` | `.pre-commit-config.yaml`, written by the merge task | `prek install` | a Rust binary, no Python |
| `lefthook` | `.hooks.d/*.yaml`, glob expanded by lefthook itself | `lefthook install` | a Go binary, no Python |
| `pre-commit` | the same file `prek` reads | `pre-commit install --install-hooks` | Python |

Default to `prek`. It reads pre-commit's config format unchanged, so the whole
pre-commit hook ecosystem works against it, and it needs no Python runtime.
Answer `pre-commit` when the user asks for it by name.

Pick `lefthook` when the user wants hooks that run the project's own commands
against staged files rather than hooks installed from pinned upstream repos.

`requires_bin` names only `git`. The manager binary depends on the answer, which
frontmatter cannot express, so a missing one surfaces as a failed install task
rather than as a precheck. Tell the user to run the install command after
installing the tool.

## The merge step, for pre-commit and prek only

Neither has an include directive: an `include:` key at the root produces
`[WARNING] Unexpected key(s) present at root: include` and the referenced hooks
never run. So `tasks/merge_precommit.py` runs first, reads every
`.pre-commit.d/*.yaml`, deduplicates repos by URL and hooks by id, and writes
`.pre-commit-config.yaml` sorted by repo URL. On a rev-pin conflict for one repo
URL the highest rev wins and the script warns on stderr.

The generated file is derived. A user who edits it loses the edit on the next
render; the edit belongs in a `.pre-commit.d/` fragment.

`lefthook` needs no merge. It expands `extends: [.hooks.d/*.yaml]` at hook time,
so a fragment written after this package renders still takes effect.

## Destination must be a git repository

Every install command fails outside a git work tree. Run `git init` first, or
answer `install_hooks: false` and tell the user which command to run.

## Ordering

Render this package last of the hook packages, after `baseline` and after every
language package. The merge runs at render time for `pre-commit` and `prek`, so a
fragment written afterwards does not reach the config until this package
re-renders.

## After rendering

Verify with the manager's own command: `lefthook dump`, or
`pre-commit run --all-files`, or `prek run --all-files`. `lefthook validate` and
`prek validate-config` check the config without running the hooks.
