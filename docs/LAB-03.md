# LAB 03 — Nginx reverse proxy i zasada jednego punktu wejścia

[Spis wszystkich działów](COURSE.md) · [Proste wyjaśnienia tego działu](OD-ZERA.md#lab-03)


**Cel:** udostępniać API jedynie przez reverse proxy, pracować z portami, HTTP i awarią 502.

## 1. Zanim zaczniesz

Utwórz branch:

```bash
git switch -c lab/03-nginx-proxy
mkdir -p nginx
```

Narysuj żądanie: `curl → port 8080 hosta → Nginx:80 → api:8000 → db:5432`.

## 2. Utwórz `nginx/default.conf`

Poniżej wersja bazowa. Przeczytaj znaczenie każdego `proxy_set_header`:

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 3. Edytuj `compose.yaml`

Pod `services:` dodaj nowy serwis (`proxy`) na tym samym poziomie co `api` i `db`:

```yaml
  proxy:
    image: nginx:stable-alpine
    ports:
      - '127.0.0.1:8080:80'
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      api:
        condition: service_healthy
    restart: unless-stopped
```

**Ważne:** z serwisu `api` usuń cały blok `ports:`. Dzięki temu aplikacja nadal działa wewnątrz sieci Compose, ale nie jest bezpośrednio opublikowana na porcie hosta. Nie musisz dodawać `expose` — kontenery w sieci Compose mogą kontaktować się na porcie, na którym aplikacja nasłuchuje.

Nie zmieniaj `DATABASE_URL` (`db` musi pozostać nazwą hosta bazy). Na tym etapie Nginx udostępnia lokalnie **HTTP**, nie HTTPS.

## 4. Uruchom i sprawdź

```bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
curl -i http://localhost:8080/health
curl -i http://localhost:8080/ready
BASE_URL=http://localhost:8080 bash scripts/smoke-test.sh
bash scripts/check-lab-03.sh
```

- Otwórz `http://localhost:8080/docs`.
- Stary `http://localhost:8000/health` nie powinien odpowiadać **przez ten stack** (chyba że inny lokalny proces sam nasłuchuje na 8000).
- Sprawdź odpowiedzi Nginx: `docker compose logs --tail=50 proxy`.

## 5. Kontrolowana awaria 502

```bash
docker compose stop api
curl -i http://localhost:8080/health
docker compose logs --tail=50 proxy
docker compose start api
curl -i http://localhost:8080/health
```

Po zatrzymaniu API, Nginx powinien zwrócić błąd bramy (zwykle **502 Bad Gateway**). Jeśli API dopiero się uruchamia, ponów test po `docker compose ps`; nie zakładaj automatycznego przywrócenia działania w pierwszej sekundzie. Nginx może wymagać restartu/reloadu, jeśli API zostanie **odtworzone** z innym IP.

## 6. Własny runbook

Stwórz `docs/POSTMORTEM-03.md`: objaw (HTTP 502), jak zdiagnozowałeś, przyczyna, naprawa, weryfikacja.

## Kryteria zaliczenia

- `http://localhost:8080/docs` i `/ready` działają.
- `docker compose ps` pokazuje 3 serwisy: `db`, `api`, `proxy`.
- API **nie ma** opublikowanego portu hosta.
- Umiesz wyjaśnić różnicę między **502** a **503**.
- `bash scripts/check-lab-03.sh` kończy się `PASS`.
- Commit: `feat(proxy): route HTTP traffic through nginx`.

**Bonus:** dodaj `location /nginx-health { return 200 'nginx alive'; }` i sprawdź, czy działa nawet przy zatrzymanym API. Sprawdź, czy konfiguracja ma poprawną składnię: `docker compose exec proxy nginx -t`.
