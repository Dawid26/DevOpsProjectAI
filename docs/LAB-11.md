# LAB 11 — skan obrazu, uprawnienia kontenera i RBAC

[Spis wszystkich działów](COURSE.md) · [Proste wyjaśnienia tego działu](OD-ZERA.md#lab-11)


W tym labie sprawdzisz trzy osobne rzeczy. Czy biblioteki w obrazie mają znane podatności? Z jakimi uprawnieniami działa proces API? Jakie operacje w Kubernetes może wykonać wybrane konto techniczne?

Pracuj na klastrze kind z LAB 08. Przykłady są w [examples/lab-11](../examples/lab-11). Ustaw LAB_SOURCE na katalog repozytorium, a KUBECONFIG na plik klastra ćwiczeniowego.

**1. Przygotuj skaner**

Zainstaluj Trivy według [oficjalnej instrukcji](https://trivy.dev/docs/latest/getting-started/installation/). Uruchom:

```bash
trivy --version
export APP_IMAGE=incidentflow:lab08
docker image inspect "$APP_IMAGE" --format '{{.Id}}'
mkdir -p /tmp/incidentflow-security
trivy image --scanners vuln --severity HIGH,CRITICAL --format json --output /tmp/incidentflow-security/image.json "$APP_IMAGE"
trivy image --scanners vuln --severity HIGH,CRITICAL --exit-code 1 "$APP_IMAGE"
echo $?
```

Pierwszy skan zapisuje raport. Drugi dodatkowo ustawia kod wyjścia 1, gdy znajdzie podatności o wybranej ważności. Błąd pobrania bazy podatności też wymaga diagnozy, dlatego przeczytaj komunikat. Raport może się zmieniać nawet dla tego samego obrazu, gdy pojawiają się nowe informacje o podatnościach.

**2. Przeczytaj jedno znalezisko**

Wybierz jeden wpis. Zanotuj nazwę pakietu, zainstalowaną wersję, identyfikator CVE i wersję z poprawką, jeśli jest podana. Sprawdź, czy pakiet pochodzi z systemu obrazu bazowego czy z zależności Pythona.

Zaktualizuj właściwą zależność lub obraz bazowy. Zbuduj obraz z nowym tagiem, uruchom testy z poprzednich labów i ponów skan. Porównaj to samo CVE przed zmianą i po niej. Jeśli skan nie wykazuje HIGH/CRITICAL, opisz ten wynik oraz datę i wersję skanera.

**3. Ogranicz uprawnienia procesu API**

Przykładowy Dockerfile IncidentFlow tworzy użytkownika appuser o UID 10001. Sprawdź go:

```bash
docker run --rm "$APP_IMAGE" id
export LAB_SOURCE=/home/twoj-login/DevOpsProjectAI
kubectl config current-context
kubectl -n incidentflow patch deployment api --type=strategic --patch-file "$LAB_SOURCE/examples/lab-11/api-security.patch.yaml"
kubectl -n incidentflow rollout status deployment/api --timeout=180s
kubectl -n incidentflow exec deployment/api -- id
```

Patch ustala UID i GID 10001, wymaga użytkownika bez uprawnień root, zabrania podnoszenia uprawnień i usuwa dodatkowe Linux capabilities. RuntimeDefault włącza profil seccomp dostarczony przez runtime. Wyłączone automatyczne montowanie tokena oznacza, że proces API nie otrzymuje domyślnie tokena konta Kubernetes.

Sprawdź /health, /ready, utworzenie incydentu i zlecenie zadania przez tunel z LAB 08. Jeżeli tunel przestał działać po wymianie Poda, uruchom ponownie port-forward. Punkt kontrolny to poprawne odpowiedzi i UID 10001.

Patch dotyczy API. Własnym zadaniem jest przygotowanie analogicznej zmiany dla kontenera worker, zachowując jego nazwę i testując wykonanie zadania. PostgreSQL korzysta z własnego użytkownika i wymaga osobnej konfiguracji.

**4. Utwórz konto tylko do odczytu Podów**

```bash
kubectl apply -f "$LAB_SOURCE/examples/lab-11/reader-rbac.yaml"
kubectl auth can-i list pods -n incidentflow --as=system:serviceaccount:incidentflow:lab-reader
kubectl auth can-i get pods/log -n incidentflow --as=system:serviceaccount:incidentflow:lab-reader
kubectl auth can-i get secrets -n incidentflow --as=system:serviceaccount:incidentflow:lab-reader
kubectl auth can-i delete pods -n incidentflow --as=system:serviceaccount:incidentflow:lab-reader
```

Oczekiwane odpowiedzi to yes, yes, no, no. To sprawdzenie uprawnień konta wskazanego przez --as. Polecenia wykonujesz ze swojego administracyjnego kontekstu klastra kind.

ServiceAccount jest kontem technicznym. Role wymienia dozwolone operacje w namespace incidentflow. RoleBinding przypisuje tę rolę kontu. Role ma zakres jednego namespace, dzięki czemu uprawnienia są związane z tym projektem.

**5. Sprawdź realny odczyt przez to konto**

```bash
kubectl -n incidentflow get pods --as=system:serviceaccount:incidentflow:lab-reader
kubectl -n incidentflow get secrets --as=system:serviceaccount:incidentflow:lab-reader
```

Pierwsze polecenie powinno pokazać Pody. Drugie powinno zakończyć się Forbidden. To oczekiwany wynik ćwiczenia.

**6. Zapisz dowody i zmianę w kodzie**

Utwórz docs/SECURITY-11.md. Zapisz wynik skanu, jeden przeanalizowany pakiet, wynik id w kontenerze oraz cztery odpowiedzi can-i. Ustawienia patcha przenieś do manifestu źródłowego API w swoim repozytorium aplikacji, żeby kolejne kubectl apply zachowało wybraną konfigurację.

Zaliczenie oznacza przeczytanie raportu, działające API po zmianie uprawnień i poprawne wyniki RBAC. Wynik skanera jest jednym elementem oceny bezpieczeństwa; dostęp do bazy, autoryzacja użytkowników i zarządzanie sekretami wymagają dalszych ćwiczeń.

[Trivy — skanowanie podatności](https://trivy.dev/docs/latest/scanner/vulnerability/) · [Kubernetes — security context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) · [Kubernetes — RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
