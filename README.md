# DevOpsProjectAI

Portfolio projektu edukacyjnego IncidentFlow. Strona prezentuje architekturę lokalnego środowiska FastAPI i PostgreSQL, uruchomienie przez Docker Compose, symulację diagnostyki awarii i filtrowaną ścieżkę nauki.

## Uruchomienie lokalne

Otwórz `index.html` w przeglądarce lub uruchom z katalogu repozytorium:

```sh
python3 -m http.server 8080 --bind 127.0.0.1
```

Otwórz [localhost:8080](http://127.0.0.1:8080/). Strona jest statyczna i działa bez zależności JavaScript. Kod aplikacji FastAPI i jej pliki Docker Compose są częścią osobnego laboratorium IncidentFlow.

## Kontynuacja laboratorium

[LAB 06 — Redis, kolejka i worker](docs/LAB-06.md) prowadzi przez dodanie powiadomień w tle, ponawianie zadań i symulację awarii kolejki. Gotowy kod i konfiguracja są w [examples/lab-06](examples/lab-06).

[LAB 07 — obrazy Docker, GHCR i rollback krok po kroku](docs/LAB-07.md) zawiera budowę obrazu, gotowy workflow, uruchomienie wybranej wersji i powrót do poprzedniej. Szablony znajdziesz w [examples/lab-07](examples/lab-07).
