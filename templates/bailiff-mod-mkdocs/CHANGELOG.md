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
  cocogitto inserts each released version's section ABOVE the `- - -` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
