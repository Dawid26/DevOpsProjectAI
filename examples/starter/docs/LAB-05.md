# LAB 05 — Bash, diagnostyka SRE i GitHub Actions

**Cel:** zautomatyzować ręczną diagnostykę IncidentFlow i zabezpieczyć zmiany testami CI.

## 1. Skrypt operatorski

Utwórz plik `scripts/diagnose.sh`, który:

1. Włącza bezpieczniejsze wykonywanie Basha: `set -euo pipefail`.
2. Wyświetla datę i godzinę (`date -Is`).
3. Pokazuje kontenery (`docker compose ps`).
4. Sprawdza przez `curl -fsS` endpointy `/health` i `/ready` (domyślnie `http://localhost:8080`).
5. Wyświetla ostatnie 20 linii logów `api` i `proxy` (`docker compose logs --tail=20 api proxy`).
6. Zwraca niezerowy exit code, jeśli readiness nie działa.

**Podpowiedź do konfiguracji:** `BASE_URL="${BASE_URL:-http://localhost:8080}"`.

Przetestuj skrypt zarówno przy **działającej bazie**, jak i po:

```bash
docker compose stop db
bash scripts/diagnose.sh
echo "exit code: $?"
docker compose start db
```

Skrypt ma w niezdrowym stanie **zwracać błąd**. Następnie sprawdź naprawę (`/ready` może potrzebować chwili po starcie bazy).

## 2. Przetestuj GitHub Actions

W repo istnieje `.github/workflows/ci.yml`, który uruchamia pytest po push/PR. Przejrzyj każdą sekcję i wytłumacz:

- `on: push` / `pull_request`
- `actions/checkout`
- `setup-python`
- `PYTHONPATH=api`
- dlaczego testy korzystają z SQLite, a nie Twojego lokalnego PostgreSQL.

Dodaj nowy krok przed pytest:

```yaml
      - name: Check Python syntax
        run: python -m compileall -q api/app
```

Pamiętaj o poprawnej indentacji YAML. Zmiana pipeline będzie widoczna dopiero po wypchnięciu na GitHub (lokalnie bez GitHub Actions jej nie uruchomisz).

## 3. Symulacja błędu builda / testu

Na osobnym branchu **celowo zmień asercję** w `api/tests/test_incidents.py`, aby jeden test nie przeszedł. Uruchom pytest i zobacz raport błędu, potem cofnij zmianę. Nie dodawaj celowo złamanych testów na główną gałąź.

## Kryteria zaliczenia

- `scripts/diagnose.sh` kończy się kodem `0`, gdy `/ready` działa, i kodem różnym od `0`, gdy baza jest niedostępna.
- `ci.yml` przechodzi po push do GitHub.
- Skrypt i własny opis awarii są w repozytorium.
- Commit: `feat(sre): add diagnostic script and CI syntax check`.

**Bonus:** przekieruj logi diagnostyczne do pliku w `reports/` (nie dodawaj wrażliwych logów do repozytorium) i pokaż poprawną obsługę argumentów w Bash.
