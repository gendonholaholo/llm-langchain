.DEFAULT_GOAL := help
COMPOSE := docker compose
APP     := app-llm-langchain-development

.PHONY: help build up down restart logs logs-app \
        migrate seed test lint shell db-shell health clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.env: ## Copy .env.example to .env (if missing)
	cp -n .env.example .env

build: ## Build Docker images
	$(COMPOSE) build

up: .env ## Start all services (detached)
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

restart: down up ## Restart all services

logs: ## Tail logs for all services
	$(COMPOSE) logs -f

logs-app: ## Tail logs for app service only
	$(COMPOSE) logs -f app

migrate: ## Run Alembic migrations in app container
	docker exec $(APP) alembic upgrade head

seed: ## Seed knowledge base from data/knowledge/
	docker exec $(APP) python scripts/seed_knowledge.py

test: ## Run pytest in app container
	docker exec $(APP) python -m pytest -v

lint: ## Run ruff linter in app container
	docker exec $(APP) python -m ruff check src/ tests/

shell: ## Open a shell in the app container
	docker exec -it $(APP) bash

db-shell: ## Open psql shell in the postgres container
	docker exec -it postgres-llm-langchain-development psql -U postgres -d whatsapp_bot

health: ## Check app health endpoint
	@curl -sf http://localhost:8000/health | python3 -m json.tool || echo "Health check failed"

clean: ## Stop services, remove volumes and local images
	$(COMPOSE) down -v --rmi local
