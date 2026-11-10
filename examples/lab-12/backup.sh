#!/usr/bin/env bash
# Uruchom: bash backup.sh /pelna/sciezka/nowy-katalog
set -euo pipefail
umask 077
context=kind-incidentflow-lab08
[[ $(kubectl config current-context) == "$context" ]] || {
  echo 'Ustaw KUBECONFIG klastra z LAB 08.' >&2; exit 1;
}
[[ $# == 1 ]] || { echo 'Podaj nowy katalog na kopię.' >&2; exit 1; }
mkdir -- "$1" # Odmowa, jeżeli katalog już istnieje; nie nadpisujemy kopii.
archive="$1/incidentflow.dump"
trap 'rm -f -- "$archive.partial"' EXIT
kubectl --context="$context" -n incidentflow exec db-0 -c postgres -- \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl' > "$archive.partial"
test -s "$archive.partial"
mv -- "$archive.partial" "$archive"
(cd -- "$1" && sha256sum incidentflow.dump > SHA256SUMS)
printf 'Zapisano kopię: %s\n' "$archive"
