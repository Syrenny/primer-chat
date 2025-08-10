PROJECT ?= primer-chat
COMPOSE := docker compose -p $(PROJECT)
FILES := -f docker/compose.infra.yaml -f docker/compose.logging.yaml -f docker/compose.yaml
FILES_INFRA := -f docker/compose.infra.yaml

# --- Full stack (infra + app + logging) ---

up:
	$(COMPOSE) $(FILES) --env-file docker/.env up -d --build

down:
	$(COMPOSE) $(FILES) down --remove-orphans

ps:
	$(COMPOSE) $(FILES) ps

logs:
	$(COMPOSE) $(FILES) logs -f --tail=100 $(service)

# --- Infra only (infra) ---

up-infra:
	$(COMPOSE) $(FILES_INFRA) --env-file docker/.env up -d --build

down-infra:
	$(COMPOSE) $(FILES_INFRA) down --remove-orphans

ps-infra:
	$(COMPOSE) $(FILES_INFRA) ps

logs-infra:
	# pass SERVICE=name to tail a single infra service
	$(COMPOSE) $(FILES_INFRA) logs -f --tail=100 $(SERVICE)

# --- Database cleanup ---
postgres-clean:
	@echo "Removing Postgres data volume..."
	docker volume rm $(PROJECT)_postgres-data || true

.PHONY: up down ps logs up-infra down-infra ps-infra logs-infra
