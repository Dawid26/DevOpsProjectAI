# LAB 02 — Linux, DNS i sieć kontenerów

**Cel:** samodzielnie znaleźć drogę komunikacji `host → api → db`, rozróżnić port hosta od portu kontenera, poznać DNS i błędy połączeń. Poziom: podstawowy / średni.

## 0. Punkt startowy

```bash
# W katalogu projektu, po LAB 01
docker compose up -d --build
docker compose ps
curl -i http://localhost:8000/ready
```

Jeśli `/ready` nie zwraca 200, zacznij od `docker compose logs --tail=100 api db`.

## 1. Odkryj sieć

```bash
docker network ls
docker network inspect incidentflow_default
docker compose ps
docker compose exec api python -c 'import socket; print("db:", socket.gethostbyname("db"))'
docker compose exec api python -c 'import socket; print("api:", socket.gethostbyname("api"))'
```

Wpisz do `docs/NETWORKING.md`:

- Nazwa sieci Compose, jej driver i subnet.
- IP usług w tej sieci. Dlaczego nie należy wpisywać tych adresów na stałe do konfiguracji?
- Jaka jest różnica między `127.0.0.1:8000:8000` a `db:5432`?

**Podpowiedź:** W Compose serwis `db` jest rozpoznawany po nazwie poprzez wewnętrzny DNS Dockera.

## 2. Sprawdź port PostgreSQL z wnętrza API

```bash
docker compose exec api python -c 'import socket; s=socket.create_connection(("db", 5432),3); print("db:5432 OK"); s.close()'
```

Teraz sam spróbuj zmienić `db` na `127.0.0.1` w powyższej **komendzie testowej** (nie zmieniaj konfiguracji produkcyjnej). Przewidź wynik, a potem sprawdź. Dlaczego to inne miejsce?

## 3. Kontrolowany błąd DNS

```bash
docker compose exec api python -c 'import socket; print(socket.gethostbyname("nie-ma-takiego-serwisu"))'
```

Ten test **powinien zakończyć się błędem** — to część laboratorium. Zapisz jego nazwę, diagnozę oraz właściwy test (`db`).

## 4. Linux i HTTP

```bash
ip addr
ip route
ss -lnt
curl -i http://localhost:8000/health
curl -i http://localhost:8000/incidents
```

W WSL i Docker Desktop `ss` nie musi pokazać wszystkich portów przekierowanych przez Docker Desktop; do mapowania użyj `docker compose ps`. Zwróć uwagę na kody odpowiedzi HTTP, adresy i porty.

## 5. Automatyczna kontrola

```bash
bash scripts/check-lab-02.sh
```

## Kryteria zaliczenia

- Potrafisz wyjaśnić **localhost wewnątrz kontenera** oraz `db:5432`.
- W `docs/NETWORKING.md` jest krótki diagram tekstowy sieci, 3 odpowiedzi i opis błędu DNS.
- `bash scripts/check-lab-02.sh` kończy się `PASS`.
- Commit: `docs(lab02): describe compose DNS and networking`.

**Bonus:** porównaj `docker compose exec api ...` z `docker compose run --rm api ...` (różnice w tworzeniu nowego kontenera).
