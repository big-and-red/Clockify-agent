# Clockify Agent Makefile

.PHONY: help install test test-verbose test-coverage run clean lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  install         - Install dependencies"
	@echo "  install-coverage- Install coverage dependencies"
	@echo "  test            - Run tests"
	@echo "  test-verbose    - Run tests with verbose output"
	@echo "  test-coverage   - Run tests with coverage report"
	@echo "  run             - Run the application"
	@echo "  clean           - Clean cache and temporary files"
	@echo "  lint            - Run linting"
	@echo "  format          - Format code"

# Install dependencies
install:
	pip3 install -r requirements.txt

# Install coverage dependencies
install-coverage:
	pip3 install pytest-cov

# Run tests
test:
	python3 -m pytest tests/ -v

# Run tests with verbose output
test-verbose:
	python3 -m pytest tests/ -v -s

# Run tests with coverage
test-coverage:
	@echo "Checking if pytest-cov is installed..."
	@python3 -c "import pytest_cov" 2>/dev/null || (echo "Installing pytest-cov..." && pip3 install pytest-cov)
	python3 -m pytest tests/ --cov=app --cov-report=html --cov-report=term

# Run the application
run:
	python run.py

# Clean cache and temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

# Run linting (if you have flake8 or similar)
lint:
	@echo "Running linting..."
	@python3 -m flake8 app/ tests/ || echo "flake8 not installed, skipping linting"

# Format code (if you have black)
format:
	@echo "Formatting code..."
	@python3 -m black app/ tests/ || echo "black not installed, skipping formatting"

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	@cp .env.example .env || echo ".env.example not found"
	@echo "Please edit .env file with your Clockify API credentials"

# Quick test (only basic tests)
test-quick:
	python -m pytest tests/test_basic.py -v

# Test specific file
test-file:
	@echo "Usage: make test-file FILE=tests/test_basic.py"
	python -m pytest $(FILE) -v

# Run with specific Python version
test-python3:
	python3 -m pytest tests/ -v

# Install test dependencies
install-test:
	pip3 install pytest pytest-asyncio pytest-httpx pytest-cov

# Full test suite with all checks
test-full: clean test-coverage lint
	@echo "Full test suite completed"
