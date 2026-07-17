# Changelog

All notable changes to `bailiff-mod-ci-gitlab` are documented here. Managed by
cocogitto fan-out (ADR-0006); do not hand-edit released sections.

## [Unreleased]

### Added

- FR-010a (spec 012): `monorepo_tool` accepts `moon`; `monorepo-affected` model
  renders `moon ci` as the affected-detection when `monorepo_tool=moon`.

- Initial implementation of the GitLab CI module (spec 011 T017): renders a
  `.gitlab-ci.yml` managed file from 5 ci_models (minimal, standard, optimized,
  monorepo-affected, merge-queue) with full grill-fix compliance:
  - `workflow:rules` duplicate-pipeline guard on all models;
  - `{job: x, optional: true}` needs on change-gated jobs (pipeline-creation safe);
  - coupled `interruptible` + `workflow:auto_cancel:on_new_commit` as one unit;
  - `rules:changes` with `compare_to` on branch arm, omitted on MR arm;
  - `fallback_keys` on caches; pinned images via `ci_lang_facts`;
  - `bun.lock` (not `bun.lockb`) cache key;
  - `gitlab_tier=free` merge-queue fallback with header warning;
  - fail-loud guard: empty `ci_languages` + `monorepo_tool=none` → warning no-op job.

- - -
## bailiff-mod-ci-gitlab-v0.1.1 - 2026-07-17
#### Bug Fixes
- (**ci-gitlab**) revert moon to agent-fed --data (R13 GENERALIZED) - (bef5eab) - Sjors Robroek
#### Documentation
- reframe reproduce invariant from byte-identical to config-consistent - (498315f) - Sjors Robroek
- reframe reproduce invariant from byte-identical to config-consistent - (c1d7faf) - Sjors Robroek

- - -

## bailiff-mod-ci-gitlab-v0.1.0 - 2026-07-16
#### Features
- (**012**) CI modules accept monorepo_tool=moon with moon ci affected branch (T002) - (114709f) - Sjors Robroek
- rename project clerk → bailiff (PyPI: bailiff, org: bailiff-io) - (52ac605) - Sjors Robroek
#### Bug Fixes
- (**012**) dedupe Unreleased Added heading in CI changelogs [skip lint] - (1b885b5) - Sjors Robroek

- - -

## bailiff-mod-ci-gitlab-v0.1.0 - 2026-07-15
#### Features
- (**011**) implement bailiff-mod-ci-gitlab (T017) - (029bf78) - Sjors Robroek
#### Bug Fixes
- (**011**) T017 address review findings - (94b82b3) - Sjors Robroek

- - -

