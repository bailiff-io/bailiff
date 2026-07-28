# Runbook: monorepo setup

Set up the root and the first packages. Read `../index.md` first for the
root-versus-package split and the workspace markers.

## Interview order

| # | Ask | Why here |
|---|---|---|
| 1 | What does this monorepo hold: the package list, and what each does | Every question below is per item on this list |
| 2 | `project_name` and `org` for the root | Also answer `layout: monorepo` in `base` |
| 3 | Where packages live: the actual paths | Decides every per-package destination |
| 4 | Language per package, walking the list one at a time | A package's own answers, not the repo's |
| 5 | Workspace mechanism, and whether they want `moon` on top | Recommend moon when the packages span more than one language |
| 6 | Root tooling, one axis at a time: hook manager, then CI host, then the release and dep-update tools | One answer each for the whole repo |
| 7 | Each remaining group in `scan.py` order | Root destination |

## Render order

Two selections, ordered separately by `scan.py --order`, because the same package
renders at more than one destination here.

1. **Root selection**, `dest = repo root`: everything the split table in
   `../index.md` puts at the root.
2. **Per-package selection**, `dest = <package dir>`, once per package: its
   language package and its readme.

Interleave them on one rule: **render a root package after the per-package pass
when its `after:` names a language package.** `scan.py --order` marks which. Those
are the hook manager, `workspace/justfile`, the CI job packages, and the release
tool, and each reads what the language packages wrote:

| Root package | Reads |
|---|---|
| `hooks/*` | the `.pre-commit.d/` and `.hooks.d/` fragments, one per package directory |
| `repo/<release tool>` | the package directories, passed as `monorepo_packages` |

Tell the hook manager where the packages are; each language package wrote its
fragment into its own package directory.

## Answers files

One per render, named for what it renders:

```
/tmp/bailiff-answers-base.yml
/tmp/bailiff-answers-python-api.yml
/tmp/bailiff-answers-ts-web.yml
```

## CI in a monorepo

Path filtering is the decision that matters. A push touching one package should
run that package's jobs and no others. `../../../packages/ci/index.md` covers the
patterns; the caller you write needs one filter per package directory.

## Verification

The core loop's verification runs the workspace resolve. In a monorepo that
command follows the mechanism: `uv sync`, `pnpm install`, `cargo check`,
`go work sync`, or `moon check --all`. Report the tree grouped by package, and say
what the user runs next per package.
