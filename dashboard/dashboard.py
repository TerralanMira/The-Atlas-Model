"""
Dashboard: reading the hum from logs/*.csv
Expected headers:
  step, R_total, R_inner, R_outer, C_cross, drift, Delta, Phi, choice_score
"""

import csv
import sys
from pathlib import Path
from statistics import mean

def summarize(csv_path: Path) -> str:
    rows = []
    with csv_path.open("r", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)

    if not rows:
        return "empty log"

    def f(name, cast=float):
        vals = []
        for row in rows:
            try:
                vals.append(cast(row[name]))
            except (KeyError, ValueError):
                pass
        return vals

    R_total = f("R_total")
    R_inner = f("R_inner")
    R_outer = f("R_outer")
    C_cross = f("C_cross")
    drift   = f("drift")
    Delta   = f("Delta")
    Phi     = f("Phi")

    msg = []
    msg.append(f"steps={len(R_total)}")
    if R_total: msg.append(f"R_total≈{mean(R_total):.2f}")
    if C_cross: msg.append(f"C_cross≈{mean(C_cross):.2f}")
    if drift:   msg.append(f"drift≈{mean(drift):.3f}")
    if Delta:   msg.append(f"Δ≈{mean(Delta):.2f}")
    if Phi:     msg.append(f"Φ≈{mean(Phi):.2f}")

    # qualitative overlay
    clamp_risk = (R_total and mean(R_total) > 0.8) and (Delta and mean(Delta) < 0.25)
    gentle = (R_total and mean(R_total) > 0.55) and (Delta and mean(Delta) >= 0.25)

    note = "gentle lift" if gentle else "watch clamp" if clamp_risk else "breathing"
    return " | ".join(msg) + f" | {note}"

def main():
    if len(sys.argv) < 2:
        print("usage: python dashboard/dashboard.py logs/sim.csv")
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"not found: {path}")
        sys.exit(2)
    print(summarize(path))

if __name__ == "__main__":
    main()
