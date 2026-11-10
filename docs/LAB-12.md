# LAB 12 — backup i odzyskiwanie danych krok po kroku

Masz już aplikację, monitoring i ograniczenia uprawnień. Teraz sprawdzisz: **czy potrafisz odzyskać zgłoszenia, gdy ktoś usunie dane?** Zrobisz kopię PostgreSQL, odtworzysz ją w osobnej bazie i porównasz wynik. Następnie zasymulujesz utratę danych wyłącznie w tej kopii testowej.

Nie musisz pamiętać wszystkich poleceń. Wykonuj po jednym kroku i sprawdzaj wynik. Przykłady są w [examples/lab-12](../examples/lab-12). Wymagany jest działający klaster oraz aplikacja po [LAB 08](LAB-08.md), w tym tabele `incidents` i `notification_events` z LAB 06. LAB 09–11 nie zmieniają sposobu wykonania tego ćwiczenia.

## 1. Co właściwie kopiujemy?

Wyobraź sobie zeszyt ze zgłoszeniami. PostgreSQL przechowuje jego aktualną treść. Backup to zapis zawartości zeszytu z wybranego momentu. Restore oznacza odtworzenie tej zawartości.

| Nazwa | Znaczenie w tym ćwiczeniu |
| --- | --- |
| `incidentflow` | Baza działającej aplikacji; pozostaje źródłem kopii. |
| `incidentflow.dump` | Plik z tabelami i danymi wyeksportowanymi z bazy. |
| `lab12_restore_1` | Osobna baza do pierwszego odtworzenia i symulacji utraty danych. |
| `lab12_restore_2` | Nowa baza do ponownego odtworzenia tego samego pliku. |
| PVC | Miejsce na bieżące dane PostgreSQL w klastrze. |

PVC zachowa dane po wymianie Poda, ale nie cofnie polecenia usuwającego zgłoszenia. Plik kopii zapisz na swoim komputerze, poza kontenerami kind. To ćwiczenie odtwarza dane na tym samym serwerze PostgreSQL; nie odtwarza całego klastra ani infrastruktury.

## 2. Przygotuj terminal i sprawdź dane

Pracujesz w Ubuntu/WSL. Podmień obie ścieżki na swoje. `LAB_SOURCE` oznacza katalog repozytorium portfolio, a plik `KUBECONFIG` pochodzi z katalogu aplikacji LAB 08.

```bash
export LAB_SOURCE=/home/twoj-login/DevOpsProjectAI
export KUBECONFIG=/home/twoj-login/incidentflow-devops-lab/.kubeconfig-lab08
kubectl config current-context
kubectl -n incidentflow get pod db-0
kubectl -n incidentflow exec db-0 -c postgres -- sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT id, title FROM incidents ORDER BY id LIMIT 5;"'
```

Oczekuj kontekstu `kind-incidentflow-lab08`, gotowego Poda `db-0` i przynajmniej jednego zgłoszenia. Jeśli tabela jest pusta, utwórz zgłoszenie przez `/docs` aplikacji, tak jak w LAB 08. Zleć też jego powiadomienie i poczekaj na wykonanie przez workera. Zanotuj ID i tytuł zgłoszenia, które ma znaleźć się w kopii.

## 3. Zapisz kopię na komputerze

```bash
umask 077
mkdir -p "$HOME/incidentflow-backups"
export BACKUP_DIR="$HOME/incidentflow-backups/lab12-$(date -u +%Y%m%dT%H%M%SZ)"
bash "$LAB_SOURCE/examples/lab-12/backup.sh" "$BACKUP_DIR"
ls -lh "$BACKUP_DIR"
```

Powinny powstać `incidentflow.dump` i `SHA256SUMS`. Nie wrzucaj ich do GitHub: mogą zawierać treść zgłoszeń. Katalog jest poza repozytorium, a `umask 077` ogranicza dostęp do nowych plików do Twojego użytkownika.

Co robi skrypt, po kolei:

1. Sprawdza kontekst klastra i tworzy nowy katalog. Odmawia użycia istniejącego katalogu, żeby zachować wcześniejszą kopię.
2. Uruchamia `pg_dump` wewnątrz kontenera PostgreSQL, gdzie są już potrzebne narzędzia i zmienne środowiskowe.
3. `--format=custom` wybiera format archiwum do późniejszego odczytu przez `pg_restore`.
4. Znak `>` zapisuje wynik na Twoim komputerze. Nie używamy `-t`, bo terminal nie jest potrzebny do przesyłania pliku binarnego.
5. Dopiero po udanym eksporcie zmienia nazwę pliku `.partial` na `.dump` i wylicza sumę SHA-256.

Suma pomaga wykryć przypadkową zmianę pliku. Nie szyfruje danych i nie dowodzi, że kopię da się odtworzyć. To sprawdzisz teraz. Kopia obejmuje jedną bazę; nie obejmuje kolejki Redis, plików Kubernetes ani kont PostgreSQL jako obiektów całego serwera.

## 4. Odtwórz kopię w nowej bazie

```bash
bash "$LAB_SOURCE/examples/lab-12/restore.sh" "$BACKUP_DIR" lab12_restore_1
kubectl -n incidentflow exec db-0 -c postgres -- sh -c 'psql -U "$POSTGRES_USER" -d lab12_restore_1 -c "SELECT id, title FROM incidents ORDER BY id LIMIT 5;"'
kubectl -n incidentflow exec db-0 -c postgres -- sh -c 'psql -U "$POSTGRES_USER" -d lab12_restore_1 -c "SELECT incident_id, event_type FROM notification_events;"'
```

Sprawdź zapisane wcześniej ID, tytuł i powiadomienie. Sam komunikat „Odtworzono” nie zastępuje sprawdzenia treści.

Skrypt sprawdza sumę pliku i jego format, tworzy pustą bazę, następnie wczytuje tabele i dane w jednej transakcji. Jeśli przy wczytywaniu wystąpi błąd, zmiany tej transakcji są wycofywane; utworzona pusta baza pozostaje. Wtedy przeczytaj błąd i po naprawie użyj nowej nazwy, np. `lab12_restore_3`.

Skrypt przyjmuje tylko nazwy `lab12_restore_NUMER` i odmawia nadpisania istniejącej bazy. Nie używa `pg_restore --create`, które mogłoby odtworzyć bazę pod nazwą zapisaną w archiwum. API nadal łączy się z `incidentflow`.

## 5. Zasymuluj utratę danych w pierwszej bazie testowej

Poniższe polecenie usuwa zawartość tabel **tylko w `lab12_restore_1`**. Nie zmieniaj nazwy po `-d`. `CASCADE` obejmuje również tabele powiązane kluczem obcym, tutaj powiadomienia.

```bash
kubectl --context=kind-incidentflow-lab08 -n incidentflow exec db-0 -c postgres -- sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d lab12_restore_1 -c "TRUNCATE TABLE incidents CASCADE; SELECT count(*) FROM incidents;"'
```

Oczekiwany wynik licznika to `0`. Właśnie pokazałeś, że działający Pod i PVC nie chronią przed usunięciem zawartości tabeli.

## 6. Odzyskaj dane z tego samego pliku

```bash
START_SECONDS=$SECONDS
bash "$LAB_SOURCE/examples/lab-12/restore.sh" "$BACKUP_DIR" lab12_restore_2
kubectl -n incidentflow exec db-0 -c postgres -- sh -c 'psql -U "$POSTGRES_USER" -d lab12_restore_2 -c "SELECT id, title FROM incidents ORDER BY id LIMIT 5; SELECT incident_id, event_type FROM notification_events;"'
echo "Czas odtworzenia i odczytu: $((SECONDS - START_SECONDS)) sekund"
```

Zgłoszenie i jego powiadomienie powinny wrócić. Sprawdź też bazę źródłową:

```bash
kubectl -n incidentflow exec db-0 -c postgres -- sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT id, title FROM incidents ORDER BY id LIMIT 5;"'
```

Źródłowe dane nadal powinny istnieć. Nowe zgłoszenia dodane po wykonaniu backupu nie pojawią się w odtworzonej kopii. To normalne: plik przechowuje wcześniejszy stan.

## 7. Co oznaczają RPO i RTO?

**RPO** to przyjęty cel określający, jak duża utrata ostatnich danych jest dopuszczalna. Jeśli robisz kopię co godzinę, awaria tuż przed następną kopią może kosztować prawie godzinę zmian, zakładając udane i dostępne kopie.

**RTO** to przyjęty cel czasu przywrócenia usługi. Pomiar powyżej dotyczy tylko odtworzenia bazy i odczytu. Pełne przywrócenie usługi obejmuje także wykrycie awarii, przygotowanie środowiska, podłączenie API i test działania. Nie nazywaj tego pomiaru dowodem osiągnięcia pełnego RTO aplikacji.

Zadanie dodatkowe: po backupie dodaj drugie zgłoszenie w aplikacji. Potwierdź, że jest w bazie źródłowej, ale nie ma go w odtworzonej bazie. W ten sposób zobaczysz lukę między momentem kopii a późniejszymi zmianami.

## 8. Zapisz wynik i posprzątaj

Wypełnij [szablon raportu](../examples/lab-12/REPORT-12.md) i zapisz go jako `docs/RECOVERY-12.md` w swoim repozytorium aplikacji. Nie wpisuj haseł ani rzeczywistych danych użytkowników.

Gdy skończysz porównania, możesz usunąć dwie bazy testowe. Te polecenia pozostawiają bazę aplikacji oraz plik backupu:

```bash
kubectl --context=kind-incidentflow-lab08 -n incidentflow exec db-0 -c postgres -- sh -c 'dropdb -U "$POSTGRES_USER" lab12_restore_1'
kubectl --context=kind-incidentflow-lab08 -n incidentflow exec db-0 -c postgres -- sh -c 'dropdb -U "$POSTGRES_USER" lab12_restore_2'
```

| Problem | Co zrobić |
| --- | --- |
| Skrypt prosi o kontekst LAB 08 | Ustaw poprawny `KUBECONFIG` i sprawdź `current-context`. |
| Katalog kopii już istnieje | Ustaw nowy `BACKUP_DIR`; zachowaj poprzednią kopię. |
| Baza testowa już istnieje | Użyj kolejnego numeru; nie nadpisuj jej automatycznie. |
| Suma kontrolna nie pasuje | Przerwij odtwarzanie i ustal, skąd pochodzi zmiana pliku. |
| Brakuje `notification_events` | Dokończ LAB 06 i uruchom jego obraz w klastrze LAB 08. |
| Zniknęła zmienna `BACKUP_DIR` | W nowej karcie ustaw ją na pełną ścieżkę istniejącej kopii. |

**Zaliczenie:** kopia na komputerze, poprawny odczyt zgłoszenia i powiadomienia w nowej bazie, licznik zero po symulacji oraz udane ponowne odtworzenie. Backup na tym samym komputerze nie zabezpiecza przed utratą tego komputera. Następnym rozszerzeniem będzie osobne miejsce przechowywania kopii i automatyczny test odtwarzania.

Źródła: [PostgreSQL 17 — pg_dump](https://www.postgresql.org/docs/17/app-pgdump.html), [pg_restore](https://www.postgresql.org/docs/17/app-pgrestore.html).
