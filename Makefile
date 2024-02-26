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
	@rye run pytest --cov=$(SRC_PATH) $(SRC_PATH) --cov-report xml:.coverage.xml --cov-report lcov:.coverage.lcov --testmon

test-with-coverage: 
	@echo "––– Testing –––"
	@make test
	@rye run diff-cover .coverage.xml
	@echo "✅✅✅ Tests passed ✅✅✅"

lint: ## Format code
	@echo "––– Linting –––"
	@rye run ruff format .
	@rye run ruff . --fix --unsafe-fixes \
		--extend-select F401 \
		--extend-select F841
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

pr: ## Submit a PR
	@lumberman sync --squash --automerge

#########################
# End template makefile #
#########################

update-snapshots:
	@pytest --snapshot-update