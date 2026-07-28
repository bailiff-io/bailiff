# Runbook: add a package to a monorepo

The repo is set up. You are adding one package into it, matching what is already
there rather than deciding conventions.

## Read the repo's conventions first

The existing packages are the specification. Read them before asking anything.

```sh
ls <dest>
cat <dest>/moon.yml 2>/dev/null
ls <dest>/.copier-answers.*.yml
ls <dest>/packages/*/.copier-answers.*.yml 2>/dev/null
```

| What to establish | Where |
|---|---|
| Where packages live | the existing package directories |
| Naming convention | the existing directory names and their manifest `name` fields |
| Language and version per package | each package's `.copier-answers.*.yml` |
| Package manager | the root lockfile |
| Workspace mechanism | the marker file, per `../index.md` |
| Root identity | the root `.copier-answers.base.yml` |

A sibling package's answers file gives you the exact answers that produced it.
Reuse those values instead of asking for them again. Ask only what is specific to
the new package.

## Ask only these

1. **What does the new package do?** Its `description`.
2. **Its name.** Check the convention: when siblings are `api`, `web`, `worker`,
   propose a name in that form.
3. **Its language.** Default to what the sibling packages use. When the user names
   a language the repo does not have yet, say that this adds a language to the
   monorepo, which means CI needs new job packages too.

Take everything else from the sibling.

## Render

```
1. workspace/package-add        dest = <repo>/<package dir>/<name>
2. languages/<pick>             dest = <repo>/<package dir>/<name>
3. foundation/readme            dest = <repo>/<package dir>/<name>
```

Destination is the new package's directory. Do not render at the repo root; every
root-level file already exists and rendering there overwrites it.

Check the destination is empty before rendering:

```sh
ls <repo>/<package dir>/<name> 2>/dev/null
```

Non-empty means the package already exists. Stop and ask the user what they meant.

## Register the package

Rendering the directory does not make the workspace see it. What remains depends
on the mechanism, and some of it is yours to edit:

| Mechanism | What to update |
|---|---|
| moon | `projects` in the root `moon.yml`, when it lists projects explicitly rather than globbing |
| pnpm | `packages` in `pnpm-workspace.yaml`, when it does not glob |
| uv | `members` under `[tool.uv.workspace]` |
| Cargo | `members` under `[workspace]` |
| Go | `go work use ./<package dir>/<name>` |

Read the file first. A glob pattern that already matches the new directory needs
no edit, and adding a redundant entry is noise.

## Extend the root-level tooling

These live at the root and the new package needs adding to them. Each is an edit,
not a render.

- **CI path filters.** Add a filter for the new package's paths, following the
  pattern the existing filters use.
- **CI jobs.** When the new package introduced a language the repo did not have,
  render that language's `ci/` test and lint packages, then add jobs to the caller.
- **Release config.** Add the package to `monorepo_packages` in the release tool's
  config when the tool tracks packages individually.

## After rendering

```sh
git -C <dest> status --short
```

Report the new files, the root files you edited, and then verify the workspace
resolves with the new member:

- `uv sync`, `pnpm install`, `cargo check`, or `go work sync`
- `moon check <name>` when the repo uses moon

Run it and report the output. A package that renders but does not resolve is not
added.
