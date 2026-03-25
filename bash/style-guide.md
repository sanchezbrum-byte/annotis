# Bash Style Guide

> **Sources:** Google Shell Style Guide (google.github.io/styleguide/shellguide.html), ShellCheck (github.com/koalaman/shellcheck), "Shell Scripting: Expert Recipes" (Chris F.A. Johnson)

---

## A. Formatting & Style

### Shebang

```bash
#!/usr/bin/env bash
# ✅ GOOD: portable — finds bash in PATH
# ❌ BAD: #!/bin/bash — not portable on all systems (e.g., macOS may have old bash)
```

Always specify `bash`, not `sh` — `/bin/sh` may be dash, busybox, or another POSIX shell. If you need POSIX portability, use only POSIX constructs and test with `shellcheck --shell=sh`.

### Required Safety Flags

```bash
#!/usr/bin/env bash
set -euo pipefail
# -e: exit immediately if a command exits with non-zero status
# -u: treat unset variables as an error
# -o pipefail: pipe returns exit status of last command that failed

# Also useful in scripts:
set -E  # ERR trap is inherited by functions
```

### Indentation

**2 spaces** (Google Shell Style Guide). Never tabs.

### Line Length

**80 characters** soft limit (Google Shell Style Guide). Use `\` for line continuation:

```bash
# ✅ GOOD: line continuation
docker run \
  --rm \
  --name myapp \
  --env-file .env \
  --publish 8080:8080 \
  myapp:latest
```

---

## B. Naming Conventions

| Concept | Convention | Example |
|---------|-----------|---------|
| Functions | `snake_case` | `get_user_by_id`, `create_backup` |
| Local variables | `snake_case` | `user_id`, `backup_path` |
| Global constants (script-level) | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `BACKUP_DIR` |
| Environment variables | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `API_KEY` |

---

## C. Variables

### Always Quote Variables

```bash
# ❌ BAD: unquoted — word splitting and globbing issues
cp $source_file $dest_dir

# ✅ GOOD: always quote
cp "${source_file}" "${dest_dir}"

# ❌ BAD: unquoted in conditions
if [ $name = "alice" ]; then

# ✅ GOOD: quoted
if [[ "${name}" == "alice" ]]; then
```

### Local Variables in Functions

```bash
# ✅ GOOD: declare local variables with local
get_config_value() {
  local key="${1}"
  local default_value="${2:-}"

  local value
  value="$(grep "^${key}=" config.env | cut -d= -f2)"

  echo "${value:-${default_value}}"
}
```

### Use `${var}` Syntax

```bash
# ❌ BAD: ambiguous with adjacent text
echo "Hello $username_file"  # is it $username + _file, or $username_file?

# ✅ GOOD: always use ${} to be explicit
echo "Hello ${username}_file"
echo "Hello ${username}"
```

### Default Values

```bash
# ✅ GOOD: parameter expansion with defaults
readonly LOG_LEVEL="${LOG_LEVEL:-info}"
readonly OUTPUT_DIR="${OUTPUT_DIR:-/tmp/output}"
readonly MAX_RETRIES="${MAX_RETRIES:-3}"
```

---

## D. Functions

```bash
# ✅ GOOD: well-structured function
# Args:
#   $1 - user ID (required)
#   $2 - output file path (required)
# Returns:
#   0 on success
#   1 if user not found
#   2 if output file is not writable
export_user_data() {
  local user_id="${1:?Usage: export_user_data <user_id> <output_file>}"
  local output_file="${2:?Usage: export_user_data <user_id> <output_file>}"

  if [[ ! -w "$(dirname "${output_file}")" ]]; then
    echo "ERROR: Output directory is not writable: $(dirname "${output_file}")" >&2
    return 2
  fi

  local data
  if ! data="$(fetch_user "${user_id}" 2>&1)"; then
    echo "ERROR: User ${user_id} not found" >&2
    return 1
  fi

  echo "${data}" > "${output_file}"
  echo "User data exported to ${output_file}"
}
```

### Argument Validation

```bash
# ✅ GOOD: ${var:?message} exits with error if var is unset or empty
required_arg="${1:?ERROR: First argument is required (user_id)}"

# ✅ GOOD: explicit argument count check
if [[ "$#" -lt 2 ]]; then
  echo "Usage: $0 <user_id> <output_file>" >&2
  exit 1
fi
```

---

## E. Conditionals

### `[[` vs `[`

Always use `[[` (bash extended test) in bash scripts — it is safer and more powerful:

```bash
# ✅ GOOD: [[ ]] — no word splitting, supports && ||, regex with =~
if [[ "${name}" == "alice" && "${role}" == "admin" ]]; then

# ❌ BAD for bash: single brackets — more error-prone
if [ "${name}" = "alice" -a "${role}" = "admin" ]; then
```

### File Tests

```bash
# ✅ GOOD: explicit file tests
if [[ -f "${config_file}" ]]; then         # file exists and is regular file
if [[ -d "${output_dir}" ]]; then          # directory exists
if [[ -x "${script_path}" ]]; then         # file is executable
if [[ -r "${input_file}" ]]; then          # file is readable
if [[ -s "${log_file}" ]]; then            # file exists and is non-empty
```

---

## F. Commands & Output

### Capture Command Output

```bash
# ✅ GOOD: $() not backticks — nestable, readable
result="$(some_command "${arg}")"

# ❌ BAD: backtick syntax — can't be nested cleanly
result=`some_command "${arg}"`
```

### Error Messages to stderr

```bash
# ✅ GOOD: errors go to stderr
echo "ERROR: Database connection failed" >&2
echo "WARNING: Config file not found, using defaults" >&2

# Status messages to stdout
echo "Successfully processed ${count} records"
```

### Check Command Exit Codes

```bash
# ✅ GOOD: check if command succeeded
if ! psql -d "${DATABASE_URL}" -c "SELECT 1" > /dev/null 2>&1; then
  echo "ERROR: Database is not reachable" >&2
  exit 1
fi

# ✅ GOOD: || for fallback
mkdir -p "${output_dir}" || {
  echo "ERROR: Cannot create output directory: ${output_dir}" >&2
  exit 1
}
```

---

## G. Security

### Never Trust User Input

```bash
# ❌ BAD: user input in eval — arbitrary code execution
eval "${user_supplied_command}"

# ❌ BAD: user input as file path without validation
cat "/var/data/${user_input}"  # path traversal: ../../../etc/passwd

# ✅ GOOD: validate user input against a whitelist
case "${user_input}" in
  production|staging|development)
    deploy_to "${user_input}"
    ;;
  *)
    echo "ERROR: Invalid environment: ${user_input}" >&2
    exit 1
    ;;
esac
```

### Never Store Secrets in Scripts

```bash
# ❌ BAD: hardcoded credential in script
DB_PASSWORD="hunter2"

# ✅ GOOD: from environment
DB_PASSWORD="${DB_PASSWORD:?DB_PASSWORD environment variable must be set}"

# ✅ GOOD: from secret manager
DB_PASSWORD="$(aws secretsmanager get-secret-value \
  --secret-id prod/myapp/db-password \
  --query SecretString \
  --output text)"
```

### Temporary Files

```bash
# ✅ GOOD: use mktemp for temporary files
tmp_file="$(mktemp)"
trap 'rm -f "${tmp_file}"' EXIT  # cleanup on exit

# ❌ BAD: predictable path — race condition (TOCTOU attack)
tmp_file="/tmp/myapp_$$"  # $$ is process ID — predictable
```

---

## H. ShellCheck Integration

Run ShellCheck on every script in CI:

```bash
# Install
brew install shellcheck  # macOS
apt-get install shellcheck  # Ubuntu

# Run
shellcheck myscript.sh

# CI: check all scripts
find . -name "*.sh" -exec shellcheck {} +

# Disable specific check with comment (document why)
# shellcheck disable=SC2034  # VAR is used by caller in sourced scripts
```
