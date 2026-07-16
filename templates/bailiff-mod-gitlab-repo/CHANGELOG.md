# Changelog

All notable changes to `bailiff-mod-gitlab-repo` are documented here. Managed by
cocogitto fan-out (ADR-0006); do not hand-edit released sections.

## [Unreleased]

### Added

- Initial implementation (spec 012 / FR-012): exact semantic port of
  bailiff-mod-github-repo to glab — pure side-effect (no file output,
  reconcile=false); glab-missing warn+exit 0; public-without-consent hard
  exit 1 before creation; creation failure non-fatal; optional push; token
  from ambient GITLAB_TOKEN (no secret: questions).

<!--
  cocogitto inserts each released version's section ABOVE the `- - -
## bailiff-mod-gitlab-repo-v0.1.0 - 2026-07-16
#### Features
- (**012**) bailiff-mod-gitlab-repo — glab port of github-repo with all three safety paths (T009) [skip lint] - (3727f81) - Sjors Robroek
- (**012**) bailiff-mod-devcontainer — managed devcontainer.json from frozen mise_tools (T003) - (1e999b3) - Sjors Robroek

- - -
` separator
  below (spec 008b). The separator MUST be present or `cog bump` fails with
  "cannot find default separator '- - -'". Keep it as the last content line.
-->

- - -
