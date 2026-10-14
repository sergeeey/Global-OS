# CLEAN_INSTALL — wheel + schema resolve

**Tip at proof:** `fcc6a70` (packaging fix)  
**Machine proof:** `CLEAN_INSTALL_PROOF.json`

## What failed before

Clean `pip install` of the wheel could not resolve JSON Schema contracts: schemas lived only under repo `contracts/schemas`, so `validate()` raised `FileNotFoundError` outside a checkout.

## Fix

1. `pyproject.toml` — hatch `force-include` maps `contracts/schemas` → `global_os/contracts/schemas` in the wheel.  
2. `src/global_os/contracts/validate.py` — `_find_schemas_dir()` prefers packaged schemas, then repo checkout.

## Agent-run procedure (this environment)

```text
python3 -m build --wheel -o /tmp/gos-clean-rc2/dist
python3 -m pip install --target /tmp/gos-clean-rc2/site <wheel>
PYTHONPATH=/tmp/gos-clean-rc2/site python3 -c "from global_os.contracts.validate import SCHEMAS_DIR; ..."
# → 29 *.schema.json under site-packages
PYTHONPATH=... python3 -c "from global_os.cli import main; sys.argv=['gos','mission','start','--help']; main()"
# → exit 0
```

Note: `--target` used because this image lacked `ensurepip`/venv for a full isolated venv; schemas and CLI still resolve from the installed tree.

## Honesty

Agent-validated clean install ≠ second-human machine confirmation. Human gate still owns final install walkthrough (`OPERATOR.md`).
