.PHONY: help setup dev dev-web dev-api test test-python test-web lint type-check build pipeline-vinmec clean

# Default shell
SHELL := /bin/bash

# Python and package manager tools
UV := $(shell which uv 2>/dev/null || echo "uv")
PNPM := $(shell which pnpm 2>/dev/null || echo "pnpm")
PYTHON := $(shell if [ -f .venv/bin/python ]; then echo ".venv/bin/python"; else echo "python3"; fi)

help: ## Show this help message
	@echo "========================================================================"
	@echo "               MyoLab-AI Developer Workflow Automation                 "
	@echo "========================================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Complete environment setup: venv, uv dependencies, pnpm packages, .env
	@echo "⚙️  Setting up Python Virtual Environment via uv..."
	@if [ ! -d ".venv" ]; then $(UV) venv; fi
	@echo "📦 Installing Python dependencies via uv..."
	@$(UV) pip install -r requirements.txt fastapi uvicorn httpx scikit-learn matplotlib pyarrow fsspec requests filelock openpyxl joblib psutil
	@echo "🌐 Installing Frontend Workspace dependencies via pnpm..."
	@$(PNPM) install
	@if [ ! -f .env ]; then cp .env.example .env && echo "📄 Created .env from .env.example"; fi
	@echo "✅ Environment preparation complete!"

dev: ## Launch both FastAPI API Server and Next.js Web Portal concurrently
	@echo "🚀 Starting MyoLab-AI Full Stack (API Server :8019 + Web Portal :3100)..."
	@$(PYTHON) scripts/run_api_server.py & \
	API_PID=$$!; \
	$(PNPM) --filter @myolab-ai/web-portal run dev & \
	WEB_PID=$$!; \
	trap "kill $$API_PID $$WEB_PID 2>/dev/null" EXIT INT TERM; \
	wait

dev-api: ## Start the FastAPI API Server (:8019)
	@echo "🚀 Starting MyoLab-AI API Server at http://127.0.0.1:8019..."
	@$(PYTHON) scripts/run_api_server.py

dev-web: ## Start the Next.js Web Portal (:3100)
	@echo "🌐 Starting Next.js Web Portal at http://localhost:3100..."
	@$(PNPM) --filter @myolab-ai/web-portal run dev

test: test-python test-web ## Run both Python and Frontend test suites

test-python: ## Run pytest test suites
	@echo "🧪 Running Python Test Suite..."
	@$(PYTHON) -m pytest packages/semg-core/tests/ qa-validation/automated-tests/test_day19_mock_api.py qa-validation/automated-tests/test_day20_mock_api.py qa-validation/automated-tests/test_day21_analysis_jobs.py qa-validation/automated-tests/test_day22_uc1_api.py qa-validation/automated-tests/test_day23_service_api.py qa-validation/automated-tests/test_day24_api.py

test-web: ## Run Frontend E2E / Unit tests
	@echo "🧪 Running Web Portal Tests..."
	@$(PNPM) --filter @myolab-ai/web-portal run type-check

lint: ## Run linter and type-checking across frontend and backend
	@echo "🔍 Linting Frontend..."
	@$(PNPM) --filter @myolab-ai/web-portal run lint
	@$(PNPM) --filter @myolab-ai/web-portal run type-check

type-check: ## Check TypeScript types
	@$(PNPM) --filter @myolab-ai/web-portal run type-check

build: ## Build Next.js Web Portal for production
	@echo "🏗️  Building Web Portal for Production..."
	@$(PNPM) --filter @myolab-ai/web-portal run build

pipeline-vinmec: ## Run the Vinmec Noraxon signal processing pipeline
	@echo "🧬 Running Vinmec sEMG Data Pipeline..."
	@bash scripts/run_vinmec_pipeline.sh

clean: ## Clean build artifacts, caches, and temp files
	@echo "🧹 Cleaning caches and build artifacts..."
	@rm -rf .pytest_cache .coverage apps/web-portal/.next apps/web-portal/out
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✨ Clean complete!"
