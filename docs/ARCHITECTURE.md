# Architecture Decision Record (ADR-001)

## Problem

Chcemy uczyć się operacji DevOps na projekcie, który jest realistyczny, lecz da się uruchomić na laptopie bez chmury.

## Decyzja

1. **FastAPI:** czytelne endpointy, wbudowane OpenAPI i dokumentacja `/docs`.
2. **PostgreSQL:** relacyjna baza, standard SQL, praktyczna obsługa volume, backup, restore.
3. **Docker Compose:** powtarzalny lokalny start kilku usług.
4. **Readiness i liveness:** możliwość odróżnienia zdrowia procesu od dostępności zależności.
5. **API dostępne tylko na `127.0.0.1`:** nie udostępniamy niezabezpieczonego MVP w sieci.

## Trade-offy

- `create_all()` zamiast Alembic jest proste, ale nie zarządza migracjami istniejącego schematu — zamienimy je w późniejszym etapie.
- Brak autoryzacji upraszcza lab, lecz wyklucza publiczne wdrożenie.
- PostgreSQL uruchamiany lokalnie w Compose jest dobry do ćwiczeń, nie do produkcyjnej odporności na awarie.
- CI testuje API na SQLite; później dodamy testy integracyjne z PostgreSQL.

## Etapy rozwoju architektury

```text
MVP:          curl -> FastAPI -> PostgreSQL (volume)
Proxy:        curl -> Nginx -> FastAPI -> PostgreSQL
Async:        FastAPI -> Redis queue -> Worker
Platform:     GH Actions -> GHCR -> Kubernetes -> Helm
Observability: API/Worker -> Prometheus/Grafana/Loki
Cloud:        Terraform -> AWS infrastructure (optional)
```
