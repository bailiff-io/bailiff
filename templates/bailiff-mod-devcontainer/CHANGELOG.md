# Changelog

All notable changes to `bailiff-mod-devcontainer` are documented here. Managed by
cocogitto fan-out (ADR-0006); do not hand-edit released sections.

## [Unreleased]

### Added

- Initial implementation (spec 012 / FR-005): managed
  `.devcontainer/devcontainer.json` derived from the frozen `mise_tools` union
  via the mise devcontainer feature; fixed base image
  `mcr.microsoft.com/devcontainers/base:ubuntu`; zero `_tasks`.

<!--
  cocogitto inserts each released version's section ABOVE the `- - -
## bailiff-mod-devcontainer-v0.2.0 - 2026-07-17
#### Features
- (**devcontainer**) migrate to bare mise install, _external_data facts, depends_on edge (spec 014 T029/T035) - (6f66925) - Sjors Robroek
#### Documentation
- reframe reproduce invariant from byte-identical to config-consistent - (498315f) - Sjors Robroek
- reframe reproduce invariant from byte-identical to config-consistent - (c1d7faf) - Sjors Robroek

- - -

## bailiff-mod-devcontainer-v0.1.0 - 2026-07-16
#### Features
- (**012**) bailiff-mod-devcontainer — managed devcontainer.json from frozen mise_tools (T003) - (1e999b3) - Sjors Robroek

- - -
` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
