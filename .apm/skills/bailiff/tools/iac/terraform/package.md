---
name: terraform
summary: Terraform or OpenTofu skeleton with tflint, mise pins, and gitignore
provides: [iac:tool]
after: [base]
---

## Renders

Under `<placement_dir>`:

| Path | Content |
|---|---|
| `main.tf` | Empty starter with a commented provider block |
| `variables.tf` | Comment showing a variable declaration |
| `outputs.tf` | Comment showing an output declaration |
| `backend.tf` | Commented local and S3 backend examples, none active |
| `terraform.tfvars.example` | Example values to copy to `terraform.tfvars` |
| `versions.tf` | `required_version` for the chosen flavor; `required_providers` commented |
| `.terraform-version` | The flavor's version, for tfenv |
| `.tflint.hcl` | The terraform ruleset enabled; provider rulesets commented |

At the repo root:

| Path | Content |
|---|---|
| `.gitignore.d/terraform` | `.terraform/`, `*.tfstate`, override files, CLI config |
| `.pre-commit.d/terraform.yaml` | `terraform_fmt`, `terraform_validate`, `tflint`, `terraform_trivy` |
| `.mise/conf.d/terraform.toml` | The IaC binary and tflint, at the pinned versions |

`main.tf`, `variables.tf`, `outputs.tf`, `backend.tf`, and
`terraform.tfvars.example` carry `_skip_if_exists`. The fragments are inert when
`precommit` or `mise` is absent from the selection.

## Ask in this order

1. `tf_flavor` -- `terraform` or `opentofu`. This gates the next question and
   changes the backend locking example.
2. `terraform_version` or `opentofu_version` -- whichever the flavor selects.
3. `placement_dir` -- defaults to `infrastructure`. Use `.` for an IaC-only repo.
   When the user also takes a second `iac` package, give each a distinct value.
4. `tflint_version`.
5. `pre_commit_terraform_rev` -- only worth asking when the user takes
   `precommit`. The default is a real tag, so pre-commit accepts the fragment.
6. `project_name` -- appears in the commented S3 backend key. Copy it from `base`
   when `base` is in the same selection.

## After rendering

The package renders definitions. It configures no state backend, sets up no
credentials, and runs no `terraform init` or `terraform apply`.

Tell the user what remains:

- Uncomment and fill in a backend in `backend.tf`. Until then state is local.
- Add the real `required_providers` constraints to `versions.tf`.
- Run `terraform init` or `tofu init` to download providers and write
  `.terraform.lock.hcl`. That lock file belongs in git.
- Set up the deployment role and the CI authentication. Prefer OIDC over a
  stored cloud key; `ci/index.md` covers it.
