# Changelog

All notable changes to `bailiff-mod-moon` are documented here. Managed by
cocogitto fan-out (ADR-0006); do not hand-edit released sections.

## [Unreleased]

### Added

- Initial implementation (spec 012 / FR-010): managed `.moon/workspace.yml`
  wired to base's package layout; supplies frozen `monorepo_tool=moon` for CI
  consumption; contributes `moon` to `mise_tools`; init-only mise preflight;
  warn-and-render on single-package layouts.

<!--
  cocogitto inserts each released version's section ABOVE the `- - -
## bailiff-mod-moon-v0.1.0 - 2026-07-16
#### Features
- (**012**) bailiff-mod-moon — managed workspace.yml, monorepo_tool supplier, warn-and-render (T007) - (10bbb5f) - Sjors Robroek
- (**012**) bailiff-mod-devcontainer — managed devcontainer.json from frozen mise_tools (T003) - (1e999b3) - Sjors Robroek

- - -
` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
