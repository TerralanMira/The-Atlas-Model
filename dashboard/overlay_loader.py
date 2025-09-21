# -*- coding: utf-8 -*-
"""
Overlay loader: summarize a CSV log produced by sims/* runners.

Expected headers (order flexible):
  step, t, R_total, R_inner, R_outer, C_cross, drift, Delta, Phi, choice_score
"""
from __future__ import annotations
import csv
from pathlib import Path
from statistics import mean

FIELDS = ["R_total","R_inner","R_outer","C_cross","drift","Delta","Phi","choice_score"]

def summary(csv_path: str | Path) -> str:
    p = Path(csv_path)
    rows = []
    with p.open("r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    if not rows:
        return f"{p.name}: empty"

    agg = {}
    for k in FIELDS:
        vals = []
        for row in rows:
            if k in row and row[k] not in (None, ""):
                try:
                    vals.append(float(row[k]))
                except ValueError:
                    pass
        agg[k] = mean(vals) if vals else None

    clamp = (agg.get("R_total",0) > 0.80) and (agg.get("Delta",1) < 0.25)
    gentle = (agg.get("R_total",0) > 0.55) and (agg.get("Phi",0) > 0.6) and (agg.get("Delta",0.3) >= 0.25)

    note = "gentle lift" if gentle else "watch clamp" if clamp else "breathing"
    parts = [p.name]
    for k in ("R_total","C_cross","Delta","Phi","choice_score"):
        v = agg.get(k, None)
        if v is not None:
            parts.append(f"{k}={v:.3f}")
    parts.append(note)
    return " | ".join(parts)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python dashboard/overlay_loader.py logs/multi_scale.csv")
        sys.exit(1)
    print(summary(sys.argv[1]))
