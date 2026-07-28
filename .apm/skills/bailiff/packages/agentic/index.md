# agentic

Configuration for coding agents working in the repository.

| Axis | How many | Packages |
|---|---|---|
| `agentic:config` | At most one | agentic |
| `agentic:packages` | At most one | apm |
| `agentic:hooks` | At most one | agent-hooks |
| `tracker:issues` | At most one | beads |

Independent axes. Nothing here is required, and a repo with no agent use takes
none of it.

## agentic

Renders per-harness configuration from the `agentic_targets` answer: `claude`,
`codex`, `kiro`, `opencode`. Ask which of these the user actually runs. Each target adds
files that a user of a different agent harness will never open.

It also renders `AGENTS.md`, which every harness reads.

## apm

Renders `apm.yml` for a repo that publishes or consumes APM packages. Offer it
when the user describes authoring skills, agents, or steering for distribution.
A repo that merely uses agents does not need it.

## agent-hooks

Renders `.agents/hooks/quality-languages`, the language list a separately
installed hook runner reads to decide which commands run at agent tool
boundaries. Render it after the language packages, whose answers it reads.

## beads

Renders nothing that copier owns. Its task runs `bd init --init-if-missing
--non-interactive --skip-agents`, which creates `.beads/` and the Dolt database.
The `--init-if-missing` flag makes a second run exit zero rather than fail.
`--skip-agents` keeps `bd init` from installing the claude and codex integrations
unasked, so the `bd_harnesses` answer decides those: the task runs one
`bd setup <harness>` per selected assistant.

Offer `beads` when the user describes multi-agent work, long-running task
tracking, or work spanning sessions. A single-session project does not need it.

`beads` needs `bd` on PATH and needs the destination to be a git repository.
`render.py` checks both and exits 3 when either is missing.

## Order

Render `base` first for `project_name`. Render `agent-hooks` after the language
packages. `beads` needs `git init` to have run, which `base` does.

Render `beads` after `agentic`. Both write `AGENTS.md`: `agentic` renders the
whole file, then `bd setup codex` appends a delimited block to it. The reverse
order drops the beads block.
