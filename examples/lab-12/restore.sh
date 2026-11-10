#!/usr/bin/env bash
# Uruchom: bash restore.sh /pelna/sciezka/katalog-kopii lab12_restore_1
set -euo pipefail
context=kind-incidentflow-lab08
[[ $(kubectl config current-context) == "$context" ]] || {
  echo 'Ustaw KUBECONFIG klastra z LAB 08.' >&2; exit 1;
}
[[ $# == 2 ]] || { echo 'Podaj katalog kopii oraz nazwę lab12_restore_NUMER.' >&2; exit 1; }
[[ $2 =~ ^lab12_restore_[0-9]+$ ]] || { echo 'Niedozwolona nazwa bazy testowej.' >&2; exit 1; }
(cd -- "$1" && sha256sum --check SHA256SUMS)
# Sprawdź, czy PostgreSQL umie przeczytać archiwum, zanim utworzysz bazę.
kubectl --context="$context" -n incidentflow exec -i db-0 -c postgres -- \
  pg_restore --list < "$1/incidentflow.dump" > /dev/null
# createdb odmawia, jeśli baza już istnieje. Skrypt wtedy się zatrzymuje.
kubectl --context="$context" -n incidentflow exec db-0 -c postgres -- \
  sh -c 'createdb -U "$POSTGRES_USER" --template=template0 "$1"' sh "$2"
kubectl --context="$context" -n incidentflow exec -i db-0 -c postgres -- \
  sh -c 'pg_restore -U "$POSTGRES_USER" --dbname="$1" --no-owner --no-acl --single-transaction --exit-on-error' sh "$2" < "$1/incidentflow.dump"
printf 'Odtworzono bazę testową: %s\n' "$2"
