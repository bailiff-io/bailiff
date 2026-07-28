---
name: baseline
summary: Repo-wide hook checks, rendered into both fragment schemas from one answer set
provides: [hooks:baseline]
after: [base]
---

## Renders

| Path | Contents |
|---|---|
| `.pre-commit.d/baseline.yaml` | the checks in pre-commit's schema, read by `manager` when `hook_manager` is `prek` or `pre-commit` |
| `.hooks.d/baseline.yaml` | the same checks in lefthook's schema |
| `.hooks-bin/check-commit-msg.py` | Conventional Commits validator, called by both |
| `.mise/conf.d/hooks.toml` | pins every binary the checks call |
| `.copier-answers.baseline.yml` | the answers |

## Why the checks live here and not in the manager packages

pre-commit installs each hook from a pinned upstream repo; lefthook runs commands
against `{staged_files}`. Neither schema can express the other, so the fragments
differ in form.

What they must not differ in is content. Rendering both from one answer set is
what prevents that: a project that picks `lefthook` gets the same secret scan,
typo check, shell lint, and commit-message rule as one that picks `precommit`.
Before this package existed the checks lived in `precommit`'s own fragment, so
choosing `lefthook` silently dropped every one of them.

The manager packages render no hook definitions. They render the manager's entry
point and install the git hooks.

`.mise/conf.d/hooks.toml` is the other half. pre-commit fetches its own pinned
copy of each hook; lefthook runs what is on PATH. Pinning the same versions in
mise is what makes `gitleaks` mean one version regardless of manager.

## Offer it with any hook manager

Offer `baseline` whenever the user takes a hook manager, and default it on. It
renders both schemas unconditionally, and the unused fragment costs nothing: a
manager reads only its own directory.

Rendering it without a manager writes fragments nothing reads. Say so rather
than rendering it alone.

## Ask

Take the hygiene and secret answers first, then the file-type checks, then the
ones that default off.

| # | Question | Default | What it adds |
|---|---|---|---|
| 1 | `check_hygiene` | true | whitespace, EOF newline, YAML/TOML syntax, merge markers, large files |
| 2 | `max_file_kb` | 500 | the large-file limit; raise it for a repo committing fixtures |
| 3 | `check_secrets` | true | a regex secret scan on the staged index |
| 4 | `secret_scanner` | betterleaks | `betterleaks` or `gitleaks` |
| 5 | `check_secrets_verified` | true | trufflehog, which verifies a credential against its API |
| 6 | `check_typos` | true | typos |
| 7 | `check_shell` | true | shellcheck; offer false when the repo holds no shell scripts |
| 8 | `check_workflows` | true | actionlint and zizmor; offer false when there is no `.github/workflows` |
| 9 | `check_toml` | true | taplo |
| 10 | `check_links` | true | lychee, offline only |
| 11 | `check_complexity` | false | lizard thresholds, which fail the commit |
| 12 | `complexity_ccn` / `_length` / `_args` | 15 / 80 / 6 | the thresholds, asked only when 11 is true |
| 13 | `show_repo_stats` | false | a non-blocking scc summary |
| 14 | `enforce_conventional_commits` | true | the commit-msg hook |
| 15 | `hook_exclude_patterns` | `[]` | regexes for vendored or generated trees |

Keep `check_secrets_verified` on for any repo that will be public. The regex
scanners and trufflehog find different things: in a fixture of seven planted
credentials, the regex scanners caught four and trufflehog caught three,
including an AWS key pair both regex scanners missed.

Recommend `enforce_conventional_commits` whenever the user picked `cocogitto` or
`release-please`, because both read conventional commits to compute a version.

## What defaults off, and why

`check_complexity` fails a commit whose staged functions exceed a threshold,
which is a policy a team has to agree to rather than a default. Offer it when the
user asks for complexity limits.

`show_repo_stats` prints line counts and cannot fail: scc has no threshold flag.
Offer it to a user who wants the shape of a commit reported back.

## Ordering

Render `baseline` before `manager`. When `hook_manager` is `prek` or
`pre-commit`, the merge runs at render time, so a fragment written afterwards
does not reach `.pre-commit-config.yaml` until `manager` re-renders. `lefthook`
expands its glob at hook time and picks up a later fragment on its own.

## After rendering

`hook_exclude_patterns` reaches only the pre-commit schema, because lefthook
scopes exclusions per command rather than globally. A project on lefthook that
needs an exclusion takes a `glob:` on the command in question, which means
editing the fragment. Tell the user when you rendered a non-empty exclude list
alongside `lefthook`.
