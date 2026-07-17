# Changelog

All notable changes to `bailiff-mod-ci-github` are documented here. Managed by
cocogitto fan-out (ADR-0006); do not hand-edit released sections.

## [Unreleased]

### Added

- FR-010a (spec 012): `monorepo_tool` accepts `moon`; `monorepo-affected` model
  renders `moon ci` as the affected-detection when `monorepo_tool=moon`.

- Initial implementation: GitHub Actions CI workflow module (spec 011).
  Pure managed render (ZERO `_tasks`); five models (minimal, standard, optimized,
  monorepo-affected, merge-queue); all sizing facts AGENT-FROZEN via `--data`;
  fail-loud R4 guard; pinned action majors; upload/download-artifact share v4.

<!--
  cocogitto inserts each released version's section ABOVE the `- - -
## bailiff-mod-ci-github-v0.1.1 - 2026-07-17
#### Bug Fixes
- (**ci-github**) drop moon from _external_data, make monorepo_tool agent-fed - (a864b7e) - Sjors Robroek
#### Documentation
- reframe reproduce invariant from byte-identical to config-consistent - (498315f) - Sjors Robroek
- reframe reproduce invariant from byte-identical to config-consistent - (c1d7faf) - Sjors Robroek

- - -

## bailiff-mod-ci-github-v0.1.0 - 2026-07-16
#### Features
- (**012**) CI modules accept monorepo_tool=moon with moon ci affected branch (T002) - (114709f) - Sjors Robroek
- rename project clerk → bailiff (PyPI: bailiff, org: bailiff-io) - (52ac605) - Sjors Robroek
#### Bug Fixes
- (**012**) dedupe Unreleased Added heading in CI changelogs [skip lint] - (1b885b5) - Sjors Robroek

- - -

## bailiff-mod-ci-github-v0.1.0 - 2026-07-15
#### Features
- (**011**) implement bailiff-mod-ci-github (T016) - (add09f2) - Sjors Robroek

- - -
` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
