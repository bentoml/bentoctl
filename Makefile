SHELL := /bin/bash
.DEFAULT_GOAL := help

GIT_ROOT ?= $(shell git rev-parse --show-toplevel)

help: ## Show all Makefile targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'

format: ## Running code formatter: black and isort
	black --config ./pyproject.toml bentoctl tests
	isort .
lint: ## Running lint checker: pylint
	pylint --rcfile=.pylintrc bentoctl tests
