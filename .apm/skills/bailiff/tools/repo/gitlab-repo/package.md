---
name: gitlab-repo
summary: GitLab forge metadata (CODEOWNERS, issue and MR templates), optional project creation
provides: [repo:host]
after: [base]
precheck: precheck.py
---

Renders:

- `.gitlab/CODEOWNERS` with `* @<org>`
- `.gitlab/issue_templates/bug_report.md`
- `.gitlab/issue_templates/feature_request.md`
- `.gitlab/merge_request_templates/default.md`

The `.gitlab/` files render whether or not the project is created.
`create_remote: false` still writes all four.

## Questions, in order

1. `project_name` -- lowercased and hyphenated into the created project path. Thread the value you already collected for `base`.
2. `org` -- GitLab group or user handle written into CODEOWNERS. Thread the value from `base`.
3. `create_remote` -- `true` runs `glab repo create`, `false` renders metadata only.
4. `visibility` -- `private`, `public`, or `internal`.
5. `public_confirm` -- ask only when `visibility: public` and `create_remote: true`.
6. `remote_protocol` -- `https` or `ssh`, passed to `glab config set git_protocol`.
7. `push_after_create` -- `true` runs `git push -u origin HEAD` after creation.
8. `team` -- GitLab group path to create the project under. Empty uses the personal namespace.

## The public gate

State the visibility answer back to the user in words before you render. Wait for
the user to confirm.

`precheck.py` blocks the render when `visibility: public` and `create_remote:
true` unless `public_confirm` equals `project_name` exactly. A wrong or empty
`public_confirm` exits 3 and writes nothing. Do not fill `public_confirm` in from
`project_name` on your own; the user has to say it.

## Failure behavior

`glab` is not in `requires_bin`. When `glab` is missing or any `glab` call fails,
the tasks print a message and exit 0, so the rendered `.gitlab/` files survive.
Tell the user which step did not run and what to run by hand.

## After rendering

The user supplies GitLab credentials out of band. `glab` reads its own auth
(`glab auth login` or an ambient `GITLAB_TOKEN`); no token enters an answers file.

`glab repo create` does not take `--source .` the way `gh` does, so `origin` may
be missing after creation. Check `git remote -v` and add the remote by hand when
it is absent.
