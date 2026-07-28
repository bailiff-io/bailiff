# iac

Infrastructure definitions.

| Axis | How many | Packages |
|---|---|---|
| `iac:tool` | At most one per deployment target | terraform, cdk, cloudformation |

## Usually one

Most projects take one. A project takes two when it genuinely has separate
targets: Terraform for shared account-level infrastructure, CDK for the
application stack. Ask which target each covers before rendering both, and give
each a distinct destination directory.

Offer nothing here when the user has not described infrastructure. An unused
`terraform/` directory is a maintenance obligation with no return.

| Choose | When |
|---|---|
| `terraform` | Multi-cloud, or the user names Terraform or OpenTofu |
| `cdk` | AWS only, and the project already has TypeScript or Python |
| `cloudformation` | AWS only, and the user wants no build step between source and template |

`cdk` needs a language package for its own toolchain. Confirm the CDK language
matches one the project already has rather than adding a language for CDK alone.

## State and credentials

These packages render definitions. They configure no remote state backend and no
credentials, and they run no `apply`.

Tell the user what remains: the state backend, the deployment role, and the CI
authentication. `ci/index.md` covers OIDC, which is the path to prefer over a
stored cloud key.
