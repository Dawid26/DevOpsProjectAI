# IncidentFlow — cała ścieżka nauki

Zacznij od [wyjaśnienia od zera](OD-ZERA.md). Potem wykonuj jeden dział naraz. Każdy wiersz poniżej prowadzi do instrukcji. Pole „wynik” uzupełnij we własnej kopii dopiero po wykonaniu ćwiczenia.

To komplet 17 laboratoriów lokalnego projektu edukacyjnego. AWS w LAB 10 jest opcjonalnym planem infrastruktury, nie wdrożeniem produkcyjnym. Przygotowane instrukcje nie oznaczają, że ćwiczenia zostały wykonane na Twoim komputerze.

| Dział | Co potrafisz po ćwiczeniu | Twój wynik |
| --- | --- | --- |
| [LAB 01 — Docker i pierwsza aplikacja](LAB-01.md) | Uruchomić API i bazę | Do wykonania |
| [LAB 02 — Linux, DNS i sieć](LAB-02.md) | Wyjaśnić drogę do db:5432 | Do wykonania |
| [LAB 03 — Nginx](LAB-03.md) | Przekazać żądanie przez proxy | Do wykonania |
| [LAB 04 — Python, SQL i testy](LAB-04.md) | Filtrować zgłoszenia | Do wykonania |
| [LAB 05 — Bash i CI](LAB-05.md) | Automatycznie sprawdzić zmianę | Do wykonania |
| [LAB 06 — Redis i worker](LAB-06.md) | Wykonać zadanie w tle | Do wykonania |
| [LAB 07 — Obrazy i CD](LAB-07.md) | Wdrożyć wersję i ją wycofać | Do wykonania |
| [LAB 08 — Kubernetes](LAB-08.md) | Uruchomić usługi w klastrze | Do wykonania |
| [LAB 09 — Helm i monitoring](LAB-09.md) | Zobaczyć metryki i alert | Do wykonania |
| [LAB 10 — Terraform](LAB-10.md) | Przeczytać i wykonać lokalny plan | Do wykonania |
| [LAB 11 — Bezpieczeństwo](LAB-11.md) | Sprawdzić obraz i uprawnienia | Do wykonania |
| [LAB 12 — Backup](LAB-12.md) | Odtworzyć dane z kopii | Do wykonania |
| [LAB 13 — GitOps i Argo CD](LAB-13.md) | Porównać Git ze stanem klastra | Do wykonania |
| [LAB 14 — Metryki HTTP](LAB-14.md) | Zmierzyć błędy API | Do wykonania |
| [LAB 15 — Logi i Loki](LAB-15.md) | Odnaleźć zdarzenie w logach | Do wykonania |
| [LAB 16 — Ansible](LAB-16.md) | Powtarzalnie przygotować konfigurację | Do wykonania |
| [LAB 17 — Próba końcowa](LAB-17.md) | Zdiagnozować awarię i pokazać dowody | Do wykonania |

## Przygotowanie od pierwszego uruchomienia

Potrzebujesz Git, Ubuntu/WSL i działającego Docker Engine lub Docker Desktop z integracją WSL. W terminalu `docker version` ma pokazać klienta i serwer. Polecenia poniżej uruchamiaj w Ubuntu/WSL, nie w oknie Pythona ani PowerShell.

Jeśli nie masz klonu repozytorium:

```bash
cd "$HOME"
git clone https://github.com/Dawid26/DevOpsProjectAI.git
cd DevOpsProjectAI
```

Jeśli już go masz, przejdź do niego, sprawdź `git status` i pobierz zmiany przez `git pull --ff-only`. Przy własnych niezapisanych zmianach najpierw zapisz je w commicie. Nie klonuj kolejnego repozytorium wewnątrz istniejącego.

## Utwórz osobny katalog aplikacji

W katalogu DevOpsProjectAI wykonaj:

```bash
export LAB_SOURCE="$PWD"
mkdir "$HOME/incidentflow-app"
cp -R "$LAB_SOURCE/examples/starter/." "$HOME/incidentflow-app/"
cd "$HOME/incidentflow-app"
pwd
ls
```

Jeśli mkdir mówi, że katalog istnieje, zatrzymaj się: sprawdź, czy masz już tam aplikację. Nie nadpisuj wcześniejszej pracy. Kropka w `starter/.` kopiuje również .env.example, .gitignore i szablon workflow. W nowym katalogu mają być `compose.yaml`, `api/`, `scripts/` i `docs/`.

Repozytorium DevOpsProjectAI to materiały i portfolio. Katalog incidentflow-app to aplikacja, którą zmieniasz podczas ćwiczeń. Polecenia `docker compose` wykonuj w katalogu aplikacji. Instrukcje aktualne czytaj w `DevOpsProjectAI/docs`; dokumenty wewnątrz startera opisują początkową wersję.

```bash
cp .env.example .env
docker compose config --quiet
docker compose up -d --build
docker compose ps
curl -i http://localhost:8000/ready
```

Oczekuj 200 i `database: connected`. Plik .env.example zawiera jawne hasło tylko do lokalnego ćwiczenia. Nie używaj go w usłudze dostępnej z Internetu. Zacznij [LAB 01](LAB-01.md).

## Jak uczyć się z tych materiałów

1. Przeczytaj objaśnienie danego labu w OD-ZERA.
2. Przeczytaj cel i wymagania instrukcji.
3. Wykonaj jeden blok poleceń, nie cały rozdział naraz.
4. Porównaj wynik z opisem. Gdy się różni, zatrzymaj się i przeczytaj błąd.
5. Zapisz jednym zdaniem: „Zrobiłem X, bo Y; wiem, że działa, ponieważ Z”.
6. Dopiero wtedy przejdź dalej.

Nowa karta terminala zwykle nie zna zmiennych ustawionych w poprzedniej. Ustaw ponownie `LAB_SOURCE`, `KUBECONFIG` lub `BASE_URL`, gdy instrukcja ich wymaga. Nie zmieniaj wszystkich ustawień naraz podczas diagnozy.

## Co jest sprawdzone

Zakres kontroli przygotowanych przykładów jest opisany w [VALIDATION.md](VALIDATION.md). Próby wymagające Dockera, klastra, GitHub Actions lub AWS musisz potwierdzić na swoim środowisku. Do raportów dodawaj własne wyniki.
