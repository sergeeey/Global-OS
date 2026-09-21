.PHONY: lint test schemas check

schemas:
	python -m tools.validate_schemas

lint:
	ruff check src tests tools
	mypy

test:
	pytest -q

check: schemas lint test
