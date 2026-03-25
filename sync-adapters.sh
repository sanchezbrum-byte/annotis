#!/usr/bin/env bash
# sync-adapters.sh — Regenerate all AI tool adapter files from core/ source files.
#
# Usage:
#   ./sync-adapters.sh
#
# This script reads the canonical rule files from ai-rules/core/ and
# regenerates all adapter files for every supported AI coding tool.
# Run this whenever you update a core/ file.

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CORE_DIR="${SCRIPT_DIR}/ai-rules/core"
readonly ADAPTERS_DIR="${SCRIPT_DIR}/ai-rules/adapters"

log_info()  { echo "[INFO]  $*"; }
log_error() { echo "[ERROR] $*" >&2; }

# Language configurations: "name|globs"
declare -a LANGUAGES=(
  "universal|[\"**/*\"]"
  "python|[\"**/*.py\"]"
  "javascript|[\"**/*.js\", \"**/*.mjs\", \"**/*.cjs\"]"
  "typescript|[\"**/*.ts\", \"**/*.tsx\"]"
  "java|[\"**/*.java\"]"
  "cpp|[\"**/*.cc\", \"**/*.cpp\", \"**/*.h\", \"**/*.hpp\"]"
  "rust|[\"**/*.rs\"]"
  "go|[\"**/*.go\"]"
  "sql|[\"**/*.sql\"]"
  "swift|[\"**/*.swift\"]"
  "kotlin|[\"**/*.kt\", \"**/*.kts\"]"
  "bash|[\"**/*.sh\"]"
  "git-workflow|[\"**/.git*\"]"
  "testing|[\"**/*test*\", \"**/*spec*\"]"
  "security|[\"**/*\"]"
  "architecture|[\"**/*\"]"
)

# ---------------------------------------------------------------------------
# Cursor adapter (.mdc files with YAML frontmatter)
# ---------------------------------------------------------------------------
generate_cursor() {
  local cursor_dir="${ADAPTERS_DIR}/cursor/.cursor/rules"
  mkdir -p "${cursor_dir}"
  log_info "Generating Cursor adapters → ${cursor_dir}"

  for entry in "${LANGUAGES[@]}"; do
    local lang="${entry%%|*}"
    local globs="${entry##*|}"
    local core_file="${CORE_DIR}/${lang}.md"
    local out_file="${cursor_dir}/${lang}.mdc"

    if [[ ! -f "${core_file}" ]]; then
      log_error "Core file not found: ${core_file}"
      continue
    fi

    local description
    description="$(grep '^#' "${core_file}" | head -1 | sed 's/^# //')"

    {
      echo "---"
      echo "description: ${description}"
      echo "globs: ${globs}"
      if [[ "${lang}" == "universal" || "${lang}" == "security" ]]; then
        echo "alwaysApply: true"
      else
        echo "alwaysApply: false"
      fi
      echo "---"
      echo ""
      cat "${core_file}"
    } > "${out_file}"
  done

  log_info "Cursor: generated ${#LANGUAGES[@]} .mdc files"
}

# ---------------------------------------------------------------------------
# Windsurf adapter (plain .md files)
# ---------------------------------------------------------------------------
generate_windsurf() {
  local windsurf_dir="${ADAPTERS_DIR}/windsurf/.windsurf/rules"
  mkdir -p "${windsurf_dir}"
  log_info "Generating Windsurf adapters → ${windsurf_dir}"

  for entry in "${LANGUAGES[@]}"; do
    local lang="${entry%%|*}"
    local core_file="${CORE_DIR}/${lang}.md"
    local out_file="${windsurf_dir}/${lang}.md"

    if [[ ! -f "${core_file}" ]]; then continue; fi

    cp "${core_file}" "${out_file}"
  done

  log_info "Windsurf: generated ${#LANGUAGES[@]} .md files"
}

# ---------------------------------------------------------------------------
# GitHub Copilot adapter (single merged file)
# ---------------------------------------------------------------------------
generate_copilot() {
  local copilot_dir="${ADAPTERS_DIR}/github-copilot/.github"
  mkdir -p "${copilot_dir}"
  local out_file="${copilot_dir}/copilot-instructions.md"
  log_info "Generating GitHub Copilot adapter → ${out_file}"

  {
    echo "# Engineering Standards — GitHub Copilot Instructions"
    echo ""
    echo "> Auto-generated from ai-rules/core/. Do not edit directly."
    echo "> Edit core/ files and run sync-adapters.sh to regenerate."
    echo ""
    echo "---"
    echo ""

    for entry in "${LANGUAGES[@]}"; do
      local lang="${entry%%|*}"
      local core_file="${CORE_DIR}/${lang}.md"
      if [[ ! -f "${core_file}" ]]; then continue; fi

      local title
      title="$(grep '^#' "${core_file}" | head -1 | sed 's/^# //')"
      echo "## ${title}"
      echo ""
      tail -n +2 "${core_file}"
      echo ""
      echo "---"
      echo ""
    done
  } > "${out_file}"

  log_info "Copilot: generated merged file ($(wc -l < "${out_file}") lines)"
}

# ---------------------------------------------------------------------------
# Continue.dev adapter (config.json with systemMessage)
# ---------------------------------------------------------------------------
generate_continue() {
  local continue_dir="${ADAPTERS_DIR}/continue/.continue"
  mkdir -p "${continue_dir}"
  local out_file="${continue_dir}/config.json"
  log_info "Generating Continue.dev adapter → ${out_file}"

  # Build system message from universal + key language summaries
  local system_message
  system_message="$(cat "${CORE_DIR}/universal.md" | sed 's/"/\\"/g' | tr '\n' '\\n')"

  cat > "${out_file}" << EOF
{
  "models": [
    {
      "title": "Default Model",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    }
  ],
  "systemMessage": "You are an expert software engineer. Apply all engineering standards from the ai-rules/core/ directory. Key rules:\\n\\n$(cat "${CORE_DIR}/universal.md" | head -60 | sed 's/"/\\"/g' | tr '\n' '\\n')\\n\\nFor language-specific rules, refer to ai-rules/core/<language>.md for the active language.",
  "contextProviders": [
    {"name": "file", "params": {}},
    {"name": "code", "params": {}}
  ]
}
EOF

  log_info "Continue.dev: generated config.json"
}

# ---------------------------------------------------------------------------
# Aider adapter (CONVENTIONS.md)
# ---------------------------------------------------------------------------
generate_aider() {
  local out_dir="${ADAPTERS_DIR}/aider"
  mkdir -p "${out_dir}"
  local out_file="${out_dir}/CONVENTIONS.md"
  log_info "Generating Aider adapter → ${out_file}"

  {
    echo "# Engineering Conventions — loaded automatically by Aider"
    echo ""
    echo "> Auto-generated from ai-rules/core/. Do not edit directly."
    echo "> Edit core/ files and run sync-adapters.sh to regenerate."
    echo ""
    echo "---"
    echo ""

    for lang in universal git-workflow testing security architecture python javascript typescript java go rust cpp sql bash; do
      local core_file="${CORE_DIR}/${lang}.md"
      if [[ -f "${core_file}" ]]; then
        cat "${core_file}"
        echo ""
        echo "---"
        echo ""
      fi
    done
  } > "${out_file}"

  log_info "Aider: generated CONVENTIONS.md ($(wc -l < "${out_file}") lines)"
}

# ---------------------------------------------------------------------------
# Claude adapter (CLAUDE.md)
# ---------------------------------------------------------------------------
generate_claude() {
  local out_dir="${ADAPTERS_DIR}/claude"
  mkdir -p "${out_dir}"
  local out_file="${out_dir}/CLAUDE.md"
  log_info "Generating Claude adapter → ${out_file}"

  {
    echo "# Project Engineering Standards — Claude Memory File"
    echo ""
    echo "> Auto-generated from ai-rules/core/. Do not edit directly."
    echo "> Edit core/ files and run sync-adapters.sh to regenerate."
    echo ""
    echo "---"
    echo ""

    for entry in "${LANGUAGES[@]}"; do
      local lang="${entry%%|*}"
      local core_file="${CORE_DIR}/${lang}.md"
      if [[ -f "${core_file}" ]]; then
        cat "${core_file}"
        echo ""
        echo "---"
        echo ""
      fi
    done
  } > "${out_file}"

  log_info "Claude: generated CLAUDE.md ($(wc -l < "${out_file}") lines)"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  log_info "Starting adapter sync from: ${CORE_DIR}"

  if [[ ! -d "${CORE_DIR}" ]]; then
    log_error "Core directory not found: ${CORE_DIR}"
    exit 1
  fi

  generate_cursor
  generate_windsurf
  generate_copilot
  generate_continue
  generate_aider
  generate_claude

  log_info "✓ All adapters synced successfully"
  log_info ""
  log_info "Generated adapters:"
  log_info "  Cursor:          ai-rules/adapters/cursor/.cursor/rules/*.mdc"
  log_info "  Windsurf:        ai-rules/adapters/windsurf/.windsurf/rules/*.md"
  log_info "  GitHub Copilot:  ai-rules/adapters/github-copilot/.github/copilot-instructions.md"
  log_info "  Continue.dev:    ai-rules/adapters/continue/.continue/config.json"
  log_info "  Aider:           ai-rules/adapters/aider/CONVENTIONS.md"
  log_info "  Claude:          ai-rules/adapters/claude/CLAUDE.md"
}

main "$@"
