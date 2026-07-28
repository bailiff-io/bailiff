# docs

Documentation site and decision-record scaffolding.

| Axis | How many | Packages |
|---|---|---|
| `docs:site` | At most one | mkdocs |
| `docs:decisions` | At most one | decision-records |

Independent axes. Take both, either, or neither.

## mkdocs

Renders `mkdocs.yml`, a `docs/` tree, and the nav. Offer it for a library or a
service with an external audience. A private service with three readers does not
need a published site, so ask what the audience is before offering.

`mkdocs` needs Python on the toolchain to build. When the project has no Python
language package, the site still renders and the build command needs Python
installed separately. Say that.

## decision-records

Renders `docs/decisions/` with a template and an index. It writes no decision.

Offer it when the user says the project will carry architectural decisions, or
when they have already described a decision worth recording. Recording the first
decision is your work after rendering, not the package's.

## Order

Render after `base`, which supplies `project_name` and `description` for the site
title. Nothing else in the catalog depends on either package.
