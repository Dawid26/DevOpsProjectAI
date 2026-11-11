#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
echo "[1/3] Liveness"
curl --fail-with-body --silent --show-error "${BASE_URL}/health"
echo

echo "[2/3] Readiness (with PostgreSQL)"
curl --fail-with-body --silent --show-error "${BASE_URL}/ready"
echo

echo "[3/3] Create demo incident"
curl --fail-with-body --silent --show-error \
  -X POST "${BASE_URL}/incidents" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Example: web server unavailable","severity":"high"}'
echo
echo "PASS: API responds. Check ${BASE_URL}/docs"
