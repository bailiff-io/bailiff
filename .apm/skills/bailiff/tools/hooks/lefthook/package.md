---
name: lefthook
summary: lefthook as the git hook manager, reading .hooks.d/ fragments
provides: [hooks:manager]
after: [base, python, ts, go, rust]
requires_bin: [lefthook, git]
---

## Renders

| Path | Contents |
|---|---|
| `lefthook.yml` | `extends: [.hooks.d/*.yaml]` and nothing else |
| `.copier-answers.lefthook.yml` | the answers |

lefthook expands the glob itself and merges every fragment it matches. No merge
step runs, and no file lists the fragments. `lefthook dump` prints the merged
config; `lefthook validate` checks it. A glob matching zero files is valid, so
rendering this package before any language package writes a fragment works.

## Ask

One question:

1. `install_hooks` (bool, default true) -- run `lefthook install`, which writes
   the hook scripts under `.git/hooks/`. Answer false when the destination is not
   a git repository yet.

## Destination must be a git repository

`lefthook install` fails outside a git work tree. Run `git init` first, or answer
`install_hooks: false` and tell the user to run `lefthook install` after the
first commit.

## After rendering

Language packages own their hooks. Each writes `.hooks.d/<package>.yaml` in
lefthook's own schema: a top-level stage key (`pre-commit`, `commit-msg`,
`pre-push`) holding `commands.<id>.run` and optionally `glob`. Render this
package after them so the user sees the merged result on the first commit.

Verify with `lefthook dump`. It prints the config lefthook will run, fragments
included.
