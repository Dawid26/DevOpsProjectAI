#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8080}"
echo "[1/3] Check Nginx is running"
docker compose ps --services --status running | grep -qx proxy

echo "[2/3] Check API is available through Nginx"
curl --fail-with-body -sS "${BASE_URL}/health" >/dev/null
curl --fail-with-body -sS "${BASE_URL}/ready" >/dev/null

echo "[3/3] Check API does not publish port 8000 to the host"
if docker compose port api 8000 >/dev/null 2>&1; then
  echo "FAIL: api publishes a port. Remove api.ports from compose.yaml" >&2
  exit 1
fi

echo "PASS — LAB 03 reverse proxy checks"
