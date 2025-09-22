# Dashboard Quickstart

Render the living canopy in 60 seconds.

## 0) Minimal data (optional)
If you have none, pages will synthesize examples. To use your own:

- Time-series (CSV, first column float):
logs/timeseries.csv

0.62
0.64
0.71
- Coherence matrix (NumPy):
```python
# build once in a REPL
import numpy as np
C = np.eye(24)
np.save("logs/coherence_matrix.npy", C)
Generate pages
# Fields
python -m dashboard.page_fields --out docs/assets/dashboard/fields_page.png

# Pulse
python -m dashboard.page_pulse --out docs/assets/dashboard/pulse_page.png

# Awareness
python -m dashboard.page_awareness --out docs/assets/dashboard/awareness_page.png

# Overlays (Live) with archetype
python -m dashboard.page_overlays_live \
  --coh logs/coherence_matrix.npy \
  --series logs/timeseries.csv \
  --archetype Seer \
  --out docs/assets/dashboard/overlays_live.png
View
mkdocs serve
Open http://127.0.0.1:8000 and navigate to Dashboard.
