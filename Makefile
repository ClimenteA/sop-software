re:
	docker compose up -d --force-recreate app

up:
	docker compose up -d --force-recreate

down:
	docker compose down

down-v:
	docker compose down -v

logs:
	docker compose logs -f app

proxy:
	docker compose up -d --force-recreate proxy

logs-proxy:
	docker compose logs -f proxy

build:
	docker compose build

exec:
	docker compose exec app bash

test:
	pytest ./tests/*
