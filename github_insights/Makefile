# Cardano Insights Makefile

.PHONY: help install run-github run-dbt test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e .[test]

run-github: ## Run GitHub data pipeline
	python src/cardano_insights/github_pipeline.py

run-github-sample: ## Run GitHub pipeline with sample data (limited records)
	python src/cardano_insights/github_pipeline.py --max-prs 50 --max-releases 20 --max-issues 30

run-dbt: ## Run dbt models
	dbt run

run-dbt-test: ## Run dbt tests
	dbt test

run-pipeline: ## Run complete pipeline (GitHub + dbt)
	make run-github && make run-dbt

test: ## Run tests
	pytest tests/ -v

test-connectors: ## Run connector tests only
	pytest tests/connectors/ -v

clean: ## Clean up generated files
	rm -rf target/
	rm -rf .dlt/.pipeline/
	rm -f github_cardano.duckdb*
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

lint: ## Run code linting
	ruff check src/ tests/

format: ## Format code
	ruff format src/ tests/

docs: ## Generate dbt documentation
	dbt docs generate
	dbt docs serve

export: ## Export data to parquet files
	python scripts/export_data.py