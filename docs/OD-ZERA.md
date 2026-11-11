# Od zera — co się tu dzieje?

Nie zakładam, że znasz Docker, Python ani Kubernetes. W projekcie budujemy prosty system zgłoszeń: wpisujesz „serwer nie działa”, aplikacja zapisuje zgłoszenie, a osobny proces symuluje powiadomienie. Kolejne narzędzia pomagają to uruchamiać, sprawdzać i naprawiać.

[Pełny spis i przygotowanie](COURSE.md)

## Jak czytać terminal

| Zapis | Znaczenie |
| --- | --- |
| `pwd` | Pokaż bieżący katalog. |
| `ls` | Pokaż pliki. |
| `cd katalog` | Przejdź do katalogu. |
| `export NAZWA=wartosc` | Zapamiętaj ustawienie w tej sesji terminala. |
| `$NAZWA` | Użyj wartości ustawienia. |
| `# komentarz` | Objaśnienie; powłoka ignoruje resztę linii. |
| `\` na końcu linii | Polecenie trwa w następnym wierszu. |
| `>` / `>>` | Zapisz wynik do pliku, zastępując / dopisując treść. |
| `|` | Przekaż wynik pierwszego programu drugiemu. |
| `Ctrl+C` | Przerwij aktualnie działający program. |
| `echo $?` | Pokaż kod zakończenia poprzedniego polecenia; 0 zwykle oznacza sukces. |

Nie wpisuj znaków ``` otaczających blok. Nie wpisuj przykładowego loginu „twoj-login”; zastąp go własną nazwą. Wcięcia w YAML i Pythonie mają znaczenie. Jeżeli kopiujesz fragment funkcji, wstaw go w opisane miejsce zamiast zastępować nim cały plik.

## Jedno zgłoszenie od początku do końca

1. Przeglądarka lub curl wysyła JSON, np. tytuł i ważność.
2. Nginx przekazuje HTTP do API, jeśli jest już dodany w LAB 03.
3. FastAPI sprawdza dane wejściowe. SQLAlchemy zapisuje w PostgreSQL wiersz zgłoszenia.
4. Otrzymujesz ID, np. 42. To numer rekordu, a nie numer kontenera.
5. Osobnym żądaniem zlecasz powiadomienie. Redis przyjmuje zadanie.
6. Worker pobiera zadanie i zapisuje notification_events.
7. Metryki mówią, ile było odpowiedzi i błędów; logi pomagają wyjaśnić konkretne zdarzenie.

<a id="lab-01"></a>

## LAB 01 — Docker i pierwsza aplikacja

**O co chodzi:** Masz dwa programy: API przyjmuje zgłoszenie, a PostgreSQL je przechowuje. Docker uruchamia każdy program w oddzielnym kontenerze. Compose czyta jeden plik opisujący oba kontenery i ich połączenie.

**Jak czytać kod i polecenia:** `docker compose up -d --build`: docker to narzędzie; compose czyta compose.yaml; up uruchamia usługi; -d zostawia je w tle; --build buduje obraz aplikacji z Dockerfile. `ps` pokazuje stan. `logs --tail=50 api` pokazuje ostatnich 50 linii logu API.

**Co robisz i sprawdzasz:** Wyślij zgłoszenie przez /docs. Otrzymujesz ID, np. 42. Odczytaj je ponownie. /health pyta „czy proces odpowiada?”, a /ready pyta też „czy działa połączenie z bazą?”. Po stop db health może działać, a ready zwracać 503.

**Pytanie kontrolne:** Czy restart kontenera usuwa dane? Dane PostgreSQL są w wolumenie. Zwykły restart ich nie usuwa; usunięcie wolumenu może je skasować.

[Otwórz instrukcję LAB 01](LAB-01.md)

<a id="lab-02"></a>

## LAB 02 — Linux, DNS i sieć

**O co chodzi:** Adres komputera i adres wewnątrz kontenera to różne miejsca. Każdy kontener ma własne localhost. API znajduje bazę po nazwie db dzięki DNS sieci Compose.

**Jak czytać kod i polecenia:** `docker compose exec api ...` wykonuje polecenie w już działającym kontenerze API. `socket.gethostbyname("db")` pyta o adres nazwy. `create_connection(("db",5432),3)` próbuje połączenia TCP z limitem 3 sekund.

**Co robisz i sprawdzasz:** Najpierw sprawdź nazwę db, potem port 5432. Jeżeli nazwa nie działa, diagnozujesz DNS. Jeżeli nazwa działa, ale port nie, sprawdzasz uruchomienie bazy i jej nasłuchiwanie. Samo otwarcie portu nie dowodzi poprawnego hasła ani działania zapytań.

**Pytanie kontrolne:** Co oznacza 127.0.0.1 w API? Sam kontener API. Dlatego nie jest to adres osobnego kontenera bazy.

[Otwórz instrukcję LAB 02](LAB-02.md)

<a id="lab-03"></a>

## LAB 03 — Nginx

**O co chodzi:** Nginx stoi przed API. Użytkownik wysyła żądanie do Nginx, a Nginx przekazuje je do API. Taki pośrednik nazywa się reverse proxy.

**Jak czytać kod i polecenia:** `listen 80` ustawia port kontenera Nginx. Mapowanie 127.0.0.1:8080:80 łączy port 8080 Twojego komputera z tym portem 80. `proxy_pass http://api:8000` wskazuje usługę API w sieci Compose. `:ro` przy pliku konfiguracji pozwala kontenerowi tylko go czytać.

**Co robisz i sprawdzasz:** Po tym labie używasz localhost:8080 zamiast localhost:8000. Jeśli zatrzymasz API, Nginx zwykle zwróci 502, bo nie może uzyskać odpowiedzi z usługi za nim. Gdy API samo stwierdzi brak bazy, może zwrócić 503.

**Pytanie kontrolne:** Czy to już HTTPS? Nie. Ten etap używa lokalnego HTTP. Certyfikat TLS i publiczna domena są osobną konfiguracją.

[Otwórz instrukcję LAB 03](LAB-03.md)

<a id="lab-04"></a>

## LAB 04 — Python, SQL i testy

**O co chodzi:** Endpoint to adres funkcji API, np. GET /incidents. Parametr po znaku ? dodaje warunek: severity=critical oznacza „pokaż krytyczne”. SQLAlchemy tłumaczy opis zapytania w Pythonie na zapytanie do bazy.

**Jak czytać kod i polecenia:** `severity: Severity | None = None` oznacza parametr z dozwolonego zbioru albo brak parametru. `if severity is not None` sprawdza, czy go podano. `where(Incident.severity == severity)` ogranicza wyniki w SQL. `return` oddaje wynik funkcji.

**Co robisz i sprawdzasz:** Stwórz zgłoszenie critical i low. Bez filtra mają być dwa, z critical tylko jedno. Test automatycznie sprawdza te warunki; assert przerywa test, gdy warunek jest fałszywy. Niedozwolone urgent ma dać 422.

**Pytanie kontrolne:** Czy test zapisuje dane w mojej bazie? Testy startowe używają osobnej bazy SQLite w pamięci. To szybki test logiki, nie pełny test PostgreSQL.

[Otwórz instrukcję LAB 04](LAB-04.md)

<a id="lab-05"></a>

## LAB 05 — Bash i CI

**O co chodzi:** Ręczne sprawdzanie kilku rzeczy można zapisać w skrypcie Bash. CI uruchamia podobne kontrole po zmianie kodu w repozytorium.

**Jak czytać kod i polecenia:** `set -euo pipefail` pomaga wykryć błędy i brakujące zmienne. `curl -fsS` zgłasza błędny HTTP i pokazuje komunikat. `|| result=1` zapamiętuje niepowodzenie, ale pozwala zebrać logi. `exit 1` mówi programowi uruchamiającemu, że kontrola się nie udała.

**Co robisz i sprawdzasz:** Uruchom diagnose przy zdrowej aplikacji i po zatrzymaniu bazy. Drugi przebieg ma zgłosić błąd. Plik workflow działa dopiero w .github/workflows repozytorium aplikacji na GitHub. Sam plik w examples nie uruchamia CI.

**Pytanie kontrolne:** Czy zielone CI oznacza brak wszystkich błędów? Oznacza tylko, że przeszły zapisane kontrole w danym środowisku.

[Otwórz instrukcję LAB 05](LAB-05.md)

<a id="lab-06"></a>

## LAB 06 — Redis i worker

**O co chodzi:** API przyjmuje zlecenie, Redis przechowuje zadanie w kolejce, a worker wykonuje je później. Dzięki temu użytkownik nie czeka na każdą czynność. W projekcie powiadomienie jest symulowane wpisem do bazy.

**Jak czytać kod i polecenia:** POST /incidents/42/notification oznacza „zleć powiadomienie dla zgłoszenia 42”. 202 oznacza przyjęcie, nie zakończenie. job_id identyfikuje zadanie. Retry to ponowienie po błędzie. UniqueConstraint zapobiega powieleniu tej samej pary incydentu i typu zdarzenia.

**Co robisz i sprawdzasz:** Zatrzymaj worker, zleć zadanie, zobacz 202, uruchom worker i sprawdź wpis w bazie. Dwa zadania dla tego samego zgłoszenia mają dać jeden wpis. Zatrzymany Redis utrudnia już samo przyjęcie zadania, dlatego dostajesz 503.

**Pytanie kontrolne:** Czy to gwarantuje jednokrotną wysyłkę prawdziwego e-maila? Nie. Unikalny wpis zabezpiecza tę symulację w bazie; integracja z zewnętrzną usługą wymaga dodatkowego projektu.

[Otwórz instrukcję LAB 06](LAB-06.md)

<a id="lab-07"></a>

## LAB 07 — Obrazy i CD

**O co chodzi:** Obraz Docker to przygotowana wersja programu z zależnościami. Kontener to uruchomiony egzemplarz obrazu. GHCR przechowuje obrazy, tak jak GitHub przechowuje kod.

**Jak czytać kod i polecenia:** Tag to nazwa wersji obrazu, którą można przepisać. Digest sha256 identyfikuje konkretną zawartość. Build tworzy obraz, push wysyła go do rejestru, pull pobiera. Rollback uruchamia poprzednią wersję programu.

**Co robisz i sprawdzasz:** Zapisz działający digest przed wdrożeniem następnego. Po zmianie sprawdź ready, utworzenie zgłoszenia i zadanie workera. Przy powrocie do starego obrazu wykonaj te same kontrole.

**Pytanie kontrolne:** Czy rollback obrazu cofa bazę? Nie. Zmiany danych i schematu wymagają osobnego planu zgodności i odzyskiwania.

[Otwórz instrukcję LAB 07](LAB-07.md)

<a id="lab-08"></a>

## LAB 08 — Kubernetes

**O co chodzi:** Kubernetes pilnuje zadeklarowanego stanu: np. „mają działać dwie kopie API”. kind uruchamia lokalny klaster jako kontener Docker. Pod jest jednostką, w której działa kontener aplikacji.

**Jak czytać kod i polecenia:** `kubectl -n incidentflow get pods` pokazuje Pody z przestrzeni incidentflow. `apply -f` wczytuje opis zasobów. Deployment pilnuje kopii. Service daje stałą nazwę. ConfigMap przechowuje ustawienia, Secret dane dostępowe, a PVC miejsce na dane.

**Co robisz i sprawdzasz:** Zwiększ liczbę kopii API do dwóch. Usuń jednego Poda: kontroler powinien odtworzyć brakującą kopię. Tunel port-forward może wymagać ponownego uruchomienia, bo był przypięty do usuniętego Poda.

**Pytanie kontrolne:** Czy dwie kopie oznaczają ochronę przed awarią laptopa? Nie. Lokalny kind nadal działa na jednej maszynie.

[Otwórz instrukcję LAB 08](LAB-08.md)

<a id="lab-09"></a>

## LAB 09 — Helm i monitoring

**O co chodzi:** Helm instaluje zestaw powiązanych manifestów. Prometheus okresowo odczytuje liczby, Grafana je pokazuje, a reguła alertu opisuje warunek wymagający uwagi.

**Jak czytać kod i polecenia:** values.yaml zmienia ustawienia paczki Helm. retention ogranicza czas przechowywania pomiarów. Alert z for: 1m wymaga, by warunek trwał minutę. Pending oznacza oczekiwanie na ten czas, Firing aktywny alert.

**Co robisz i sprawdzasz:** Sprawdź liczbę gotowych replik, zmniejsz API do zera i obserwuj alert. Potem przywróć wcześniejszą liczbę. Brak metryki i wartość zero to różne sytuacje.

**Pytanie kontrolne:** Czy dashboard z LAB 09 liczy 5xx? Jeszcze nie. Metryki odpowiedzi API dodajesz w LAB 14.

[Otwórz instrukcję LAB 09](LAB-09.md)

<a id="lab-10"></a>

## LAB 10 — Terraform

**O co chodzi:** Terraform porównuje opis zasobów z ich znanym stanem i proponuje zmiany. Na początku ćwiczysz lokalnie na terraform_data, bez tworzenia serwera w chmurze.

**Jak czytać kod i polecenia:** init przygotowuje katalog. validate sprawdza konfigurację. plan pokazuje zamiar. apply wykonuje plan. State zapisuje informacje o zarządzanych zasobach. Zmienna api_replicas w tym lokalnym przykładzie jest opisem, nie poleceniem skalującym Kubernetes.

**Co robisz i sprawdzasz:** Przeczytaj plan przed apply. Zmień liczbę, zaplanuj i zobacz różnicę. Nie publikuj state ani danych dostępowych. W opcjonalnej części AWS tylko przygotowujesz plan VPC.

**Pytanie kontrolne:** Czy sam plan tworzy VPC? Nie. Plan pokazuje proponowane operacje; wykonanie wymaga apply i odpowiednich uprawnień.

[Otwórz instrukcję LAB 10](LAB-10.md)

<a id="lab-11"></a>

## LAB 11 — Bezpieczeństwo

**O co chodzi:** Bezpieczeństwo składa się z kilku warstw. Skaner szuka znanych podatności bibliotek. Uprawnienia kontenera ograniczają proces. RBAC ogranicza operacje konta w Kubernetes.

**Jak czytać kod i polecenia:** runAsNonRoot wymaga użytkownika bez uprawnień root. allowPrivilegeEscalation: false ogranicza podnoszenie uprawnień. Role opisuje operacje, a RoleBinding przypisuje je kontu. --as sprawdza operację jako wskazane konto techniczne.

**Co robisz i sprawdzasz:** Przeczytaj jedną podatność zamiast tylko liczyć czerwone wyniki. Sprawdź, że konto lab-reader widzi Pody, ale nie sekrety i nie może usuwać Podów. Forbidden jest w tej próbie poprawnym wynikiem.

**Pytanie kontrolne:** Czy Secret jest automatycznie tajny dla każdego? Nie. Dostęp zależy od uprawnień, a base64 to kodowanie, nie szyfrowanie.

[Otwórz instrukcję LAB 11](LAB-11.md)

<a id="lab-12"></a>

## LAB 12 — Backup

**O co chodzi:** Backup jest kopią danych z wybranego momentu. Restore odtwarza tę kopię. Dopiero odczyt właściwych danych po restore daje praktyczny dowód, że procedura działa.

**Jak czytać kod i polecenia:** pg_dump eksportuje bazę. pg_restore wczytuje archiwum. > zapisuje wynik do pliku, < przekazuje plik programowi. SHA-256 pomaga wykryć zmianę pliku. Bazy lab12_restore_1 i _2 są oddzielone od bazy aplikacji.

**Co robisz i sprawdzasz:** Zrób kopię, odtwórz i znajdź znane zgłoszenie. Usuń dane tylko z testowej kopii. Odtwórz plik w drugiej bazie i porównaj zgłoszenie. Nowych wpisów utworzonych po backupie nie będzie w kopii.

**Pytanie kontrolne:** Czy plik na tym samym laptopie wystarczy na każdą awarię? Nie. Utrata laptopa może zabrać również kopię.

[Otwórz instrukcję LAB 12](LAB-12.md)

<a id="lab-13"></a>

## LAB 13 — GitOps i Argo CD

**O co chodzi:** GitOps polega na porównywaniu stanu w Git ze stanem klastra. Argo CD czyta wskazany katalog i pokazuje różnice. Najpierw ćwiczysz to na jednym ConfigMap.

**Jak czytać kod i polecenia:** repoURL wskazuje repozytorium, targetRevision gałąź lub wersję, path katalog. Refresh odczytuje aktualny stan. Diff pokazuje różnicę. Sync stosuje opis. Self Heal potrafi automatycznie cofnąć ręczną rozbieżność.

**Co robisz i sprawdzasz:** Zsynchronizuj wersję 1, zmień tekst przez kubectl i zobacz OutOfSync. Sync przywróci wartość z Git. Potem wyślij wersję 2 na własną gałąź i wskaż ją w Application.

**Pytanie kontrolne:** Czy Argo zobaczy zmianę tylko w moim edytorze? Nie. Musi być zapisana i wysłana do repozytorium, z którego Argo czyta.

[Otwórz instrukcję LAB 13](LAB-13.md)

<a id="lab-14"></a>

## LAB 14 — Metryki HTTP

**O co chodzi:** API zaczyna liczyć odpowiedzi HTTP. Osobny adres /metrics udostępnia licznik. Prometheus go pobiera, a reguła wykrywa pojawienie się 5xx.

**Jak czytać kod i polecenia:** Middleware to kod uruchamiany wokół obsługi żądania. Counter rośnie, etykieta status rozdziela 200 od 503. rate oblicza szybkość przyrostu w czasie. PodMonitor wskazuje Pody i port, z których Prometheus pobiera dane.

**Co robisz i sprawdzasz:** Najpierw sprawdź metrykę przez curl, potem target UP. Dopiero później wywołaj 503 przez niedostępny Redis. Bez tych dwóch pierwszych kontroli brak alertu niewiele mówi.

**Pytanie kontrolne:** Czy odczyt /metrics ma zwiększać licznik? W tym przykładzie nie; inaczej sam monitoring dopisywałby obserwowany ruch.

[Otwórz instrukcję LAB 14](LAB-14.md)

<a id="lab-15"></a>

## LAB 15 — Logi i Loki

**O co chodzi:** Loki przechowuje linie logów i pozwala je wyszukiwać. Grafana jest interfejsem do zadawania pytań. Importujesz najpierw trzy fikcyjne linie, potem fragment workera.

**Jak czytać kod i polecenia:** Etykieta job wybiera strumień. Operator |= szuka fragmentu tekstu. source=manual-import oznacza jednorazowy import. Czas w tej prostej wersji to czas importu, niekoniecznie czas zdarzenia.

**Co robisz i sprawdzasz:** Wyświetl wszystkie linie, potem tylko ERROR, a potem wszystkie dla incident_id=42. Nie wyciągaj wniosku o obecnej awarii wyłącznie z historycznego wpisu.

**Pytanie kontrolne:** Czy to już stały agent logów? Nie. Ten lab uczy zapisu i wyszukiwania; automatyczne zbieranie wymaga np. Alloy.

[Otwórz instrukcję LAB 15](LAB-15.md)

<a id="lab-16"></a>

## LAB 16 — Ansible

**O co chodzi:** Ansible wykonuje opis czynności na wskazanych komputerach. Tutaj działa na localhost i przygotowuje tylko katalog z plikiem. Nie potrzebujesz serwera ani sudo.

**Jak czytać kod i polecenia:** Inventory to lista hostów. Playbook to lista zadań. Moduł file zarządza katalogiem, a copy zawartością pliku. --check próbuje przewidzieć zmianę, --diff ją pokazuje. changed=0 oznacza brak potrzeby modyfikacji.

**Co robisz i sprawdzasz:** Uruchom playbook dwa razy. Drugi raz oczekuj braku zmian. Dopisz ręcznie linię do zarządzanego pliku, zobacz diff i uruchom ponownie — treść wróci do opisu.

**Pytanie kontrolne:** Czy check mode daje pewność? Nie. Niektóre czynności zależą od realnych zmian wykonanych wcześniej i symulacja może być niepełna.

[Otwórz instrukcję LAB 16](LAB-16.md)

<a id="lab-17"></a>

## LAB 17 — Próba końcowa

**O co chodzi:** Końcowa próba łączy części projektu. Przestajesz patrzeć tylko na pojedyncze narzędzie, a sprawdzasz, czy użytkownik może utworzyć zgłoszenie i otrzymać wynik zadania.

**Jak czytać kod i polecenia:** Postmortem to spokojny opis zdarzenia: objaw, wpływ, oś czasu, przyczyna, naprawa, dowód. Nie szukasz winnego; szukasz mechanizmu awarii i sposobu poprawy.

**Co robisz i sprawdzasz:** Zatrzymaj worker, pokaż czekające zadanie, uruchom worker i potwierdź wynik. Osobno sprawdź Redis i alert. Odtwórz backup. Dołącz wyłącznie własne dowody; brak wykonanego ćwiczenia zapisz wprost.

**Pytanie kontrolne:** Czy muszę znać wszystkie komendy na pamięć? Nie. Musisz rozumieć, czego oczekujesz, umieć znaleźć właściwą instrukcję i ocenić wynik.

[Otwórz instrukcję LAB 17](LAB-17.md)

## NotificationEvent — wyjaśnienie kodu linia po linii

To opis tabeli, a nie funkcja wysyłająca wiadomość. Każdy zapisany obiekt ma reprezentować ślad symulowanego powiadomienia.

| Fragment | Co znaczy |
| --- | --- |
| Potrójny cudzysłów na początku pliku | Opis modułu dla osoby czytającej kod. |
| `from datetime import datetime, timezone` | Pobierz narzędzia do daty i strefy czasowej. |
| Importy z sqlalchemy | Pobierz elementy potrzebne do opisania tabeli i kolumn. |
| `from .db import Base` | Użyj wspólnej klasy bazowej modeli z naszego pliku db.py. Kropka oznacza import w tym pakiecie. |
| `from .models import Incident` | Pobierz model zgłoszenia, żeby wskazać relację. |
| `class NotificationEvent(Base)` | Utwórz model tabeli należący do tej samej konfiguracji SQLAlchemy. |
| `__tablename__ = "notification_events"` | Tabela w bazie ma taką nazwę. |
| `UniqueConstraint("incident_id", "event_type", ...)` | Nie pozwól na dwa rekordy z tą samą parą wartości. |
| `id: Mapped[int]` | To pole modelu ma przechowywać liczbę całkowitą. |
| `mapped_column(primary_key=True)` | Kolumna jednoznacznie identyfikuje wiersz. |
| `ForeignKey(Incident.id)` | incident_id ma wskazywać istniejące zgłoszenie. |
| `nullable=False` | W kolumnie nie może być SQL NULL, czyli braku wartości. |
| `String(40)` | W PostgreSQL tekst ma maksymalnie 40 znaków. |
| `DateTime(timezone=True)` | Kolumna daty ma obsługiwać informację o strefie czasowej. |
| `default=lambda: datetime.now(timezone.utc)` | Przy zapisie przez SQLAlchemy oblicz aktualny czas UTC. Lambda opóźnia obliczenie do momentu potrzeby. |

Dlaczego para jest unikalna? Dla incydentu 42 zdarzenie „notification_sent” może istnieć raz. Dla incydentu 43 ten sam typ jest dozwolony. W przykładzie worker używa INSERT ON CONFLICT DO NOTHING, więc duplikat zostaje pominięty. Bez takiej obsługi naruszenie unikalności wywołałoby błąd.

`default` to domyślna wartość po stronie SQLAlchemy, nie automatycznie SQL DEFAULT dla każdego ręcznego INSERT. Sam import modelu też nie tworzy tabeli; starter uruchamia create_all podczas startu API. Zmiany istniejących kolumn wymagają migracji, bo create_all nie przebudowuje automatycznie schematu.

## Gdy nic nie rozumiesz w błędzie

Zapisz: w którym katalogu jesteś, jakie dokładnie polecenie wykonałeś, jaki był oczekiwany wynik i jaki komunikat otrzymałeś. Nie wklejaj zawartości .env ani tokenów. Czytaj końcową przyczynę błędu, ale zachowaj też kontekst. Zmieniaj jedną rzecz i ponów ten sam test. To normalny sposób pracy z tymi narzędziami.
