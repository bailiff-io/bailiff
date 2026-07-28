# Runbook: add a package to a monorepo

The repo is set up. You are adding one package into it, matching what is already
there rather than deciding conventions.

## Rules

1. **The existing packages are the specification.** `probe.py` reports
   `package_dirs`, `workspace`, `package_managers`, and `rendered_packages`. A
   sibling's `.copier-answers.*.yml` holds the exact answers that produced it;
   reuse those values rather than asking again.
2. **Ask only what is specific to the new package.** Everything else comes from
   the sibling.
3. **Render at the package directory, never at the root.** Every root-level file
   already exists, and rendering there overwrites it.
4. **Refuse a destination that is not empty.** A populated directory means the
   package already exists. Stop and ask the user what they meant.
5. **Register the package by editing the workspace file.** Extending the
   root-level tooling is an edit too. No package renders either. Read each file
   before you change it.

## What to ask

| Ask | Then |
|---|---|
| What does the new package do | Its `description` |
| Its name | Check the sibling convention; when siblings are `api`, `web`, `worker`, propose a name in that form |
| Its language | Default to the siblings'. A language the repo does not have yet means CI needs new job packages too |

## Render

`dest = <repo>/<package dir>/<name>` for all three, in `scan.py --order`:
`repo/package-add`, the language package, `foundation/readme`.

## Register the package

Rendering the directory does not make the workspace see it.

| Mechanism | What to update |
|---|---|
| moon | `projects` in the root `moon.yml`, when it lists projects explicitly rather than globbing |
| pnpm | `packages` in `pnpm-workspace.yaml`, when it does not glob |
| uv | `members` under `[tool.uv.workspace]` |
| Cargo | `members` under `[workspace]` |
| Go | `go work use ./<package dir>/<name>` |

A glob that already matches the new directory needs no edit; a redundant entry is
noise.

## Extend the root-level tooling

- **CI path filters.** Add one for the new package's paths, following the pattern
  the existing filters use.
- **CI jobs.** When the new package introduced a language the repo did not have,
  render that language's `ci/` test and lint packages, then add jobs to the caller.
- **Release config.** Add the package to `monorepo_packages` when the release tool
  tracks packages individually.

## Verification

The core loop's workspace resolve has to see the new member: `uv sync`,
`pnpm install`, `cargo check`, `go work sync`, or `moon check <name>`. A package
that renders but does not resolve is not added.
