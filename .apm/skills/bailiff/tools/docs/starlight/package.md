---
name: starlight
summary: Astro + Starlight documentation site in a placement directory of its own
provides: [docs:site]
after: [base]
requires_bin: [mise]
---

## Renders

Everything except the two repo-root fragments lands under `placement_dir`
(default `docs`), because a Starlight site is a full Node project with its own
`package.json` and `node_modules`. Answer `placement_dir` with a single dot for
a docs-only repo.

| Path | Content |
|---|---|
| `<placement_dir>/package.json` | astro, @astrojs/starlight, sharp pins; the astro dev/build/preview scripts |
| `<placement_dir>/astro.config.mjs` | the starlight integration: title, description, optional editLink/social, optional explicit sidebar |
| `<placement_dir>/tsconfig.json` | extends `astro/tsconfigs/strict` |
| `<placement_dir>/src/content.config.ts` | the `docs` collection with Starlight's `docsLoader` and `docsSchema` |
| `<placement_dir>/src/content/docs/index.md` | front page seeded from `project_name` and `description` |
| `.mise/conf.d/starlight.toml` | node pin, plus bun or pnpm |
| `.gitignore.d/starlight` | `dist/`, `.astro/`, `node_modules/`, prefixed with `placement_dir` |

`package.json`, `astro.config.mjs`, and `src/content/docs/index.md` carry
`_skip_if_exists`, so a repo that already has a site keeps it.

## Ask in this order

1. `project_name` -- the Starlight site title and the docs package name. Thread
   the value the user gave `base`.
2. `description` -- one line. An empty answer omits `description` from the
   Starlight config and the front page.
3. `placement_dir` -- where the Astro project lives. `docs` for a project repo,
   a single dot for a docs-only repo.
4. `js_pkg_manager` -- bun, pnpm, or npm. Decides the install command and which
   tool the mise fragment lists. Thread the `ts` package's answer when that
   package is in the same selection.
5. `node_version` -- pinned in the mise fragment. Astro 7 needs node >=22.12.
   Thread the `ts` package's answer when present.
6. `sidebar_autogenerate` -- true leaves the sidebar out of the config so
   Starlight derives it from the `src/content/docs/` tree; false renders an
   explicit `sidebar` list with one entry to extend.
7. `repo_url` -- the GitHub repository URL. Non-empty wires
   `editLink.baseUrl` (pointing at `main` and `placement_dir`) and a GitHub
   `social` entry; empty omits both.

## Prerequisites

`mise` must be on PATH for the trust/install task.

## After rendering

- Tasks fold `.gitignore.d/*` into `.gitignore`, then run
  `mise trust --yes && mise install`. Dependency install is your work: run
  `<js_pkg_manager> install` inside `placement_dir`.
- With `sidebar_autogenerate: false`, add every new page to the `sidebar` list
  in `astro.config.mjs`; the rendered list holds only the front page.
- `editLink.baseUrl` assumes the default branch is `main`. Fix the URL when it
  is not.
- No CI job builds or publishes the site. `ci/index.md` covers adding one.
