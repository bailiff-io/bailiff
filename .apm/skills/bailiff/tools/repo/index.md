# repo

Forge metadata, release tooling, and dependency updates.

| Axis | How many | Packages |
|---|---|---|
| `repo:host` | Exactly one, or none | github-repo, gitlab-repo |
| `release:tool` | At most one | cocogitto, release-please |
| `deps:updates` | At most one | dep-updates |

Every axis here is independent of the others. A project takes a repo host with no
release tool, or a release tool with no dep-updates.

## repo host

`github-repo` renders `CODEOWNERS`, issue templates, and the PR template. It
creates the remote only when the user answers `create_remote: true`.

Ask about visibility explicitly and read the answer back to the user. Rendering
`visibility: public` publishes the repository the moment `gh repo create` runs,
and no later step undoes that.

Match the host to where the code will live. Do not offer `gitlab-repo` for a
project the user described as living on GitHub.

## release tool

| Choose | When |
|---|---|
| `cocogitto` | The user wants version bumps and changelog generation driven from a local command |
| `release-please` | The user wants a release PR opened by CI, and the repo host is GitHub |

Both read conventional commits and both own the changelog, so a repo with both
gets two tools writing `CHANGELOG.md`. Pick one.

`release-please` needs a GitHub workflow to run in, so it needs `ci:host` set to
`github`. When the user picks `release-please` without GitHub CI, say so and let
them decide.

## dep-updates

One package, with `dep_update_tool` taking `renovate` or `dependabot`. The
answer decides which config file renders; the other is not written and not
deleted. Switching tools on a live project means removing the old config by hand,
so ask once and confirm.

The `dep_ecosystems` answer lists the ecosystems to watch, in the chosen tool's
vocabulary. Derive it from the language packages the project has and read the
list back to the user.

## Order

Render `base` first for `project_name` and `org`. Render the release tool after
the language packages, because a monorepo release config names the package
directories.
