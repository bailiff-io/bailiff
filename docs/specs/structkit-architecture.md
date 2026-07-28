---
title: structkit template architecture
status: Proposed
date: 2026-07-28
---

# structkit template architecture

A proposal for `structkit-templates`, the repository that replaces the bailiff
copier catalog if `bfsh-asl` decides that way. Everything below was verified
against structkit 3.2.1.

## Capabilities, verified

| Capability | Verified how |
|---|---|
| Structures stack | `folders:` with a `struct:` list rendered `base/repo` plus `lang/python` into one tree, each entry taking its own `with:` variables |
| A package can be added later | Pointing `generate` at `<repo>/packages/newsvc` wrote only there; a hand-edited sibling file survived untouched |
| Per-package variables in a monorepo | Three `folders:` entries produced `packages/api` and `packages/worker` with their own `project_name` |
| Named sources | `sources add` writes `~/.config/structkit/sources.yaml`; a source renders as `<name>/<structure>` |
| Remote content | `file: github://github/gitignore/main/Python.gitignore` fetched correctly |
| Existing repos are safe | `--file-strategy=skip` leaves what is there |

## Untemplated hooks

**Hooks are not templated.** A `post_hooks` entry containing `{{@ name @}}`
passes the braces to the shell unrendered, while a file in the same structure
renders the value. Hooks are therefore unconditional one-liners.

That is survivable because the preferences are fixed rather than asked. With prek,
uv, biome, bun, release-please, and GitHub settled, every task in the copier
catalog becomes either a file to commit or an unconditional command. Only
`go mod init <module-path>` and `cdk init` take a value, and it is one the user
supplies.

## Do not reuse the bundled `project/*` structures

`structkit list` reports 48 bundled structures. `project/python` ships `setup.py`,
`setup.cfg`, `requirements.txt`, `MANIFEST.in`, a `Makefile`, and fetches
structkit's own `LICENSE` from its repository. It declares no variables, so none
of it is parameterised. `project/generic` writes `.devops/apps/environments/`
Terraform and `REMOVE_ME.md` placeholders.

An opinionated default that disagrees with our tooling costs more to correct than
a structure costs to write.

The single-purpose ones are reusable: `configs/editor-config` renders exactly one
`.editorconfig`. The `github/workflows/*` set and the Terraform and Helm
structures are worth reading before deciding.

## Proposed layout

```
structkit-templates/
  structures/
    base/
      repo.yaml            README, .gitignore, .gitattributes, .editorconfig, AGENTS.md
      community.yaml       SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md
      license-mpl.yaml     one per licence in the policy: MPL, AGPL, Apache
      license-agpl.yaml
      license-apache.yaml
    lang/
      python.yaml          pyproject.toml, ruff.toml, mypy.ini, pytest.ini
      ts.yaml              package.json, tsconfig.json, biome.json, vitest.config.ts
      go.yaml              go.mod, .golangci.yml
      rust.yaml            Cargo.toml, rustfmt.toml, rust-toolchain.toml, deny.toml
    hooks/
      prek.yaml            .pre-commit-config.yaml, .hooks-bin/check-commit-msg.py
    ci/
      github.yaml          gate, changes, per-language test and lint, security, quality, publish
    repo/
      release-please.yaml
      dep-updates.yaml
    mono/
      root.yaml            workspace manifest, moon.yml
    iac/
      terraform.yaml
    docs/
      starlight.yaml
  .struct/
    single-python.yaml     the compositions below
    single-ts.yaml
    go-cli.yaml
    rust-lib.yaml
    monorepo.yaml
```

Licences are separate structures rather than one parameterised file. The policy
assigns a licence per repository kind, so selection is the decision and the file
itself never varies.

## The compositions

### Single Python service

```yaml
variables:
  - project_name:
      type: string
files: []
folders:
  - ./:
      struct:
        - base/repo
        - base/community
        - base/license-mpl
        - lang/python
        - hooks/prek
        - ci/github
        - repo/release-please
      with:
        project_name: "{{@ project_name @}}"
post_hooks:
  - git init -b main
  - mise trust --yes && mise install
  - prek install
```

The other single-language shapes differ only in the `lang/*` entry and the
licence.

### Monorepo

```yaml
variables:
  - project_name:
      type: string
folders:
  - ./:
      struct:
        - base/repo
        - base/community
        - base/license-apache
        - mono/root
        - hooks/prek
        - ci/github
      with:
        project_name: "{{@ project_name @}}"
  - packages/api/:
      struct: lang/python
      with:
        project_name: api
  - packages/web/:
      struct: lang/ts
      with:
        project_name: web
```

### Adding a package later

One command, no composition file:

```sh
structkit generate templates/lang/python ./packages/newsvc --vars project_name=newsvc
```

Verified: it writes only that directory. This replaces the whole
`repo/package-add` runbook.

### Retrofitting a tool onto an existing repo

```sh
structkit generate --file-strategy=skip templates/hooks/prek .
```

`skip` leaves every existing file alone, so the render adds what is missing and
reports what it skipped.

## What the agent does

The `structkit` package in `agentic-packages` carries the MCP server and a skill.
The skill covers structure selection, the stacking rules, the subpath render for a
monorepo package, and the `--file-strategy` discipline for a non-empty
destination. That replaces the runbooks and the group-index prose.

## Open questions

- How fine to slice the structures. A project listing a dozen entries is
  unwieldy, and too few means a variant needs a fork. Tracked as `bfsh-z0b`.
- Whether the two value-taking commands become a rendered bootstrap script, a
  prompt to the user, or a fixed convention. Tracked as `bfsh-cin`.
- Whether remote content references replace committed fragments, given that an
  unpinned reference makes a render non-reproducible. Tracked as `bfsh-ehp`.

## What is deliberately excluded

The `prompt:` file key, which generates content through an LLM at render time.
The agent driving structkit is already a model, so a second separately-keyed call
inside the renderer costs reproducibility for nothing. Tracked as `bfsh-f3f`.
