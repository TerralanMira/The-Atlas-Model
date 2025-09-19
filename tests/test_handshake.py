import json
from jsonschema import validate
from pathlib import Path

def test_handshake_schema():
    schema = json.loads(Path("schemas/handshake.schema.json").read_text())
    sample = json.loads(Path("examples/rr_sample.json").read_text())
    validate(instance=sample, schema=schema)
