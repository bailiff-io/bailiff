---
name: github-repo
summary: GitHub forge metadata (CODEOWNERS, issue and PR templates), optional remote creation
provides: [repo:host]
after: [base]
precheck: precheck.py
---

Renders:

- `.github/CODEOWNERS` with `* @<org>`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md`

The `.github/` files render whether or not the remote is created. `create_remote:
false` still writes all four.

## Questions, in order

1. `project_name` -- the repository name passed to `gh repo create`. Thread the value you already collected for `base`.
2. `org` -- GitHub owner or team handle written into CODEOWNERS. Thread the value from `base`.
3. `create_remote` -- `true` runs `gh repo create`, `false` renders metadata only.
4. `visibility` -- `private`, `public`, or `internal`.
5. `public_confirm` -- ask only when `visibility: public` and `create_remote: true`.
6. `remote_protocol` -- `https` or `ssh`, passed to `gh config set git_protocol`.
7. `push_after_create` -- `true` runs `git push -u origin HEAD` after creation.
8. `team` -- GitHub team slug granted access. Empty omits the `--team` flag.

## The public gate

State the visibility answer back to the user in words before you render, for
example "this will create github.com/acme/widget as a public repository, visible
to anyone". Wait for the user to confirm.

`precheck.py` blocks the render when `visibility: public` and `create_remote:
true` unless `public_confirm` equals `project_name` exactly. A wrong or empty
`public_confirm` exits 3 and writes nothing. Do not fill `public_confirm` in from
`project_name` on your own; the user has to say it.

`gh repo create --public` publishes the repository the moment it runs, and no
later step undoes that.

## Failure behavior

`gh` is not in `requires_bin`. When `gh` is missing or any `gh` call fails, the
tasks print a message and exit 0, so the rendered `.github/` files survive. Tell
the user which step did not run and what to run by hand.

## After rendering

The user supplies GitHub credentials out of band. `gh` reads its own auth (`gh
auth login` or an ambient `GITHUB_TOKEN`); no token enters an answers file.

Check `git remote -v` after a `create_remote: true` run to confirm `origin`
exists.
