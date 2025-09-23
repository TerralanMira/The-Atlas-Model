#!/usr/bin/env python3
import json, sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

def load_jsonl(path):
    xs, ys = [], []
    with Path(path).open() as f:
        for i, line in enumerate(f):
            r = json.loads(line)
            xs.append(i if "t+" in str(r.get("timestamp","")) else i)
            ys.append(float(r["value"]))
    return np.array(xs), np.array(ys)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python tools/quicklook_plot.py logs/ingest/normalized_*.jsonl")
        sys.exit(1)
    x, y = load_jsonl(sys.argv[1])
    plt.plot(x, y, marker="o")
    plt.title("Quick Look")
    plt.xlabel("index")
    plt.ylabel("value")
    plt.tight_layout()
    plt.show()
  Flow-on: Dashboards, Sims, Coherence
	•	Dashboards: docs/dashboard.md shows how to render layered visuals (time series, coherence, maps). Use any file in logs/ingest/*.jsonl as a source.
	•	Sim presets: add summary stats derived from your ingest (mean frequency, variance, labels → groups) into sims/presets.json to seed multi_scale_kuramoto.py.
	•	Coherence metrics: pipe normalized values into algorithms/coherence_metrics.py to compute R_inner, R_outer, R_total and compare to live thresholds.
Naming & Organization
	•	Place raw files in logs/ingest/raw/ (optional).
	•	Normalized outputs land in logs/ingest/.
	•	Add brief notes in logs/README.md (purpose, source, consent).
Consent & Ethics

Data is relation. Only ingest what is consensual, anonymized where appropriate, and safe to share. See ETHICS.md.
Next Steps
	1.	Paste one of the examples above and normalize it.
	2.	Open docs/dashboard.md and wire that normalized file into a chart/map.
	3.	If useful, promote derived parameters to sims/presets.json and explore system behavior.

The forest grows when signals meet structure. This page keeps that meeting simple and alive.
