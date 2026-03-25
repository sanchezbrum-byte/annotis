# Go Tooling

## Required Tools

```bash
# Install all tooling
go install golang.org/x/tools/cmd/goimports@latest
go install honnef.co/go/tools/cmd/staticcheck@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
go install golang.org/x/vuln/cmd/govulncheck@latest
```

## Makefile (Reference)

```makefile
.PHONY: fmt lint test test-race build clean

fmt:
    goimports -l -w .
    gofmt -l -w .

lint:
    go vet ./...
    staticcheck ./...
    golangci-lint run

test:
    go test -count=1 ./...

test-race:
    go test -race -count=1 ./...

test-integration:
    go test -race -run Integration ./...

build:
    go build -o bin/myapp ./cmd/myapp

clean:
    rm -rf bin/

ci: fmt lint test-race
```

## go.mod Standards

```
module github.com/mycompany/myapp

go 1.22

require (
    github.com/jackc/pgx/v5 v5.6.0
    github.com/stretchr/testify v1.9.0
    go.uber.org/zap v1.27.0
)
```

- Pin exact versions; use `go mod tidy` to clean up
- Audit dependencies with `govulncheck` in CI
- Use `go mod vendor` for reproducible builds in CI (optional but recommended)
