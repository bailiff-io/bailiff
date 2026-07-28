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
| `ruff.toml` | target-version, line-length, lint selection, quote style, docstring rules |
| `pytest.ini` | pytest config, plus coverage and doctest flags; only when `add_tests` is true |
| `mypy.ini` | strict-ish mypy config; only when `python_type_checker` is mypy |
| `noxfile.py` | multi-interpreter sessions; only when `python_multiversion` is nox |
| `tests/test_example.py` | one placeholder test; only when `add_tests` is true |
| `.mise/conf.d/python.toml` | python version, plus uv when `python_pkg_manager` is uv |
| `.pre-commit.d/python.yaml` | ruff, the type checker, deptry, and the advisory docstring pass |
| `.hooks.d/python.yaml` | the same hooks in lefthook's schema |
| `.gitignore.d/python` | Python ignore lines |
| `pyproject.toml` | written by `uv init` or `pdm init` after the render, then left alone |

The dev tooling is installed rather than assumed: a task runs
`uv add --dev`/`pdm add --dev` with the type checker, pytest, pytest-cov, deptry,
and nox as the answers select them. `ci/github-python` used to run
`uv run mypy .` while nothing installed mypy, so the lint job failed on a missing
binary rather than on a type error.

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

## Docstrings: presence warns, accuracy fails

ruff has no per-rule severity. The package therefore renders two passes:

| Pass | Rules | Behaviour |
|---|---|---|
| blocking hook | everything except `D` | fails the commit |
| advisory hook | `--select D --exit-zero` | prints missing docstrings, never fails |

`D` is therefore absent from `ruff.toml`'s `select` when
`python_docstring_check` is `warn`. Putting it there would make a bare
`ruff check` fail, which is the opposite of advisory. Answer `enforce` to select
it and block instead.

`DOC` rules are the accuracy half, and they block. They are ruff's pydoclint
port, so they compare the documented parameters, returns, and raises against the
real signature. A documented parameter absent from the signature means the
docstring drifted from the code. Verified against a fixture documenting a phantom
parameter `c` alongside an unraised `ValueError`: ruff reports both.

`DOC` is preview-gated, so `ruff.toml` sets `preview = true` when
`python_docstring_accuracy` is on. Without it ruff prints `Selection \`DOC\` has
no effect because preview is not enabled` and checks nothing.

## Type checking is whole-program

The type-checker hook passes `pass_filenames: false` and the lefthook command
takes no `{staged_files}`. A per-file run cannot resolve a type defined in a file
that was left out, so it reports errors that do not exist.

It also runs through `uv run`/`pdm run` rather than in an isolated hook
environment. A type checker without the project's dependencies installed reports
a missing import for every one of them.

## Multi-version testing

`python_multiversion: nox` renders a `noxfile.py`. Python has no builtin way to
run a suite against several interpreters, and the CI matrix already does it in
parallel, so this exists for checking the matrix locally before pushing. Offer it
for a library published to PyPI; leave it off for an application pinned to one
version.

The rendered `PYTHONS` list holds the one version the package was told about.
Widen it by hand to the versions the project supports.
