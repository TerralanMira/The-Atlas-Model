# -*- coding: utf-8 -*-
import csv
from pathlib import Path
import subprocess
import sys

def test_runner_writes_csv(tmp_path: Path):
    # Run the script for a tiny number of steps and ensure CSV appears and is well-formed.
    logs = tmp_path / "logs"
    out_csv = logs / "multi_scale.csv"

    cmd = [
        sys.executable, "-m", "sims.multi_scale_kuramoto",
        "--steps", "50",
        "--save_csv", str(out_csv),
        "--seed", "0"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"runner failed: {r.stderr}"

    assert out_csv.exists(), "CSV not written"
    with out_csv.open() as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["step","R_total","R_inner","R_outer","C_cross"]
        first = next(reader)
        assert len(first) == 5
