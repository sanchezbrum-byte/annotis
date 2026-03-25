# Go Standards

Go is used for backend services, CLI tools, DevOps tooling, and high-performance APIs.

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Line length | No hard limit; gofmt wraps naturally | Effective Go |
| Indentation | Tabs (gofmt enforces) | gofmt |
| Naming: exported | `PascalCase` | Effective Go |
| Naming: unexported | `camelCase` | Effective Go |
| Naming: interfaces | Noun (single method: `er` suffix) | Effective Go |
| Error returns | Always last return value | Effective Go |
| Error values | `errors.New` or `fmt.Errorf` with `%w` for wrapping | Go 1.13+ |
| goroutines | Always document goroutine ownership and cancellation | Google Go Style Guide |
| `panic` | Never in library code; only truly unrecoverable conditions | Effective Go |

## Contents

| File | Topic |
|------|-------|
| [style-guide.md](style-guide.md) | Full formatting and code rules |
| [concurrency.md](concurrency.md) | Goroutines, channels, sync primitives |
| [error-handling.md](error-handling.md) | Error types, wrapping, sentinel errors |
| [testing.md](testing.md) | testing package, testify, table-driven tests |
| [tooling.md](tooling.md) | go vet, staticcheck, golangci-lint |
| [examples/](examples/) | Good and bad Go examples |

## Tooling Summary

```bash
gofmt -l -w .             # format
go vet ./...              # built-in analysis
staticcheck ./...         # advanced static analysis
golangci-lint run         # aggregated linting
go test -race ./...       # tests with race detector
govulncheck ./...         # security vulnerability scan
```
