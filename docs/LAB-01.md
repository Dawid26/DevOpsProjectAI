# LAB 01 — uruchom, zbadaj, zepsuj, napraw

[Spis wszystkich działów](COURSE.md) · [Proste wyjaśnienia tego działu](OD-ZERA.md#lab-01)


## Cel

Uruchomić **dwa serwisy** (`api`, `db`), udowodnić, że API komunikuje się z PostgreSQL, a następnie świadomie wywołać awarię i ją zdiagnozować.

## Część A — przygotowanie (WSL Ubuntu)

```bash
docker version
docker compose version
git --version
pwd
```

Jeśli `docker version` nie może połączyć się z daemonem, przejdź do `TROUBLESHOOTING.md`. Jeśli WSL nie jest poprawnie zintegrowany z Docker Desktop, `docker compose` nie zadziała.

## Część B — start

```bash
cp .env.example .env
docker compose config
docker compose up -d --build
docker compose ps
```

**Odpowiedz sobie:**

1. Dlaczego w Compose używamy `db`, a nie `localhost`, aby API połączyło się z bazą?
2. Co oznacza `127.0.0.1:8000:8000`?
3. Dlaczego `api` ma `depends_on: condition: service_healthy`?
4. Czy usunięcie kontenera PostgreSQL usuwa dane?

## Część C — operacje na aplikacji

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
curl -X POST http://localhost:8000/incidents \
  -H 'Content-Type: application/json' \
  -d '{"title":"Serwer API nie odpowiada","severity":"critical"}'
curl http://localhost:8000/incidents
```

Wejdź na http://localhost:8000/docs i wykonaj dodatkowe żądanie za pomocą Swagger UI.

## Część D — obserwacja

```bash
docker compose ps
docker compose logs --tail=50 api
docker compose exec db psql -U incidentflow -d incidentflow \
  -c 'SELECT id, title, severity, status FROM incidents;'
docker volume ls
```

**Zadanie:** znajdź nazwę wolumenu PostgreSQL i wyjaśnij, po co służy.

## Część E — kontrolowana awaria

UWAGA: wykonuj tylko na lokalnym środowisku edukacyjnym.

```bash
docker compose stop db
curl -i http://localhost:8000/health
curl -i http://localhost:8000/ready
docker compose logs --tail=30 api
docker compose start db
docker compose ps
curl -i http://localhost:8000/ready
```

**Oczekiwane:** liveness `/health` może nadal zwracać 200, ale readiness `/ready` zwróci 503, gdy PostgreSQL nie odpowiada. Po restarcie bazy readiness powinien wrócić do 200. Jeśli start bazy jeszcze trwa, sprawdź logi i ponów test.

## Część F — Git i notatka z incydentu

```bash
git init
git switch -c lab/01-docker-postgres
git status
git add .
git commit -m "feat: bootstrap IncidentFlow Compose and API"
```

**Uwaga:** zanim zrobisz commit sprawdź `git status` i upewnij się, że `.env` nie jest dodany. Jeśli masz już repozytorium Git, pomiń `git init`, a jeśli branch istnieje, wybierz inną nazwę.

Utwórz `docs/POSTMORTEM-01.md` i zapisz: objawy, komendy diagnostyczne, przyczyna, naprawa, wnioski.

## Co mi pokażesz po LAB 01?

- `docker compose ps`
- odpowiedź `curl -i http://localhost:8000/ready` przy uruchomionej bazie
- wynik `/ready` przy zatrzymanej bazie
- własne odpowiedzi na cztery pytania z części B

Następny LAB: **Linux + DNS + sieci Dockera** (sprawdzenie nazwy `db`, portów i ruchu HTTP).

## Kod startowy

Komplet plików jest teraz w [examples/starter](../examples/starter). Sposób skopiowania do osobnego katalogu jest w [instrukcji startowej](COURSE.md).
