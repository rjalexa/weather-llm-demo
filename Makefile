.PHONY: help install run dev test clean docker-build docker-run

help:
	@echo "Weather LLM Demo - UV Commands"
	@echo "=============================="
	@echo "make install    - Install dependencies with uv"
	@echo "make run        - Run the application"
	@echo "make dev        - Run in development mode with auto-reload"
	@echo "make test       - Run tests"
	@echo "make clean      - Clean cache and temporary files"
	@echo "make docker-build - Build Docker image"
	@echo "make docker-run - Run with Docker Compose"

install:
	uv sync

run:
	uv run python -m weather_llm_demo.main

dev:
	uv run uvicorn weather_llm_demo.main:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .ruff_cache

docker-build:
	docker build -f Dockerfile -t weather-llm-demo .

docker-run:
	docker-compose -f docker-compose.yml up

docker-down:
	docker-compose -f docker-compose.yml down
