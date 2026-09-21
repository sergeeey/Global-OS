.PHONY: lint test schemas pins status check

schemas:
	python -m tools.validate_schemas

pins:
	python -m tools.validate_action_pins

status:
	python -m tools.project_status

lint:
	ruff check src tests tools
	mypy

test:
	pytest -q

check: schemas pins lint test status
