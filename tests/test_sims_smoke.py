import os
import sys
import csv
import shutil
import subprocess
from pathlib import Path

# Always use a headless backend for CI plots
os.environ["MPLBACKEND"] = "Agg"

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "sims" / "figures"
OUT_DIR = ROOT / "sims" / "out"

def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run a command and return the CompletedProcess (no shell)."""
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=ROOT,
    )

def _clean_outputs():
    if FIG_DIR.exists():
        shutil.rmtree(FIG_DIR)
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)

def _assert_csv_has_rows(path: Path, min_rows: int = 10):
    assert path.exists(), f"Missing CSV: {path}"
    with path.open() as f:
        rows = list(csv.reader(f))
    assert len(rows) >= min_rows, f"CSV too short ({len(rows)} rows): {path}"

def test_sims_list():
    cp = _run([sys.executable, "-m", "sims", "--list"])
    assert cp.returncode == 0, cp.stderr

def test_harmonic_observation_smoke():
    _clean_outputs()
    # keep it fast: fewer steps
    cp = _run([
        sys.executable, "-m", "sims", "run", "harmonic_observation",
        "--n", "96", "--K", "1.1", "--rho", "0.6", "--lam", "0.1",
        "--steps", "400"
    ])
    assert cp.returncode == 0, cp.stderr
    png = FIG_DIR / "harmonic_observation_R.png"
    csv_path = OUT_DIR / "harmonic_observation_metrics.csv"
    assert png.exists(), f"Missing plot: {png}"
    _assert_csv_has_rows(csv_path)

def test_entropy_drift_smoke():
    _clean_outputs()
    cp = _run([
        sys.executable, "-m", "sims", "run", "entropy_drift",
        "--steps", "2000", "--pulse_T", "400", "--gain", "0.2", "--gamma", "0.002"
    ])
    assert cp.returncode == 0, cp.stderr
    png = FIG_DIR / "entropy_drift.png"
    csv_path = OUT_DIR / "entropy_drift.csv"
    assert png.exists(), f"Missing plot: {png}"
    _assert_csv_has_rows(csv_path)

def test_civic_resonance_smoke():
    _clean_outputs()
    cp = _run([
        sys.executable, "-m", "sims", "run", "civic_resonance",
        "--n", "200", "--blocks", "5", "--Kintra", "1.1", "--Kglobal", "0.35",
        "--steps", "800"
    ])
    assert cp.returncode == 0, cp.stderr
    png = FIG_DIR / "civic_resonance_R.png"
    csv_path = OUT_DIR / "civic_resonance.csv"
    assert png.exists(), f"Missing plot: {png}"
    _assert_csv_has_rows(csv_path)
    # Quick shape check (header + rows with 3 columns)
    with csv_path.open() as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["step", "R_global", "R_blocks_mean"], f"Unexpected header: {rows[0]}"

def test_atlas_coherence_smoke():
    _clean_outputs()
    cp = _run([
        sys.executable, "-m", "sims", "run", "atlas_coherence",
        "--nH", "120", "--nA", "120", "--K_HA", "0.25", "--K_AH", "0.25",
        "--rhoH", "0.5", "--rhoA", "0.7", "--steps", "800"
    ])
    assert cp.returncode == 0, cp.stderr
    png = FIG_DIR / "atlas_coherence.png"
    csv_path = OUT_DIR / "atlas_coherence.csv"
    assert png.exists(), f"Missing plot: {png}"
    _assert_csv_has_rows(csv_path)
    # Quick shape check (header + rows with 4 columns)
    with csv_path.open() as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["step", "R_H", "R_A", "R_all"], f"Unexpected header: {rows[0]}"
