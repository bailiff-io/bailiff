# Changelog

All notable changes to `bailiff-mod-dep-updates` are documented here. Managed by
cocogitto fan-out (ADR-0006); do not hand-edit released sections.

## [Unreleased]

### Added

- Initial implementation (spec 012 / FR-008): `dep_update_tool
  [renovate, dependabot]` axis with host-derived default (FR-004); managed
  `renovate.json` or `.github/dependabot.yml` sized from frozen
  `dep_ecosystems`; warn-and-render for dependabot on non-GitHub hosts; never
  deletes the other tool's file; zero `_tasks`.

<!--
  cocogitto inserts each released version's section ABOVE the `- - -
## bailiff-mod-dep-updates-v0.1.0 - 2026-07-16
#### Features
- (**012**) bailiff-mod-dep-updates — dep_update_tool axis, host-derived default, warn-and-render (T006) - (eeb3a7b) - Sjors Robroek
- (**012**) bailiff-mod-devcontainer — managed devcontainer.json from frozen mise_tools (T003) - (1e999b3) - Sjors Robroek

- - -
` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
