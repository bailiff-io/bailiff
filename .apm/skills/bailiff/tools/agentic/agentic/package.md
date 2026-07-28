---
name: agentic
summary: Per-harness agent configuration and the AGENTS.md every harness reads
provides: [agentic:config]
after: [base]
---

## Renders

`AGENTS.md` always. Everything else is a conditional path keyed on
`agentic_targets`:

| Harness | Paths |
|---|---|
| `claude` | `.claude/settings.json`, plus `.mcp.json` when `mcp_config` |
| `codex` | `.codex/config.toml`, plus `.agents/plugins/marketplace.json` when `native_marketplace` |
| `opencode` | `opencode.json` |
| `kiro` | `.kiro/steering/project.md`, plus `.kiro/settings/mcp.json` when `mcp_config`, plus `.kiro/agents/agents.json` when `kiro_cli_agents` |

An empty `agentic_targets` renders `AGENTS.md` and the answers file, nothing more.

`.kiro/steering/project.md` carries `_skip_if_exists`.

## Ask in this order

1. `agentic_targets` -- which harnesses the user actually runs. Each entry adds
   files a user of a different harness never opens, so do not offer the full set
   by default.
2. `mcp_config` -- whether to commit an MCP server list. Only worth `true` when
   the user can name the servers.
3. `mcp_servers` -- ask only when `mcp_config` is `true`. Each entry is
   `{name, command, args, env}`.
4. `native_marketplace` -- Claude and Codex only. `true` has no effect for
   `opencode` or `kiro`.
5. `agentic_plugins` -- ask only when `native_marketplace` is `true`. Each entry is
   `{name, owner_repo}`.
6. `kiro_cli_agents` -- ask only when `kiro` is among the targets.
7. `project_name` -- copy from `base` when `base` is in the same selection.

## Secrets

Write every MCP `env` value as a `${VAR}` reference. Copier records a literal
token in `.copier-answers.agentic.yml`, which is committed. The user supplies the
token itself through the environment, out of band.

## Interaction with other packages

- `apm` handles APM package installation. Set its `apm_target` answer from
  `agentic_targets` so the two agree on which harnesses the repo targets.
- `beads` also writes `AGENTS.md`. Render this package first; `beads` appends its
  block to the file this package wrote. See `beads/package.md`.

## After rendering

Marketplace plugin registration and the Kiro MCP toggle are steps no committed
file can carry. The rendered `AGENTS.md` lists whichever ones apply.
