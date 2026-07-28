---
name: api
summary: OpenAPI 3.1 contract at the repo root plus a spectral lint step
provides: [language:api]
after: [base, python, ts, go, rust]
---

## Renders

| Path | Contents |
|---|---|
| `openapi.yaml` | OpenAPI 3.1 skeleton with empty `paths` and `components.schemas` |
| `.spectral.yaml` | spectral config extending `spectral:oas` |
| `.mise/conf.d/api.toml` | `npm:@stoplight/spectral-cli` |
| `.pre-commit.d/api.yaml` | local `spectral lint openapi.yaml` hook |

`openapi.yaml` carries `_skip_if_exists`.

The package runs no tasks and needs no binary at render time. spectral arrives
through the mise fragment.

## Requires a language package

`api` supplies the contract and its lint step. It supplies no server code and no
dependency manifest. Render one of `python`, `ts`, `go`, or `rust` for the server
toolchain. The `after:` list names all four so `api` renders last when any of them
is also selected; none of them is mandatory, so `depends_on` names nothing.

## Question order

1. `project_name` -- becomes `info.title`, falling back to `API` when empty.
   Thread the value the user gave `base`.
2. `description` -- becomes `info.description`.

## After rendering

- Write the paths and schemas. The skeleton declares none.
- `openapi.yaml` sits at the repo root, where spectral and editor extensions find
  it without configuration. Moving it means updating `.spectral.yaml`, the
  `.pre-commit.d/api.yaml` entry, and any CI step that names the path.
- The `.pre-commit.d/` fragment stays inert until a `hooks` group package folds it
  into a config.
