---
name: dep-updates
summary: Automated dependency updates via renovate or dependabot
provides: [deps:updates]
after: [base]
---

Renders one file, chosen by `dep_update_tool`:

| Answer | Path | Contents |
|---|---|---|
| `renovate` | `renovate.json` | `$schema`, `extends: [config:recommended]`, and `enabledManagers` when ecosystems are listed |
| `dependabot` | `.github/dependabot.yml` | `version: 2` and one `updates` entry per ecosystem |

The unchosen tool's file is neither written nor deleted. Switching tools on a
live project means deleting the old config by hand.

With `dep_ecosystems: []`, the dependabot config falls back to a single
`github-actions` entry and the renovate config omits `enabledManagers`, which
leaves renovate's own manager detection in charge.

## Questions, in order

1. `dep_update_tool` -- `renovate` or `dependabot`. Confirm the answer before rendering, because the switch is a manual cleanup later.
2. `dep_ecosystems` -- a YAML list of ecosystem ids in the chosen tool's vocabulary. Derive it from the language packages the project has, read the list back to the user, and leave it `[]` when unsure.

Vocabularies differ between the two tools. Dependabot takes values such as
`pip`, `npm`, `cargo`, `gomod`, `github-actions`; renovate takes manager names
such as `pip_requirements`, `npm`, `cargo`, `gomod`, `github-actions`. Check the
tool's docs for an ecosystem you have not written before.

## After rendering

The user enables the tool on the forge side. Renovate needs its GitHub App or
GitLab bot installed on the repository; dependabot needs Dependabot version
updates enabled in the repository settings. No token enters an answers file.
