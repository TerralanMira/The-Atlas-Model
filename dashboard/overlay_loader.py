#!/usr/bin/env python3
"""
dashboard/overlay_loader.py

Tiny helper: load sim CSV, compute quick indicators, and
print a human-readable summary so you can sanity-check runs
from a phone or minimal environment.

No plotting; just numbers.
"""

from __future__ import annotations
import csv
from pathlib import Path
from typing import Dict, Any, List, Tuple

def load_csv(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows

def to_float(row: Dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except Exception:
        return default

def summary(path: str) -> str:
    data = load_csv(path)
    if not data:
        return f"[overlay] empty log: {path}"

    # last row view
    last = data[-1]
    R = to_float(last, "R_total")
    C = to_float(last, "C")
    D = to_float(last, "Delta")
    Phi = to_float(last, "Phi")
    drift = to_float(last, "drift")
    k_eff = last.get("K_eff", "")

    lines = []
    lines.append(f"[overlay] {Path(path).name} — steps={len(data)} preset={last.get('preset','?')} K_eff={k_eff}")
    lines.append(f"  R_total={R:.3f}  C={C:.3f}  Δ={D:.3f}  Φ={Phi:.3f}  drift={drift:.3f}")

    # quick qualitative reads
    if R > 0.8 and D < 0.25 and drift < 0.02:
        lines.append("  note: clamp risk — high order with low diversity and low drift.")
    elif C > 0.6 and Phi > 0.6 and D > 0.35:
        lines.append("  note: gentle learning — coherence rising while diversity preserved.")
    else:
        lines.append("  note: mixed state — adjust K, geometry, or ω spread.")

    return "\n".join(lines)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Read sim CSV and print overlay summary.")
    ap.add_argument("csv_path", help="Path to logs/*.csv produced by sims/")
    args = ap.parse_args()
    print(summary(args.csv_path))
