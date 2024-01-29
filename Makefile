SRC_PATH = memorymarker
MAKEFLAGS = --no-print-directory

# Dependency management
install:
	pip install --upgrade -e .[dev]

# Tasks
generate_coverage:
	@pytest --cov=$(SRC_PATH) $(SRC_PATH) --cov-report xml:.coverage.xml --cov-report lcov:.coverage.lcov

test: ## Run tests
	@echo "––– Testing –––"
	@make generate_coverage
	@diff-cover .coverage.xml
	@echo "✅✅✅ Tests passed ✅✅✅"

lint: ## Format code
	@echo "––– Linting –––"
	@ruff format . 
	@ruff . --fix \
		--extend-select F401 \
		--extend-select F841
	@echo "✅✅✅ Lint ✅✅✅"

types: ## Type-check code
	@echo "––– Type-checking –––"
	@pyright $(SRC_PATH)
	@echo "✅✅✅ Types ✅✅✅"

validate: ## Run all checks
	@echo "––– Running all checks –––"
	@make lint
	@make types
	@make test

validate_ci: ## Run all checks
	@echo "––– Running all checks –––"
	@make lint
	@make types
## CI doesn't support local coverage report, so skipping full tests
	@make generate_coverage 