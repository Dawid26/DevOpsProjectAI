# LAB 16 — Ansible: komputer wykonuje listę przygotowań

[Spis](COURSE.md) · [Wyjaśnienie](OD-ZERA.md#lab-16)

**Cel:** przygotować katalog i plik przez opis oczekiwanego stanu. Uruchomisz ten sam opis dwa razy i sprawdzisz, że drugi przebieg niczego nie zmienia. Pracujemy lokalnie bez sudo i bez modyfikowania usług systemowych.

## 1. Przygotuj środowisko

W Ubuntu/WSL z Pythonem 3.11 lub nowszym utwórz osobne środowisko. Nie musisz mieć uruchomionego Kubernetes.

```bash
python3 -m venv "$HOME/incidentflow-ansible-venv"
source "$HOME/incidentflow-ansible-venv/bin/activate"
python -m pip install 'ansible-core>=2.19,<2.20'
ansible --version
```

Jeśli polecenie venv zgłasza brak modułu, zainstaluj pakiet `python3-venv` odpowiedni dla swojej dystrybucji. Zapisz wersję Ansible i Pythona w raporcie; przykłady używają standardowych modułów file i copy.

## 2. Przeczytaj dwa pliki

[Inventory](../examples/lab-16/inventory.ini) zawiera host `localhost` w grupie `learning`. `ansible_connection=local` oznacza pracę na tym komputerze, bez połączenia SSH.

[Playbook](../examples/lab-16/playbook.yaml) wskazuje grupę hostów i dwie czynności: katalog oraz plik. `state: directory` mówi „ten katalog ma istnieć”. `mode: '0700'` daje właścicielowi dostęp do katalogu, a `0600` pozwala właścicielowi czytać i zmieniać plik. `{{ ... }}` wstawia wartość zmiennej.

## 3. Sprawdź składnię i zapowiedź zmian

```bash
export LAB_SOURCE=/home/twoj-login/DevOpsProjectAI
ansible-playbook -i "$LAB_SOURCE/examples/lab-16/inventory.ini" "$LAB_SOURCE/examples/lab-16/playbook.yaml" --syntax-check
ansible-playbook -i "$LAB_SOURCE/examples/lab-16/inventory.ini" "$LAB_SOURCE/examples/lab-16/playbook.yaml" --check --diff
```

Podmień ścieżkę. `-i` oznacza inventory. `--check` symuluje, a `--diff` pokazuje różnice plików. Przy pierwszym check mode plik może zgłosić brak katalogu: symulowane utworzenie katalogu nie tworzy go naprawdę. Właśnie dlatego check mode nie jest gwarancją udanego wykonania.

## 4. Wykonaj zmianę i powtórz

```bash
ansible-playbook -i "$LAB_SOURCE/examples/lab-16/inventory.ini" "$LAB_SOURCE/examples/lab-16/playbook.yaml"
cat "$HOME/incidentflow-ansible-lab/CHECKLIST.txt"
ansible-playbook -i "$LAB_SOURCE/examples/lab-16/inventory.ini" "$LAB_SOURCE/examples/lab-16/playbook.yaml"
```

Pierwszy przebieg powinien pokazać zmiany, drugi `changed=0` i `failed=0`. To idempotencja: ponowne wykonanie prowadzi do tego samego stanu.

## 5. Zrób ręczną zmianę i zobacz naprawę

```bash
printf '\nRęcznie dopisana linia\n' >> "$HOME/incidentflow-ansible-lab/CHECKLIST.txt"
ansible-playbook -i "$LAB_SOURCE/examples/lab-16/inventory.ini" "$LAB_SOURCE/examples/lab-16/playbook.yaml" --check --diff
ansible-playbook -i "$LAB_SOURCE/examples/lab-16/inventory.ini" "$LAB_SOURCE/examples/lab-16/playbook.yaml"
```

Diff powinien zapowiedzieć usunięcie dopisku, a realny przebieg przywróci treść z playbooka. Ansible zarządza całym tym plikiem. Ręczne dopiski nie stają się częścią źródła konfiguracji.

## 6. Jak to łączy się z DevOps?

Terraform z LAB 10 opisuje zasoby infrastruktury. Ansible może konfigurować systemy, użytkowników, pakiety i pliki na przygotowanych maszynach. Kubernetes zarządza uruchomieniem kontenerów. Każde narzędzie wymaga ustalenia, którymi zasobami ma zarządzać.

Na realnym serwerze dopisałbyś host i użytkownika SSH do inventory, zweryfikował klucz hosta i dopiero wtedy rozszerzał playbook. Nie wpisuj haseł do publicznego inventory. To lokalne ćwiczenie nie instaluje Docker ani Nginx na Twoim serwerze.

**Zaliczenie:** dwa przebiegi, drugi bez zmian, potem wykrycie i naprawa dopisku. Zapisz `docs/ANSIBLE-16.md`. Zakończ środowisko poleceniem `deactivate`. Katalog ćwiczenia możesz zachować jako dowód.

[Moduł copy](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html) · [Moduł file](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/file_module.html)
