# Runbook: polyrepo

Several separate repos that share conventions. Each repo is a full setup that
delegates to another runbook. What makes this a scenario of its own is that the
shared answers must agree across every repo.

## Rules

1. **Ask the shared answers once, before touching any repo.** Re-asking per repo
   is how the fourth repo ends up with a different `org`.
2. **Render the first repo completely, then stop and confirm.** A convention the
   user dislikes is cheap to change in one repo and expensive across six.
3. **Copy the shared answers, never retype them.** A typo in `org` puts the wrong
   holder in that repo's LICENSE and nothing downstream catches it.
4. **Delegate per repo.** `probe.py` each destination and run
   `../new-project/index.md` or `../existing-repo/index.md` as it reports. Beyond
   the shared set, this runbook holds no interview of its own.
5. **Report per repo.** When one repo's verification fails and the others pass,
   name it. A pass rate is not a result.

## What is shared and what differs

| Differs per repo | Identical across repos |
|---|---|
| `project_name`, `description` | `org`, `default_branch` |
| language and its version | hook manager |
| CI job packages, following the language | CI host and composition patterns |
| whether infrastructure applies | release tool, dep-updates tool |

Ask the right-hand column once, in that order, plus agentic configuration when
they use it. Write the answers into a fragment and copy it into each repo's
answers file:

```yaml
# /tmp/bailiff-answers-shared.yml
org: acme
default_branch: main
```

Then get the repo list: name, description, and language per repo, one at a time.

## When a shared answer changes partway

Say which repos already carry the old value, and ask whether to re-render those.
Changing it only for the repos still to come leaves the set inconsistent in a way
nothing reports.
