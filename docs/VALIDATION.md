# Zakres sprawdzenia materiałów

Kontrole dotyczą przygotowania materiałów, nie ukończenia ćwiczeń przez ucznia.

- Sprawdzenie składni Pythona, skryptów Bash i bloków poleceń.
- Parsowanie manifestów YAML i sprawdzenie lokalnych linków dokumentacji.
- Testy API startera oraz rozwiązania filtra LAB 04 w osobnej kopii.
- Test licznika HTTP LAB 14: 200, 503, nieobsłużony błąd 500 i pomijanie odczytów metryk.
- Kontrola struktury JSON do importu logów LAB 15.
- Lokalny playbook LAB 16 (ansible-core 2.19): dwa wykonania i potwierdzenie braku zmian w drugim.
- Sprawdzenie składni JavaScript portfolio.

Pełne uruchomienie Docker Compose, Kubernetes, Helm, Argo CD, Prometheus i Loki wymaga środowiska użytkownika i nie zostało tu wykonane. GitHub Actions wymaga workflow w repozytorium aplikacji. AWS pozostaje przykładem planowania. Biblioteki z przedziałami wersji mogą się zmieniać; zapisuj użyte wersje we własnych raportach.

Materiały LAB 01–05 zawierają zachowany kod startowy i jego dokumentację; główna, aktualna ścieżka znajduje się w [COURSE.md](COURSE.md). Status „Ćwiczenie” w portfolio oznacza dostępność instrukcji, nie zaliczenie.

Podczas kontroli nowsza gałąź Ansible zgłosiła błąd uruchomienia lokalnego serwera RPC w tym środowisku. Instrukcję ograniczono do przetestowanej gałęzi 2.19. Testy API: 6 zaliczonych; biblioteka Starlette zgłasza ostrzeżenie o przyszłej zmianie klienta testowego.
