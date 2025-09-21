from pathlib import Path
import csv

REQUIRED = ["step","R_total","R_inner","R_outer","C_cross","drift","Delta","Phi","choice_score"]

def test_headers_present():
    # find any csv in logs; if none, pass (design-first repo)
    logs = Path("logs")
    if not logs.exists():
        return
    files = list(logs.glob("*.csv"))
    if not files:
        return
    with files[0].open("r", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
    for h in REQUIRED:
        assert h in headers, f"missing header {h}; unify naming across sims/dashboard/docs"
