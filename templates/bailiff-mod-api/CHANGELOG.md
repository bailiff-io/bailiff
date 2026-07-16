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
  cocogitto inserts each released version's section ABOVE the `- - -` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
