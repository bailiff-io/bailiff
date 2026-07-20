# Changelog

All notable changes to `bailiff-mod-cocogitto` are documented here. Managed by
cocogitto fan-out (ADR-0006); do not hand-edit released sections.

## [Unreleased]

### Added

- Initial implementation (spec 012 / FR-007): managed `cog.toml` sized to
  project layout (single vs monorepo); contributes `cog` to `mise_tools` and a
  commit-msg-lint block to `hook_blocks`; trust-gated init-only mise preflight;
  NO release actions at scaffold time; CI left to the CI modules.

<!--
  cocogitto inserts each released version's section ABOVE the `- - -
## bailiff-mod-cocogitto-v0.3.0 - 2026-07-20
#### Features
- fail fast (before writing) when a module's required tool is missing (#58) - (d02a12d) - Sjors Robroek

- - -

## bailiff-mod-cocogitto-v0.2.0 - 2026-07-17
#### Features
- (**cocogitto**) migrate to spec-014 fragment/facts model (T024/T035/T036/T041/T045/T049) - (f381738) - Sjors Robroek
#### Bug Fixes
- (**cocogitto**) revert moon to agent-fed --data per R13 GENERALIZED - (eb919e7) - Sjors Robroek
#### Documentation
- reframe reproduce invariant from byte-identical to config-consistent - (498315f) - Sjors Robroek
- reframe reproduce invariant from byte-identical to config-consistent - (c1d7faf) - Sjors Robroek

- - -

## bailiff-mod-cocogitto-v0.1.0 - 2026-07-16
#### Features
- (**012**) bailiff-mod-cocogitto — managed cog.toml, cog/hook tokens, init-only preflight (T005) - (9ac6a51) - Sjors Robroek
- (**012**) bailiff-mod-devcontainer — managed devcontainer.json from frozen mise_tools (T003) - (1e999b3) - Sjors Robroek

- - -
` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
