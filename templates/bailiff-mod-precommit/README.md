# bailiff-mod-precommit

Copier module that manages Git hook configuration for a project using pre-commit.
Assembles `.pre-commit-config.yaml` from a fragment/merge model: each contributing
module writes a `.pre-commit.d/<name>.yaml` fragment; this module's bundler
post-task merges them after the full render loop.

Selecting this module is choosing pre-commit as the hook manager. Lefthook support
is a separate module (`bailiff-mod-lefthook`, spec 015).

## Usage

```sh
copier copy https://github.com/bailiff-io/bailiff-mod-precommit.git <destination>
```

## Questions

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enforce_conventional_commits` | bool | `true` | Add Conventional Commits commit-msg hook |
| `enable_typo_check` | bool | `true` | Add typo-check hook (crate-ci/typos) |
| `precommit_exclude_patterns` | yaml | `[]` | Extra exclude patterns for `.pre-commit-config.yaml` |
| `install_hooks` | bool | `true` | Run `pre-commit install` on init |

## Outputs

- `.pre-commit.d/bailiff-mod-precommit.yaml` — fragment (always written)
- `.pre-commit-config.yaml` — assembled by bundler post-task from all `.pre-commit.d/` fragments
- `.pre-commit-hooks/check-commit-msg.py` — vendored Conventional Commits validator (MANAGED)

## Dependencies

`depends_on: [bailiff-mod-base]`
