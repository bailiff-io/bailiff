# Runbook: polyrepo

Several separate repos that share conventions. Each repo gets its own full setup;
what makes this a distinct scenario is that the answers must agree across them.

## Establish the shared set first

Ask for the conventions once, before touching any repo. These are the answers you
will reuse verbatim:

1. **`org`** and **`default_branch`**.
2. **Repo host**, and whether remotes get created now.
3. **Hook manager**, one for all repos.
4. **CI host** and the composition patterns.
5. **Release tool** and **dep-updates tool**.
6. **Agentic configuration**, when they use it.

Write these into a shared answers fragment and copy it into each repo's answers
file:

```yaml
# /tmp/bailiff-answers-shared.yml
org: acme
default_branch: main
```

Per repo, only `project_name`, `description`, and the language answers differ.

## Then get the repo list

Ask for the repos and what each does, one at a time. For each, capture the name,
the description, and the language. A repo whose language differs from the others
is fine, and it changes only that repo's language and CI job packages.

## Render one repo completely, then confirm

Run `runbooks/new-project/index.md` or `runbooks/existing-repo/index.md` for the
first repo, whichever its state calls for. Then stop.

Show the user the tree and ask whether this is the shape they want repeated. A
convention the user dislikes is cheap to change in one repo and expensive across
six.

Once they confirm, render the rest without re-asking the shared questions. Ask
per repo only what is specific to it.

## Keep the answers identical

The value of a polyrepo setup is that the repos agree. Copy the shared answers;
do not retype them. A typo in `org` in the fourth repo puts the wrong copyright
holder in its LICENSE, and nothing downstream catches it.

When the user asks to change a shared answer partway through, say which repos
already have the old value and ask whether to re-render those.

## Per-repo differences that are legitimate

| Differs per repo | Stays the same |
|---|---|
| `project_name`, `description` | `org`, `default_branch` |
| language and its version | hook manager |
| CI job packages, following the language | CI host and composition patterns |
| whether infrastructure applies | release tool, dep-updates tool |

## After rendering

Report per repo: the destination, the packages rendered, and the files written.
Then state what is consistent across all of them and what differs, so the user can
see the convention held.

Verify each repo independently. A repo that renders is not a repo that builds; run
each one's install and test command and report the output per repo. When one fails
and the others pass, say which and why rather than reporting a summary.
