# Rust Standards

Rust is used for performance-critical services, systems programming, WebAssembly, and CLI tools where safety and performance are paramount.

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Line length | 100 characters | rustfmt default |
| Indentation | 4 spaces | rustfmt default |
| Function naming | `snake_case` | Rust Style Guide |
| Type/struct naming | `PascalCase` | Rust Style Guide |
| Constants | `SCREAMING_SNAKE_CASE` | Rust Style Guide |
| Error handling | `Result<T, E>` — never panic in library code | Rust API Guidelines |
| Unsafe | Document every `unsafe` block with a safety comment | C++ Core Guidelines equivalent |
| `unwrap()` / `expect()` | Only in tests and scripts; never in library/production code | Rust API Guidelines |
| Clippy | All lints must pass at `clippy::pedantic` | Team convention |

## Contents

| File | Topic |
|------|-------|
| [style-guide.md](style-guide.md) | Formatting, naming, code patterns |
| [ownership-patterns.md](ownership-patterns.md) | Borrowing, lifetimes, ownership design |
| [error-handling.md](error-handling.md) | Result, thiserror, anyhow |
| [testing.md](testing.md) | Unit, integration, property-based tests |
| [performance.md](performance.md) | Profiling, async, allocation patterns |
| [examples/](examples/) | Good and bad Rust examples |

## Tooling Summary

```bash
cargo fmt                     # format
cargo clippy -- -D warnings   # lint (deny all warnings)
cargo test                    # test
cargo audit                   # security scan
cargo tarpaulin --out Html    # coverage
```
