# Package contract

Every directory under `packages/<group>/<package>/` obeys this. `scan.py` enforces
the mechanical half and exits 1 on a violation.

## Required files

```
packages/<group>/<package>/
  package.md            frontmatter manifest + agent steering prose
  copier.yml            copier config; omit for a steering-only package
  template/             the render subtree; copier.yml sets _subdirectory: template
    {{ _copier_conf.answers_file }}.jinja
  precheck.py           optional; runs before render, exits non-zero to abort
  tasks/                optional; scripts named in copier.yml _tasks
```

A rendering package MUST ship `template/{{ _copier_conf.answers_file }}.jinja`
containing `{{ _copier_answers|to_nice_yaml }}`. Without it copier writes no
answers file and `scan.py` reports the violation.

## package.md frontmatter

Only these fields. Any other key is a lint error.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `name` | string | yes | Must equal the directory name |
| `summary` | string | yes | One line; the agent offers the package with this |
| `provides` | list | yes | Tags as `axis:value`; the namespace names the choice axis |
| `after` | list | no | Package names that render first when also selected |
| `depends_on` | list | no | Package names this one needs; the agent warns when absent |
| `requires_bin` | list | no | Executables on PATH; `render.py` exits 3 when one is missing |
| `precheck` | string | no | Path to a script, relative to the package directory |

`after` and `depends_on` name bare package names (`base`, `python`), not
`<group>/<package>` ids.

## package.md body

Steering the agent reads once the user picks the package. State:

- What the package renders, by path.
- What to ask, in what order, and what each answer changes.
- Which answers come from another package rather than from the user.
- What remains for the agent or the user after rendering.

Every package that declares questions MUST state an order for them.

## copier.yml

- `_subdirectory: template` on every rendering package.
- Questions carry `type`, `help`, and `choices` where the answer is closed.
- No `secret:` questions. The answers file is committed, so a secret answer would
  be committed with it. A task fetches the value at the point of use instead.
- Ordering edges live in `package.md` frontmatter, never in `copier.yml`.
- `_tasks` entries run after rendering, in written order, with answers available
  as jinja values and as environment variables.

A package with no questions is valid. `copier.yml` holding only
`_subdirectory: template` renders its template as-is.

## Fragment conventions

A package that contributes to a shared config writes one namespaced file into a
`.d` directory rather than editing a merged file. What merges the fragments
differs per directory.

| Directory | Filename | How it is consumed |
|---|---|---|
| `.hooks.d/` | `<package>.yaml` | lefthook expands `extends: [.hooks.d/*.yaml]` itself |
| `.mise/conf.d/` | `<package>.toml` | mise reads the directory itself |
| `.pre-commit.d/` | `<package>.yaml` | `precommit`'s `merge_precommit.py` task writes `.pre-commit-config.yaml`; pre-commit has no include directive |
| `.gitignore.d/` | `<package>` | each contributing package ships `tasks/fold_gitignore.py` and folds its own block into `.gitignore` |

## Verify a package

```sh
python3 scripts/scan.py --lint-only            # exit 0 required
python3 scripts/render.py <group>/<pkg> /tmp/t --answers /tmp/a.yml
```

The render must produce `.copier-answers.<package>.yml` in the destination.
