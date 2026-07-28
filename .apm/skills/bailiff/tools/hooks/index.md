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

| Choose | When |
|---|---|
| `lefthook` | Any language mix; hooks run native project commands; Go binary, no Python needed |
| `precommit` | The repo is already Python-centric, or the user wants the pre-commit hook ecosystem |

## Order

Render the hook manager after every language package. Both managers read the
`.pre-commit.d/` and `.hooks.d/` fragments that language packages write, so the
fragments must exist first. `after:` in each package's frontmatter states this.

## Related

`workspace/justfile` asks which hook manager the project uses so its lint recipe
names the right command. Pass the same answer you gave here.
