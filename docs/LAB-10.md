# LAB 10 — Terraform od pierwszego planu do przygotowania AWS

Terraform pozwala opisać oczekiwany stan w plikach. Polecenie plan pokazuje proponowane zmiany, a apply je wykonuje. State zapisuje informacje o zasobach zarządzanych przez dany katalog konfiguracji.

Najpierw przećwiczysz ten mechanizm lokalnie, na danych planu wdrożenia IncidentFlow. Następnie obejrzysz osobną konfigurację sieci AWS.

**1. Przygotuj pliki**

Zainstaluj Terraform według [instrukcji HashiCorp](https://developer.hashicorp.com/terraform/install). Użyj wersji co najmniej 1.4. W terminalu Ubuntu/WSL:

```bash
terraform version
export LAB_SOURCE=/home/twoj-login/DevOpsProjectAI
mkdir -p ~/incidentflow-iac
cp -Ri "$LAB_SOURCE/examples/lab-10/"* ~/incidentflow-iac/
cp -i "$LAB_SOURCE/examples/lab-10/.gitignore" ~/incidentflow-iac/
cd ~/incidentflow-iac/local
```

Podmień LAB_SOURCE na ścieżkę Twojego klonu. Folder local zawiera przykład korzystający z wbudowanego zasobu terraform_data. Przechowuje on opis w stanie Terraform. Liczba replik w tym przykładzie jest daną do nauki; rzeczywisty Deployment Kubernetes zmieniasz osobno.

**2. Przeczytaj main.tf**

Blok terraform ustala wersję narzędzia. Zmienna api_replicas przyjmuje liczbę całkowitą od 1 do 3. Blok resource opisuje dane projektu, a output wybiera wynik, który będzie można odczytać po zastosowaniu planu.

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=first.tfplan
terraform show first.tfplan
```

Init przygotowuje katalog. Validate sprawdza konfigurację, a plan porównuje ją ze stanem. W pierwszym planie powinien pojawić się jeden zasób do dodania.

**3. Zastosuj lokalny plan i odczytaj stan**

```bash
terraform apply first.tfplan
terraform output deployment_plan
terraform state list
terraform plan
```

Po zastosowaniu zobaczysz dane projektu i api_replicas równe 1. Ponowny plan powinien poinformować o braku zmian. Plik terraform.tfstate jest pamięcią Terraform o wykonanej operacji.

**4. Zmień liczbę i przewidź wynik**

```bash
terraform plan -var='api_replicas=2' -out=second.tfplan
terraform show second.tfplan
terraform apply second.tfplan
terraform output deployment_plan
terraform plan -var='api_replicas=2'
```

Plan pokaże zmianę danych zasobu, a wynik po apply będzie zawierał 2. Za każdym razem używaj tej samej wartości zmiennej, jeśli chcesz utrzymać ten stan. Zwykły plan bez -var wróci do wartości domyślnej 1 i zaproponuje kolejną zmianę.

Sprawdź walidację:

```bash
terraform plan -var='api_replicas=0'
```

Oczekiwany wynik to błąd z wyjaśnieniem zakresu 1–3. Ta operacja nie zmieni wcześniej zapisanego stanu.

**5. Zrozum state i plik blokady**

State może zawierać dane wrażliwe pochodzące z rzeczywistej infrastruktury. Dodany .gitignore wyklucza state, plany i katalog .terraform. Plik .terraform.lock.hcl, gdy powstanie przy instalacji providerów, warto zapisać w Git, aby zachować wybrane wersje.

Utwórz docs/TERRAFORM-10.md. Zapisz różnicę między plan i apply oraz wyniki dla wartości 1, 2 i 0.

**6. Opcjonalnie przygotuj plan sieci AWS**

Folder aws-plan zawiera provider AWS i jedną VPC z zakresem 10.42.0.0/16. VPC to wydzielona sieć w chmurze. Ta część wymaga własnego konta AWS i poświadczeń skonfigurowanych zgodnie z [dokumentacją providera](https://registry.terraform.io/providers/hashicorp/aws/latest/docs). Poświadczenia przekazuj przez konfigurację AWS lub zmienne środowiskowe.

```bash
cd ../aws-plan
terraform init
terraform fmt -check
terraform validate
terraform plan -out=aws.tfplan
terraform show aws.tfplan
```

Plan powinien pokazać dodanie jednej VPC w eu-central-1. W tym ćwiczeniu kończysz na przejrzeniu planu. Faktyczne utworzenie zasobów przez apply wymaga wcześniejszego ustalenia kosztów, uprawnień i sposobu sprzątania. Zachowaj plan lokalnie.

**7. Przećwicz usunięcie lokalnego zasobu**

Wróć do folderu local i przejrzyj proponowane usunięcie:

```bash
cd ../local
terraform plan -destroy -out=cleanup.tfplan
terraform show cleanup.tfplan
terraform apply cleanup.tfplan
terraform state list
```

Sprawdź w planie nazwę terraform_data.deployment_plan. Usuwasz lokalny zasób ćwiczeniowy. Po operacji lista stanu będzie pusta.

Zaliczenie oznacza odczytanie planów, zastosowanie wartości 1 i 2, sprawdzenie błędnej wartości oraz opis mechanizmu state. Plan AWS jest dodatkiem dla osób z przygotowanym kontem.

[Opis terraform_data](https://developer.hashicorp.com/terraform/language/resources/terraform-data)
