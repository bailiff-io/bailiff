---
name: cdk
summary: AWS CDK app scaffolded by cdk init in the language you pick
provides: [iac:tool]
after: [base, python, ts, go]
requires_bin: [cdk]
precheck: precheck.py
---

## Renders

The template holds only `.copier-answers.cdk.yml`. Every CDK file comes from the
task, which runs `cdk init app --language=<cdk_language>` inside
`<placement_dir>`. The task skips itself when `<placement_dir>/cdk.json` already
exists, because `cdk init` refuses a non-empty directory.

## Toolchain

`cdk` must be on PATH; `render.py` exits 3 without it. Install it with
`npm install -g aws-cdk`.

`cdk_language` decides a second binary, which `precheck.py` checks:

| `cdk_language` | Binary | Install |
|---|---|---|
| `typescript` | `node` | `mise use node@lts` |
| `python` | `python3` | `mise use python@latest` |
| `go` | `go` | `mise use go@latest` |
| `java` | `java` | `mise use java@latest` |
| `csharp` | `dotnet` | `mise use dotnet@latest` |

Set `cdk_language` to a language the project already has. Adding a language
toolchain for the CDK app alone puts a second build system in the repo.

## Ask in this order

1. `cdk_language` -- confirm it matches a language package in the selection.
2. `placement_dir` -- defaults to `infrastructure`. Use `.` for an IaC-only repo.
3. `project_name` -- recorded in the answers file. `cdk init` names the app after
   the directory, so this answer does not reach the generated code. Copy it from
   `base` when `base` is in the same selection.

## After rendering

The package renders definitions. It runs no `cdk bootstrap`, no `cdk deploy`, and
no `cdk synth`, and it configures no credentials.

Tell the user what remains:

- Bootstrap the target account and region once with `cdk bootstrap`.
- Run `cdk synth` to check the stack compiles.
- Commit `cdk.context.json` when `cdk synth` creates it. It pins looked-up
  account values.
- Set up the deployment role and the CI authentication. Prefer OIDC over a
  stored cloud key; `ci/index.md` covers it.

`cdk init` writes its own `.gitignore` inside `<placement_dir>`. Reconcile it
with the repo `.gitignore` when the repo folds `.gitignore.d/` fragments.
