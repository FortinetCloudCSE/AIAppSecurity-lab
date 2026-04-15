#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ENV_FILE:-${APP_DIR}/.env}"

if [[ -f "${ENV_FILE}" ]]; then
  set -a
  source "${ENV_FILE}"
  set +a
fi

IMAGE_NAME="${IMAGE_NAME:-ai-agent-local}"
CONTAINER_NAME="${CONTAINER_NAME:-ai-agent-local}"
HOST_PORT="${HOST_PORT:-8080}"
CONTAINER_PORT="8080"

ENV_VARS=(
  OPENAI_API_KEY
  OPENAI_MODEL
  FLASK_SECRET_KEY
  AWS_REGION
  AWS_DEFAULT_REGION
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  AWS_SESSION_TOKEN
  S3_BUCKET_NAME
)

DOCKER_ENV_ARGS=()
for var_name in "${ENV_VARS[@]}"; do
  if [[ -n "${!var_name:-}" ]]; then
    DOCKER_ENV_ARGS+=("-e" "${var_name}=${!var_name}")
  fi
done

echo "Building Docker image: ${IMAGE_NAME}"
docker build -t "${IMAGE_NAME}" "${APP_DIR}"

echo "Removing existing container if present: ${CONTAINER_NAME}"
docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

echo "Starting container on http://localhost:${HOST_PORT}"
docker run -d \
  --name "${CONTAINER_NAME}" \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  -v "${APP_DIR}/uploads:/app/uploads" \
  "${DOCKER_ENV_ARGS[@]}" \
  "${IMAGE_NAME}" >/dev/null

echo "Container started successfully."
echo "Name: ${CONTAINER_NAME}"
echo "Image: ${IMAGE_NAME}"
echo "URL: http://localhost:${HOST_PORT}"
