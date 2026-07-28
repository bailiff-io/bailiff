---
name: decision-records
summary: Numbered decision-record directory with a record template and an index
provides: [docs:decisions]
after: [base]
---

## Renders

| Path | Content |
|---|---|
| `<decisions_dir>/0000-template.md` | The record template: Status, Context, Decision, Consequences |
| `<decisions_dir>/index.md` | Heading, the copy-and-number instruction, an empty record table |

Both paths carry `_skip_if_exists`. An existing decision directory keeps its own
index and template.

The package writes no decision. Number 0000 is the template, so the first real
record is 0001.

## Ask in this order

1. `project_name` -- appears in the index heading.
2. `decisions_dir` -- defaults to `docs/decisions`. Use `docs/adr` only when the
   repo already uses that path.

`project_name` also belongs to `base`. Copy it from there when `base` is in the
same selection.

## After rendering

Write the first record when the user has already described a decision worth
recording: copy `0000-template.md` to `0001-<short-title>.md`, fill it in, and
add a row to the index table. Ask the user for the status before setting it.

When `mkdocs` is also selected, add the decisions directory to the `nav` list in
`mkdocs.yml`.
