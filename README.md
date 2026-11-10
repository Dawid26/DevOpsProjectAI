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

[LAB 08 — Kubernetes krok po kroku](docs/LAB-08.md) zawiera lokalny klaster kind, manifesty API, workera, PostgreSQL i Redis oraz ćwiczenia skalowania i awarii. Pliki są w [examples/lab-08](examples/lab-08).

## Zrozum projekt

Otwórz [zrozum-projekt.html](zrozum-projekt.html), aby przeczytać prostym językiem, co robi każda część projektu. Zakładka prowadzi przez jedno zgłoszenie, kolejkę, bazę, kontenery i kolejne etapy nauki.

## Kolejne rozdziały

- [LAB 09 — Helm, Prometheus, Grafana i pierwszy alert](docs/LAB-09.md). [Konfiguracja](examples/lab-09).
- [LAB 10 — Terraform od pierwszego planu do przygotowania AWS](docs/LAB-10.md). [Przykłady lokalne i plan AWS](examples/lab-10).
- [LAB 11 — skan obrazu, uprawnienia kontenera i RBAC](docs/LAB-11.md). [Przykłady](examples/lab-11).

- [LAB 12 — backup PostgreSQL i próba odzyskiwania danych](docs/LAB-12.md). [Skrypty i raport](examples/lab-12).

Wykonuj je w kolejności 09 → 10 → 11 → 12. Każdy rozdział zawiera wyjaśnienia, punkty kontrolne i zadanie do samodzielnego sprawdzenia.
