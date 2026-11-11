# Troubleshooting — pierwsza pomoc

## Docker Desktop / WSL

```bash
docker version
docker context ls
wsl.exe -l -v
```

- Docker Desktop musi być uruchomiony.
- W ustawieniach Docker Desktop > Resources > WSL Integration włącz właściwą dystrybucję Ubuntu.
- Jeśli w WSL pojawia się `Cannot connect to the Docker daemon`, to problem z silnikiem lub integracją, nie z FastAPI.
- Jeżeli usługa `com.docker.service` na Windows nie startuje, diagnozujemy ją po stronie Windows i czytamy dokładny komunikat; nie usuwaj ręcznie danych Dockera przed backupem.

## API się restartuje

```bash
docker compose ps
docker compose logs --tail=100 api
docker compose logs --tail=100 db
```

Możliwe przyczyny: zmienna `DATABASE_URL`, brak połączenia, błąd startowy Python.

## `curl: connection refused`

- Sprawdź, czy `api` istnieje i czy ma status `Up`.
- Sprawdź w `docker compose ps` port `127.0.0.1:8000->8000/tcp`.
- Jeśli inny proces używa 8000, zmień `APP_PORT=8080` w `.env` i ponownie uruchom Compose, a następnie otwórz `http://localhost:8080`.

## Baza nie zachowuje danych

Dane PostgreSQL żyją w named volume `postgres_data`. `docker compose down` go zachowuje, ale `docker compose down -v` usuwa go. Nigdy nie wykonuj `-v` na ważnej bazie bez backupu.

## Testy nie działają

Uruchamiaj z katalogu głównego:

```bash
PYTHONPATH=api python -m pytest -q api/tests
```

Testy korzystają z SQLite, więc nie wymagają PostgreSQL ani Dockera.
