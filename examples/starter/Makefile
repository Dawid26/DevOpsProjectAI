.PHONY: up down ps logs test smoke config clean
up:
	docker compose up -d --build

ps:
	docker compose ps

logs:
	docker compose logs -f --tail=100

down:
	docker compose down

config:
	docker compose config

smoke:
	bash scripts/smoke-test.sh

test:
	PYTHONPATH=api python -m pytest -q

# USUWA DANE Z BAZY. Używaj tylko w środowisku testowym.
clean:
	docker compose down -v
