# bailiff-mod-python

The Python **language overlay** (spec 014 / v2.0.0). Provides structured choice
axes for Python toolchain configuration, native-command scaffold via `uv` or `pdm`
init, and a managed `ruff.toml`. Ordered after `bailiff-mod-base` via `depends_on`.

## What it produces

| Output | Lifecycle | Notes |
|---|---|---|
| `pyproject.toml` | **task-output** → **seed-once** | Written by `uv init` / `pdm init` (init-only-guarded). Never clobbered on reproduce. |
| `ruff.toml` | **managed** (byte-identical) | Re-rendered on every reproduce from the frozen answers. |
| `.mise/conf.d/bailiff-mod-python.toml` | **managed** (byte-identical) | Drop-in tool file; mise merges all `.mise/conf.d/*.toml` at runtime. |
| `.pre-commit.d/bailiff-mod-python.yaml` | **managed** (byte-identical) | ruff hook fragment; consumed by `bailiff-mod-precommit`'s bundler `_post_task`. Only written when `hook_manager=pre-commit`. |
| `.gitignore.d/bailiff-mod-python` | **managed** (byte-identical) | Python gitignore fragment; folded into `.gitignore` by `bailiff-mod-base`'s `_post_task`. |

## Questions

| Key | Choices / default | Notes |
|---|---|---|
| `project_name` | str / from base | Read from `_external_data.base.project_name`. |
| `description` | str / from base | Read from `_external_data.base.description`. |
| `python_pkg_manager` | [uv, pdm] / uv | |
| `python_version` | [3.11, 3.12, 3.13, 3.14] / 3.13 | pins requires-python + ruff target + mise |
| `python_layout` | [src, flat] / src | src = `uv init --package` (installable) |
| `python_framework` | [none, fastapi, django, flask] / none | recorded only; no scaffolding branch |
| `ruff_line_length` | [79, 88, 100, 119, 120] / 88 | |
| `ruff_quote_style` | [double, single] / double | |
| `ruff_rule_profile` | [standard, strict] / standard | strict adds ANN, RUF, PERF, C4, PT |
| `add_tests` | bool / false | adds tests/ scaffold with pytest example |
| `ruff_version` | str / "" | pinned ruff version for the pre-commit fragment; agent-resolved |

## Ordering

`depends_on: [bailiff-mod-base]`, `_bailiff_phase: normal`. The engine orders base
before this overlay. `project_name` and `description` are read from base via
`_external_data.base` (spec 014 FR-004). The `.pre-commit.d/` fragment renders
unconditionally; `bailiff-mod-precommit`'s bundler `_post_task` merges it only when
`hook_manager=pre-commit`.

## Prerequisites (FR-007)

This template runs trust-gated `_tasks`; the source must be trusted before it
renders. Preflight checks:

- **mise** — <https://mise.jdx.dev>
- **uv** (when `python_pkg_manager=uv`) — <https://docs.astral.sh/uv/>
- **pdm** (when `python_pkg_manager=pdm`) — <https://pdm-project.org/>

## Usage

Prefer bailiff (multi-layer):

```sh
uvx bailiff init --run-spec <run-spec with [bailiff-mod-base, bailiff-mod-python]>
```

Copier-only (standalone; renders with defaults):

```sh
copier copy --trust https://github.com/bailiff-io/bailiff-mod-python.git <destination>
```
