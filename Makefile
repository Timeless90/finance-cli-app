.DEFAULT_GOAL := help
PYTHON ?= python3
UV ?= uv
PNPM ?= pnpm
BIND_HOST ?= 127.0.0.1
COMPOSE = docker compose --env-file /dev/null -f compose.yml
OBS = otel-collector prometheus tempo loki grafana
.PHONY: init template-test help doctor install dev dev-full backend-dev frontend-dev check test lint format backend-check backend-test backend-lint backend-format frontend-check frontend-test frontend-test-watch frontend-lint frontend-format frontend-build e2e e2e-ui infra-up infra-down infra-logs observability-up observability-down observability-logs containers-up containers-down compose-check api-generate api-check backend-migrate backend-migration-check diff-coverage acceptance
help:
	@echo "make init | install | dev | dev-full | check | e2e | containers-up | acceptance"
	@echo "Development: backend-dev frontend-dev; Infrastructure: infra-up infra-down"
	@echo "Optional telemetry: observability-up observability-down"
	@echo "Run through mise exec -- make <target> to use the pinned runtimes."
init:
	@echo "Already initialized: finance-cli-app"
template-test:
	$(PYTHON) -m unittest discover -s scripts/tests -v
doctor:
	$(PYTHON) scripts/doctor.py
install:
	$(PYTHON) scripts/bootstrap.py
dev:
	$(PYTHON) scripts/dev.py
dev-full:
	$(PYTHON) scripts/dev.py --full
backend-dev:
	cd backend && $(UV) run --locked uvicorn app.main:app --host $(BIND_HOST) --port 8000 --reload --no-access-log
frontend-dev:
	cd frontend && $(PNPM) dev --host $(BIND_HOST)
backend-lint:
	cd backend && $(UV) run --locked ruff check .
	cd backend && $(UV) run --locked ruff format --check .
	cd backend && $(UV) run --locked pyright
backend-format:
	cd backend && $(UV) run --locked ruff check --fix .
	cd backend && $(UV) run --locked ruff format .
backend-test:
	cd backend && $(UV) run --locked pytest --cov=app --cov=finance_cli --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=80
backend-check: backend-lint backend-test
frontend-lint:
	cd frontend && $(PNPM) typecheck
	cd frontend && $(PNPM) lint
	cd frontend && $(PNPM) format:check
frontend-format:
	cd frontend && $(PNPM) format
frontend-test:
	cd frontend && $(PNPM) test
frontend-test-watch:
	cd frontend && $(PNPM) test:watch
frontend-check: frontend-lint frontend-test
frontend-build:
	cd frontend && $(PNPM) build
lint: backend-lint frontend-lint
format: backend-format frontend-format
test: backend-test frontend-test
check: template-test backend-check frontend-check api-check diff-coverage
	cd backend && $(UV) run --locked python ../scripts/validate_config.py
api-generate:
	cd backend && $(UV) run --locked python ../scripts/export_openapi.py
	cd frontend && $(PNPM) api:generate
api-check:
	$(PYTHON) scripts/check_api.py
diff-coverage:
	$(PYTHON) scripts/diff_coverage.py
infra-up:
	@if [ "$$TEMPLATE_INFRA_MANAGED" != "1" ]; then $(COMPOSE) up -d --wait postgres; fi
infra-down:
	$(COMPOSE) stop postgres
infra-logs:
	$(COMPOSE) logs --tail=100 -f postgres
observability-up:
	$(COMPOSE) -f compose.observability.yml up -d $(OBS)
observability-down:
	$(COMPOSE) -f compose.observability.yml stop $(OBS)
observability-logs:
	$(COMPOSE) -f compose.observability.yml logs --tail=100 -f $(OBS)
containers-up:
	$(COMPOSE) -f compose.app.yml up -d --build --wait
containers-down:
	$(COMPOSE) -f compose.app.yml stop
compose-check:
	$(COMPOSE) -f compose.app.yml -f compose.observability.yml config --quiet
backend-migrate:
	cd backend && $(UV) run --locked python ../scripts/database.py init
backend-migration-check:
	cd backend && $(UV) run --locked python ../scripts/database.py check
e2e: infra-up
	cd frontend && $(PNPM) e2e
e2e-ui: infra-up
	cd frontend && $(PNPM) e2e:ui
acceptance:
	$(PYTHON) scripts/acceptance.py

.PHONY: extensions
extensions:
	$(PYTHON) scripts/install_extensions.py

.PHONY: frontend-local cli
frontend-local:
	cd frontend && $(PNPM) dev:local --host $(BIND_HOST)
cli:
	cd backend && $(UV) run --locked finance-cli $(ARGS)

.PHONY: e2e-live dev-mock
e2e-live: infra-up
	cd backend && $(UV) run --locked python ../scripts/e2e_live.py
dev-mock:
	cd frontend && VITE_API_MODE=mock $(PNPM) dev
