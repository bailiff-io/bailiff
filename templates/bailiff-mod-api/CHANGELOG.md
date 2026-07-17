# Changelog

All notable changes to `bailiff-mod-api` are documented here. Managed by
cocogitto fan-out (ADR-0006); do not hand-edit released sections.

## [Unreleased]

### Added

- Initial implementation (spec 012 / FR-013): seed-once OpenAPI 3.1 skeleton
  at the repo root (`openapi.yaml`); managed `.spectral.yaml`; contributes
  `spectral` to `mise_tools` and a spectral-lint block to `hook_blocks` (inert
  when hook_manager=none); zero `_tasks`, no codegen, no server scaffold.

<!--
  cocogitto inserts each released version's section ABOVE the `- - -
## bailiff-mod-api-v0.2.0 - 2026-07-17
#### Features
- (**014/api**) migrate bailiff-mod-api to fragment/fact model (T026/T035/T037/T039/T045) - (ef0bad4) - Sjors Robroek
#### Bug Fixes
- (**014/api**) apply R13 — remove hook_manager/precommit dependency, unconditional fragment - (d12082a) - Sjors Robroek
#### Documentation
- (**api**) sync README with R13 — unconditional fragment, base-only dependency - (f9fda81) - Sjors Robroek
- reframe reproduce invariant from byte-identical to config-consistent - (498315f) - Sjors Robroek
- reframe reproduce invariant from byte-identical to config-consistent - (c1d7faf) - Sjors Robroek

- - -

## bailiff-mod-api-v0.1.0 - 2026-07-16
#### Features
- (**012**) bailiff-mod-api — seed-once OpenAPI 3.1 skeleton + managed spectral config (T010) - (0f887f6) - Sjors Robroek
- (**012**) bailiff-mod-devcontainer — managed devcontainer.json from frozen mise_tools (T003) - (1e999b3) - Sjors Robroek

- - -
` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
