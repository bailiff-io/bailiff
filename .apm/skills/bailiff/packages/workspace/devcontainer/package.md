---
name: devcontainer
summary: devcontainer on Ubuntu with the mise feature and mise install on create
provides: [workspace:container]
after: [base]
---

## Renders

| Path | Contents |
|---|---|
| `.devcontainer/devcontainer.json` | image `mcr.microsoft.com/devcontainers/base:ubuntu`, the `devcontainers-extra/features/mise` feature, and `postCreateCommand: mise trust && mise install` |
| `.copier-answers.devcontainer.yml` | the answers |

No task runs and no binary is needed. The container installs the toolchain by
reading the `.mise/conf.d/*.toml` fragments other packages write, so render this
package after them or the first build installs nothing.

## Ask

One question:

1. `project_name` (default empty) -- the container name the editor displays. An
   empty answer renders `project`.

## After rendering

The base image is fixed. A project needing system packages beyond the language
toolchain edits `.devcontainer/devcontainer.json`: change `image`, or add a
`Dockerfile` and point `build.dockerfile` at it.
