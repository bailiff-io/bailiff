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
  cocogitto inserts each released version's section ABOVE the `- - -` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
