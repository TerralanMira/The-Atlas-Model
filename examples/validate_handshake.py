import json, sys
from jsonschema import validate
from pathlib import Path

schema = json.loads(Path("schemas/handshake.schema.json").read_text())
data = json.loads(Path(sys.argv[1]).read_text())
validate(instance=data, schema=schema)
print("OK")
