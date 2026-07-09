<!--
SYNC IMPACT REPORT
==================
Version change: (template / unratified) → 1.0.0
Bump rationale: First ratification. Establishes the full principle set from the
six accepted ADRs (docs/decisions/0001-0006) and the grilling session.

Modified principles: n/a (initial adoption)
Added sections:
  - I.    clerk Is a Conductor, Not a Scaffolder
  - II.   Two-Phase Boundary, CLI Seam (NON-NEGOTIABLE)
  - III.  Reproduce Is Faithful and Agent-Free (NON-NEGOTIABLE)
  - IV.   Drive copier's Stable API Only; Isolate Deprecated Surface
  - V.    Determinism Discipline via Pinning
  - VI.   Template-Author Contract (Enforced at Discovery)
  - VII.  Hardening Is a Per-Step Mandate
  - VIII. Machine-Checkable Seam Contracts
  - Additional Constraints (copier facts, verified)
  - Development Workflow & Quality Gates
  - Governance
Removed sections: none

Templates requiring updates:
  ✅ .specify/memory/constitution.md (this file)
  ✅ .specify/templates/plan-template.md — Constitution Check gate aligned (see below)
  ⚠  .specify/templates/spec-template.md — no principle-driven change required;
     re-verify at first /speckit.specify
  ⚠  .specify/templates/tasks-template.md — hardening-per-step (VII) should map to
     mandatory determinism/error-taxonomy/contract-test task rows; verify at first
     /speckit.tasks
  ✅ README.md — bare `copier recopy` reproduce claim flagged for correction in
     spec 001 (violates Principle III)

Follow-up TODOs: none deferred.
-->

# clerk Constitution

clerk is an agentic conductor for [copier](https://copier.readthedocs.io). copier
is the deterministic render + reproduce engine; clerk is the thin agentic layer
that decides *what* to render and authors the *inputs*, then hands off to copier.
Every principle below is source-verified against copier 9.16.0 and derives from
the six architecture decisions in `docs/decisions/0001-0006`, which are binding.

## Core Principles

### I. clerk Is a Conductor, Not a Scaffolder

clerk is exactly three things and nothing more: (1) a **skills bundle** — the
agent-facing `SKILL.md` procedures; (2) the **minimal deterministic tools** those
skills need; and (3) a **thin wrapper** that manages copier via its Python API.
clerk MUST NOT render files itself, and MUST NOT embed an agent loop (no Claude
Agent SDK or equivalent runs in-process). copier owns all rendering, the committed
answers file, git-ref pinning, and the reproduce/update cycle. Any capability that
copier already provides MUST be delegated to copier, never re-implemented.

Rationale: clerk's only durable value is the agentic layer copier structurally
lacks. Re-implementing copier's engine relocates its hard problems into clerk and
dilutes the boundary that makes the system testable and trustworthy.

### II. Two-Phase Boundary, CLI Seam (NON-NEGOTIABLE)

Work is split at a CLI seam into a non-deterministic phase and a deterministic
phase. The **agent (phase 1)** performs ONLY non-deterministic work: discover and
present templates, collect the human's selection, author answer *values*, and
explain/obtain consent for trust. It then hands the deterministic core a **frozen
JSON run-spec**. The **core (phase 2)** deterministically validates → drives copier
→ reproduces, with ZERO agent or LLM involvement. Everything mechanical MUST be
testable without an LLM. The agent is NEVER in the reproduce path.

Rationale: confining the LLM to genuinely non-deterministic judgment makes the
whole mechanical surface unit-testable and keeps reproduce trustworthy.

### III. Reproduce Is Faithful and Agent-Free (NON-NEGOTIABLE)

`reproduce` MUST call `run_recopy(vcs_ref=VcsRef.CURRENT, defaults=True,
overwrite=True)` — a byte-faithful replay of the committed answers at the recorded
`_commit`. Bare `recopy` (no `vcs_ref`) silently resolves the LATEST tag and
UPGRADES; it MUST NEVER be exposed. Moving to a newer template version is a
DISTINCT, explicit `clerk upgrade` verb backed by `run_update`. `_tasks` run at
BOTH init and reproduce; migrations are update-only. Reproduce is
process-deterministic (same pinned inputs → same commands executed), not
necessarily byte-identical output, because tasks may touch external state.

Rationale: faithful reproduce is clerk's headline guarantee and the reason the
pinning discipline exists; a reproduce that drifts to "latest" makes CI
drift-detection and disaster-recovery meaningless.

### IV. Drive copier's Stable API Only; Isolate Deprecated Surface

clerk MUST use ONLY copier's verified-stable public surface: `run_copy`,
`run_recopy`, `run_update`, `copier.errors.*`, `Settings`, `Phase`, `VcsRef`.
`copier.Template` and `copier.Worker` are deprecated-as-internal ("will become
inaccessible in the future"; verified: no copier v10 exists, the deprecation is
warnings-only and unscheduled). Any use of deprecated/internal copier surface —
today: template introspection during discovery, and reading `message_after_copy`
— is PERMITTED ONLY inside a SINGLE clerk adapter module, guarded by a contract
test that fails CI if copier's internal shape drifts. copier is pinned
`copier>=9.16,<10`.

Rationale: one quarantined adapter converts an unbounded "deprecated API
everywhere" risk into a single, contract-tested migration point when copier 10
eventually lands.

### V. Determinism Discipline via Pinning

Because `_tasks` run at reproduce, byte-stability holds only as far as inputs are
pinned. clerk MUST pin the template `#ref` (tag or sha), the copier version,
`apm.lock`, and tool versions. FORBIDDEN in clerk-driven templates: `jinja2_time`
(`{% now %}`) and the random filters — both nondeterministic. The current date
MUST be injected as an answer (`data={"today": ...}`) and referenced as
`{{ today }}`, so it freezes into the answers file and reproduce replays the
original date. Trust MUST be configured via copier `settings.yml` `trust:`
(a prefix matching the RAW, pre-expansion URL), NEVER blanket `unsafe=True`. The
deterministic core MUST NEVER auto-write trust: it raises a structured
`UntrustedSource` error; only the agent writes the prefix on explicit human
consent. Reproduce/CI never prompts and MUST fail loudly if trust is absent.

Rationale: reproduce determinism is only as strong as its least-pinned input;
trust grants code execution, so consent must stay with a human and out of the
non-interactive path.

### VI. Template-Author Contract (Enforced at Discovery)

Every clerk-consumable template MUST: (a) ship a
`{{ _copier_conf.answers_file }}.jinja` file — VERIFIED: without it copier writes
NO `.copier-answers.yml` and the project is unreproducible; clerk MUST REFUSE to
render a template lacking it; (b) be one git repo = one template with clean PEP 440
tags (`vX.Y.Z`) — copier silently discards non-PEP440 tags; (c) declare dependency
edges as `when: false` hidden answers (`depends_on` / `run_after` / `run_before`),
statically read from `copier.yml`; (d) use copier's NEW `_migrations` format (the
`before`/`after` dict form is deprecated and warns). clerk's discovery step MUST
verify (a) and (b) and refuse non-conforming templates with a structured error.

Rationale: these are copier's real, verified constraints; enforcing them at
discovery turns silent unreproducibility into a loud, early failure.

### VII. Hardening Is a Per-Step Mandate

Hardening is NOT a trailing phase. EVERY spec MUST land, as part of its own
definition-of-done: (a) its determinism checks (e.g. reproduce byte/drift
assertions where applicable); (b) its error-taxonomy mapping — copier raises both
`copier.errors.*` AND a bare `builtins.ValueError` for the missing-required-question
case, and both MUST be caught and translated to typed clerk errors; (c) its
adapter/seam contract tests. No spec is complete with any of these deferred.

Rationale: deferred hardening becomes never-done hardening; folding it into each
spec's DoD keeps the determinism and error guarantees continuously true.

### VIII. Machine-Checkable Seam Contracts

The phase-1 ↔ phase-2 artifacts — the agent-authored **run-spec** and the
**discover output** the agent reads — MUST be defined as pydantic v2 models.
pydantic is a DIRECT clerk dependency (not merely copier-transitive). The model is
the single source of truth: it validates in the core (typed fast-fail before copier
runs) AND emits a committed JSON Schema via `model_json_schema()`. A contract test
MUST fail CI if the committed schema drifts from the model. `SKILL.md` points the
agent at the committed schema.

Rationale: a machine-checkable seam lets the core reject a malformed handoff
deterministically and gives the agent a precise, testable contract instead of
prose.

## Additional Constraints (copier facts, verified against 9.16.0)

- **Answer precedence** (verified): `data=` (highest) > `.copier-answers.yml` last
  execution > `user_defaults=` > `settings.yml` `defaults:` > template `copier.yml`
  default. clerk injects fixed/derived values via `data=` and user-changeable
  defaults via `user_defaults=`.
- **Three operations, three version behaviors:** `run_copy` (init) → latest tag or
  explicit `vcs_ref`; `run_recopy` (faithful reproduce) → `VcsRef.CURRENT`;
  `run_update` (upgrade) → from `_commit` to latest.
- **`data=` answers ARE persisted** to `.copier-answers.yml` even when never
  interactively asked (verified) — but only if the answers-file template exists
  (Principle VI). `when: false` hidden answers are NOT persisted and are read from
  `copier.yml` at discovery.
- **Catalog holds SOURCES, not pinned refs.** The reproduce pin lives in the
  generated project's answers file (`_commit`). `_src_path` MUST be the split
  (per-template) repo, never the authoring monorepo.
- **`_tasks`/migrations/`_jinja_extensions` are all trust-gated.** A trusted source
  is the sanctioned enabler; `unsafe=True` is reserved for the narrow
  `_external_data`-outside-destination case only, opt-in per template.

## Development Workflow & Quality Gates

- Work is spec-driven via SpecKit. The constitution and the six ADRs gate every
  spec; a `Constitution Check` in each plan MUST confirm compliance with Principles
  I–VIII or justify deviation against the "thin conductor" ethos.
- The roadmap decomposes delivery into dependency-ordered specs; the first spec is
  a tight single-module vertical slice. Breadth (catalog, DAG, secrets, defaults,
  upgrade/migrations, agentic-ecosystem module, release/fan-out, project-setup port)
  is captured as roadmap placeholder specs, not built up front.
- Every change runs `just test` (pytest), `just types` (mypy strict), and
  `just lint` (pre-commit) before merge. Adapter and seam contract tests
  (Principles IV, VIII) are blocking.
- Dependencies are added via the package-manager CLI (`uv add`), not manifest
  edits.

## Governance

This constitution supersedes ad-hoc practice. The six ADRs in `docs/decisions/`
are the architectural source of truth and are binding; this constitution encodes
their cross-cutting invariants. Amending a principle REQUIRES updating the
governing ADR in the same change. All specs and PRs MUST verify compliance with
Principles I–VIII; complexity beyond them MUST be justified in writing against the
"clerk is a thin conductor" ethos, or be rejected.

Versioning of this document follows semantic versioning: MAJOR for
backward-incompatible principle removals or redefinitions, MINOR for a new
principle or materially expanded guidance, PATCH for clarifications and wording.

**Version**: 1.0.0 | **Ratified**: 2026-07-09 | **Last Amended**: 2026-07-09
