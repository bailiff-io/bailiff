# hooks

Git hooks: what they check, and which manager runs them.

| Axis | How many | Packages |
|---|---|---|
| `hooks:baseline` | At most one | baseline |
| `hooks:manager` | At most one | manager |

Two packages, two decisions. `baseline` decides what the hooks check; `manager`
decides which tool runs them, as a `hook_manager` answer over prek, lefthook, and
pre-commit.

Default to `prek`. It reads pre-commit's config format unchanged and needs no
Python runtime, so it runs the same hook ecosystem with fewer prerequisites.
Offer `pre-commit` when the user asks for it by name.

Offer both together, `baseline` first. A manager with no baseline runs only what
the language packages contribute. A baseline with no manager writes fragments
nothing reads.

## One package owns the manager choice

prek, lefthook, and pre-commit each write `.git/hooks/`, so a repo takes one.
Copier's `choices:` on `hook_manager` makes that exclusive at render time. A
package per manager made it exclusive by convention, and duplicated the merge
task three ways to do it.

## Checks live in baseline, in both schemas

Each fragment directory carries the same checks written twice, because neither
schema can express the other:

| Directory | Read by | Form |
|---|---|---|
| `.hooks.d/*.yaml` | lefthook, which expands the glob itself | stage key holding `commands.<id>.run`, against `{staged_files}` |
| `.pre-commit.d/*.yaml` | pre-commit and prek, after `manager`'s merge task | a `repos:` list of pinned upstream hook repos |

`baseline` renders both from one answer set, so a project cannot get weaker
checks by picking a different manager. Before it existed the baseline checks
lived in the pre-commit package alone, and choosing lefthook silently dropped
secret scanning, the typo check, shell linting, and commit-message enforcement.

`.mise/conf.d/hooks.toml` pins gitleaks, typos, and shellcheck. pre-commit
installs its own copy from each hook repo; lefthook runs what is on PATH. The
pins are what make a version mean one thing across managers.

A language package contributes its own fragment to each directory, in the same
pair of schemas.

## Verify after rendering

| Manager | Config check | Run everything |
|---|---|---|
| lefthook | `lefthook validate`, `lefthook dump` | `lefthook run pre-commit` |
| pre-commit | none | `pre-commit run --all-files` |
| prek | `prek validate-config` | `prek run --all-files` |

A fragment in the wrong schema is valid YAML, so nothing rejects it at render
time. lefthook reports `hooks: Value is array but should be object` and runs no
hooks at all.

## Related

`../workspace/justfile` asks which hook manager the project uses so its lint
recipe names the right command. Pass the same `hook_manager` answer.
