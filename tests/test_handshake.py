import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")


def test_handshake_schema_ok():
    root = Path(__file__).resolve().parents[1]
    schema_path = root / "schemas" / "handshake.schema.json"
    sample_path = root / "examples" / "rr_sample.json"

    assert schema_path.exists(), f"Missing schema: {schema_path}"
    assert sample_path.exists(), f"Missing sample: {sample_path}"

    schema = json.loads(schema_path.read_text())
    sample = json.loads(sample_path.read_text())

    # Validate (raises on error)
    from jsonschema import validate
    validate(instance=sample, schema=schema)
