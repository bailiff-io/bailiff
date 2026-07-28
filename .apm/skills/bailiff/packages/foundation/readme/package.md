---
name: readme
summary: README.md skeleton -- heading, description, install command, section stubs
provides: [scaffold:readme]
after: [base]
depends_on: [base]
---

`readme` renders `README.md` and `.copier-answers.readme.yml`. The render is a
skeleton: heading, description, an install command chosen from `stack`, and
comment stubs for Usage and Contributing.

## Question order

1. `project_name` -- the heading. Pass `base`'s answer at the repo root. In a
   monorepo package directory, pass the package's name.
2. `description` -- one line under the heading. Pass `base`'s answer, or a
   package-specific line in a monorepo.
3. `stack` -- a summary such as `Python/FastAPI/uv`. A value containing `python`
   or `uv` renders `uv sync`, `bun` renders `bun install`, `pnpm` renders
   `pnpm install`, anything else renders a placeholder comment. Read the stack
   off the language packages the user picked rather than asking twice.

`project_name` and `description` come from the `base` interview. Ask again only
when the destination is a monorepo package directory that needs its own values.

`README.md` is listed in `_skip_if_exists`, so a destination that already holds
one keeps it.

## Authored prose

When the user wants prose you write rather than a skeleton, render the package
first and edit `README.md` afterward. Tell the user you are doing so. The
skeleton fixes the section order and the install command; your edit replaces the
Overview, Usage, and Contributing bodies.
