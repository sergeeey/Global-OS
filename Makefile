.PHONY: lint test schemas pins status check preflight-48h perf-bench

perf-bench:
	PYTHONPATH=src python3 tools/perf_bench.py --out artifacts/perf/latest.json \
		--compare artifacts/perf/baseline_pre_opt.json

schemas:
	python3 -m tools.validate_schemas

pins:
	python3 -m tools.validate_action_pins

status:
	python3 -m tools.project_status

lint:
	ruff check src tests tools
	mypy

test:
	pytest -q

# Compressed long-horizon research program preflight (≠ wall-clock 48h; ≠ M1.5 claim)
preflight-48h:
	python3 artifacts/hardening/run_48h_preflight.py

check: schemas pins lint test status
