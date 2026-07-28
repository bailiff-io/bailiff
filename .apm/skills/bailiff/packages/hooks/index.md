# hooks

Git hook managers. Selecting a package here is how the project chooses its manager.

| Axis | How many | Packages |
|---|---|---|
| `hooks:manager` | Exactly one, or none | lefthook, precommit |

## Pick one

`lefthook install` and `pre-commit install` both write `.git/hooks/`, so whichever
runs second overwrites the first. When the user asks for both, say that and ask
which one runs the hooks.

Offer nothing here when the user does not want managed hooks. Language packages
still write their `.pre-commit.d/<package>.yaml` fragments; without a manager
those files sit unread, which costs nothing.

Both packages install into `.git/hooks/`, so the destination must be a git
repository. Each carries an `install_hooks` question; answer it false when the
repository is not initialised yet, then install by hand.

| Choose | When |
|---|---|
| `lefthook` | Any language mix; hooks run native project commands; Go binary, no Python needed |
| `precommit` | The repo is already Python-centric, or the user wants the pre-commit hook ecosystem |

## Order

Render the hook manager after every language package, because each manager reads
the fragments those packages write.

| Package | Reads | How |
|---|---|---|
| `lefthook` | `.hooks.d/*.yaml` | `lefthook.yml` carries `extends: [.hooks.d/*.yaml]`; lefthook expands the glob and merges the fragments itself |
| `precommit` | `.pre-commit.d/*.yaml` | a merge task writes `.pre-commit-config.yaml`; pre-commit has no include directive |

The fragment schemas differ. A `.hooks.d/` fragment is lefthook config, keyed by
stage name with a `commands:` map; a `.pre-commit.d/` fragment is a pre-commit
`repos:` list. Neither manager reads the other's directory, so a language package
supporting both ships a fragment in each.

Run `lefthook validate` after rendering. A fragment in the wrong schema is valid
YAML, so nothing rejects it at render time; lefthook reports `hooks: Value is
array but should be object` and runs no hooks at all.

`after:` in each package's frontmatter states the ordering.

Re-render `precommit` after adding a `.pre-commit.d/` fragment, because its merge
runs at render time. `lefthook` needs no re-render: the glob picks up a new
fragment on the next hook run.

## Related

`workspace/justfile` asks which hook manager the project uses so its lint recipe
names the right command. Pass the same answer you gave here.
