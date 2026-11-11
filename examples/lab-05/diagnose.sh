#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${BASE_URL:-http://localhost:8080}"
date -Is
result=0
docker compose ps || result=1
for endpoint in health ready; do
  printf '\nSprawdzam /%s\n' "$endpoint"
  curl -fsS --max-time 10 "$BASE_URL/$endpoint" || result=1
done
# Zbieramy logi nawet wtedy, gdy wcześniejszy curl zgłosił błąd.
docker compose logs --tail=20 api proxy || result=1
exit "$result"
