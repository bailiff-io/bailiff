<!--
SYNC IMPACT REPORT
==================
Version change: (none) → 1.0.0
Bump rationale: MINOR-baseline — initial roadmap creation. Captures the full
delivery breadth decided during the constitution + grilling session as a
dependency-ordered ledger; only spec 001 is built now, the rest are placeholders
preserving intent.

Changes this revision:
  - Added specs 001–009 + one deferred entry (rewrite/brownfield)
  - Recorded decisions C-01 … C-10 from the grilling session
  - Recorded 3 Open Questions
Specs affected: 001, 002, 003, 004, 005, 006, 007, 008, 009, DEFERRED-rewrite
Open questions added/resolved: added Q1, Q2, Q3; none resolved
Notes: ADRs live in docs/decisions/ (the roadmap loader's default docs/adr/ is not
used by this project). All copier facts here are source-verified against 9.16.0.
-->

# clerk — Spec Roadmap

Living, non-binding map of the specs planned for clerk. It is **not a commitment to
order or scope** — it captures the spec-specific discussion, decisions, technology
choices, outcomes, and constraints surfaced during the constitution and grilling
phases so they are not lost before the spec that needs them is written. Specs are
scoped and clarified when they are actually started. Foundations: the project
[constitution](constitution.md) and the six ADRs in
[`docs/decisions/`](../../docs/decisions/).

Status legend (lifecycle): **undecided** · **needs-info** · **planned** ·
**specced** · **in-progress** · **implemented** · **verified** · **deferred** ·
**abandoned**.

---

## Vision & End States

- clerk is an **agentic conductor for copier**, shipped as a **skills bundle +
  minimal deterministic tools + a thin copier-managing wrapper** — never a
  scaffolder, never an in-process agent loop.
- A **two-phase model**: the agent authors the *inputs* (selection + answer
  values), a deterministic core drives copier. The agent is confined to the
  non-deterministic work; everything mechanical is testable without an LLM.
- **Faithful, agent-free reproduce is the headline guarantee**: a committed answers
  file replays byte-faithfully at its recorded `_commit`, with no agent in the loop.
- Users bring **their own template catalog**; clerk depends on no first-party hub.
- clerk's distinctive value is the **agentic-ecosystem wiring** (APM / MCP /
  SpecKit / ADR) that copier has no analog for.

## Constraints & Decisions

- **C-01 — copier is the engine; clerk is the conductor:** copier owns all
  rendering, the committed answers file, git-ref pinning, and reproduce/update.
  clerk never re-implements it. _See ADR-0001, Constitution Principle I._
- **C-02 — Two-phase CLI seam (non-negotiable):** agent (phase 1) authors a frozen
  JSON run-spec; deterministic core (phase 2) validates → drives copier →
  reproduces with zero LLM involvement. _See Principle II._
- **C-03 — Faithful reproduce, distinct upgrade:** `reproduce` =
  `run_recopy(vcs_ref=VcsRef.CURRENT)`; bare recopy (silently upgrades to latest) is
  never exposed; `upgrade` = `run_update` is a separate, explicit, announced verb.
  _See ADR-0001, Principle III._
- **C-04 — Stable copier API only; one deprecated-surface adapter:** use only
  `run_copy/recopy/update`, `copier.errors`, `Settings`, `Phase`, `VcsRef`.
  `Template`/`Worker` (deprecated-as-internal; no copier v10 exists — deprecation is
  warnings-only + unscheduled) are confined to ONE adapter module + a contract test.
  Pin `copier>=9.16,<10`. _See Principle IV._
- **C-05 — Determinism via pinning; trust by source:** pin template `#ref`, copier
  version, `apm.lock`, tool versions. Forbid `jinja2_time`/random filters; inject
  `{{ today }}` as an answer. Trust via `settings.yml trust:` (expanded-https prefix
  matching the RAW url), never blanket `unsafe=True`; core never auto-trusts —
  raises `UntrustedSource`, agent writes prefix on human consent. _See ADR-0001,0004,
  Principle V._
- **C-06 — Template-author contract, enforced at discovery:** template MUST ship
  `{{ _copier_conf.answers_file }}.jinja` (verified: without it no `.copier-answers.yml`
  is written → unreproducible; clerk refuses to render it); one repo = one template
  with clean PEP 440 tags; `when:false` edges in `copier.yml`; new `_migrations`
  format only. _See ADR-0002,0006, Principle VI._
- **C-07 — Hardening is a per-step DoD, not a spec:** every spec lands its
  determinism checks, error-taxonomy translation (catch `copier.errors.*` AND
  `builtins.ValueError`), and adapter/seam contract tests. _See Principle VII._
- **C-08 — Machine-checkable seam contracts:** run-spec + discover-output are
  pydantic v2 models (pydantic is a DIRECT dep); model is the source of truth,
  validates in core AND emits a committed JSON Schema; contract test fails CI on
  drift. _See Principle VIII._
- **C-09 — Authoring monorepo → per-template fan-out:** templates authored in one
  monorepo; cocogitto tags `<name>-vX.Y.Z`; a hand-rolled snapshot-mirror CI step
  fans out to read-only `copier-clerk/clerk-mod-*` repos with clean `vX.Y.Z` tags;
  consumers always source the split repos, never the monorepo. _See ADR-0006,0002._
- **C-10 — Validation wraps copier, not re-implements it:** clerk catches and
  translates copier's own validation errors; `--check` uses copier `pretend=True`.
  The all-gaps cross-module preflight (collate every question + dry-run) is a
  planned forward-extension at spec 003, not a slice-1 build. _See Principle VII, C-07._

## Planned Specs

### 001 — Single-module vertical slice  [status: planned]

- **Description:** Prove the whole clerk→copier→reproduce loop end-to-end for ONE
  trusted source repo with ONE template — both halves shipped (deterministic core +
  thin agent skill).
- **Outcome:** `clerk discover` a real template, author a run-spec, `clerk init` it
  (renders + runs one `_task`), and `clerk reproduce` it faithfully — all agent-free
  in phase 2, fully covered by hermetic tests.
- **Scope (in):**
  - Core CLI, four verbs: `init --run-spec f.json [--check]`, `reproduce`,
    `trust add|list`, `discover <src>` (emits questions/secrets/`when:false` edges/
    answers-file-check as JSON).
  - `init`: validate (wrap copier errors incl. `builtins.ValueError`; `--check` uses
    copier `pretend=True`) → `run_copy(data=answers, defaults=True, overwrite=True,
    settings=<trust>)`. `reproduce`: `run_recopy(vcs_ref=VcsRef.CURRENT, ...)`.
  - ONE hermetic `git init` `_task` proving tasks fire at init AND reproduce,
    agent-free.
  - Trust onboarding: core raises `UntrustedSource`; agent writes the expanded-https
    prefix via `clerk trust add` on human consent.
  - run-spec + discover-output as pydantic v2 models + committed JSON Schema + drift
    contract test.
  - Deprecated copier surface (`Template`/`Worker` for discovery + `message_after_copy`
    re-rendered) isolated in ONE adapter module + contract test.
  - Exemplar: ONE real, disposable `clerk-mod-base` repo (renders core identity →
    README/LICENSE/.gitignore/dirs; `git init` task; ships answers-file template).
  - Add `pydantic` as a direct dependency (`uv add`).
  - Fix the README's bare-`copier recopy` reproduce claim (violates Principle III).
- **Scope (out):** meta-templates/catalog injection (002); multi-module/DAG (003);
  defaults (004); secrets (005); upgrade/migrations (006); agentic module (007);
  release/fan-out (008); project-setup port (009).
- **Depends on:** none.
- **Governed by:** ADR-0001, ADR-0002, ADR-0004; Constitution Principles I–VIII;
  C-02, C-03, C-04, C-05, C-06, C-08.
- **Notes:** `clerk-mod-base` deliberately collapses 5 project-setup base modules
  (core-identity, dirs-scaffold, gitignore-generate, license-write, git-init) into
  one template; spec 009 may re-split them (kept documented). The exemplar is
  hand-published now (fan-out not built yet) and recreatable/disposable in 008. The
  real-remote e2e test is marked so the rest of the suite stays offline-hermetic.

### 002 — Catalog + meta-templates + runtime injection  [status: planned]

- **Description:** Let users point clerk at their own source repos and get the
  available templates discovered and presented.
- **Outcome:** A user supplies one or more source repos; clerk extracts + verifies
  their templates and presents a selectable catalog injected at runtime.
- **Scope (in):** repos-collector template (persists source repo URLs+refs in its
  `.copier-answers.yml`); selector template with catalog injected via
  `run_copy(data={"catalog":[...]})` (verified in scope from question 1); extraction/
  verification is clerk's job, not a copier task; full-id (`catalog/template`)
  collision handling; one-or-more catalog pointers; optional swappable reference
  catalog.
- **Scope (out):** dependency ordering / multi-module execution (003).
- **Depends on:** 001.
- **Governed by:** ADR-0002, ADR-0003; C-06.
- **Notes:** The runtime-injection hinge (dynamic `choices` reading `data=`) is
  source-verified against copier 9.16. No sidecar `clerk.yml`, no CI catalog
  generator, no template mutation.

### 003 — Multi-module enablement + dependency DAG  [status: planned]

- **Description:** Select many modules and have clerk run them in correct dependency
  order.
- **Outcome:** clerk builds a DAG from declared edges and issues one `run_copy` per
  template in topological order, threading answers between them.
- **Scope (in):** read `when:false` `depends_on`/`run_after`/`run_before` from
  `copier.yml`; build DAG; one `run_copy` per template in topo order, each with a
  distinct `answers_file`; thread one module's answers into the next via `data=`;
  handle a module whose `_tasks` must run after another's. **Forward-deliver the
  all-gaps preflight** (C-10): collate every question across all enabled modules and
  dry-run (`pretend=True`) to report ALL missing answers in one pass (extends 001's
  `--check` seam).
- **Scope (out):** the agentic-ecosystem module's internal multiselect (007).
- **Depends on:** 002.
- **Governed by:** ADR-0003; C-07, C-10.
- **Notes:** copier does zero cross-template coordination — sequencing is entirely
  clerk's pure function. `_external_data` stays out of the core.

### 004 — Global per-module defaults  [status: planned]

- **Description:** Stop users re-entering the same values on every run.
- **Outcome:** clerk pre-fills per-module defaults from its own config, still
  overridable by the human.
- **Scope (in):** read `~/.config/clerk` defaults; select keys relevant to each
  module; pass as `user_defaults=` (SOFT, overridable) — NOT `data=`; optionally
  fold copier `settings.yml defaults:` (user_name/email).
- **Scope (out):** secret values (005 — those are never persisted defaults).
- **Depends on:** 003.
- **Governed by:** ADR-0005.
- **Notes:** Verified precedence: `data=` > answers-last > `user_defaults=` >
  `settings.defaults` > `copier.yml` default. Per-module scoping is clerk's, because
  clerk decides which keys to pass per invocation.

### 005 — Secrets injection  [status: planned]

- **Description:** Inject secret answers per-run without ever persisting them.
- **Outcome:** Secret questions are filled from an external store at run time and
  never written to `.copier-answers.yml`, identically at init and reproduce.
- **Scope (in):** discover `secret_questions`; fetch values per-run from an external
  store (env / 1Password / etc.); pass via `data=`; `clerk reproduce` is
  secret-aware.
- **Scope (out):** the store implementations beyond a first adapter.
- **Depends on:** 003.
- **Governed by:** ADR-0001 (secrets); C-05.
- **Notes:** copier does not write `secret: true` answers to the answers file — this
  is the mechanism clerk leans on.

### 006 — Upgrade + copier migrations  [status: planned]

- **Description:** Move an existing generated project to a newer template version
  safely, running any author-provided migrations.
- **Outcome:** `clerk upgrade` performs a smart 3-way merge from the recorded
  `_commit` to latest, clearly announcing from→to, and runs version-crossing
  migrations.
- **Scope (in):** `clerk upgrade` = `run_update`; surface copier `_migrations`:
  update-only (verified: `migration_tasks` returns `[]` without `from_template.version`);
  version-crossing trigger `self.version >= current > from_template.version`;
  before/after stages; trust-gated; enforce the NEW `_migrations` format (before/after
  dict form is deprecated and warns).
- **Scope (out):** brownfield adoption of a project with no answers file (deferred).
- **Depends on:** 003.
- **Governed by:** ADR-0001 (three operations); Constitution Principles III, VI.
- **Notes:** This is the ONLY place "move to latest" is exposed, and it is explicit
  and announced — reproduce never drifts (C-03).

### 007 — Agentic-ecosystem module  [status: planned]

- **Description:** clerk's distinctive value — wire APM / MCP / SpecKit / ADR into
  generated projects.
- **Outcome:** A generated project can opt into a fully wired agentic toolchain that
  copier has no native concept of.
- **Scope (in):** an `apm` module template whose internal skills/agents/bundles/mcp
  multiselect reuses copier's own multiselect; APM install as a trust-gated `_task`;
  SpecKit bridge; steering/ADR scaffolding.
- **Scope (out):** the base/language templates (009).
- **Depends on:** 003 (DAG); likely 002.
- **Governed by:** ADR-0001, ADR-0003.
- **Notes:** The piece with no off-the-shelf analog; stays bespoke by design.

### 008 — Release + fan-out  [status: planned]

- **Description:** Author templates in one monorepo, distribute them as per-template
  read-only repos with clean PEP 440 tags.
- **Outcome:** A monorepo release automatically publishes changed templates to
  `copier-clerk/clerk-mod-*` and updates the published catalog index.
- **Scope (in):** cocogitto monorepo mode tags `<name>-vX.Y.Z`
  (`generate_mono_repository_global_tag=false`, `tag_prefix=v`, `[monorepo.packages]`);
  ONE CI job — `cog bump` → `push --follow-tags` → `git tag --points-at HEAD` to
  derive the changed set → hand-rolled ~25-line snapshot-mirror (cp + commit +
  strip-prefix tag + push, PAT-scoped, skip-if-no-diff) to `clerk-mod-*`; publish a
  catalog JSON index; direct push (not PR).
- **Scope (out):** history-preserving splits (rejected as over-engineering).
- **Depends on:** 001 (real templates exist), 002 (catalog).
- **Governed by:** ADR-0006, ADR-0002; C-09.
- **Notes:** Recreate/replace the disposable 001 exemplar here if needed. Fan-out
  is a later STEP in the release job (NOT a cog post_bump hook — no rollback there).

### 009 — project-setup module port  [status: planned]

- **Description:** Re-home the mature ~26-module `project-setup` capability onto
  copier templates.
- **Outcome:** The project-setup module set is available as `clerk-mod-*` copier
  templates driven by clerk.
- **Scope (in):** port base (core-identity/dirs-scaffold/gitignore/license/agents-md/
  git-init) + languages (python/ts/go/rust) + apm-install/mcp-config/precommit/
  ci-github-actions/readme/justfile/etc. as `clerk-mod-*` templates.
- **Scope (out):** any new capability not already in project-setup.
- **Depends on:** 002, 003, 006, 008.
- **Governed by:** ADR-0002, ADR-0003, ADR-0006.
- **Notes:** spec 001's `clerk-mod-base` collapses the 5 base modules into one
  template; 009 MAY re-split them into separate `clerk-mod-*` repos — kept documented
  so the decision is explicit when 009 is scoped.

### DEFERRED — Rewrite / brownfield adoption  [status: deferred]

- **Description:** Point clerk at an EXISTING project that has no
  `.copier-answers.yml`, reverse-infer the answers, adopt a template, and write the
  answers file so the project becomes reproducible.
- **Outcome:** _to be defined._
- **Scope (in):** _to be defined — large, unbounded agentic inference problem; title
  captured so it is not lost, no scope committed._
- **Notes:** Distinct from init (greenfield), reproduce (replay), and upgrade (bump
  ref). Would move to `planned` only after the greenfield lifecycle (001–006) is
  solid and the inference approach is scoped.

## Open Questions

- **Q1 — Secret store adapters:** which external store(s) does spec 005 support
  first (env var, 1Password, both)? Resolved when 005 is scoped against real usage.
- **Q2 — 009 base re-split:** does the project-setup port keep `clerk-mod-base` as
  one template or re-split into per-module repos? Resolved when 009 is scoped;
  depends on how the DAG (003) and catalog (002) feel in practice.
- **Q3 — Third-party template discovery fidelity:** the discovery adapter uses
  copier `Template` (handles `!include`/inheritance). If a future need arises to
  discover templates whose parsing the adapter can't cover, revisit whether a
  raw-YAML fallback is warranted. Resolved by evidence from real third-party
  templates (post-002).

## Cross-Cutting Notes

- **Hardening every step (C-07):** determinism/drift checks, error-taxonomy
  translation, and adapter/seam contract tests are part of each spec's
  definition-of-done — never a trailing spec.
- **One deprecated-surface adapter (C-04):** every future spec that needs copier
  introspection or `message_after_copy` goes through the single adapter module, so
  the copier-10 migration stays a one-file change.
- **The seam is the product boundary (C-02/C-08):** the run-spec and discover-output
  pydantic models are the contract between the agent skill and the deterministic
  core; they evolve additively and stay schema-tested.

---

**Version**: 1.0.0 | **Ratified**: 2026-07-09 | **Last Amended**: 2026-07-09
