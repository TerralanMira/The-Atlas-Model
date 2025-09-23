# Data Input Gateway (Feed the Canopy)
**Path:** `docs/data_input.md`

This is the portal for bringing *your* signals into the Atlas field. Minimal friction, clear shapes. You can paste data, point to a file, or stream. The ingest normalizes inputs into a simple, portable format that every layer (algorithms, sims, dashboard) can read.

---

## TL;DR

- **CSV** with headers: `timestamp,value,label,group,lat,lon`
- **JSON** list of objects with the same keys.
- Missing fields are OK; we’ll infer sane defaults.
- Output: a normalized file in `logs/ingest/normalized_<stamp>.jsonl` and an optional quick-look plot.

---

## 1) Paste-in Examples (copy → save → commit)

### CSV (example)
```csv
# save as logs/ingest/examples/breath_session.csv
timestamp,value,label,group,lat,lon
2025-09-19T19:00:00Z,0.42,breath,inner,34.05,-118.24
2025-09-19T19:00:10Z,0.45,breath,inner,34.05,-118.24
2025-09-19T19:00:20Z,0.51,breath,inner,34.05,-118.24
2025-09-19T19:00:30Z,0.49,breath,inner,34.05,-118.24
JSON (example)
[
  {"timestamp": "2025-09-19T19:00:00Z", "value": 0.78, "label": "hrv", "group": "outer"},
  {"timestamp": "2025-09-19T19:00:10Z", "value": 0.74, "label": "hrv", "group": "outer"},
  {"timestamp": "2025-09-19T19:00:20Z", "value": 0.81, "label": "hrv", "group": "outer"}
]
2) Minimal Schema (flexible-by-design)
Field
Type
Required
Notes
timestamp
string
no
ISO8601 (2025-09-19T19:00:00Z) recommended; auto-index if absent.
value
number
yes
Primary measurement (e.g., amplitude, rate, coherence).
label
string
no
What the value represents (breath, hrv, theta, R_inner).
group
string
no
Cohort/tag (inner, outer, city, node42).
lat,lon
number
no
Geospatial context for maps/overlays.
meta
object
no
Free-form extras; kept as-is.
Normalization will:
	•	ensure numeric value
	•	attach monotonically increasing index if timestamp missing
	•	coerce field names to lowercase
	•	drop empty lines / null-only rows
