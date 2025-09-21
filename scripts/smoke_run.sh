#!/usr/bin/env bash
# Minimal end-to-end smoke run (no long compute).
# Creates tiny sample logs and produces a suggestions file.

set -euo pipefail

mkdir -p logs sessions

# Tiny runs (short steps) to keep it quick/light
python sims/multi_scale_kuramoto.py --preset circle6_center --steps 200 --csv logs/circle.csv || true
python sims/multi_scale_kuramoto.py --preset grid_rect        --steps 200 --csv logs/grid.csv   || true

# Ingest and propose gentle deltas
python scripts/ingest_sessions.py logs/circle.csv logs/grid.csv --out sessions/suggestions.json || true

echo "Smoke run complete. See sessions/suggestions.json"
