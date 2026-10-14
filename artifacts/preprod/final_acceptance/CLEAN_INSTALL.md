# CLEAN_INSTALL — wheel + runtime assets

**Machine proof:** `CLEAN_INSTALL_PROOF.json`, `CLEAN_INSTALL_MISSION.json`

## What failed before

Clean `pip install` of the wheel could not run a supervised mission:

1. JSON Schema contracts missing → `validate()` FileNotFoundError  
2. SQL `migrations/` missing → workflow sqlite init failed  
3. Cedar `base.cedar` missing → Authority default-deny (`cedar policy file missing`)

## Fix

Hatch `force-include` in `pyproject.toml`:

| Source | Wheel path |
|--------|------------|
| `contracts/schemas` | `global_os/contracts/schemas` |
| `migrations` | `global_os/adapters/storage/migrations` |
| `policies/cedar` | `global_os/kernel/policy/cedar` |

Resolvers: `validate._find_schemas_dir`, `sql._migrations_dir`, `policy._resolve_cedar_path`.

## Agent-run procedure (this environment)

```text
python3 -m build --wheel -o /tmp/gos-rc-final/dist
python3 -m pip install --target /tmp/gos-rc-final/site <wheel>
PYTHONPATH=/tmp/gos-rc-final/site  → 29 schemas; migrations; cedar present
accept-nonce mission → SUCCEEDED; ACCEPT_NONCE_RC1.txt written
```

`--target` used because this image lacked ensurepip/venv; assets still resolve from the installed tree.

## Honesty

Agent-validated clean install + mission ≠ second-human machine confirmation. Human gate still owns final install walkthrough.
