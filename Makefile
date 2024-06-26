###########################
# Start template makefile #
###########################

SRC_PATH = memorymarker
MAKEFLAGS = --no-print-directory

# Dependency management
install:
	rye sync

quicksync:
	rye sync --no-lock

test:
	rye test

test-with-coverage: 
	@echo "––– Testing –––"
	@make test
	@rye run diff-cover .coverage.xml
	@echo "✅✅✅ Tests passed ✅✅✅"

lint: ## Format code
	@echo "––– Linting –––"
	@rye run ruff format .
	@rye run ruff . --fix --unsafe-fixes
	@echo "✅✅✅ Lint ✅✅✅"

types: ## Type-check code
	@echo "––– Type-checking –––"
	@rye run pyright .
	@echo "✅✅✅ Types ✅✅✅"

validate_ci: ## Run all checks
	@echo "––– Running all checks –––"
	@make lint
	@make types
	## CI doesn't support local coverage report, so skipping full test
	@make test

docker_ci: ## Run all checks in docker
	@echo "––– Running all checks in docker –––"
	docker build -t memorymarker_ci -f .github/Dockerfile.dev .
	docker run --env-file .env memorymarker_ci make validate_ci

#########################
# End template makefile #
#########################

docker-smoketest:
	cp compose.sample.yml compose.smoketest.yml
	perl -pi -e 's#YOUR_OUTPUT_DIR#./smoketest_output#' compose.smoketest.yml

	cp .env .env.smoketest
	echo "MAX_N=1" >> .env.smoketest
	echo "LOG_LEVEL=DEBUG" >> .env.smoketest

	docker build . -t ghcr.io/martinbernstorff/memorymarker:latest
	docker compose -f compose.smoketest.yml --env-file .env.smoketest up

update-snapshots:
	@rye run pytest --snapshot-update
