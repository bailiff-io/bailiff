# docs

Documentation site and decision-record scaffolding.

| Axis | How many | Packages |
|---|---|---|
| `docs:site` | At most one | mkdocs, starlight |
| `docs:decisions` | At most one | decision-records |

Independent axes. Take a site package and decision-records, either, or neither.
`mkdocs` and `starlight` share the `docs:site` axis: select at most one.

Offer a site for a library or a service with an external audience. A
private service with three readers does not need a published site, so ask what
the audience is before offering either site package.

## mkdocs

Renders `mkdocs.yml`, a `docs/` tree, and the nav, all at the repo root.

`mkdocs` needs Python on the toolchain to build. When the project has no Python
language package, the site still renders and the build command needs Python
installed separately. Say that.

## starlight

Renders an Astro + Starlight project into a placement directory (default
`docs/`), plus mise and gitignore fragments at the repo root. It is a full Node
project with its own `package.json`.

Prefer it over mkdocs when the toolchain already carries Node (the `ts`
package), and thread that package's `js_pkg_manager` and `node_version` answers.
Without Node on the toolchain, the mise fragment installs it.

## decision-records

Renders `docs/decisions/` with a template and an index. It writes no decision.

Offer it when the user says the project will carry architectural decisions, or
when they have already described a decision worth recording. Recording the first
decision is your work after rendering, not the package's.

Its default `decisions_dir` is `docs/decisions`. When `starlight` places its
project at `docs/`, that default lands inside the Astro project, so answer
`decisions_dir` with a path outside it.
