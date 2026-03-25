# Bash Testing Standards

> **Tools:** BATS (Bash Automated Testing System), shellcheck

---

## BATS (bats-core)

```bash
# Install
npm install --save-dev bats bats-support bats-assert
# Or via Homebrew: brew install bats-core
```

## Test File Structure

```bash
#!/usr/bin/env bats
# tests/export_user_data.bats

load '../node_modules/bats-support/load'
load '../node_modules/bats-assert/load'

# Source the script under test (functions only, not main execution)
source "${BATS_TEST_DIRNAME}/../scripts/export_user_data.sh"

# Setup and teardown
setup() {
  # Create temp directory for each test
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR
}

teardown() {
  rm -rf "${TEST_DIR}"
}

# Test naming: description of what it tests
@test "export_user_data creates output file with user data" {
  # Arrange
  local output_file="${TEST_DIR}/user_data.json"
  export DATABASE_URL="sqlite://:memory:"

  # Act
  run export_user_data "user-1" "${output_file}"

  # Assert
  assert_success
  assert [ -f "${output_file}" ]
  assert_output --partial "user-1"
}

@test "export_user_data fails when output directory is not writable" {
  local output_file="/root/no_permission/data.json"  # not writable

  run export_user_data "user-1" "${output_file}"

  assert_failure
  assert_output --partial "not writable"
}

@test "export_user_data fails when user_id argument is missing" {
  run export_user_data

  assert_failure
  assert_output --partial "Usage:"
}

@test "retry succeeds after transient failure" {
  local call_count=0
  flaky_command() {
    (( call_count++ ))
    if [[ "${call_count}" -lt 3 ]]; then
      return 1
    fi
    echo "success"
  }
  export -f flaky_command

  run retry 3 1 flaky_command

  assert_success
  assert_output "success"
}
```

## Running Tests

```bash
# Run all tests
bats tests/

# Run with TAP output (for CI)
bats --formatter tap tests/

# Run specific test file
bats tests/export_user_data.bats

# ShellCheck on all scripts
shellcheck scripts/*.sh

# Both in CI
make test
```
