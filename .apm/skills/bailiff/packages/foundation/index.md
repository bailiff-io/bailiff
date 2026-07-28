# foundation

Project identity and the files every repo carries regardless of language.

| Axis | How many | Packages |
|---|---|---|
| `scaffold:identity` | Exactly one, always | base |
| `scaffold:readme` | At most one | readme |
| `scaffold:editorconfig` | At most one | editorconfig |

## base is not optional

`base` collects `project_name`, `org`, `description`, `layout`, and
`default_branch`. Other packages ask for the same values, and you pass the same
answer to each. Render `base` first so the values you thread onward are the ones
the user confirmed.

Skip `base` only when the destination already holds a
`.copier-answers.base.yml`. Read the identity out of that file instead of asking
again.

## readme

Offer `readme` for a repo whose root holds no `README.md`. In a monorepo, offer
it once for the root and once per package the user names, with a different
`project_name` in each answers file.

When the user wants prose you write rather than a rendered skeleton, treat
`readme` as the skeleton and edit the result afterward. Say that you are doing so.
