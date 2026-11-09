# LAB 07 — obrazy Docker, GHCR i rollback krok po kroku

W LAB 06 dodawałeś Redis i workera. Teraz nauczysz się przygotować konkretną wersję aplikacji, zapisać ją na GitHubie jako obraz Docker i uruchomić ją lokalnie. Potem przygotujesz drugą wersję i wrócisz do pierwszej. Taki powrót nazywa się rollbackiem.

Zarezerwuj około 60–90 minut. Wykonuj kroki po kolei. Każdy ma punkt kontrolny.

| Pojęcie | Znaczenie w tym ćwiczeniu |
| --- | --- |
| Obraz Docker | Paczka zawierająca Pythona, biblioteki i kod aplikacji. |
| GHCR | Magazyn obrazów GitHuba pod adresem `ghcr.io`. |
| Tag | Nazwa wersji obrazu. Użyjemy `sha-` i identyfikatora commita. |
| Digest | Odcisk konkretnego obrazu, zaczynający się od `sha256:`. Wdrożenie będzie wskazywać ten odcisk. |
| SBOM | Lista składników i wersji bibliotek w obrazie. |
| Rollback | Uruchomienie poprzednio sprawdzonego obrazu. |

Ćwiczenie kończy się lokalnym wdrożeniem wybranego obrazu i ręcznym rollbackiem. Kolejnym krokiem automatyzacji może być uruchamianie tych samych poleceń przez CD.

**Gdzie pracujesz.** To repozytorium `DevOpsProjectAI` przechowuje portfolio i instrukcje. Poniższe kroki wykonuj w repozytorium aplikacji IncidentFlow, gdzie istnieją `api/Dockerfile`, `api/requirements-dev.txt`, `api/tests/` i `compose.yaml`. Usługi `api`, `db`, `redis` i `worker` powinny już działać po LAB 06. Aplikacja potrzebuje własnego repozytorium na Twoim GitHubie, aby Actions mogło pobrać jej kod. Sprawdź, czy w przeglądarce widać w nim katalog `api/`.

**1. Sprawdź punkt startowy**

Otwórz Ubuntu/WSL i wejdź do katalogu aplikacji. Wpisz:

```bash
pwd
ls api/Dockerfile api/requirements-dev.txt compose.yaml
docker compose version
docker buildx version
docker compose up -d --build
docker compose ps
```

`pwd` pokazuje bieżący katalog, a `ls` sprawdza obecność potrzebnych plików. `up -d --build` uruchamia lokalny stack. Jeśli poprzednie ćwiczenie dodało Nginx, zachowaj je w Compose.

```bash
export BASE_URL=http://localhost:8000
curl -fsS "$BASE_URL/health"
curl -fsS "$BASE_URL/ready"
```

Użyj `http://localhost:8080` w `BASE_URL`, jeśli wejście prowadzi przez Nginx. Punkt kontrolny to odpowiedź API i działający dostęp do bazy.

**2. Zbuduj pierwszy obraz na swoim komputerze**

```bash
docker build -t incidentflow:lab07-local ./api
docker image inspect incidentflow:lab07-local --format '{{.Id}}'
docker run --rm incidentflow:lab07-local python -c "import app.main; print('Import aplikacji OK')"
```

`build` czyta `api/Dockerfile`. Flaga `-t` nadaje obrazowi nazwę `incidentflow` i tag `lab07-local`. Ostatni argument `./api` wybiera katalog plików potrzebnych do budowy. `run --rm` tworzy jednorazowy kontener, sprawdza import kodu i usuwa kontener po zakończeniu. Punkt kontrolny to `Import aplikacji OK`.

**3. Skopiuj dwa szablony do aplikacji**

W drugiej karcie terminala pobierz instrukcje:

```bash
git clone https://github.com/Dawid26/DevOpsProjectAI.git DevOpsProjectAI-lab07
cd DevOpsProjectAI-lab07
pwd
```

Zanotuj pełną ścieżkę wyświetloną przez `pwd`. Jeśli masz już lokalny klon tego repozytorium, możesz go wykorzystać po pobraniu zmian.

W pierwszej karcie, w katalogu aplikacji IncidentFlow, ustaw zmienną na zanotowaną ścieżkę. Podmień przykładowy adres:

```bash
export LAB_SOURCE=/home/twoj-login/DevOpsProjectAI-lab07
ls "$LAB_SOURCE/examples/lab-07"
mkdir -p .github/workflows
cp "$LAB_SOURCE/examples/lab-07/images.yml" .github/workflows/images.yml
cp "$LAB_SOURCE/examples/lab-07/compose.image.yaml" compose.image.yaml
```

Pierwszy plik to przepis dla GitHub Actions. Drugi dopisuje adres obrazu do usług `api` i `worker`, zachowując ich dotychczasowe zmienne i polecenia.

**4. Uruchom budowę na GitHubie**

Sprawdź w `git status`, czy etap LAB 06 został wcześniej zapisany. Dodaj nowe pliki:

```bash
git add .github/workflows/images.yml compose.image.yaml
git diff --cached --check
git commit -m "feat(images): add manual GHCR build with SBOM"
git push origin HEAD
```

Workflow musi znaleźć się na domyślnej gałęzi repozytorium aplikacji. Jeśli pracujesz na osobnej gałęzi, utwórz pull request i połącz go z gałęzią domyślną. Następnie na GitHubie otwórz **Actions → LAB 07 - Build and publish image → Run workflow** i wybierz tę gałąź.

Workflow instaluje zależności, uruchamia istniejące testy, buduje obraz i zapisuje go w GHCR. Na końcu generuje SBOM i informacje o sposobie budowy. Poczekaj na zielony wynik. W **Summary** znajdziesz tag oraz `APP_IMAGE` z digestem.

| Fragment pliku images.yml | Co robi |
| --- | --- |
| `workflow_dispatch` | Udostępnia przycisk ręcznego uruchomienia. |
| `contents: read` | Pozwala workflow pobrać kod. |
| `packages: write` | Pozwala zapisać obraz w GHCR. |
| `GITHUB_TOKEN` | Automatyczny token danego uruchomienia Actions. |
| `context: ./api` | Wybiera pliki aplikacji do budowy. |
| `platforms: linux/amd64` | Buduje obraz dla Linuksa na procesorze x86-64, np. WSL na komputerze Intel/AMD. |
| `push: true` | Zapisuje zbudowany obraz w rejestrze. |
| `sbom: true` | Dołącza listę składników obrazu. |
| `provenance: mode=max` | Dołącza informacje o źródle i parametrach budowy. |

Nazwa obrazu powstaje z nazwy repozytorium aplikacji zapisanej małymi literami. Dla `Dawid26/incidentflow-devops-lab` będzie to `ghcr.io/dawid26/incidentflow-devops-lab`. Tag wskazuje commit źródłowy. Ponowna budowa tego samego commita może dać inny digest, np. po zmianie zależności, dlatego wdrożenie przypinamy do digestu.

GitHub ustawia pierwszą publikację pakietu jako prywatną. Do pobrania prywatnego obrazu lokalnie przygotuj na GitHubie osobisty token **classic** z uprawnieniem `read:packages`. W terminalu wpisz:

```bash
docker login ghcr.io --username Dawid26
```

W polu hasła wklej token. W workflow logowanie odbywa się automatycznie przez `GITHUB_TOKEN`. Punkt kontrolny to zielone Actions, adres `APP_IMAGE` i poprawne logowanie lokalne.

**5. Uruchom wersję A z GHCR**

Skopiuj cały adres `APP_IMAGE` z Summary. W poniższym poleceniu zastąp cały przykładowy adres swoim. Fragment po `sha256:` musi zawierać rzeczywisty digest:

```bash
export APP_IMAGE='ghcr.io/dawid26/incidentflow-devops-lab@sha256:WKLEJ_DIGEST_Z_SUMMARY'
docker compose -f compose.yaml -f compose.image.yaml config --quiet
docker compose -f compose.yaml -f compose.image.yaml pull api worker
docker compose -f compose.yaml -f compose.image.yaml up -d --no-build --no-deps --wait --wait-timeout 60 api worker
curl -fsS "$BASE_URL/"
curl -fsS "$BASE_URL/ready"
docker inspect "$(docker compose ps -q api)" --format '{{.Config.Image}}'
docker inspect "$(docker compose ps -q worker)" --format '{{.Config.Image}}'
export PREVIOUS_IMAGE="$APP_IMAGE"
```

Każde `-f` wskazuje plik Compose. Pliki są łączone w podanej kolejności. `pull` pobiera obraz. `--no-build` wybiera gotowy obraz. `--no-deps` aktualizuje wskazane usługi, korzystając z działającej bazy i Redis. `--wait` czeka na uruchomienie kontenerów i ich zdefiniowane kontrole stanu. Dla workera dodatkowo zleć powiadomienie według LAB 06 i sprawdź jego logi.

Punkt kontrolny to działające `/ready`, wykonane zadanie i ten sam adres obrazu w obu wynikach `docker inspect`. Zmienna `PREVIOUS_IMAGE` zachowuje obraz A na czas tej sesji terminala.

**6. Przygotuj wersję B i wykonaj rollback**

W `api/app/main.py` znajdź funkcję `index()`, która odpowiada pod `GET /`. Zmień wartość zwracanego pola `version`, np. z `0.1.0` na `0.1.1`. Zapisz i wypchnij zmianę:

```bash
git add api/app/main.py
git commit -m "feat(api): mark lab07 version B"
git push origin HEAD
```

Po umieszczeniu zmiany na domyślnej gałęzi ponownie uruchom workflow. Skopiuj nowy `APP_IMAGE` z jego Summary i wykonaj polecenia wdrożenia z punktu 5, od `export APP_IMAGE` do obu poleceń `docker inspect`. Zachowaj `PREVIOUS_IMAGE` wskazujące A.

Odpowiedź `curl -fsS "$BASE_URL/"` powinna teraz zawierać `0.1.1`. W tej samej sesji terminala wróć do obrazu A:

```bash
export APP_IMAGE="${PREVIOUS_IMAGE:?Ustaw adres sprawdzonego obrazu A}"
docker compose -f compose.yaml -f compose.image.yaml pull api worker
docker compose -f compose.yaml -f compose.image.yaml up -d --no-build --no-deps --wait --wait-timeout 60 api worker
curl -fsS "$BASE_URL/"
curl -fsS "$BASE_URL/ready"
```

Punkt kontrolny to poprzednia wartość `version`, działające `/ready` i wykonanie zadania workera. Powrót obrazu zmienia kod uruchamianej aplikacji. Dane w PostgreSQL i ewentualne zmiany schematu wymagają własnej strategii odzyskiwania.

**7. Obejrzyj SBOM i zapisz wynik**

Dla aktualnie wybranego obrazu wpisz:

```bash
docker buildx imagetools inspect "$APP_IMAGE"
docker buildx imagetools inspect "$APP_IMAGE" --format '{{json .SBOM}}' > /tmp/incidentflow-lab07-sbom.json
python3 -m json.tool /tmp/incidentflow-lab07-sbom.json
```

Znajdź przynajmniej jeden składnik i jego wersję. Zapisz w `docs/DEPLOYMENT-07.md` adresy i commity obrazów A i B, odczytane wersje aplikacji, wynik `/ready`, test workera oraz jeden znaleziony składnik SBOM. Plik raportu pozwoli odtworzyć adresy obrazów po zamknięciu terminala.

| Gdy coś nie działa | Co sprawdzić |
| --- | --- |
| Actions zgłasza brak `api/Dockerfile` | Czy workflow skopiowano do repozytorium aplikacji i czy kod aplikacji jest wypchnięty. |
| Brakuje przycisku Run workflow | Czy plik jest w `.github/workflows/` na domyślnej gałęzi. |
| GHCR zwraca denied podczas budowy | `packages: write` i uprawnienia repozytorium do istniejącego pakietu. |
| Lokalny pull zwraca unauthorized | Logowanie do GHCR tokenem classic z `read:packages`. |
| Obraz ma niewłaściwą nazwę lub digest | Wklej pełny `APP_IMAGE` z Summary konkretnego uruchomienia. |
| Worker nie wykonuje zadania | Logi `worker` i `redis`, nazwa kolejki oraz działające zależności z LAB 06. |
| API działa po błędzie wdrożenia | Sprawdź kod wyjścia komendy wdrożenia oraz oba wyniki `docker inspect`; aktualizacja dwóch usług może zakończyć się częściowo. Wróć do A i sprawdź obie usługi. |

**Kryteria zaliczenia**

- Zbudowałeś obraz lokalnie, a Actions zakończyło testy i zapisało obraz do GHCR.
- Uruchomiłeś wersję A, potem B, a potem ponownie A.
- API i worker używają tego samego wskazanego obrazu, a PostgreSQL zachował dane.
- Potrafisz wskazać różnicę między tagiem, digestem i commitem.
- Odczytałeś SBOM i zapisałeś raport z rollbacku.

Dokumentacja do sprawdzenia szczegółów jest w [Docker — attestations w Actions](https://docs.docker.com/build/ci/github-actions/attestations/), [GitHub — Container registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry), [Docker — imagetools inspect](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/) i [Docker — Compose up](https://docs.docker.com/reference/cli/docker/compose/up/).
