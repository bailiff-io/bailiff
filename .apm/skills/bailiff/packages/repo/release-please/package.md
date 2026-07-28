---
name: release-please
summary: Release PRs opened by GitHub Actions from conventional commits
provides: [release:tool]
after: [base, github-repo]
depends_on: [github-repo]
---

Renders:

- `release-please-config.json` -- the manifest-mode config, schema-referenced against `googleapis/release-please`
- `.release-please-manifest.json` -- the current version per package path
- `.github/workflows/release-please.yml` -- a push-triggered job running `googleapis/release-please-action` pinned to the v5.0.0 commit SHA

The workflow file carries its own name, so it does not collide with the caller
`ci.yml` you compose from the `ci/` packages.

## GitHub CI requirement

The workflow runs on GitHub Actions only. Select this package when `ci:host` is
`github`, alongside `github-repo`. On GitLab, offer `cocogitto` instead.

The rendered job uses `secrets.GITHUB_TOKEN`. Releases and tags created with that
token do not trigger other workflows. When the user wants a release tag to start a
publish workflow, tell them to create a PAT with `contents: write` and
`pull-requests: write`, store it as a repository secret, and change the `token:`
line to name it.

The repository setting "Allow GitHub Actions to create and approve pull requests"
must be on, under Settings, Actions, General. Without it the job fails when it
tries to open the release PR.

## Questions, in order

1. `release_type` -- `node`, `python`, `rust`, `go`, or `simple`. Match it to the language package the project uses. `simple` bumps a `version.txt`.
2. `layout` -- `single` or `monorepo`.
3. `monorepo_packages` -- a YAML list of package directories relative to the repo root, such as `[packages/api, packages/web]`. Leave it `[]` for `single`.
4. `initial_version` -- the version written into the manifest for each package before the first release. Default `0.1.0`.
5. `default_branch` -- the branch the workflow triggers on. Default `main`.

A `single` layout writes one `"."` entry in both files and sets
`include-component-in-tag: false`, giving tags `vX.Y.Z`. A `monorepo` layout
writes one entry per directory with a `component` taken from the last path
segment, sets `include-component-in-tag: true` for `<component>-vX.Y.Z` tags, and
sets `separate-pull-requests: false` so one PR covers every package.

## Order

Render this after the language packages, so `monorepo_packages` names directories
that exist, and after `github-repo`, which owns the rest of `.github/`.

## After rendering

`release-please-config.json` applies one `release-type` to every package. A
monorepo mixing languages needs a per-package `"release-type"` key added by hand;
point the user at the manifest-releaser docs when they say the packages differ.

The first workflow run opens a release PR. Nothing is tagged until that PR merges.
