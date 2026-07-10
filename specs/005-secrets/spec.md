# Feature Specification: clerk secrets policy — no scaffold-time secrets; agent never handles credentials

**Feature Branch**: `005-secrets`

**Created**: 2026-07-10

**Status**: Draft

**Input**: Roadmap spec 005 (Secrets injection) — **reframed**. The roadmap's
"inject secret answers from an external store (`op read …` → `--data secret=…`)"
model is superseded: it assumes a specific store (not platform-agnostic) and, worse,
routes the credential through the **phase-1 agent** (an LLM context leak). Grounded in
verified copier 9.16.0 behavior + the constitution (II two-phase, V trust/secrets).

## Overview

A `secret: true` copier question is a credential asked at generation time. Spec 005
answers "how does clerk handle secrets" with a deliberate, evidence-driven **policy
rather than a store-integration engine**:

> **clerk-authored templates MUST NOT use `secret: true` questions.** Scaffolding
> generates *files and structure*, not a running service — a credential is virtually
> never needed to lay down a project. Secrets belong in the **generated project's
> runtime configuration** (a template-authored `.env.example` + docs, or the secret
> manager the generated project itself uses), and any *task* that genuinely needs a
> token reads it from the **ambient environment** (exactly as slice-001's
> LICENSE-via-`gh` task already reads `gh`'s auth), never as a copier answer.

Because there is then **no secret question**, the phase-1 agent never has a
credential to collect, log, or leak — the risk is *eliminated by construction*, not
mitigated. This is the C-11 / YAGNI-aligned choice: do not build a secrets subsystem
for a need scaffolding does not have; introduce one later, with evidence, only if a
concrete template proves it necessary.

The spec is therefore small: a **policy** (clerk templates avoid secret questions),
a **contributor lint** (fail if a clerk-authored template declares one), and a
**defensive guardrail** for the case clerk drives a *third-party* template that
declares a secret question — the SKILL MUST refuse to collect the value and instead
tell the user how to supply it out-of-band. The existing `secret_questions` discovery
and the non-persistence test are kept as the safety net.

## Verified copier behavior (9.16.0, source-checked)

- A `secret: true` question **REQUIRES a default value** (`_user_data.py`
  `_check_secret_question_default_value` — raises `ValueError` otherwise). A secret
  question is never truly empty; absent input it falls back to its default.
- The interactive prompt is **masked** (rendered as a `password` field).
- A secret answer is **NOT persisted** to `.copier-answers.yml` (confirmed by our own
  `tests/loop/test_secret_edge_exclusion.py`; matches ADR-0002). So the committed
  project never contains the value — the reproduce-time re-supply problem is real,
  and the cleanest way to not have it is to not have secret questions.
- `make_secret` (auto-generate) is **deprecated** — not a mechanism to build on.

## Motivating decisions

1. **No secret questions in clerk-authored templates (the policy).** Enforced by a
   contributor lint at discovery: a clerk template whose `copier.yml` declares a
   `secret: true` question fails the check with a message pointing to the runtime-
   config pattern. (This is authoring-plane enforcement; it reuses the existing
   `secret_questions` discovery.)
2. **Secrets live in generated-project runtime, not copier answers.** Templates that
   need to convey a secret requirement ship a `.env.example` + README guidance (plain
   render content) — the *generated project* owns its secrets at run time. clerk's
   answer layer stays credential-free.
3. **Tasks read tokens from ambient env, never as answers.** A `_task` needing a
   credential (e.g. `gh`, a registry token) reads it from the environment the user
   already has (`GH_TOKEN`, etc.), exactly like the existing LICENSE task. Copier
   never sees it; it is not a question, not persisted, not agent-visible.
4. **Agent never collects a secret (the guardrail).** If clerk drives a *third-party*
   template that declares a `secret: true` question, the SKILL MUST NOT ask the user
   for the value and MUST NOT place it in the run-spec. It explains the situation and
   directs the user to supply it out-of-band — via copier's own **masked interactive
   prompt** at the deterministic step, or an environment mechanism — so the value
   never enters the LLM context or a committed file.
5. **Never on argv; never in logs.** Any value that *does* reach copier (third-party
   case, via the deterministic step) travels through the programmatic
   `run_copy(data=…)` path clerk already uses — **never** `copier --data key=SECRET`
   on a command line (which leaks into `ps`/process listings). Secret values MUST NOT
   appear in clerk logs, error messages, or the `--pretend` preflight output.
6. **Platform-agnostic by omission.** Because clerk integrates no store, there is
   nothing OS- or manager-specific to depend on (no `op`, no `vault`, no keychain).
   The generated project's own runtime secret handling is the template author's and
   user's choice, outside clerk.
7. **Evidence-gated escalation.** If a real, concrete template ever needs a
   scaffold-time secret that runtime-config cannot cover, a fuller mechanism
   (agent-hands-off env-var/resolver injection) is specced THEN, with that evidence —
   not preemptively (C-11 / roadmap Q1 resolves to "none for now").

## User Scenarios & Testing

### US1 — A clerk-authored template with a secret question is rejected (Priority: P1)

A contributor authoring a `clerk-mod-*` template adds a `secret: true` question; the
contract lint refuses it, pointing to the runtime-config pattern.

**Why this priority**: this is the policy — it keeps clerk's own family credential-free.

**Independent Test**: run the discovery-backed contract lint against a template
fixture that declares a `secret: true` question; assert it fails naming the question
and citing the "secrets belong in generated-project runtime, not copier answers"
guidance. A clean template (no secret questions) passes.

**Acceptance Scenarios**:
1. **Given** a clerk template with a `secret: true` question, **When** the lint runs,
   **Then** it fails naming the offending question.
2. **Given** a template conveying a secret need via `.env.example` + docs (no secret
   question), **When** the lint runs, **Then** it passes.

### US2 — The agent never collects a third-party template's secret (Priority: P1)

clerk drives a third-party template that declares a `secret: true` question; the
agent does not ask for the value and instead instructs out-of-band supply.

**Why this priority**: the LLM-leak guardrail — the reason the roadmap's store-inject
model was rejected.

**Independent Test**: with discovery reporting a `secret_questions` entry for a
source, assert the SKILL's documented procedure (a) does NOT put the secret in the
run-spec, (b) tells the user to supply it via copier's masked prompt / env, and (c)
the mechanical path never receives the value from the agent. (Verified by the SKILL
contract + a discovery test that the secret question is surfaced as "do not collect".)

### US3 — A secret value never lands in a committed file, log, or dry-run (Priority: P1)

**Independent Test**: for the third-party case where a value IS supplied at the
deterministic step, assert it is (a) absent from `.copier-answers.yml` (existing
non-persistence test), (b) absent from clerk's stdout/stderr and any error text, and
(c) absent from the `--pretend` all-gaps preflight output (which reports the *question*
as needing a secret, never a value).

### Edge Cases

- **Third-party secret question with only its (required) default**: reproduce/CI with
  no value supplied uses copier's default; clerk does not prompt in a non-interactive
  path (Constitution V) — it proceeds with the default or fails loud, never hangs.
- **A task needs a token but none is in the env**: the task fails with the ambient
  tool's own message (e.g. `gh` "not authenticated") — clerk surfaces it; it is not a
  clerk secret-management concern.
- **A contributor argues a secret is genuinely needed**: the lint failure names the
  escalation path (decision 7) — spec a real mechanism with evidence, don't smuggle a
  `secret:` question past the policy.

## Requirements

### Functional Requirements

- **FR-001**: clerk-authored (`clerk-mod-*` / example) templates MUST NOT declare
  `secret: true` questions. A contract lint (reusing `discovery`'s `secret_questions`)
  MUST fail an authored template that declares one, naming the question and citing the
  runtime-config pattern.
- **FR-002**: The secrets policy MUST be documented: secrets belong in the generated
  project's runtime config (`.env.example` + docs) or are read from ambient env by
  tasks — never as a copier answer. Template-author guidance MUST state this.
- **FR-003**: The SKILL MUST instruct the agent, for ANY `secret: true` question
  surfaced by discovery (third-party templates), to NEVER collect the value and NEVER
  put it in the run-spec; instead explain out-of-band supply (copier's masked prompt
  at the deterministic step, or an env mechanism). The value MUST NOT enter the
  agent's inputs.
- **FR-004**: Any secret value that reaches copier MUST travel via the programmatic
  `run_copy(data=…)` path, NEVER via `copier --data key=value` on argv. Secret values
  MUST NOT appear in clerk logs, error messages, or `--pretend` preflight output.
- **FR-005**: The existing non-persistence guarantee MUST be preserved and tested — a
  secret answer is never written to `.copier-answers.yml` (keep
  `test_secret_edge_exclusion.py`).
- **FR-006**: clerk MUST NOT integrate any specific secret store or manager (no `op`,
  `vault`, keychain, etc.) — remaining platform-agnostic. Generated-project runtime
  secret handling is the template author's / user's choice, outside clerk.
- **FR-007**: This spec MUST NOT build a secret-injection engine, resolver chain, or
  store adapter. Escalation to a fuller mechanism is deferred and evidence-gated
  (C-11); if introduced later it MUST remain agent-hands-off (FR-003) and
  store-agnostic (FR-006).

### Key Entities

- **Secret question**: a copier `secret: true` question (requires a default, masked,
  never persisted). clerk templates avoid them; third-party ones are handled
  defensively.
- **Contract lint**: the authoring-plane check (reusing `discovery.secret_questions`)
  that fails a clerk-authored template declaring a secret question.
- **Runtime-config pattern**: `.env.example` + README guidance shipped by a template
  so the *generated project* owns its secrets at run time.
- **Out-of-band supply**: copier's masked prompt / env — the only channels a
  third-party secret value may use; never the agent, never argv, never a committed file.

## Success Criteria

- **SC-001**: A clerk-authored template declaring a `secret: true` question fails the
  contract lint, naming the question; a secret-free template passes.
- **SC-002**: The SKILL documents (and a discovery test confirms) that a surfaced
  secret question is treated as "do not collect — instruct out-of-band"; the value
  never enters the run-spec / agent context.
- **SC-003**: No secret value appears in `.copier-answers.yml`, clerk logs/errors, or
  `--pretend` output (persistence test kept; log/dry-run assertions added).
- **SC-004**: clerk introduces no secret-store dependency and remains
  platform-agnostic (no `op`/`vault`/keychain code).
- **SC-005**: Secrets that generated projects need at runtime are conveyed via
  template `.env.example` + docs, not copier answers (documented; an example template
  may demonstrate the pattern).

## Out of scope

- A secret-injection engine / resolver chain / store adapters (deferred, evidence-
  gated — FR-007). The roadmap's `op read → --data secret=` model is explicitly
  superseded by this policy.
- Generated-project runtime secret management (the project's own concern; clerk only
  provides the `.env.example` + docs pattern via template content).
- Multi-template ordering (003), defaults (004), upgrade (006).

## Open Questions

- **Q-005a — Lint home**: the "no secret question" check runs at the authoring-plane
  contract lint. That lint is part of the deferred authoring-lifecycle (008b/009-era).
  Until it exists, is the policy enforced by (a) a standalone test over
  `examples/`/`templates/` now, or (b) documented-only until the lint lands? Lean:
  **(a) a small test now** over any in-repo clerk-authored templates, folded into the
  full lint later. Resolve at planning.
- **Q-005b — Third-party masked-prompt vs fail-loud default**: for a third-party
  secret question in a non-interactive reproduce, do we (a) let copier use its
  required default, or (b) fail loud demanding out-of-band supply? Lean: **(a) use the
  default** (copier's own contract; clerk stays non-prompting per Constitution V) and
  document that a real secret must be supplied out-of-band interactively. Resolve at
  planning.

## Governing constitution & ADRs

- Constitution II (two-phase — the agent does judgment, never handles credentials),
  V (secrets/determinism; deterministic phase never prompts in CI, fails loud).
- ADR-0001 (secrets: injected per-run, never persisted — honored, and taken further:
  clerk templates avoid them entirely), ADR-0002 (secret + `when:false` not
  persisted). Constraints: C-05 (trust/secrets), C-11 (no speculative engine — the
  reason this is a policy, not a subsystem). Roadmap Q1 (which store first) resolves
  to **none** under this policy.
