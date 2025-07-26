up:
	docker compose -f docker/compose.infra.yaml --env-file docker/infra.env up -d
	docker compose -f docker/compose.logging.yaml \
	               -f docker/compose.yaml \
	               up -d --build

down:
	docker compose -f docker/compose.logging.yaml \
	               -f docker/compose.infra.yaml \
	               -f docker/compose.yaml \
	               down
