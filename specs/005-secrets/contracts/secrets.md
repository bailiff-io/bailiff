# Contract — clerk secrets policy + guardrail (spec 005)

clerk handles secrets by **policy, not by a store engine**: clerk-authored templates
avoid secret questions; the phase-1 agent never handles a credential; clerk depends
on no secret store. This contract states the policy, the third-party guardrail, the
runtime-secret pattern, and the leak rules.

## The policy (clerk-authored templates)

- A `clerk-mod-*` / example template's `copier.yml` **MUST NOT declare a `secret:
  true` question.** Enforced by a contract lint reusing `discovery.discover(...).
  secret_questions` — a non-empty list for a clerk-authored template is a failure,
  with a message naming the question(s) and pointing to the runtime-secret pattern.
- A template that needs to convey a secret *requirement* ships a **`.env.example`**
  (render content) + README guidance: the **generated project** owns its secrets at
  runtime. clerk's copier-answer layer stays credential-free.
- A `_task` that needs a token reads it from the **ambient environment** (e.g.
  `GH_TOKEN`, like the existing LICENSE-via-`gh` task) — never a copier answer, never
  a question, never persisted, never agent-visible.

## The guardrail (third-party templates clerk drives)

clerk cannot control third-party templates. If discovery reports a `secret_questions`
entry for a source clerk is asked to drive:

- The **SKILL MUST NOT** ask the user for the secret value and **MUST NOT** place it
  in the run-spec / `--data` it authors. (Phase-1 agent stays credential-free — the
  whole point.)
- The SKILL explains the situation and directs **out-of-band supply**:
  - copier's own **masked interactive prompt** at the deterministic step (the human
    types it into copier directly, not to the agent), OR
  - an environment mechanism the user controls.
- **Non-interactive reproduce/CI** (Constitution V): clerk never prompts. copier uses
  the secret question's **required default** (verified: secret questions must have a
  default). A real secret needed at reproduce must be supplied out-of-band
  interactively; clerk documents this and never hangs.

## Leak rules (any value that DOES reach copier)

For the third-party case where a value is supplied at the deterministic step:

- It travels via the programmatic **`run_copy(data=…)`** path clerk already uses —
  **NEVER** `copier --data key=value` on argv (leaks into `ps`/process listings).
- Secret values **MUST NOT** appear in clerk logs, error messages, or the
  `--pretend` / all-gaps-preflight output. The preflight reports the *question* as
  needing a secret, never a value.
- Secret answers are **NOT persisted** to `.copier-answers.yml` (copier's own
  behavior; guarded by `test_secret_edge_exclusion.py`). Reproduce re-obtains the
  value out-of-band, identically — it is never read back from a committed file.

## The runtime-secret pattern (what templates ship instead)

```text
{{ _copier_conf.answers_file }}.jinja   # (existing) records non-secret answers
.env.example.jinja                       # NEW pattern: documents the secrets the GENERATED
                                          #   project needs at RUNTIME (names, not values)
README.md.jinja                           # guidance: "copy .env.example → .env, fill secrets"
```

The generated project's runtime secret handling (dotenv, the project's own secret
manager, CI secrets) is the **template author's + user's** choice — outside clerk,
which is why clerk stays platform-agnostic (no `op`/`vault`/keychain code).

## What clerk does NOT build (deferred, evidence-gated)

No secret-injection engine, resolver chain, or store adapter. The roadmap's `op read
→ --data secret=` model is **superseded** by this policy. If a concrete template ever
proves a scaffold-time secret is unavoidable, a fuller mechanism is specced then — and
it MUST remain **agent-hands-off** (the value never enters the LLM context) and
**store-agnostic** (no clerk dependency on a specific manager).

## Exit codes

| Surface | Code | Meaning |
|---|---|---|
| policy lint (clerk-authored template) | 0 | no secret questions |
| | non-zero | a `secret: true` question found — named, with the runtime-pattern pointer |
| existing clerk verbs | 0/1/2/3 | unchanged (spec 010/002/003) |

(No new runtime exit codes — 005 adds a lint/policy + guardrail wording, not a new
command surface.)
