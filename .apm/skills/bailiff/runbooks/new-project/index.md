# Runbook: new single project

An empty or near-empty directory, with neither a git history nor source to read.
The user decides the project's shape in the interview; you have no repo to infer
it from.

## Interview order

Ask one question, wait, then ask the next. Each answer narrows what you offer
next, so asking ahead wastes the user's attention on options you will withdraw.

1. **What is this project?** One sentence. This becomes `description` and it tells
   you whether to offer a language, an API contract, or infrastructure.
2. **Name and owner.** `project_name` and `org`.
3. **Language.** Offer what `languages/` reports. Take one.
4. **Runtime version and package manager.** From the language package's
   `questions`, using its `choices` verbatim.
5. **Repo host.** Ask whether they want the remote created now or later.
6. **CI.** Ask whether the project needs CI at all before offering job packages.
7. **The optional groups.** Visit `hooks/`, `repo/` release, `docs/`, `iac/`,
   `agentic/`, `workspace/` in that order. For each, state what it gives them and
   ask whether they want it. Accept "no" without arguing.

## Render order

```
foundation/base
languages/<pick>
foundation/readme
foundation/editorconfig
repo/github-repo          (or gitlab-repo)
hooks/<pick>
ci/<host>, then each ci/<job>
repo/<release tool>
repo/dep-updates
docs/*, iac/*, agentic/*, workspace/*
```

`base` first because everything else takes `project_name` and `description` from
its answers. Language before hooks and CI because both read what the language
packages wrote.

A framework scaffold breaks that order. `create-vite` and `nuxi init` refuse a
directory that holds files, so they run before `foundation/base`, not after it:
scaffold into the empty destination, then render `base` and the language package
over the result. `languages/ts/package.md` carries the commands and their
non-interactive flags. `ts_framework: sst` has no non-interactive path at all --
tell the user to run `npx sst@4 init` and continue once they have.

## What to recommend

Recommend, then accept what the user says.

| Group | Recommend for a new project |
|---|---|
| `foundation` | base, readme, editorconfig |
| `hooks` | lefthook |
| `ci` | The host they chose, plus test and lint for their language |
| `repo` | The host, and dep-updates with renovate |
| `agentic` | agentic, when they say they use coding agents |

Recommend nothing from `iac/` or `docs/` unprompted. A new project has no
infrastructure to describe and no audience to document for yet.

## After rendering

Run the project's own verification and report what it says:

```sh
git -C <dest> status --short
```

Then name the commands the user runs next: the toolchain install, the dependency
install, the test command. Take them from the language package's `package.md`.

The rendered tree holds no commit. Tell the user that and let them make the first
commit themselves, unless they ask you to.
