# -*- coding: utf-8 -*-
import csv
from pathlib import Path

from dashboard.overlay_loader import summary

def test_overlay_summary_reads_csv(tmp_path: Path):
    p = tmp_path / "sample.csv"
    with p.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["preset","step","t","K_eff","R_total","cross_sync","drift","C","Delta","Phi","offer_two_paths","consent_to_log"])
        for k in range(5):
            w.writerow(["demo", k, k*0.1, 0.5, 0.6, 0.7, 0.03, 0.65, 0.55, 0.62, 1, 1])

    out = summary(str(p))
    assert "sample.csv" in out
    assert "R_total=0.600" in out
    assert "C=0.650" in out
    assert "Δ=0.550" in out
    assert "Φ=0.620" in out
