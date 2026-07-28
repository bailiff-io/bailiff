---
name: mkdocs
summary: mkdocs-material documentation site with a docs/ tree and nav
provides: [docs:site]
after: [base]
---

## Renders

| Path | Content |
|---|---|
| `mkdocs.yml` | `site_name`, `site_description`, `docs_dir: docs`, the material theme, a one-entry nav |
| `docs/index.md` | Front page seeded from `project_name` and `description` |
| `.mise/conf.d/mkdocs.toml` | `mkdocs` and `mkdocs-material` pins for mise |

`docs/index.md` carries `_skip_if_exists`, so a repo that already has one keeps it.

## Ask in this order

1. `project_name` -- the site title.
2. `description` -- the one-line site description. An empty answer omits
   `site_description` from `mkdocs.yml`.

Both values also belong to `base`. When `base` is in the same selection, copy its
answers into this package's answers file rather than asking twice.

## After rendering

- Add every new page to the `nav` list in `mkdocs.yml`. The rendered nav holds
  only `index.md`.
- Building the site needs Python on the toolchain. When the selection has no
  Python language package, tell the user that `mkdocs serve` needs a separate
  Python install.
- No CI job publishes the site. `ci/index.md` covers adding one.
