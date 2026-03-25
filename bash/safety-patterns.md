# Bash Safety Patterns

---

## Error Traps and Cleanup

```bash
#!/usr/bin/env bash
set -euo pipefail

# ✅ GOOD: cleanup handler runs on any exit
readonly WORK_DIR="$(mktemp -d)"
readonly LOG_FILE="${WORK_DIR}/process.log"

cleanup() {
  local exit_code=$?
  if [[ "${exit_code}" -ne 0 ]]; then
    echo "ERROR: Script failed with exit code ${exit_code}" >&2
    echo "Log file: ${LOG_FILE}" >&2
  fi
  rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

# ERR trap for detailed error reporting
err_handler() {
  local line_no="${1}"
  echo "ERROR: Command failed at line ${line_no}: ${BASH_COMMAND}" >&2
}
trap 'err_handler ${LINENO}' ERR
```

## Locking to Prevent Concurrent Runs

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly LOCK_FILE="/var/run/myapp-backup.lock"

acquire_lock() {
  if ! mkdir "${LOCK_FILE}" 2>/dev/null; then
    echo "ERROR: Another instance is running (lock: ${LOCK_FILE})" >&2
    exit 1
  fi
  trap 'rmdir "${LOCK_FILE}"' EXIT
}

acquire_lock
# ... rest of script runs with lock held
```

## Retry Pattern

```bash
# ✅ GOOD: retry with exponential backoff
retry() {
  local max_attempts="${1}"
  local delay="${2}"
  local cmd=("${@:3}")

  local attempt=1
  while true; do
    if "${cmd[@]}"; then
      return 0
    fi

    if [[ "${attempt}" -ge "${max_attempts}" ]]; then
      echo "ERROR: Command failed after ${max_attempts} attempts: ${cmd[*]}" >&2
      return 1
    fi

    echo "Attempt ${attempt} failed. Retrying in ${delay}s..." >&2
    sleep "${delay}"
    (( attempt++ ))
    (( delay = delay * 2 ))  # exponential backoff
  done
}

# Usage
retry 3 2 curl -f "https://api.example.com/health"
```

## Checking Dependencies

```bash
# ✅ GOOD: check required tools at startup
check_dependencies() {
  local -r required_tools=("curl" "jq" "aws" "docker")
  local missing_tools=()

  for tool in "${required_tools[@]}"; do
    if ! command -v "${tool}" &>/dev/null; then
      missing_tools+=("${tool}")
    fi
  done

  if [[ "${#missing_tools[@]}" -gt 0 ]]; then
    echo "ERROR: Required tools not found: ${missing_tools[*]}" >&2
    echo "Install them and try again." >&2
    exit 1
  fi
}

check_dependencies
```
