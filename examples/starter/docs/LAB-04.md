# LAB 04 — rozwój API, filtrowanie SQL i testy

**Cel:** dodać funkcję, która wymaga pracy z Python, FastAPI, SQLAlchemy, PostgreSQL i pytest. To ćwiczenie implementacyjne — rozwiązanie piszesz samodzielnie.

## Zadanie biznesowe

Operator NOC chce zobaczyć **tylko incydenty `critical`**. API ma obsługiwać:

```text
GET /incidents                     -> wszystkie
GET /incidents?severity=critical  -> wyłącznie critical
GET /incidents?severity=high      -> wyłącznie high
GET /incidents?severity=urgent    -> HTTP 422 (błędna wartość)
```

Po LAB 03 wywołuj je przez `http://localhost:8080`, przed LAB 03 przez `http://localhost:8000`.

## 1. Znajdź kod, który zmienisz

- `api/app/main.py`: funkcja `list_incidents`.
- `api/app/schemas.py`: `Severity = Literal["low", "medium", "high", "critical"]`.
- `api/tests/test_incidents.py`: istniejące przykłady testów.
- `api/app/models.py`: model tabeli `incidents`.

## 2. Dopisz opcjonalny query parameter

W `list_incidents` użyj wskazówki: `severity: Severity | None = None` (zaimportuj `Severity` z `.schemas`). Użyj budowania zapytania SQLAlchemy:

```python
query = select(Incident)
# TODO: jeśli severity jest podana, dodaj query.where(...)
# TODO: zachowaj sortowanie po id malejąco i zwróć listę
```

**Nie filtruj w Pythonie po pobraniu wszystkich rekordów**; filtr ma być wykonywany w bazie.

## 3. Testy (dopisz sam)

W `api/tests/test_incidents.py` dodaj `test_filter_incidents_by_severity`, który:

1. Tworzy incydent `critical` i incydent `low`.
2. Wywołuje `/incidents?severity=critical`.
3. Sprawdza, że otrzymał tylko jeden incydent o `severity=critical`.
4. Sprawdza `/incidents?severity=urgent` → `422`.
5. Sprawdza, że `/incidents` bez parametru nadal zwraca oba incydenty.

Uruchom testy:

```bash
PYTHONPATH=api python -m pytest -q api/tests
```

Jeśli nie masz lokalnego środowiska Python, możesz użyć jednorazowego środowiska testowego lub zainstalować zależności z `api/requirements-dev.txt` zgodnie z README. Aby odświeżyć kod w działającym kontenerze:

```bash
docker compose up -d --build
```

## 4. Weryfikacja na PostgreSQL

```bash
curl -X POST http://localhost:8080/incidents   -H 'Content-Type: application/json'   -d '{"title":"Brak dostepnosci sieci","severity":"critical"}'
curl 'http://localhost:8080/incidents?severity=critical'
docker compose exec db psql -U incidentflow -d incidentflow   -c 'SELECT id, title, severity, status FROM incidents ORDER BY id DESC LIMIT 10;'
```

Jeśli zmieniłeś dane dostępu w `.env`, dostosuj użytkownika i nazwę bazy.

## Kryteria zaliczenia

- Działają cztery przypadki z sekcji „Zadanie biznesowe”.
- Nowy test przechodzi, a stare nadal są zielone.
- Rozumiesz, czemu walidacja `Literal` daje 422.
- Commit: `feat(api): filter incidents by severity`.

**Bonus:** dodaj analogiczne filtrowanie `status`, a później limitowanie wyników `limit` (np. 1–100). W osobnym commicie.
