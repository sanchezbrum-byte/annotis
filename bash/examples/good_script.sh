#!/usr/bin/env bash
# deploy.sh — Deploy application to an environment.
#
# Usage:
#   ./deploy.sh <environment> <version>
#
# Examples:
#   ./deploy.sh staging v2.4.0
#   ./deploy.sh production v2.4.0
#
# Environment variables required:
#   AWS_REGION        - AWS region (e.g., us-east-1)
#   ECR_REGISTRY      - ECR registry URL
#   DEPLOY_TIMEOUT    - Deployment timeout in seconds (default: 300)

set -euo pipefail

# ✅ Constants are UPPER_SNAKE_CASE and readonly
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly DEPLOY_TIMEOUT="${DEPLOY_TIMEOUT:-300}"
readonly ALLOWED_ENVIRONMENTS=("staging" "production")

# ✅ Colors for output (with terminal check)
if [[ -t 1 ]]; then
  readonly RED='\033[0;31m'
  readonly GREEN='\033[0;32m'
  readonly YELLOW='\033[1;33m'
  readonly NC='\033[0m'
else
  readonly RED='' GREEN='' YELLOW='' NC=''
fi

# ✅ Structured log functions — errors to stderr
log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ✅ cleanup runs on any exit via trap
cleanup() {
  local exit_code=$?
  if [[ "${exit_code}" -ne 0 ]]; then
    log_error "Deployment failed with exit code ${exit_code}"
  fi
}
trap cleanup EXIT

# ✅ Validate required tools at startup — fail fast
check_dependencies() {
  local required=("aws" "docker" "jq")
  for tool in "${required[@]}"; do
    if ! command -v "${tool}" &>/dev/null; then
      log_error "Required tool not found: ${tool}"
      exit 1
    fi
  done
}

# ✅ Local variables in all functions
validate_arguments() {
  local environment="${1}"
  local version="${2}"

  # ✅ Whitelist validation — not blacklist
  local is_valid=false
  for allowed in "${ALLOWED_ENVIRONMENTS[@]}"; do
    if [[ "${environment}" == "${allowed}" ]]; then
      is_valid=true
      break
    fi
  done

  if [[ "${is_valid}" == false ]]; then
    log_error "Invalid environment: ${environment}"
    log_error "Allowed environments: ${ALLOWED_ENVIRONMENTS[*]}"
    return 1
  fi

  if [[ ! "${version}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    log_error "Version must match vMAJOR.MINOR.PATCH format, got: ${version}"
    return 1
  fi
}

# ✅ Functions are small and focused (Single Responsibility)
build_image() {
  local version="${1}"
  local image_tag="${ECR_REGISTRY}/myapp:${version}"

  log_info "Building image: ${image_tag}"
  docker build \
    --tag "${image_tag}" \
    --build-arg "VERSION=${version}" \
    "${SCRIPT_DIR}/.."

  log_info "Pushing image to ECR"
  docker push "${image_tag}"

  echo "${image_tag}"
}

deploy_to_ecs() {
  local environment="${1}"
  local image_tag="${2}"

  log_info "Deploying ${image_tag} to ${environment}"

  aws ecs update-service \
    --region "${AWS_REGION:?AWS_REGION must be set}" \
    --cluster "myapp-${environment}" \
    --service "myapp" \
    --force-new-deployment \
    --output json | jq -r '.service.serviceName'

  log_info "Waiting for deployment to stabilize (timeout: ${DEPLOY_TIMEOUT}s)"
  aws ecs wait services-stable \
    --region "${AWS_REGION}" \
    --cluster "myapp-${environment}" \
    --services "myapp"
}

# ✅ Main function — clear top-level script flow
main() {
  # ✅ Validate argument count before accessing $1, $2
  if [[ "$#" -ne 2 ]]; then
    log_error "Usage: ${SCRIPT_NAME} <environment> <version>"
    log_error "Example: ${SCRIPT_NAME} staging v2.4.0"
    exit 1
  fi

  local environment="${1}"
  local version="${2}"

  check_dependencies
  validate_arguments "${environment}" "${version}"

  log_info "Starting deployment: ${version} → ${environment}"
  local image_tag
  image_tag="$(build_image "${version}")"
  deploy_to_ecs "${environment}" "${image_tag}"

  log_info "Deployment complete: ${image_tag} is live in ${environment}"
}

main "$@"
