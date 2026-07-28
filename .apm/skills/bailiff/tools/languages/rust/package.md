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
