---
name: rust
summary: Rust overlay -- rust-toolchain pin, rustfmt, clippy hook, cargo init
provides: [language:rust]
after: [base]
requires_bin: [cargo]
---

## Renders

| Path | Contents |
|---|---|
| `rust-toolchain.toml` | the channel pin |
| `rustfmt.toml` | `max_width = 100` plus `use_small_heuristics` |
| `.mise/conf.d/rust.toml` | rust channel, plus cargo-nextest when `test_runner` is nextest |
| `.pre-commit.d/rust.yaml` | local `cargo fmt` and `cargo clippy` hooks |
| `.gitignore.d/rust` | `/target`, plus `Cargo.lock` for a library |
| `Cargo.toml`, `src/main.rs` or `src/lib.rs` | written by `cargo init` after the render |

`Cargo.toml`, `src/main.rs`, and `src/lib.rs` carry `_skip_if_exists`.

## Question order

1. `project_name` -- passed to `cargo init --name`, lowercased with spaces and
   underscores turned into hyphens. Thread the value the user gave `base`.
2. `description` -- recorded in the answers file.
3. `rust_channel` -- written to `rust-toolchain.toml` and to the mise fragment.
4. `rust_edition` -- passed to `cargo init --edition`.
5. `crate_kind` -- lib passes `--lib` to `cargo init` and adds `Cargo.lock` to the
   gitignore fragment. bin commits the lockfile.
6. `test_runner` -- nextest adds cargo-nextest to the mise fragment. Test
   commands run `cargo nextest run` instead of `cargo test`.
7. `rustfmt_heuristics` -- Off omits `use_small_heuristics`.
8. `clippy_stage` -- pre-push or pre-commit.

## Prerequisites

`cargo` must be on PATH. Install it from https://rustup.rs.

## After rendering

- The task runs `cargo init` only when `Cargo.toml` is absent.
- Add dependencies with `cargo add`. The render writes none.
- The clippy hook fails the build on any warning (`-D warnings`). Loosen the
  entry in `.pre-commit.d/rust.yaml` if that is too strict for the project.
- The `.pre-commit.d/` fragment stays inert until a `hooks` group package folds it
  into a config.

## cargo-deny is policy, not vulnerability scanning

`osv-scanner` overlaps on one of cargo-deny's four checks.

| Check | Covered by osv-scanner |
|---|---|
| `advisories` (RustSec CVEs) | yes |
| `licenses` (SPDX allow list) | no |
| `bans` (duplicate or banned crates) | no |
| `sources` (permitted registries) | no |

`licenses` is the one worth having: it fails the build when a dependency carries
a licence outside `rust_license_allow`, which is how a licence policy becomes
enforced rather than documented.

`multiple-versions` warns rather than denies. A duplicated crate usually reflects
a transitive lag nobody in the tree can fix, and denying it blocks work on
someone else's dependency graph.

## The crate needs its own licence field

`cargo init` writes no `license` key, so cargo-deny reported the project's own
crate as `unlicensed` and failed the licences check with an otherwise valid
config. A task writes `rust_license_spdx` into `Cargo.toml`. Thread the same
SPDX id the user gave `base`.

## What runs when

| Hook | Stage | Why |
|---|---|---|
| `cargo fmt` | pre-commit | fast, and fixes in place |
| `cargo machete` | pre-commit | no compile, so it costs little |
| `clippy` | `clippy_stage` | crate-scoped compile; pre-push by default |
| `cargo deny check` | pre-push | resolves the whole dependency graph |

`cargo machete` finds unused dependencies without compiling, which is what makes
it cheap enough for a commit where `cargo udeps` (nightly, compiler-accurate)
would not be.

## Doc lints

`cargo test` already runs `///` examples, so a stale example fails as a test. The
answers add the `[lints]` table on top of that.

| Lint | Severity | Reason |
|---|---|---|
| `missing_docs` | `rust_doc_lints`, lib crates only | a binary has no public API to document |
| `rustdoc::broken_intra_doc_links` | always `deny` | the link resolves to nothing, so it is broken for every reader |

Verified: `missing_docs = "warn"` reports an undocumented public function without
failing the build, and a link to a nonexistent item fails `cargo doc` with exit
101.
