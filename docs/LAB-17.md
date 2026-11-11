# LAB 17 — próba końcowa i prezentacja projektu

[Spis](COURSE.md) · [Wyjaśnienie](OD-ZERA.md#lab-17)

Masz już gotowe instrukcje. Teraz sprawdzisz, co umiesz wykonać i wyjaśnić. Ukończenie kursu oznacza własne wyniki ćwiczeń; same pliki w repozytorium nie dowodzą działającej infrastruktury.

## 1. Zapisz stan przed ćwiczeniem

Pracuj na kind z LAB 08. Ustaw jego KUBECONFIG. Sprawdź:

```bash
kubectl config current-context
kubectl -n incidentflow get pods,services,pvc
kubectl -n incidentflow get deployments -o wide
kubectl -n monitoring get pods
```

Zapisz nazwy obrazów i liczbę replik. Przygotuj tunel do API jak w LAB 14. Utwórz nowe zgłoszenie z tytułem „Próba końcowa” przez `/docs`, zanotuj jego ID. Zleć powiadomienie i sprawdź wpis `notification_events`. Wykonaj kopię według LAB 12, odtwórz ją w osobnej bazie i potwierdź to samo ID.

## 2. Awaria workera

Zatrzymaj tylko workera i zleć powiadomienie dla nowego zgłoszenia:

```bash
WORKER_REPLICAS=$(kubectl -n incidentflow get deployment worker -o jsonpath='{.spec.replicas}')
kubectl -n incidentflow scale deployment/worker --replicas=0
```

Zleć zadanie przez `/docs`. Oczekuj 202: przyjęto zadanie, lecz nie oznacza to jego wykonania. Sprawdź brak nowego wpisu w tabeli powiadomień dla tego ID. Następnie:

```bash
kubectl -n incidentflow scale deployment/worker --replicas="$WORKER_REPLICAS"
kubectl -n incidentflow rollout status deployment/worker --timeout=180s
kubectl -n incidentflow logs deployment/worker --tail=50
```

Oczekuj wykonania oczekującego zadania i nowego wiersza w bazie. Nie zatrzymuj Redis w tym scenariuszu: jego pamięciowa kolejka musi przetrwać oczekiwanie.

## 3. Awaria Redis i alert

Wykonaj scenariusz z LAB 14. Zapisz czas pierwszego 503, pojawienia się alertu, przywrócenia Redis i powrotu 202. Użyj tylko danych ćwiczeniowych. Odczytaj logi API i workera. Wyjaśnij, dlaczego `/health` i `/ready` mogą nadal być poprawne, skoro nie działa zlecanie powiadomień.

## 4. Dowody zamiast deklaracji

| Umiejętność | Co zachować w raporcie |
| --- | --- |
| Docker i sieć | Nazwy usług, port wejścia, wyjaśnienie `db:5432`. |
| CI | Link do własnego udanego uruchomienia testów na GitHub. |
| CD | Identyfikator obrazu i wynik wdrożenia/rollbacku LAB 07. |
| Kubernetes | Gotowość Podów, próba odtworzenia Poda. |
| Monitoring | Zapytanie metryk i obserwacja alertu. |
| Logi | Zanonimizowany fragment i wniosek diagnostyczny. |
| Backup | Wynik odtworzenia konkretnego zgłoszenia. |
| GitOps | Commit, Diff i stan po Sync. |
| Ansible | Drugi przebieg `changed=0`. |
| Bezpieczeństwo | Wyniki RBAC i analiza jednego znaleziska skanera. |

## 5. Napisz krótki postmortem

Skopiuj [szablon](../examples/lab-17/POSTMORTEM.md) do swoich dokumentów. Opisz co się stało, wpływ na użytkownika, jak rozpoznałeś przyczynę, jak przywróciłeś działanie i jak udowodniłeś naprawę. Oddziel fakty od hipotez. Nie wpisuj haseł, tokenów ani prywatnej treści logów.

## 6. Jak opowiedzieć o projekcie pracodawcy?

Przygotuj pięć minut prezentacji:

1. „IncidentFlow przyjmuje zgłoszenia i zleca zadania w tle”. Pokaż jedno zgłoszenie.
2. „API zapisuje w PostgreSQL, kolejka Redis przekazuje pracę workerowi”. Wskaż odpowiadające im usługi.
3. „Potrafię odróżnić działający proces od gotowości zależnej od bazy”. Pokaż health i ready.
4. „Przećwiczyłem awarię i odtworzenie danych”. Pokaż własne wyniki, nie sam skrypt.
5. „To projekt edukacyjny; pozostałe ograniczenia to m.in. autoryzacja użytkowników, trwałość kolejki i wdrożenie produkcyjne”. Wymień tylko to, co rozumiesz.

## 7. Chmura i dalsze granice

LAB 10 zawiera plan AWS VPC, a nie gotowe wdrożenie API w AWS. Przed chmurą trzeba wybrać region, budżet, sposób dostępu, usługę obliczeniową, magazyn danych i plan usunięcia zasobów. Nie uruchamiaj płatnej infrastruktury tylko po to, by zaznaczyć dział jako zakończony. Tę ścieżkę lokalną możesz ukończyć bez konta chmurowego.

Produkcyjne rozszerzenia to osobne projekty: HTTPS i DNS, logowanie i autoryzacja użytkowników, migracje Alembic zamiast create_all, trwała kolejka, automatyczny backup poza komputerem, odtwarzanie całego środowiska oraz aktualizacje zależności. Nie są wymagane do zaliczenia przedstawionych 17 laboratoriów.

**Koniec ścieżki:** uzupełnij tabelę postępu w COURSE.md we własnej kopii, wskaż wykonane ćwiczenia i te, które wymagają pomocy. Przećwicz jeszcze raz jeden problem bez zaglądania do rozwiązania. Nie musisz znać komend na pamięć — powinieneś umieć wyjaśnić, co sprawdzają.
