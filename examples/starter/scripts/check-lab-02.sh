#!/usr/bin/env bash
set -euo pipefail

echo "[1/3] Verify API readiness"
curl --fail-with-body -sS http://localhost:8000/ready >/dev/null

echo "[2/3] Verify Compose DNS and db TCP reachability"
docker compose exec -T api python - <<'PYCODE'
import socket
resolved = socket.gethostbyname("db")
print("db resolves to:", resolved)
with socket.create_connection(("db", 5432), timeout=3):
    print("db:5432 reachable")
PYCODE

echo "[3/3] Verify broken DNS gives an error"
docker compose exec -T api python - <<'PYCODE'
import socket
try:
    socket.gethostbyname("nie-ma-takiego-serwisu")
except socket.gaierror:
    print("Unknown service name fails as expected")
else:
    raise SystemExit("Unexpected DNS resolution; check network")
PYCODE

echo "PASS — LAB 02 network checks"
