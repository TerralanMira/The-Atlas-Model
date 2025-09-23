import json
from pathlib import Path

def test_import_coherence_metrics():
    # Must import without side effects
    from algorithms.coherence_metrics import order_parameter  # noqa: F401

def test_presets_schema():
    p = Path("sims/presets.json")
    assert p.exists(), "sims/presets.json missing"
    data = json.loads(p.read_text())
    assert isinstance(data, dict) and data, "presets must be a non-empty dict"
    for name, cfg in data.items():
        assert "inner" in cfg and "outer" in cfg and "noise" in cfg, f"preset {name} missing fields"
        assert 0 <= cfg["noise"] <= 1, f"noise out of range in {name}"

def test_readme_has_directive():
    text = Path("README.md").read_text(encoding="utf-8")
    assert "Directive of the Hum" in text
