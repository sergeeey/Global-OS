from __future__ import annotations

from jsonschema import Draft202012Validator

from global_os.contracts import list_schema_files, load_schema


def test_all_schemas_are_valid():
    files = list_schema_files()
    assert len(files) >= 8
    for path in files:
        schema = load_schema(path.name)
        Draft202012Validator.check_schema(schema)
