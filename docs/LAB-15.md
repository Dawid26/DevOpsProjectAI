# LAB 15 — logi w Loki i szukanie przyczyny błędu

[Spis](COURSE.md) · [Wyjaśnienie](OD-ZERA.md#lab-15)

**Cel:** wysłać kilka kontrolowanych linii logu do Loki, znaleźć ERROR i prześledzić jedno zgłoszenie. Potrzebujesz klastra LAB 08 oraz Grafany z LAB 09.

## 1. Uruchom mały magazyn logów

Ustaw KUBECONFIG klastra edukacyjnego i LAB_SOURCE jak wcześniej. Wczytaj [manifest](../examples/lab-15/loki.yaml):

```bash
kubectl apply -f "$LAB_SOURCE/examples/lab-15/loki.yaml"
kubectl -n monitoring rollout status deployment/loki-lab --timeout=180s
kubectl -n monitoring logs deployment/loki-lab --tail=30
```

ConfigMap przechowuje ustawienia. Deployment uruchamia jeden proces Loki. Service daje mu nazwę sieciową. `emptyDir` przechowuje dane tylko przez życie Poda — to ćwiczenie wyszukiwania, nie trwała archiwizacja. Port nie jest publikowany w Internecie. Loki w tej konfiguracji nie wymaga logowania; traktuj sieć klastra jako zaufane środowisko lokalne.

Obraz jest przypięty do 3.6.0 dla powtarzalności przykładu, nie oznacza to deklaracji najnowszej ani wolnej od podatności wersji. Przed użyciem poza labem wykonaj ocenę aktualizacji z LAB 11.

## 2. Otwórz tunel i sprawdź gotowość

W drugiej karcie, z tym samym KUBECONFIG:

```bash
kubectl -n monitoring port-forward svc/loki-lab 13100:3100 --address 127.0.0.1
```

W pierwszej:

```bash
curl -i http://127.0.0.1:13100/ready
python3 "$LAB_SOURCE/examples/lab-15/send_logs.py" < "$LAB_SOURCE/examples/lab-15/sample.log"
```

Poczekaj na 200 z `/ready`; po wysyłce powinno być HTTP 204. To znaczy, że Loki przyjął porcję logów. `<` przekazuje zawartość pliku na standardowe wejście Pythona. Skrypt buduje JSON zawierający etykiety i listę par: czas w nanosekundach oraz treść linii.

## 3. Podłącz Grafanę

Otwórz Grafanę z LAB 09 (`http://localhost:13000` przy działającym tunelu). W Connections / Data sources dodaj Loki. Ustaw URL na `http://loki-lab.monitoring.svc.cluster.local:3100`, następnie Save & test.

To adres widziany przez serwer Grafany w klastrze. `localhost:13100` w ustawieniach Grafany wskazywałby sam jej kontener, a nie Twój komputer.

W Explore wybierz Loki i ostatnie 15 minut. Wpisz kolejno:

```logql
{job="incidentflow-lab"}
{job="incidentflow-lab"} |= "ERROR"
{job="incidentflow-lab"} |= "incident_id=42"
```

Pierwsza kwerenda pokazuje cały strumień, druga filtruje linie z ERROR, trzecia szuka zdarzeń jednego zgłoszenia. Jeśli nic nie ma, odśwież przedział czasu, sprawdź źródło danych i odpowiedź importu.

## 4. Przeczytaj historię

W przykładowym pliku są trzy linie: zlecenie, problem Redis i wykonanie. To dane demonstracyjne — nie dowód rzeczywistej awarii. Zapisz własnymi słowami, co każda linia sugeruje i jakim poleceniem sprawdziłbyś Redis oraz workera.

## 5. Wczytaj prawdziwy fragment logów laboratorium

```bash
umask 077
kubectl -n incidentflow logs deployment/worker --tail=20 > /tmp/incidentflow-worker.log
less /tmp/incidentflow-worker.log
```

Przejrzyj plik. Usuń dane dostępowe i treści prywatne, jeśli się pojawiły, następnie:

```bash
python3 "$LAB_SOURCE/examples/lab-15/send_logs.py" < /tmp/incidentflow-worker.log
```

W Explore wyszukaj `notification=`. Brak dopasowania może oznaczać, że ostatnie 20 linii nie zawiera wykonanego zadania — zleć nowe powiadomienie i pobierz logi ponownie.

To import ręczny. Czas Loki oznacza moment importu, a oryginalny czas pozostaje w tekście, jeśli był zapisany. Ponowny import może dodać duplikaty. Ciągłe zbieranie, pozycje odczytu i zachowanie czasu zdarzenia wymagają agenta, np. Grafana Alloy; ten skrypt nie zastępuje agenta.

**Zaliczenie:** odczyt trzech przykładowych linii, filtr ERROR, import fragmentu workera i opis różnicy między metryką a logiem. Zapisz `docs/LOGS-15.md`. Sprzątanie: `kubectl delete -f "$LAB_SOURCE/examples/lab-15/loki.yaml"` usunie Loki i jego tymczasowe dane.

[Konfiguracja Loki](https://grafana.com/docs/loki/latest/configure/examples/configuration-examples/) · [HTTP API](https://grafana.com/docs/loki/latest/reference/loki-http-api/)
