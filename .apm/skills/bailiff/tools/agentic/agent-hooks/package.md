---
name: agent-hooks
summary: Declares which languages the agent tool-boundary hooks run commands for
provides: [agentic:hooks]
after: [base, python, ts, go, rust, api]
---

## Renders

| Path | Content |
|---|---|
| `.agents/hooks/quality-languages` | The sorted unique `hook_languages` entries, one per line |
| `.gitignore.d/agent-hooks` | Ignores Aider working files, keeps its config files tracked |

The rendered filename stays `quality-languages` because the hook runner reads
that exact path. An empty `hook_languages` list suppresses the file: the
`.agents` directory name is a jinja conditional on the answer.

The file declares language names. A hook runner installed separately reads that
list and decides which commands to run at each agent tool boundary. This package
installs no runner and defines no command.

## Ask in this order

1. `hook_languages` -- the language identifiers. Derive the list from the language
   packages in the selection rather than asking the user to retype it: `python`
   for `python`, `typescript` for `ts`, `go` for `go`, `rust` for `rust`. Confirm
   the derived list with the user before rendering.

Render after the language packages, so the list matches what the repo has.

## After rendering

- The file names languages, not commands. Install a hook runner that reads
  `.agents/hooks/quality-languages`, or the file has no effect.
- Adding a language later means adding a line and keeping the file sorted.
- The `.gitignore.d/agent-hooks` fragment is inert until something folds
  `.gitignore.d/` into `.gitignore`.
