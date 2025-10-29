.PHONY: help install install-dev test lint format clean build upload docs check generate-client

help:
	@echo "Available commands:"
	@echo "  install      Install package"
	@echo "  install-dev  Install package with development dependencies"
	@echo "  test         Run all tests"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-client  Run generated client tests only"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  test-watch   Run tests in watch mode"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with ruff"
	@echo "  check        Run all checks (lint + format check + type check)"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build distribution packages"
	@echo "  upload       Upload to PyPI (requires credentials)"
	@echo "  docs         Generate documentation"
	@echo "  generate-client  Generate API client from OpenAPI spec"

install:
	@if [ ! -d ".venv" ]; then \
		echo "🔄 Creating virtual environment..."; \
		uv venv; \
	fi
	uv sync
	uv pip install -e .
	@echo "✅ Installation complete!"
	@echo "💡 To activate the virtual environment, run: source .venv/bin/activate"
	@echo "   Or use 'uv run workato' to run commands without activation"

install-dev:
	@if [ ! -d ".venv" ]; then \
		echo "🔄 Creating virtual environment..."; \
		uv venv; \
	fi
	uv sync --group dev
	uv run pre-commit install

test:
	uv run pytest tests/ -v

test-unit:
	uv run pytest tests/unit/ -v

test-integration:
	uv run pytest tests/integration/ -v

test-client:
	uv run pytest src/workato_platform_cli/client/workato_api/test/ -v

test-cov:
	uv run pytest tests/ --cov=src/workato_platform_cli --cov-report=html --cov-report=term --cov-report=xml

test-watch:
	uv run pytest tests/ -v --tb=short -x --lf

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

check:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/
	uv run mypy --explicit-package-bases src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	twine check dist/*
	twine upload dist/*

docs:
	@echo "Documentation generation not yet implemented"
	@echo "Consider using sphinx-quickstart to set up docs/"

generate-client:
	@echo "🔄 Generating API client from OpenAPI spec..."
	openapi-generator-cli generate -i workato-api-spec.yaml -g python -c openapi-config.yaml -o ./src/
	@echo "✅ API client generated successfully"

# Development shortcuts
dev: install-dev format check test

# CI/CD command
ci: check test
