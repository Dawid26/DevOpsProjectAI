# LAB 09 — Helm, Prometheus, Grafana i pierwszy alert

Wyobraź sobie, że API przestało odpowiadać. W poprzednim labie sam wpisywałeś polecenia diagnostyczne. Teraz uruchomisz narzędzia, które regularnie zbierają informacje o stanie klastra i pokazują je na wykresach.

Prometheus przechowuje pomiary. Grafana pokazuje je na dashboardach. Alert to reguła, która zmienia stan, gdy pomiary spełniają określony warunek. Helm instaluje gotowy zestaw zasobów Kubernetes na podstawie pakietu nazywanego chartem.

**1. Przygotuj środowisko**

Użyj działającego klastra z LAB 08. W terminalu ustaw KUBECONFIG na jego plik. Pobierz zmiany w DevOpsProjectAI i zanotuj pełną ścieżkę katalogu. Dalej LAB_SOURCE oznacza tę ścieżkę.

```bash
export LAB_SOURCE=/home/twoj-login/DevOpsProjectAI
export KUBECONFIG=/home/twoj-login/incidentflow-devops-lab/.kubeconfig-lab08
kubectl config current-context
kubectl -n incidentflow get deployments
helm version
```

Kontekst powinien wskazywać kind-incidentflow-lab08. Zainstaluj Helm według [oficjalnej instrukcji](https://helm.sh/docs/intro/install/), jeśli polecenie jest niedostępne. Monitoring potrzebuje dodatkowej pamięci RAM. Gdy Pody zostaną Pending, sprawdź ich opis i dostępne zasoby Dockera.

**2. Pobierz chart i zapisz wybraną wersję**

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm search repo prometheus-community/kube-prometheus-stack --versions
```

Pierwsza komenda zapisuje adres katalogu pakietów, druga odświeża listę. Z wyniku trzeciej wybierz wersję chartu i podstaw ją zamiast poniższego tekstu.

```bash
export CHART_VERSION=WPISZ_WERSJE_CHARTU
helm show values prometheus-community/kube-prometheus-stack --version "$CHART_VERSION" > /tmp/lab09-default-values.yaml
helm template observe prometheus-community/kube-prometheus-stack --version "$CHART_VERSION" --namespace monitoring -f "$LAB_SOURCE/examples/lab-09/values.yaml" > /tmp/lab09-rendered.yaml
```

Plik values.yaml zmienia ustawienia pakietu. Helm template pokazuje wynikowe zasoby przed instalacją. Zapisana wersja chartu pozwoli później odtworzyć ten sam zestaw ustawień.

**3. Zainstaluj monitoring**

```bash
helm upgrade --install observe prometheus-community/kube-prometheus-stack --version "$CHART_VERSION" --namespace monitoring --create-namespace -f "$LAB_SOURCE/examples/lab-09/values.yaml" --wait --timeout 10m
kubectl -n monitoring get pods
kubectl -n monitoring get services
```

Nazwa instalacji to observe, a namespace to monitoring. Flaga --wait czeka na gotowość zasobów. Punkt kontrolny to gotowe Pody Prometheusa, operatora, Grafany i pozostałych składników. W kind część domyślnych celów control-plane może być niedostępna. Sprawdzaj konkretny alert IncidentFlow.

**4. Otwórz Grafanę**

W drugiej karcie terminala z tym samym KUBECONFIG uruchom:

```bash
kubectl -n monitoring port-forward service/observe-grafana 13000:80 --address 127.0.0.1
```

Otwórz http://localhost:13000. Login i wygenerowane hasło odczytasz lokalnie:

```bash
kubectl -n monitoring get secret observe-grafana -o jsonpath='{.data.admin-user}' | base64 --decode
echo
kubectl -n monitoring get secret observe-grafana -o jsonpath='{.data.admin-password}' | base64 --decode
echo
```

W Grafanie otwórz Explore, wybierz źródło Prometheus i wykonaj zapytanie:

```promql
kube_deployment_status_replicas_available{namespace="incidentflow",deployment="api"}
```

Powinieneś zobaczyć liczbę dostępnych kopii API. Dla restartów kontenerów użyj:

```promql
kube_pod_container_status_restarts_total{namespace="incidentflow"}
```

Zapisz panel z pierwszym zapytaniem na własnym dashboardzie. Ustaw zakres ostatnich 15 minut i odświeżanie. Te pomiary opisują zasoby Kubernetes. Odsetek błędów HTTP wymaga dodatkowego instrumentowania API.

**5. Wywołaj kontrolowaną awarię i zobacz alert**

```bash
export PREVIOUS_REPLICAS=$(kubectl -n incidentflow get deployment api -o jsonpath='{.spec.replicas}')
kubectl -n incidentflow get hpa
```

Jeżeli włączyłeś dodatkowy HPA z LAB 08, zatrzymaj jego sterowanie na czas ćwiczenia, usuwając wyłącznie HPA o nazwie api. Manifest do późniejszego przywrócenia masz w LAB 08.

```bash
kubectl -n incidentflow delete hpa api --ignore-not-found
kubectl -n incidentflow scale deployment/api --replicas=0
kubectl -n monitoring port-forward service/observe-prometheus 19090:9090 --address 127.0.0.1
```

Ostatnia komenda utrzymuje tunel. Otwórz http://localhost:19090, przejdź do Alerts i znajdź IncidentFlowApiUnavailable. Po zebraniu próbek reguła przejdzie do Pending, a po minucie utrzymywania warunku do Firing. Odstępy pobierania danych i oceny reguł mogą dodać opóźnienie.

W osobnej karcie przywróć API:

```bash
kubectl -n incidentflow scale deployment/api --replicas="$PREVIOUS_REPLICAS"
kubectl -n incidentflow rollout status deployment/api --timeout=180s
```

Zmienna PREVIOUS_REPLICAS jest dostępna w karcie, w której ją ustawiłeś. Jeśli przechodzisz do nowej, ustaw zapisaną wcześniej liczbę. Obserwuj powrót reguły do stanu nieaktywnego. W razie potrzeby ponownie zastosuj manifest HPA.

**6. Zapisz runbook**

Utwórz docs/RUNBOOK-09.md. Opisz znaczenie alertu, polecenia get pods, describe pod i logs, przyczynę kontrolowanej awarii oraz sposób przywrócenia replik. Dołącz nazwę dashboardu i wersję chartu.

Zaliczenie oznacza własny panel, zaobserwowane Pending i Firing, przywrócenie API oraz runbook. Do logów aplikacji używaj na tym etapie kubectl logs. Loki i zbieranie logów są osobnym rozszerzeniem.

[Dokumentacja chartu i konfiguracji](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
