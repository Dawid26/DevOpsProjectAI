# LAB 14 — metryki HTTP i alert na błędy

[Spis](COURSE.md) · [Wyjaśnienie](OD-ZERA.md#lab-14)

W LAB 09 monitorowałeś liczbę gotowych replik. Teraz API samo policzy odpowiedzi 200, 404 i 503. Prometheus będzie okresowo pobierał liczby z `/metrics`. Log opisuje konkretne zdarzenie, a metryka pozwala obserwować ich liczbę w czasie.

## 1. Dodaj licznik do aplikacji

W katalogu aplikacji po LAB 06 skopiuj plik z repozytorium:

```bash
cp -i "$LAB_SOURCE/examples/lab-14/observability.py" api/app/
cp -i "$LAB_SOURCE/examples/lab-14/test_observability.py" api/tests/
```

Do `api/requirements.txt` dodaj osobną linię `prometheus-client>=0.21,<1`. W `api/app/main.py` dodaj import `from .observability import install_metrics`, a bezpośrednio po `app = FastAPI(...)` dodaj `install_metrics(app)`. Zrób to jeden raz. Nie usuwaj istniejących tras ani routera powiadomień.

W swoim środowisku Python zainstaluj zależności developerskie i uruchom test:

```bash
python -m pip install -r api/requirements-dev.txt
PYTHONPATH=api python -m pytest -q api/tests
```

Oczekuj zielonych testów. Test przykładu sprawdza odpowiedź poprawną, 503, nieobsłużony błąd 500 oraz to, że samo pobieranie metryk nie zwiększa licznika.

## 2. Co robi kod?

`CollectorRegistry` jest pojemnikiem na metryki tej aplikacji. `Counter` liczy zdarzenia i resetuje się po restarcie procesu. `middleware` otacza obsługę żądania. `try` próbuje wykonać obsługę, a `finally` zapisuje wynik także przy wyjątku. `/metrics` zwraca tekst w formacie Prometheus.

Etykiety to metoda HTTP i status. Nie dodajemy tytułów zgłoszeń ani ID do etykiet — ich liczba mogłaby stale rosnąć. Przykład zakłada jeden proces Uvicorn na kontener, jak w Dockerfile projektu.

## 3. Zbuduj nowy obraz i wdroż do kind

```bash
docker build -t incidentflow:lab14 ./api
kind load docker-image incidentflow:lab14 --name incidentflow-lab08
kubectl -n incidentflow set image deployment/api api=incidentflow:lab14
kubectl -n incidentflow rollout status deployment/api --timeout=180s
```

Jeśli pracowałeś na obrazie z innymi zmianami, zapisz jego nazwę przed wymianą. Otwórz ponownie tunel `kubectl -n incidentflow port-forward svc/api 18000:8000 --address 127.0.0.1` w drugiej karcie z tym samym KUBECONFIG.

```bash
curl -fsS http://localhost:18000/health
curl -fsS http://localhost:18000/metrics
```

Znajdź `incidentflow_http_responses_total`. Licznik może obejmować również sondy Kubernetes.

## 4. Podłącz Prometheus z LAB 09

Sprawdź, czy kontener API w `k8s/40-api.yaml` ma port nazwany `http` i wartość 8000. Oryginalny szablon LAB 08 używa tej nazwy. Następnie:

```bash
kubectl apply -f "$LAB_SOURCE/examples/lab-14/monitoring.yaml"
kubectl -n monitoring get podmonitor,prometheusrule
kubectl -n monitoring get prometheus -o yaml
```

W ostatnim wyniku sprawdź selektory PodMonitor i reguł: konfiguracja z LAB 09 powinna wybierać etykietę `release: observe` w namespace monitoring. Jeśli użyłeś innej nazwy instalacji Helm, dopasuj etykiety i selektory. W Prometheus Targets poczekaj na endpoint API w stanie UP.

W jego oknie zapytań wpisz:

```promql
sum by (status) (rate(incidentflow_http_responses_total{namespace="incidentflow"}[2m]))
```

`rate` przelicza wzrost licznika na sekundę i uwzględnia jego reset. Poczekaj na co najmniej dwa pomiary. Tę samą kwerendę możesz wkleić do panelu Grafana z LAB 09.

## 5. Wywołaj kontrolowane 503

Zatrzymamy Redis, więc źródłem błędu będzie endpoint powiadomień; API pozostanie gotowe do odczytu incydentów. Zanotuj dotychczasową liczbę replik Redis i ustaw prawdziwy ID zgłoszenia:

```bash
REDIS_REPLICAS=$(kubectl -n incidentflow get deployment redis -o jsonpath='{.spec.replicas}')
INCIDENT_ID=1
kubectl -n incidentflow scale deployment/redis --replicas=0
for attempt in $(seq 1 45); do
  curl -sS --max-time 5 -o /dev/null -w '%{http_code}\n' -X POST "http://localhost:18000/incidents/$INCIDENT_ID/notification"
  sleep 3
done
```

Oczekuj 503. Jeśli widzisz 404, ID nie istnieje. W Prometheus Alerts reguła powinna przejść Pending → Firing po utrzymaniu warunku przez minutę. Próg to dowolny ruch 5xx, odpowiedni do demonstracji; dla realnej usługi określisz udział błędów i minimalny ruch.

Przywróć Redis, również gdy przerwiesz pętlę przez Ctrl+C:

```bash
kubectl -n incidentflow scale deployment/redis --replicas="$REDIS_REPLICAS"
kubectl -n incidentflow rollout status deployment/redis --timeout=180s
curl -i -X POST "http://localhost:18000/incidents/$INCIDENT_ID/notification"
```

Oczekuj 202 i wykonania zadania. Alert wygaśnie po zniknięciu błędów z okna pomiarowego. Zapisz obraz i port metryk także w swoich manifestach źródłowych, aby następne apply nie cofnęło zmiany.

**Zaliczenie:** testy, dostępne metryki, target UP, alert i jego wygaśnięcie. Przywrócenie starego obrazu usuwa `/metrics`, więc wycofaj wtedy także PodMonitor i regułę. [Dokumentacja Counter](https://prometheus.github.io/client_python/instrumenting/counter/).
