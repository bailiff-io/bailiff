---
name: beads
summary: Beads issue tracker bootstrapped by bd init, with per-assistant integration
provides: [tracker:issues]
after: [base, agentic]
requires_bin: [bd]
precheck: precheck.py
---

## Renders

Copier writes `.copier-answers.beads.yml` and nothing else. Every other file comes
from the task, which runs `bd init --init-if-missing --non-interactive
--skip-agents` and then one `bd setup <harness>` per selected assistant.

| Path | Written by |
|---|---|
| `.beads/config.yaml`, `.beads/metadata.json`, `.beads/README.md` | `bd init` |
| `.beads/embeddeddolt/` | `bd init`, the Dolt database holding the issues |
| `.beads/hooks/` | `bd init`, only with `bd_install_git_hooks` |
| `.gitignore` | `bd init` appends `.dolt/`, `*.db`, `.beads-credential-key`, `.beads/proxieddb/` |
| `.claude/settings.json`, `CLAUDE.md`, `.agents/skills/beads/` | `bd setup claude` |
| `.codex/config.toml`, `.codex/hooks.json`, `AGENTS.md` section | `bd setup codex` |
| `.cursor/rules/beads.mdc` | `bd setup cursor` |

`--init-if-missing` makes a second run exit 0. Without it a re-run aborts.

## Why --skip-agents, always

`bd init` without that flag installs the claude and codex integrations whether or
not the user asked for them, and writes `AGENTS.md` and `CLAUDE.md`. A repo whose
user runs neither assistant would still get both. `--skip-agents` suppresses all
of it, so `bd_harnesses` is the only thing that decides which assistant files
appear.

Each `bd setup <harness>` recipe appends a delimited block to the file it targets:
`<!-- BEGIN BEADS CODEX SETUP -->` in `AGENTS.md`, `<!-- BEGIN BEADS INTEGRATION
... -->` in `CLAUDE.md`. Content above the marker survives, and a re-run rewrites
the block in place.

## AGENTS.md, shared with the agentic package

Both packages write `AGENTS.md`, so `after: [agentic]` renders `agentic` first and
`bd setup codex` appends to the file it wrote.

Do not run this package before `agentic`. `agentic` renders `AGENTS.md` whole and
would drop the beads block.

`bd setup claude` merges into an existing `.claude/settings.json` rather than
replacing it: it adds a `SessionStart` hook running `bd prime --hook-json` and
leaves the keys `agentic` wrote intact.

## Ask in this order

1. `bd_harnesses` -- which assistants the user runs. Set this from the
   `agentic_targets` answer when `agentic` is in the same selection. The recipe
   list is wider than `agentic_targets`: `aider`, `claude`, `codex`, `cody`,
   `copilot`, `cursor`, `factory`, `gemini`, `junie`, `kilocode`, `mux`,
   `opencode`, `windsurf`.
2. `bd_prefix` -- the issue id prefix. Empty uses the destination directory name.
   Every issue id carries it, so ask when the directory name is long or generic.
3. `bd_dolt_sync` -- `git-origin` keeps the Dolt remote that `bd init` derives
   from the repo's git origin, which is what lets the database survive a reclone.
   `local-only` removes that remote, keeping the issues on one machine.
4. `bd_install_git_hooks` -- defaults to `false`. `true` points `core.hooksPath`
   at `.beads/hooks`, which displaces any other hook manager. Keep it `false`
   whenever `lefthook` or `precommit` is in the selection.
5. `bd_github_sync` -- whether to mirror issues to GitHub issues. Independent of
   `bd_dolt_sync`: Dolt moves the database, GitHub mirrors the issues.
6. `bd_github_owner` and `bd_github_repo` -- asked only when `bd_github_sync` is
   `true`. `bd` derives neither from the git origin, so both answers are needed.
7. `bd_auto_export` -- writes `.beads/issues.jsonl` after each write. Needed only
   by a viewer such as `bv`. The Dolt database stays the source of truth.

## Requirements

- `bd` on PATH. `render.py` exits 3 without it.
- The destination must already be a git repository. `precheck.py` checks it and
  exits 1 otherwise, before anything is written. `base` runs `git init`.

## Secrets

The GitHub token is never a question and never enters an answers file. Fetch it at
the point of use:

```sh
GITHUB_TOKEN=$(gh auth token) bd github sync
```

`bd github status` reports the token as not set until `GITHUB_TOKEN` is in the
environment. Nothing about it is persisted.

## After rendering

- `bd init` makes its own commit, "bd init: initialize beads issue tracking".
  Expect a commit that no agent authored.
- Issues live in the embedded Dolt database, not in `.beads/issues.jsonl`. With
  `bd_dolt_sync: git-origin`, run `bd dolt push` to move them between machines.
- Run `bd quickstart` to create the first issue.
