# languages

Toolchain, dependency manifest, formatter, and linter config for one language.

| Axis | How many | Packages |
|---|---|---|
| `language:*` | One or more | python, ts, go, rust |
| `language:api` | At most one, alongside a language | api |

## How many to pick

A single-language repo takes one. A repo with a Python backend and a TypeScript
frontend takes both, and each writes its own manifest, its own
`.mise/conf.d/<package>.toml`, and its own `.pre-commit.d/<package>.yaml`. The
fragments do not collide.

In a monorepo, ask which language belongs to which package directory, then render
once per package with a `dest` pointing at that directory. Rendering two language
packages into one directory produces two manifests in one place, which is correct
only when the directory genuinely holds both.

## api

`api` adds an OpenAPI contract and a spec-lint step. It needs a language package
to supply the server toolchain, so offer it after the user has picked one.

## What downstream packages take from these

The CI, hook, and `agent-hooks` packages ask which languages the project has, and
the answer is what you rendered here rather than what is on disk.
