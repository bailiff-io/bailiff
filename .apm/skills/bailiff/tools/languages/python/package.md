---
name: python
summary: Python overlay -- uv or pdm, ruff, mise pin, optional pytest scaffold
provides: [language:python]
after: [base]
requires_bin: [mise]
precheck: precheck.py
---

## Renders

| Path | Contents |
|---|---|
| `ruff.toml` | target-version, line-length, lint selection, quote style |
| `pytest.ini` | pytest config; only when `add_tests` is true |
| `tests/test_example.py` | one placeholder test; only when `add_tests` is true |
| `.mise/conf.d/python.toml` | python version, plus uv when `python_pkg_manager` is uv |
| `.pre-commit.d/python.yaml` | ruff and ruff-format hooks at `ruff_version` |
| `.hooks.d/python.yaml` | the same two hooks in manager-neutral form |
| `.gitignore.d/python` | Python ignore lines |
| `pyproject.toml` | written by `uv init` or `pdm init` after the render, then left alone |

`tests/test_example.py` and `pyproject.toml` carry `_skip_if_exists`: an existing
file survives the render.

## Question order

1. `project_name` -- passed to `uv init --name`. Thread the value the user gave
   `base`; the package does not read another answers file.
2. `description` -- recorded in the answers file.
3. `python_pkg_manager` -- uv or pdm. Decides which native init task runs and
   whether the mise fragment lists uv.
4. `python_version` -- pins `requires-python`, ruff `target-version`, and the
   mise python entry.
5. `python_layout` -- src passes `--package` to `uv init` for an installable
   layout; flat omits it. pdm ignores this answer.
6. `python_framework` -- recorded only.
7. `ruff_line_length`
8. `ruff_quote_style`
9. `ruff_rule_profile` -- strict adds ANN, RUF, PERF, C4, and PT to the standard
   selection.
10. `add_tests` -- true adds `pytest.ini` and `tests/test_example.py`.
11. `ruff_version` -- rev for the ruff-pre-commit hook. The default tracks a
    released tag; raise it if a newer one exists.

## Prerequisites

`mise` must be on PATH. The precheck also requires whichever of `uv` or `pdm`
`python_pkg_manager` names.

## After rendering

- Tasks run `mise trust --yes && mise install`, then the native init for the
  chosen manager.
- Add runtime dependencies with `uv add` or `pdm add`. The render writes none.
- `python_framework` selects no scaffold. Install the framework and write its
  entry point.
- The `.pre-commit.d/` and `.hooks.d/` fragments stay inert until a `hooks` group
  package folds them into a config.
