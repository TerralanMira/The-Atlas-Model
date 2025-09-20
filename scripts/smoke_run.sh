#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$ROOT/logs" "$ROOT/sessions"

# Write tiny sample logs if they don't exist (safe to re-run)
if [ ! -f "$ROOT/logs/sample_circle.csv" ]; then
  cat > "$ROOT/logs/sample_circle.csv" <<'CSV'
step,t,R_total,R_mean,cross_sync,drift,ready,choice_score,offer_two_paths,consent_to_log
0,0.00,0.62,0.62,0.58,0.21,0.66,0.00,1,1
1,0.01,0.67,0.64,0.61,0.19,0.70,0.00,1,1
2,0.02,0.71,0.66,0.64,0.17,0.73,1.00,1,1
3,0.03,0.74,0.68,0.66,0.16,0.76,1.00,1,1
CSV
fi

if [ ! -f "$ROOT/logs/sample_grid.csv" ]; then
  cat > "$ROOT/logs/sample_grid.csv" <<'CSV'
step,t,R_total,R_mean,cross_sync,drift,ready,choice_score,offer_two_paths,consent_to_log
0,0.00,0.48,0.48,0.44,0.28,0.55,0.00,0,1
1,0.01,0.50,0.49,0.45,0.27,0.56,0.00,0,1
2,0.02,0.51,0.50,0.46,0.27,0.56,0.00,0,1
3,0.03,0.52,0.50,0.46,0.26,0.57,0.00,0,1
CSV
fi

echo "→ Running ingest on sample logs…"
python "$ROOT/scripts/ingest_sessions.py" \
  "$ROOT/logs/sample_circle.csv" "$ROOT/logs/sample_grid.csv" \
  --out "$ROOT/sessions/suggestions.json"

echo "✓ Wrote $ROOT/sessions/suggestions.json"
jq . "$ROOT/sessions/suggestions.json" 2>/dev/null || cat "$ROOT/sessions/suggestions.json"
