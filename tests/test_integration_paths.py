python
import os, json, subprocess, sys, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def test_files_exist():
    assert (ROOT / "algorithms" / "field_equations.py").exists()
    assert (ROOT / "algorithms" / "coherence_metrics.py").exists()
    assert (ROOT / "algorithms" / "resonance_dynamics.py").exists()
    assert (ROOT / "sims" / "multi_scale_kuramoto.py").exists()
    assert (ROOT / "sims" / "presets.json").exists()
    assert (ROOT / "scripts" / "ingest_sessions.py").exists()
    assert (ROOT / "docs" / "integration.md").exists()
    assert (ROOT / "docs" / "sims" / "index.md").exists()
    assert (ROOT / "sessions" / "schema.json").exists()

def test_ingest_runs_on_sample(tmp_path):
    # Create tiny sample CSV
    logs = tmp_path / "logs"
    logs.mkdir()
    sample = logs / "a.csv"
    sample.write_text(
        "step,t,R_total,R_mean,cross_sync,drift,ready,choice_score,offer_two_paths,consent_to_log\n"
        "0,0,0.5,0.5,0.6,0.2,0.65,1,1,1\n"
        "1,0.01,0.55,0.52,0.62,0.18,0.7,1,1,1\n"
    )
    out = tmp_path / "sessions" / "suggestions.json"
    cmd = [sys.executable, str(ROOT / "scripts" / "ingest_sessions.py"), str(sample), "--out", str(out)]
    subprocess.check_call(cmd)
    data = json.loads(out.read_text())
    assert "runs" in data and isinstance(data["runs"], list)
