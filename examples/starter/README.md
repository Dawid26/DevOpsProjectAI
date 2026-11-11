# IncidentFlow — DevOps Engineering Lab

**One evolving portfolio project**: incident management API + infrastructure and DevOps practices.

> Stan na start: **Etap 1–3 / MVP lokalny**. Działa FastAPI, PostgreSQL i Docker Compose. Redis, worker, Nginx, Kubernetes, Grafana i AWS to zaplanowane etapy — **nie są jeszcze zaimplementowane**.

## Dlaczego taki projekt?

To prawdziwy scenariusz operacyjny: rejestracja incydentów, zmiana statusów, health checks, baza danych i dalsza automatyzacja. Nie jest to tylko "Hello World" z kontenerem.

## Architektura MVP (naprawdę działa)

```text
Przeglądarka / curl
        |
        | http://localhost:8000
        v
   FastAPI (api) ---------> PostgreSQL (db)
      |                         |
    /docs                  volume z danymi
    /health
    /ready
    /incidents
```

**Docelowo:** Nginx → API → PostgreSQL + Redis/worker, CI/CD → GHCR → Kubernetes/Helm, Prometheus/Grafana/Loki, Terraform/AWS, alerty, backup, security.

## Wymagania lokalne

- Windows 11 + WSL Ubuntu lub Linux/macOS
- Docker Desktop z aktywnym silnikiem Docker i integracją WSL (jeśli używasz WSL)
- Git, curl; opcjonalnie Python 3.12 i make
- Nie potrzebujesz konta AWS ani płatnych usług na start

## Uruchomienie

W terminalu WSL, w katalogu repozytorium:

```bash
cp .env.example .env
# Opcjonalnie zmień dane lokalne w .env, NIE dodawaj .env do Git.
docker compose config
docker compose up -d --build
docker compose ps
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Dokumentacja interaktywna: http://localhost:8000/docs

Test utworzenia incydentu:

```bash
curl -X POST http://localhost:8000/incidents \
  -H 'Content-Type: application/json' \
  -d '{"title":"API nie odpowiada","severity":"high"}'

curl http://localhost:8000/incidents
curl -X PATCH http://localhost:8000/incidents/1 \
  -H 'Content-Type: application/json' \
  -d '{"status":"investigating"}'
```

Kontrola i debugowanie:

```bash
docker compose logs -f api
docker compose logs --tail=50 db
docker compose exec db psql -U incidentflow -d incidentflow -c 'SELECT * FROM incidents;'
docker compose down             # zatrzymaj, ZACHOWAJ dane
docker compose down -v          # UWAGA: usuwa również dane na volume
```

## Testy (bez bazy i bez Dockera)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r api/requirements-dev.txt
PYTHONPATH=api python -m pytest -q api/tests
```

`pytest` używa SQLite w pamięci. Główna aplikacja korzysta z PostgreSQL.

## Kurs i zadania

Zacznij od **[docs/LAB-01.md](docs/LAB-01.md)**. Kontynuacja: **[LAB 02 — sieci](docs/LAB-02.md)**, **[LAB 03 — Nginx](docs/LAB-03.md)**, **[LAB 04 — SQL i API](docs/LAB-04.md)**, **[LAB 05 — Bash i CI](docs/LAB-05.md)**. Pełna ścieżka: [docs/ROADMAP.md](docs/ROADMAP.md). Problemy: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Co umieścić na GitHubie

1. Repozytorium publiczne `incidentflow-devops-lab` bez `.env`, haseł i logów produkcyjnych.
2. Każdy etap = osobny branch/PR lub wyraźny commit z opisem tego, co rozwiązałeś.
3. Dokumentuj incydent: objawy → diagnoza → naprawa → weryfikacja (runbook).
4. Po późniejszych etapach dołącz diagram, screenshot Grafany, status CI i opis deploymentu.

## Bezpieczeństwo i ograniczenia

- MVP **nie ma logowania/autoryzacji**. Uruchamiaj wyłącznie lokalnie; nie wystawiaj publicznie.
- Przykładowe hasło w `.env.example` służy tylko do lokalnego labu. Użyj innego sekretu w prawdziwym środowisku.
- Tabele tworzone są na starcie przez `create_all`; migracje Alembic dodamy później.
- Zależności mają zakresy wersji; na etapie CI/CD dodamy lockowanie i skanowanie obrazów.


> Uwaga: kolejne LAB-y zawierają ćwiczenia do wykonania przez Ciebie; nowy ZIP nie modyfikuje jeszcze MVP. Jeśli masz już własne zmiany, skopiuj do istniejącego repo wyłącznie nowe dokumenty i skrypty sprawdzające zamiast nadpisywać projekt.
