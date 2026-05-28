.PHONY: test lint type cov complexity all run

test:
	pytest -v

cov:
	pytest --cov=src --cov-report=term-missing --cov-report=html

lint:
	ruff check .

type:
	mypy --strict src/

complexity:
	radon cc src/ -s -a

run:
	python -m src.main

all: lint type test cov complexity
