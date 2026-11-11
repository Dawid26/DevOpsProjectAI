# LAB 13 — GitOps i Argo CD bez zgadywania

[Spis działów](COURSE.md) · [Wyjaśnienie od zera](OD-ZERA.md#lab-13)

**Cel:** zobaczyć różnicę między ustawieniem zapisanym w Git a ustawieniem działającym w Kubernetes. Zaczniemy od pojedynczego ConfigMap. Dzięki temu najpierw poznasz synchronizację, zanim powierzysz jej bazę i całą aplikację.

## 1. Przygotuj istniejący klaster

Ustaw KUBECONFIG tak jak w LAB 08. `kubectl config current-context` ma wskazywać `kind-incidentflow-lab08`. Potrzebujesz dostępu do Internetu z klastra oraz dodatkowej pamięci dla Argo CD. Jeżeli Pody są Pending, przeczytaj `kubectl describe pod` zamiast ponawiać instalację.

Z [listy wydań Argo CD](https://github.com/argoproj/argo-cd/releases) wybierz stabilną wersję i podstaw pełny tag zamiast `vX.Y.Z`. Zapisz wybrany numer w notatkach. Nie kopiuj dosłownie placeholdera.

```bash
export ARGO_VERSION=vX.Y.Z
mkdir -p /tmp/incidentflow-argo
curl -fL "https://raw.githubusercontent.com/argoproj/argo-cd/$ARGO_VERSION/manifests/install.yaml" -o /tmp/incidentflow-argo/install.yaml
less /tmp/incidentflow-argo/install.yaml
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply --server-side -n argocd -f /tmp/incidentflow-argo/install.yaml
kubectl -n argocd rollout status deployment/argocd-server --timeout=300s
kubectl -n argocd get pods
```

`curl -fL` pobiera plik i zgłasza błąd HTTP; `less` pozwala przeczytać manifest, wyjście klawiszem `q`. Ten instalator tworzy również szerokie uprawnienia kontrolera. Używaj go w swoim lokalnym klastrze edukacyjnym.

## 2. Otwórz panel lokalnie

W drugiej karcie ustaw ten sam KUBECONFIG:

```bash
kubectl -n argocd port-forward svc/argocd-server 18443:443 --address 127.0.0.1
```

Otwórz `https://localhost:18443`. Domyślny certyfikat lokalnego Argo może wywołać ostrzeżenie przeglądarki. Login to `admin`; początkowe hasło odczytasz lokalnie:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
printf '\n'
```

Nie zapisuj hasła w raporcie. Po zalogowaniu zmień je w ustawieniach konta.

## 3. Powiedz Argo, który katalog ma czytać

```bash
export LAB_SOURCE=/home/twoj-login/DevOpsProjectAI
kubectl apply -f "$LAB_SOURCE/examples/lab-13/application.yaml"
kubectl -n argocd get applications
```

Zmień ścieżkę na własną. Application to instrukcja dla kontrolera Argo, a ConfigMap to zasób, który ma powstać. Plik Application leży poza katalogiem `workload`, żeby Argo nie zarządzało tu własną definicją.

W panelu otwórz `incidentflow-learning`, wybierz Refresh i obejrzyj Diff. Następnie wybierz Sync i Synchronize. Na tym etapie nie włączaj Prune ani automatycznej synchronizacji. Oczekuj `Synced` i odczytu:

```bash
kubectl -n gitops-lab get configmap incidentflow-learning -o jsonpath='{.data.message}'
printf '\n'
```

Powinno być „Wersja 1: konfiguracja pochodzi z Git”. GitOps nie buduje obrazu Docker; pilnuje zgodności zasobów z opisem.

## 4. Zrób rozbieżność i ją napraw

```bash
kubectl -n gitops-lab patch configmap incidentflow-learning --type=merge -p '{"data":{"message":"Ręczna zmiana poza Git"}}'
```

W panelu naciśnij Refresh. Stan powinien być `OutOfSync`. Zobacz Diff: Git ma wersję 1, klaster ręczną zmianę. Kliknij Sync. Odczytaj ConfigMap ponownie — wróci treść z repozytorium. To podstawowy mechanizm, który miałeś zobaczyć.

## 5. Wdróż prawdziwą zmianę z Git

W lokalnym klonie DevOpsProjectAI utwórz osobną gałąź. Zmień tylko `message` w `examples/lab-13/workload/configmap.yaml` na wersję 2:

```bash
cd "$LAB_SOURCE"
git switch -c lab/13-gitops-message
# Teraz edytuj plik w edytorze i zapisz go.
git diff -- examples/lab-13/workload/configmap.yaml
git add examples/lab-13/workload/configmap.yaml
git commit -m "lab13: change learning message"
git push -u origin lab/13-gitops-message
kubectl -n argocd patch application incidentflow-learning --type=merge -p '{"spec":{"source":{"targetRevision":"lab/13-gitops-message"}}}'
```

Refresh, Diff i Sync powinny pokazać wersję 2. Gałąź musi istnieć na GitHub, ponieważ Argo nie czyta Twoich niezacommitowanych plików. Przy pracy na fork podmień repoURL w Application na swój adres.

## 6. Powrót i opcja self-heal

Przywróć `targetRevision` na `main`, wykonaj Refresh i Sync. Oczekuj wersji 1. To ćwiczenie powrotu konfiguracji; nie cofa danych zapisanych w bazie.

```bash
kubectl -n argocd patch application incidentflow-learning --type=merge -p '{"spec":{"source":{"targetRevision":"main"}}}'
```

Dopiero po ręcznej próbie możesz w panelu włączyć Auto-Sync oraz Self Heal bez Prune. Powtórz ręczny patch i zobacz automatyczny powrót. Następnie wyłącz Auto-Sync. Prune to osobna opcja usuwania zasobów usuniętych z Git.

Zapisz `docs/GITOPS-13.md`: trzy stany, treść przed/po, commit zmiany. Pełna adopcja API wymaga najpierw umieszczenia jego manifestów w osobnym katalogu, zachowania Secret poza Git i ustalenia, kto zarządza replikami (HPA czy Git). Ten lab świadomie testuje mechanizm na jednym zasobie.

Sprzątanie: usuń Application bez kaskadowego usuwania w panelu, następnie `kubectl delete namespace gitops-lab`. Nie usuwaj namespace `incidentflow`.

[Oficjalna instalacja](https://argo-cd.readthedocs.io/en/stable/getting_started/) · [Automatyczna synchronizacja](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/)
