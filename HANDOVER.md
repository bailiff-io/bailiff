# Handover

Work state for bailiff v2 tooling. Task tracking is in beads (`bd ready`), not
here. This file records what is decided, what is verified, and what is unknown.

Last updated: 2026-07-28, after commit `5910701`.

## Where to look

| For | Read |
|---|---|
| Open work, priorities, dependencies | `bd ready`, `bd list` |
| Why a package is shaped as it is | that package's `package.md` |
| Architecture | `docs/specs/bailiff-v2.md` |
| Package rules | `.apm/skills/bailiff/packages/CONTRACT.md` |

## Landed this session

| Commit | What |
|---|---|
| `77aa38a` | `moon` and `package-add` into `repo/`; cocogitto `after: [base]` |
| `a6e05bd` | prek as a third hook manager (superseded by `9b714a4`) |
| `9b714a4` | hooks split into `baseline` + `manager`; CI defaults hardened |
| `3375ec2` | `fold_gitignore.py` deduplicated, 7 copies to 1 |
| `7067e7b` | Python type checker, coverage, deptry, docstring rules, nox |
| `dbb4fb4` | TS: eslint dropped for oxlint, plus tsc, knip, coverage |
| `eaf3e00` | Rust: cargo-deny, cargo-machete, cargo-llvm-cov, doc lints |
| `3ca5225` | Go: gosec and revive enabled, govulncheck, tidy check |
| `4e40b16` | ci/: five language packages collapsed into one host package |
| `c58c36e` | CI quality job; structkit recorded as considered and rejected |
| `384c083` | publish jobs with OIDC trusted publishing |
| `ca11aab` | SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md |

## Decisions that govern the remaining work

These came from the user and are not open for re-litigation.

- **Mutually exclusive options become one copier question, not one package per
  option.** The hooks group proved it: 4 packages became 2, and the manager
  choice is a `hook_manager` enum. Apply the same to `release:tool` (7+ options),
  `workspace:tasks` (justfile/taskfile), and `docs:site`.
- **A category holds one kind of thing.** Do not mix a real either/or with a
  boolean-in-costume in the same group.
- **prek is the default hook manager.** It reads pre-commit's config format
  unchanged and needs no Python runtime. Offer `pre-commit` only when asked for
  by name.
- **eslint is dropped.** `ts_linter` is `biome` or `oxlint`.
- **betterleaks over gitleaks** for commit-time scanning, with trufflehog
  verifying credentials against live APIs. CodeRabbit independently ships
  betterleaks.
- **opengrep over semgrep** for security rules.
- **Sample projects are generated with `claude -p` and no steering beyond a plain
  project-creation prompt.** The point is to test the steering, not to drive the
  scripts by hand.

## Verified facts worth not rediscovering

**copier 9.17.0 enforces all four cardinalities natively**, which is why the
`scan.py` cardinality lint was dropped in favour of enums:

| Cardinality | Mechanism |
|---|---|
| exactly one | `choices:` |
| at most one | `choices:` including a none member |
| zero or more | `multiselect: true` |
| one or more | `multiselect: true` + `validator:` erroring on empty |

Also verified in copier:

- `validator:` is a jinja render with the answer in scope, so it can read prior
  answers and `_external_data`, and supports `regex_search`.
- `_external_data` resolves **relative to the destination**, so a package can
  read a sibling's `.copier-answers.*.yml` directly. A missing file warns and
  falls back to the default, so packages still render standalone. This is the
  mechanism for `bfsh-d89` (one answers file per destination).
- `copier.yml` is parsed as YAML **before** jinja renders it. Top-level
  `{% set %}` blocks fail with "found character '%' that cannot start any token".
  Use inline expressions inside a value.
- Conditional filenames need a guard per path segment, which is why
  `agentic/agentic` has a two-clause condition repeated in one path.
- **A conditional filename must contain no quote character.** jinja compiles each
  template with the filename embedded in the generated Python, so a quote in the
  path breaks that string literal. `{% if "python" in ci_languages %}` in a name
  raises a `SyntaxError` pointing at an unrelated line of the file body. Use a
  derived boolean carrying `when: false` instead. This cost an hour to diagnose.
- A `yaml`-typed answer whose default is a jinja expression needs `| tojson`. A
  jinja list renders as a Python repr with single quotes, which the YAML parser
  rejects.

**Measured hook timings** (212-file repo, warm), which decided the
commit-vs-CI split:

| Tool | Time |
|---|---|
| actionlint | 44-154ms |
| zizmor `--offline` | 54ms |
| lychee `--offline` | 64ms |
| scc | 199ms |
| lizard (12 files) | 208ms |
| taplo | 399ms |
| yamllint | 1.1s |
| markdownlint-cli2 | 1.2s |
| pinact (network) | 1.4s |
| cspell | 1.7s |
| lizard (212 files) | 3.1s |

**Tool behaviour confirmed by running it:**

- `prek` supports `repo: builtin` (26 hygiene hooks, no clone, offline) and hook
  `groups:`. pre-commit rejects `repo: builtin` with "Missing required key: rev",
  so `use_builtin_hygiene` must match `hook_manager`.
- zizmor's `unpinned-uses` audit rejects a tag on **any** action including
  `actions/*`. Every template is now SHA-pinned because baseline runs zizmor.
- ruff `DOC` rules are preview-gated and silently do nothing without
  `preview = true`.
- ruff has no per-rule severity, so warn-vs-block needs two invocations.
- gitleaks and betterleaks found the same 4 of 7 planted secrets with 0 false
  positives; trufflehog found 3 including an AWS key pair both missed. AWS's
  documented example key is allowlisted, which made an early test look like a
  miss.
- `on.push.paths` cannot replace job-level path filtering: it gates the whole
  workflow, and a workflow that never runs leaves required checks pending
  forever, so a docs-only PR cannot merge.

## Bugs found by testing rather than reading

Each of these would have failed at first use. They are the argument for rendering
and running rather than reviewing the template.

| Package | Bug |
|---|---|
| `languages/go` | `gosec` ships inside golangci-lint and was never enabled, so Go had no security lint |
| `languages/go` | the settings block used v1's top-level `linters-settings`, which golangci v2 rejects outright |
| `languages/rust` | `cargo init` writes no `license` key, so cargo-deny failed the licences check on the project's own crate |
| `languages/ts` | `bun exec` is not a command; every fragment would have failed with "command not found" |
| `languages/python` | ruff `DOC` rules are preview-gated and silently checked nothing |
| `languages/python` | `D` in `select` made a bare `ruff check` fail, defeating the advisory intent |
| `ci/*` | `actions/*` pinned by tag failed the zizmor hook the same catalog installs |
| `ci/github` | a conditional FILENAME containing a quote character breaks jinja compilation |
| `ci/github` | a `yaml`-typed answer needs `\| tojson`, since a jinja list renders as a Python repr |

## structkit: rejection reopened (`bfsh-asl`, P0)

The user pushed back on 2026-07-28: the tool exists primarily for one person, so
if static templates with fixed preferences suffice, the hook-templating limitation
stops mattering. **The pushback holds.**

With the hook manager, package managers, linters, CI host, and release tool fixed
rather than asked, 9 of 17 task categories become "commit the file" and the other
8 become unconditional one-liners that structkit hooks run today. Only `go mod
init` and `cdk init` need a value, and it is one the user types anyway.

What is genuinely variable is the language and the licence, which is directory
selection rather than templating.

All seven bugs found this week came from *generating* configuration rather than
committing it, which argues the same way.

This is now an open P0 decision. Do not add to the copier catalog before it is
resolved.

## structkit, the original analysis

`httpdss/structkit` (Apache-2.0, v3.2.1) overlaps substantially and was evaluated
properly rather than dismissed. Verified by running it:

- Remote content works: `file: github://github/gitignore/main/Python.gitignore`
  fetches correctly. Better than the `scripts/` dedup, tracked as `bfsh-ehp`.
- File content is templated. **Hook commands are not.** A post-hook of
  `echo "NAME_IS {{@ name @}}"` printed the literal braces while a file in the
  same structure rendered the value, and a jinja conditional in a hook failed
  outright.

That was read as a blocker, and it is not one at single-user scope. See above.

## The decision, as it now stands (`bfsh-asl`, P0)

The landscape survey is complete, and the answer is the user's own proposal:
**keep copier as the renderer, keep the 161 template files, hard-code the
preferences, delete the machinery, and let the agent compute the derived parts.**

The survey found nothing that justifies replacing copier. What is worth taking
from elsewhere:

| Source | What to take |
|---|---|
| `moon codegen` (already in use) | `extends:` for template inheritance, and per-file frontmatter for skip/force/destination -- conditional inclusion declared inside the file rather than encoded in its name |
| better-t-stack | a declarative option schema as the single source of truth, with cross-option constraints beside the options |

better-t-stack's `superRefine` is the cardinality check filed as `bfsh-uub` and
never built. One zod file there yields the CLI flags, the prompts, the web builder
UI, a JSON schema, and the validation. The equivalent here is a small YAML or
Python file the skill reads.

What the fourth option costs, stated plainly: no `copier update` on existing
projects. A template improvement does not propagate; re-render and diff instead.

## structkit adoption is ON HOLD

The user, after a day of hands-on use: "i'm not sure if structkit is the right fit
after all." Warranted, and the reason is not capability.

Documented behaviours that turned out not to exist, each caught by testing rather
than reading:

| Documented | Reality |
|---|---|
| Variables in hooks, with two worked examples | Hooks are never rendered. `generate.py:132` loads YAML, `:201` reads the hooks, `:100` runs `subprocess.run(shell=True)`, with no render between |
| `completion install` offers fish | shtab has no fish support; `SUPPORTED_SHELLS` is bash, zsh, tcsh |
| `prompt:` generates file content | With no API key it writes the string `AI generation skipped: ...` into the file as its content |

The capabilities below are all verified and good. The concern is that the
documentation cannot be trusted as a specification, so every feature costs a test
before use, which works against the reason for adopting a scaffolding tool. Bus
factor is also one: `httpdss` holds 372 of 376 commits.

The live options are structkit, the existing copier catalog, or a tool the
landscape survey turns up. Do not decide before that survey returns.

## structkit capability research (done)

`docs/specs/structkit-architecture.md` holds the full proposal. Verified against
3.2.1, and these are the findings that decide the architecture:

- **Structures stack.** A `folders:` entry takes a `struct:` list, each with its
  own `with:` variables.
- **A monorepo package can be added later** by rendering at its subpath. A
  hand-edited sibling file survived untouched, which replaces the whole
  `repo/package-add` runbook.
- **Named sources** live in `~/.config/structkit/sources.yaml`, so the templates
  repo is registered once and referenced by name. A chezmoi target.
- **Do not reuse the bundled `project/*` structures.** `project/python` ships
  `setup.py`, `setup.cfg`, `requirements.txt`, a `Makefile`, and fetches
  structkit's own `LICENSE`. It declares no variables. The single-purpose
  `configs/*` ones are fine.
- **The `prompt:` key is excluded.** It generates file content through pydantic-ai
  at render time, and with no `OPENAI_API_KEY` it writes the string
  `AI generation skipped: ...` into the file as content. `AI_MODEL` does route to
  Claude, since pydantic-ai supports it.
- **`structkit` package added to agentic-packages** with the MCP server and a
  hand-written skill, at `0c89cc7d2` and `7d2ec48c2` in that repo.
- **Upstream bug:** `completion install` advertises fish and
  `--print-completion fish` rejects it. Tracked as `bfsh-dt8`.

## Unknowns and open questions

- **Container base image policy** (`bfsh-u95`). distroless vs slim vs alpine, and
  who owns the Dockerfile when a framework (nuxi, sst) generates one. Needs a
  decision before the container group can be written.
- **GitLab** (`bfsh-wr1`). `repo/gitlab-repo` is offered but `ci:host` has only
  github, so choosing GitLab yields a repo with no CI. Either build the host or
  drop the package; the user leaned toward building it.
- **Group renaming** (`bfsh-yoo`). Filed as a decision to be made. The rename
  invalidates every `<group>/<package>` id and buys tidiness rather than
  correctness. 16 of 33 axes hold exactly one package, so axis-as-directory would
  create single-member directories.
- **`depends_on` deletion** (`bfsh-ypu`) deliberately deferred, not blocked. All
  7 edges are subsets of `after:`, so they carry no ordering, but deleting them
  also deletes the only machine check that a dependent package was selected
  without its requirement. Revisit after the CI collapse removes 5 of the 7.
- **`install_hooks: true` is untestable on this machine.** git-defender owns a
  global `core.hooksPath`, so `lefthook install` fails with a permission error on
  `/usr/local/amazon/var/git-defender/hooks/`. Hook *installation* is therefore
  unverified; hook *config* is verified via `lefthook validate` and
  `prek validate-config`.
- **The global mise config at `~/.config/mise/conf.d/20-core-cli.toml:12` has a
  malformed key**, `pipx:structkit = "latest"`, which needs quoting. Until it is
  fixed every `mise install` fails, which makes six integration tests fail for
  environmental reasons rather than code ones. The user added it and owns the fix.
- **`scan.py`'s `axes` field contradicts four group indexes.** It keys an axis on
  the namespace before the colon, so `docs:site` and `docs:decisions` both
  collapse to `docs`. Any lint built on it would reject `mkdocs +
  decision-records`, which `docs/index.md` explicitly permits. This already bit
  once: `repo:monorepo` merged into `repo:host` and broke a test, which is why
  `moon`/`package-add` now tag `monorepo:*`.

## Sequencing

`bfsh-2sx` (collapse `ci/` to one package per host) gates the most: publish jobs,
coverage jobs, the container job, GitLab, and JVM all become answers inside one
package rather than ~15 new packages. Its own risk, raised by the challenger that
proposed it: a 6-language x 6-job matrix means ~36 conditional filenames with no
lint that any is reachable. Mitigate with a rendered-file-set test per selection.
