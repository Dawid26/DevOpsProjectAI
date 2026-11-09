# LAB 08 — Kubernetes krok po kroku

W tym labie uruchomisz IncidentFlow w lokalnym Kubernetes. Zobaczysz działającą aplikację, zwiększysz liczbę jej kopii i sprawdzisz, jak klaster odtwarza usunięty Pod. Wyjaśnienia całego projektu znajdziesz także w zakładce [Zrozum projekt](../zrozum-projekt.html).

**Co jest potrzebne.** Pracujesz w Ubuntu/WSL z działającym Dockerem. Zainstaluj narzędzia według oficjalnych instrukcji [kind](https://kind.sigs.k8s.io/docs/user/quick-start/) i [kubectl dla Linuksa](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/). Przygotuj kilka GB wolnej pamięci RAM. Użyj aplikacji po LAB 06, w której działa endpoint powiadomień, model nowej tabeli i worker. Szablony są w [examples/lab-08](../examples/lab-08).

| Pojęcie | Co oznacza tutaj |
| --- | --- |
| kind | Narzędzie tworzące lokalny klaster Kubernetes wewnątrz Dockera. |
| Namespace | Nazwana przestrzeń grupująca zasoby projektu. |
| Pod | Miejsce uruchomienia kontenera aplikacji. |
| Deployment | Opis obrazu i wymaganej liczby kopii aplikacji. |
| Service | Stały adres sieciowy prowadzący do Podów. |
| ConfigMap | Zwykłe ustawienia aplikacji. |
| Secret | Dane dostępowe przekazywane do kontenerów. |
| StatefulSet i PVC | Uruchomienie bazy z zachowaniem jej danych podczas wymiany Poda. |

**1. Przygotuj katalog i narzędzia**

W katalogu aplikacji IncidentFlow sprawdź:

```bash
pwd
ls api/Dockerfile api/app/notifications.py api/app/notification_models.py
docker info
kind version
kubectl version --client
```

Jeżeli brakuje plików Pythona, dokończ kopiowanie i podłączenie przykładów LAB 06. Następnie ustaw `LAB_SOURCE` na pełną ścieżkę lokalnego klonu tego repozytorium:

```bash
export LAB_SOURCE=/home/twoj-login/DevOpsProjectAI
mkdir -p k8s
cp -Ri "$LAB_SOURCE/examples/lab-08/"* k8s/
```

Podmień przykładowy login na swój. `cp -Ri` kopiuje katalogi i pyta przed nadpisaniem istniejących plików.

**2. Utwórz klaster do tego ćwiczenia**

```bash
umask 077
export KUBECONFIG="$PWD/.kubeconfig-lab08"
kind create cluster --name incidentflow-lab08 --kubeconfig "$KUBECONFIG" --wait 120s
kubectl config current-context
kubectl get nodes
kubectl get storageclass
```

`KUBECONFIG` wskazuje plik połączenia do klastra ćwiczeniowego. Kontekst ma nazywać się `kind-incidentflow-lab08`. Węzeł powinien mieć stan `Ready`. Sprawdź także, czy klaster ma domyślną klasę pamięci, zwykle `standard`.

Gdy wracasz do istniejącego klastra, ponownie ustaw `KUBECONFIG`. Jeśli potrzebujesz odtworzyć sam plik połączenia, wykonaj `kind get kubeconfig --name incidentflow-lab08 > "$KUBECONFIG"`.

**3. Zbuduj i załaduj obraz aplikacji**

```bash
docker build -t incidentflow:lab08 ./api
docker run --rm incidentflow:lab08 python -c "from app.jobs import notify_incident; print('Kod LAB 06 jest w obrazie')"
kind load docker-image incidentflow:lab08 --name incidentflow-lab08
```

kind przechowuje obrazy wewnątrz swojego węzła. Polecenie `load` kopiuje tam Twój obraz. Manifesty API i workera wskazują `incidentflow:lab08` z `imagePullPolicy: IfNotPresent`.

**4. Przygotuj konfigurację i dane dostępowe**

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/10-config.yaml
```

Utwórz lokalny plik danych dostępowych. Kod generuje hasło z bezpiecznych do użycia w tym adresie znaków. Zachowaj ten plik przy kolejnych uruchomieniach tej samej bazy:

```bash
python3 - <<'PY'
from pathlib import Path
import secrets

path = Path(".env.k8s")
if path.exists():
    print("Korzystamy z istniejącego pliku .env.k8s")
else:
    password = secrets.token_urlsafe(24)
    path.write_text(
        "POSTGRES_USER=incidentflow\n"
        f"POSTGRES_PASSWORD={password}\n"
        "POSTGRES_DB=incidentflow\n"
        f"DATABASE_URL=postgresql+psycopg://incidentflow:{password}@db:5432/incidentflow\n"
    )
    path.chmod(0o600)
    print("Utworzono .env.k8s")
PY

printf '\n.env.k8s\n.kubeconfig-lab08\n' >> .gitignore
kubectl -n incidentflow create secret generic incidentflow-secrets --from-env-file=.env.k8s --dry-run=client -o yaml | kubectl apply -f -
```

ConfigMap zawiera adres Redis. Secret zawiera login i hasło PostgreSQL oraz adres połączenia używany przez SQLAlchemy. Aplikacja i worker odczytują je jako zmienne środowiskowe.

**5. Uruchom bazę i Redis**

```bash
kubectl apply -f k8s/20-postgres.yaml
kubectl apply -f k8s/30-redis.yaml
kubectl -n incidentflow rollout status statefulset/db --timeout=180s
kubectl -n incidentflow rollout status deployment/redis --timeout=180s
kubectl -n incidentflow get pods,pvc,services
```

PostgreSQL będzie działał w Podzie `db-0`. PVC rezerwuje miejsce na dane. Redis jest osiągalny pod nazwą `redis`. Service bazy ma nazwę `db`, więc adres SQLAlchemy z poprzedniego kroku używa `db:5432`.

Punkt kontrolny to gotowe Pody i PVC w stanie `Bound`. Dane tego klastra są osobne od danych bazy uruchamianej przez Compose. W tym ćwiczeniu kolejka Redis korzysta z pamięci Poda, więc usunięcie jego Poda może usunąć oczekujące zadania.

**6. Uruchom API, a po nim workera**

```bash
kubectl apply -f k8s/40-api.yaml
kubectl -n incidentflow rollout status deployment/api --timeout=180s
kubectl apply -f k8s/50-worker.yaml
kubectl -n incidentflow rollout status deployment/worker --timeout=180s
kubectl -n incidentflow get pods
kubectl -n incidentflow logs deployment/worker --tail=30
```

Początkowo działa jedna kopia API. Podczas jej startu istniejący kod `create_all` tworzy tabele. Dopiero po gotowości API uruchamiamy workera. Więcej kopii API dodamy po utworzeniu tabel.

| Element 40-api.yaml | Co sprawdza lub ustala |
| --- | --- |
| `replicas: 1` | Wymaganą liczbę kopii API na początku ćwiczenia. |
| `startupProbe` na `/health` | Czy API zakończyło uruchamianie. |
| `livenessProbe` na `/health` | Czy proces HTTP odpowiada. |
| `readinessProbe` na `/ready` | Czy API może połączyć się z PostgreSQL. |
| `resources.requests` | Zasoby rezerwowane na potrzeby planowania. |
| `resources.limits` | Górne limity zasobów kontenera. |
| `envFrom` | Skąd wczytać zmienne środowiskowe. |

**7. Otwórz aplikację i zleć zadanie**

W drugiej karcie terminala ustaw ten sam `KUBECONFIG`, wskazując pełną ścieżkę do pliku z punktu 2:

```bash
export KUBECONFIG=/home/twoj-login/incidentflow-devops-lab/.kubeconfig-lab08
kubectl -n incidentflow port-forward service/api 18000:8000 --address 127.0.0.1
```

Dostosuj ścieżkę do swojego katalogu aplikacji. Ta karta utrzymuje połączenie. W przeglądarce otwórz [localhost:18000/docs](http://localhost:18000/docs).

W pierwszej karcie wykonaj:

```bash
export BASE_URL=http://localhost:18000
curl -i "$BASE_URL/ready"
export INCIDENT_ID=$(
  curl -fsS -X POST "$BASE_URL/incidents" \
    -H 'Content-Type: application/json' \
    -d '{"title":"Pierwszy incydent Kubernetes","severity":"high"}' |
  python3 -c 'import json, sys; print(json.load(sys.stdin)["id"])'
)
curl -i -X POST "$BASE_URL/incidents/$INCIDENT_ID/notification"
kubectl -n incidentflow logs deployment/worker --tail=30
kubectl -n incidentflow exec db-0 -- sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT incident_id, event_type FROM notification_events;"'
```

Punkt kontrolny to HTTP 202, komunikat `notification=created` i wiersz w PostgreSQL.

**8. Zwiększ liczbę kopii i sprawdź odtwarzanie**

```bash
kubectl -n incidentflow scale deployment/api --replicas=2
kubectl -n incidentflow rollout status deployment/api --timeout=180s
kubectl -n incidentflow get pods -l app=api
kubectl -n incidentflow get endpointslices -l kubernetes.io/service-name=api
```

Zobaczysz dwa Pody API. Service utrzymuje adres prowadzący do gotowych Podów. Pojedynczy tunel `port-forward` jest przypięty do wybranego Poda, więc zachowanie tunelu obserwuj osobno od mechanizmu Service.

Skopiuj nazwę jednego Poda API i podstaw ją do polecenia:

```bash
kubectl -n incidentflow delete pod WPISZ_NAZWE_JEDNEGO_PODA_API
kubectl -n incidentflow get pods -l app=api -w
```

Deployment utworzy brakującą kopię. Gdy znów zobaczysz dwie gotowe kopie, zakończ obserwację przez `Ctrl+C`. Jeśli usunięty Pod obsługiwał tunel, uruchom ponownie `port-forward` w drugiej karcie.

**9. Sprawdź readiness podczas awarii bazy**

```bash
kubectl -n incidentflow scale statefulset/db --replicas=0
kubectl -n incidentflow get pods
curl -i --max-time 10 "$BASE_URL/health"
curl -i --max-time 10 "$BASE_URL/ready"
kubectl -n incidentflow get pods -l app=api
```

Po zatrzymaniu bazy proces HTTP może nadal odpowiadać 200 na `/health`, a `/ready` zwróci 503. Poczekaj na zmianę gotowości Podów API. Przywróć bazę:

```bash
kubectl -n incidentflow scale statefulset/db --replicas=1
kubectl -n incidentflow rollout status statefulset/db --timeout=180s
kubectl -n incidentflow rollout status deployment/api --timeout=180s
curl -i "$BASE_URL/ready"
curl -i "$BASE_URL/incidents/$INCIDENT_ID"
```

Incydent powinien nadal istnieć, ponieważ pliki PostgreSQL są na PVC. Usunięcie całego klastra kind usuwa także dane przechowywane wewnątrz jego kontenera.

**10. Zadanie dodatkowe — HPA**

Plik [optional/api-hpa.yaml](../examples/lab-08/optional/api-hpa.yaml) opisuje automatyczne utrzymywanie od jednej do trzech kopii API na podstawie użycia CPU. Wymaga działającego serwisu metryk. Jeśli `kubectl -n incidentflow top pods` pokazuje pomiary, możesz go włączyć:

```bash
kubectl apply -f k8s/optional/api-hpa.yaml
kubectl -n incidentflow get hpa
kubectl -n incidentflow describe hpa api
```

Dla klastra bez pomiarów doinstaluj metrics-server według jego [oficjalnej instrukcji](https://github.com/kubernetes-sigs/metrics-server). W kind może być potrzebna opcja `--kubelet-insecure-tls`, która pomija sprawdzanie certyfikatu kubeleta w tym lokalnym klastrze. Dopiero po uzyskaniu wyników `top pods` sprawdzaj działanie HPA. Próg `60` oznacza 60% żądanego CPU kontenera. Liczba kopii zmieni się dopiero, gdy pomiary uzasadnią skalowanie.

**11. Opcjonalnie — użyj obrazu z GHCR**

Możesz pobrać sprawdzony obraz z LAB 07 na hosta i załadować go do kind. Gdy pakiet jest prywatny, zaloguj się do GHCR jak w LAB 07. Podstaw rzeczywisty adres obrazu:

```bash
export APP_IMAGE='ghcr.io/dawid26/incidentflow-devops-lab@sha256:WKLEJ_DIGEST'
docker pull "$APP_IMAGE"
docker tag "$APP_IMAGE" incidentflow:lab08-ghcr
kind load docker-image incidentflow:lab08-ghcr --name incidentflow-lab08
kubectl -n incidentflow set image deployment/api api=incidentflow:lab08-ghcr
kubectl -n incidentflow set image deployment/worker worker=incidentflow:lab08-ghcr
kubectl -n incidentflow rollout status deployment/api --timeout=180s
kubectl -n incidentflow rollout status deployment/worker --timeout=180s
```

Użyj obrazu z kodem powiadomień LAB 06. Zmiana obrazu obu Deploymentów odbywa się osobno, więc po obu poleceniach sprawdź gotowość i zadanie workera.

**Gdy coś nie działa**

| Objaw | Co sprawdzić |
| --- | --- |
| `ErrImagePull` / `ImagePullBackOff` | Nazwę obrazu, `imagePullPolicy` i wynik `kind load`. |
| Pod bazy jest Pending | `kubectl -n incidentflow describe pvc postgres-data-db-0` i domyślną klasę pamięci. |
| API ma CrashLoopBackOff | `kubectl -n incidentflow logs deployment/api --previous` oraz gotowość bazy i Secret. |
| Worker działa, a zadanie czeka | Nazwę kolejki, adres Redis i `kubectl -n incidentflow logs deployment/worker`. |
| Port 18000 przestał odpowiadać | Czy druga karta nadal utrzymuje port-forward. |
| HPA pokazuje unknown | Dostępność pomiarów przez `kubectl top pods` i requests CPU. |

Zapisz w `docs/POSTMORTEM-08.md` wynik utworzenia incydentu, wykonania zadania, odtworzenia Poda i odzyskania po awarii bazy. Kryterium zaliczenia podstawowego labu to działające API i worker w klastrze, dwie kopie API po skalowaniu oraz zachowany incydent po powrocie PostgreSQL.

Dokumentację znajdziesz w [kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/), [Kubernetes — probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/), [StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) i [HPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/).
