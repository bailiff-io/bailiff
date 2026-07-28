---
name: cloudformation
summary: CloudFormation or SAM template with per-environment parameter files
provides: [iac:tool]
after: [base]
---

## Renders

Under `<placement_dir>`:

| Path | Content |
|---|---|
| `template.yaml` | `AWSTemplateFormatVersion`, the description, an `Environment` parameter with one allowed value per environment, empty `Resources` and `Outputs` with commented examples |
| `.cfnlintrc.yaml` | `ignore_checks` from `cfnlint_ignore_rules` |
| `parameters/<env>.json` | One file per entry in `environment_names`, each setting `Environment` to that name |

`template.yaml` carries `_skip_if_exists`. The parameter files come from a task,
which skips any file that already exists. A task writes them because the file
count follows an answer, and copier renders a fixed path set.

`mode: sam` adds the `AWS::Serverless-2016-10-31` transform and a commented
`Globals` block. `mode: raw` writes plain CloudFormation.

## Ask in this order

1. `mode` -- `raw` or `sam`. Ask `sam` only when the user described Lambda or API
   Gateway work.
2. `environment_names` -- defaults to `[dev, prod]`. Drives both the allowed
   values and the parameter file set.
3. `stack_description` -- one line. An empty answer renders a placeholder.
4. `placement_dir` -- defaults to `infrastructure`. Use `.` for an IaC-only repo.
   When the user also takes a second `iac` package, give each a distinct value.
5. `cfnlint_ignore_rules` -- ask only when the user already knows which rules they
   suppress. An empty list is the normal answer.

## After rendering

The package renders definitions. It configures no credentials, calls no
`validate-template`, and deploys no stack.

Tell the user what remains:

- Add real resources to `template.yaml`. Use the AWS pseudo-parameters shown in
  the comments instead of hardcoded account and region values.
- Run `cfn-lint <placement_dir>/template.yaml` to check the template. `cfn-lint`
  is not pinned by this package.
- Fill in the real parameter values per environment.
- Set up the deployment role and the CI authentication. Prefer OIDC over a
  stored cloud key; `ci/index.md` covers it.
