---
name: github-rust
summary: GitHub Actions test and lint jobs for Rust, as reusable workflows
provides: [ci-job:test-rust, ci-job:lint-rust]
after: [github, rust]
depends_on: [github]
---

Renders three files.

| Path | What it is |
|---|---|
| `.github/actions/setup-rust` | Installs a toolchain with rustfmt and clippy |
| `.github/workflows/wc-test-rust.yml` | Callable test job |
| `.github/workflows/wc-lint-rust.yml` | Callable lint job, `cargo fmt --check` plus clippy |

## Questions, in order

1. `rust_toolchain` -- read `rust-toolchain.toml` or the `rust-version` key in
   `Cargo.toml` first. Pin a version only when the project already pins one;
   `stable` is right for most crates.
2. `rust_test_command` -- check whether the repo uses nextest, by looking for
   `.config/nextest.toml`. If it does, the answer is `nextest run --workspace`.
3. `rust_all_features` -- turn it off when the crate has mutually exclusive
   features, because `--all-features` then fails to compile.
4. `ci_cache` -- leave true.
5. `ci_os_matrix` -- ask only when the crate targets Windows or macOS.
6. `ci_version_matrix` -- ask only for a published library with an MSRV. Put the
   MSRV in the list alongside `stable` so a bump in either direction is caught.

## The lint job denies warnings

`clippy` runs with `-D warnings`, so a new lint in a toolchain upgrade turns into
a failing build. That is the point on a pinned toolchain. On `stable` it means an
upstream Rust release can break CI on an unrelated commit; tell the user that
before they pick `stable` with `ci_version_matrix` empty.

## Workspaces

Both workflows take a `working-directory` input. A cargo workspace usually does
not need it, because `--workspace` covers every member from the root. Set it only
when the repo holds several unrelated cargo projects.
