# bailiff-mod-apm

One copier template that wires an [APM](https://microsoft.github.io/apm) package
layer into a generated project: it renders `apm.yml` from a runtime-injected
package set and runs a trust-gated, version-pinned `apm install` task that writes
`apm.lock.yaml`.

## What it produces

| Output | Lifecycle | Notes |
|---|---|---|
| `apm.yml` | **managed** | Rendered from `apm_packages` + `project_name`/`description` read from base. Re-rendered config-consistently at reproduce. |
| `apm.lock.yaml` | **task-output** (`apm install`) | Written by the pinned `apm install` task. External state — regenerated at reproduce, not config-guaranteed. |
| `.copier-answers.bailiff-mod-apm.yml` | **managed** | Records `_src_path` + `_commit` + frozen answers for reproduce. |
| `.gitignore.d/bailiff-mod-apm` | **managed** | gitignore fragment; base's post-task folds all `.gitignore.d/*` into `.gitignore`. |

## Dependencies

`bailiff-mod-apm` declares `depends_on: [bailiff-mod-base]` and `phase: normal`.
The engine orders base before apm and enforces that base is present in any
multi-layer selection. `project_name` and `description` are read from base via
`_external_data.base.*` (`.copier-answers.bailiff-mod-base.yml`).

## The package set is runtime-injected

`apm_packages` is a runtime-injected list-typed answer (`type: yaml`), not a
frozen `choices:` list. The phase-1 agent determines the packages from user
input and injects them via `--data apm_packages=[…]`; the user may override.
The answer persists to the answers file so reproduce replays the same set.

Each entry is an APM dependency locator:

```
srobroek/agentic-packages/packages/speckit#>=5.0.0 <6.0.0
```

### At least one package is required

`bailiff-mod-apm` requires ≥ 1 package. If reached with an empty set, the
`apm_packages` validator refuses the render with a message telling the user to
drop the module — it never renders an empty `apm.yml`.

## Prerequisites

This template runs trust-gated `_tasks`; the source must be trusted
(`bailiff trust add …`) before it renders. A preflight task checks for `uvx`
and fails with install guidance if it is absent:

- **uv / uvx** — <https://docs.astral.sh/uv/getting-started/installation/>

No APM token is stored in a copier answer — the APM CLI reads ambient
credentials from the environment.

## Usage

```sh
uvx bailiff init --run-spec <run-spec.(json|yml)>
```

## Reproduce notes

Reproduce re-renders `apm.yml` config-consistently from the committed answers +
pinned commit. The install task re-runs under trust and regenerates `apm.lock.yaml`;
that lock is external state and may differ across runs. The task pins
`apm_cli_version` for process-determinism.

`reproduce_many` requires base to be in the selection (the `depends_on` edge is
enforced at preflight). Single-layer reproduce via `runner.reproduce` is valid for
standalone use cases.
