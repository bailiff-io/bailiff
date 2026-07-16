# Changelog

All notable changes to `bailiff-mod-mkdocs` are documented here. Managed by
cocogitto fan-out (ADR-0006); do not hand-edit released sections.

## [Unreleased]

### Added

- Initial implementation (spec 012 / FR-011): managed `mkdocs.yml` wired to
  `docs/`; seed-once `docs/index.md`; mkdocs + mkdocs-material pinned via the
  `mise_tools` union (regardless of python co-selection); zero `_tasks`, no
  build/deploy at scaffold time.

<!--
  cocogitto inserts each released version's section ABOVE the `- - -
## bailiff-mod-mkdocs-v0.1.0 - 2026-07-16
#### Features
- (**012**) bailiff-mod-mkdocs — managed mkdocs.yml, seed-once index, mise pin tokens (T008) - (02e086a) - Sjors Robroek
- (**012**) bailiff-mod-devcontainer — managed devcontainer.json from frozen mise_tools (T003) - (1e999b3) - Sjors Robroek

- - -
` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
