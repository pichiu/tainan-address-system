# 臺南市門牌坐標查詢系統 - Backend Makefile

.PHONY: help install install-dev run test lint format check clean migration upgrade downgrade

# 預設目標
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  run          - Run the development server"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (flake8, mypy)"
	@echo "  format       - Format code (black, isort)"
	@echo "  check        - Run all checks (lint + format check)"
	@echo "  clean        - Clean cache and temp files"
	@echo "  migration    - Create new migration"
	@echo "  upgrade      - Apply database migrations"
	@echo "  downgrade    - Rollback database migrations"

# 安裝依賴
install:
	uv sync --no-dev

install-dev:
	uv sync

# 執行開發服務器
run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 測試
test:
	uv run pytest

test-cov:
	uv run pytest --cov=app --cov-report=html --cov-report=term

# 程式碼品質
lint:
	uv run flake8 app
	uv run mypy app

format:
	uv run black app
	uv run isort app

format-check:
	uv run black --check app
	uv run isort --check-only app

check: format-check lint test

# 清理
clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/

# 資料庫遷移
migration:
	uv run alembic revision --autogenerate -m "$(message)"

upgrade:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1

# 資料匯入
import-data:
	uv run python -m app.utils.data_import $(file) $(args)

# 開發環境設置
dev-setup: install-dev
	uv run pre-commit install

# 生產環境準備
prod-build: clean install format-check lint test
	@echo "Production build completed successfully"

# Docker 相關 (如果使用)
docker-build:
	docker build -t tainan-address-backend .

docker-run:
	docker run -p 8000:8000 tainan-address-backend

# 健康檢查
health:
	curl -f http://localhost:8000/api/v1/health/ || exit 1