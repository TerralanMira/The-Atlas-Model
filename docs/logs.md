# Logs & Canopy

**Path:** `docs/logs.md`  
**Intent:** a living inlet for signals. Paste CSV/JSON, normalize, and let the patterns bloom across dashboards, sims, and coherence metrics.

> If you’re here to *feed the canopy now*, jump to **Quick Start**.

---

## Why Logs?

Logs are the bridge between lived signals and Atlas structure. They:
- ground claims in observable data,
- allow reproducible analysis,
- and keep the forest alive (continuous inputs → continuous learning).

Ethics first: only ingest consensual, anonymized, safe data. See `ETHICS.md`.

---

## Quick Start (90 seconds)

1. **Create folders (first time):**
logs/
└─ ingest/
├─ raw/
└─ examples/
2. **Add your data:**
- CSV → `logs/ingest/raw/your_data.csv`
- JSON → `logs/ingest/raw/your_data.json`

3. **Normalize (one-time helper scripts):**
- CSV: `python tools/ingest_csv.py logs/ingest/raw/your_data.csv`
- JSON: `python tools/ingest_json.py logs/ingest/raw/your_data.json`

Output → `logs/ingest/normalized_<name>_<stamp>.jsonl`

4. **See it:** open **[Dashboard](dashboard.md)** and select your normalized file.

> Need more detail? See **[Data Input Gateway](data_input.md)**.

---

## Minimal Schema

| Field      | Type   | Required | Notes                                                                 |
|------------|--------|----------|-----------------------------------------------------------------------|
| `timestamp`| string | no       | ISO8601 preferred; synthetic index assigned if missing                |
| `value`    | number | yes      | Primary measurement (amplitude, rate, coherence, etc.)                |
| `label`    | string | no       | Tag for the signal (`breath`, `hrv`, `theta`, `R_inner`, …)          |
| `group`    | string | no       | Cohort or node (`inner`, `outer`, `city`, `node42`)                   |
| `lat`,`lon`| number | no       | Optional geospatial context                                           |
| `meta`     | object | no       | Free-form extras (kept as-is)                                         |

Normalization guarantees:
- numeric `value`,
- lowercase keys,
- monotonic index if no `timestamp`,
- drops empty/invalid rows.

---

## Paste-In Examples

### CSV (save as `logs/ingest/examples/breath_session.csv`)
```csv
timestamp,value,label,group,lat,lon
2025-09-19T19:00:00Z,0.42,breath,inner,34.05,-118.24
2025-09-19T19:00:10Z,0.45,breath,inner,34.05,-118.24
2025-09-19T19:00:20Z,0.51,breath,inner,34.05,-118.24
2025-09-19T19:00:30Z,0.49,breath,inner,34.05,-118.24
JSON (save as logs/ingest/examples/hrv_session.json)
[
  {"timestamp":"2025-09-19T19:00:00Z","value":0.78,"label":"hrv","group":"outer"},
  {"timestamp":"2025-09-19T19:00:10Z","value":0.74,"label":"hrv","group":"outer"},
  {"timestamp":"2025-09-19T19:00:20Z","value":0.81,"label":"hrv","group":"outer"}
]
Normalize either file with the helper scripts; you’ll get a .jsonl file in logs/ingest/.
Example of Normalized Output (.jsonl)
{"timestamp":"2025-09-19T19:00:00Z","value":0.42,"label":"breath","group":"inner","lat":34.05,"lon":-118.24}
{"timestamp":"2025-09-19T19:00:10Z","value":0.45,"label":"breath","group":"inner","lat":34.05,"lon":-118.24}
{"timestamp":"2025-09-19T19:00:20Z","value":0.51,"label":"breath","group":"inner","lat":34.05,"lon":-118.24}
{"timestamp":"2025-09-19T19:00:30Z","value":0.49,"label":"breath","group":"inner","lat":34.05,"lon":-118.24}
If a row had no timestamp, you might see "timestamp":"t+000123" (synthetic index).
From Logs → Metrics → Sims
	1.	Compute coherence
Use algorithms/coherence_metrics.py to compute order parameters (R_inner, R_outer, R_total) from your normalized stream.
	2.	Seed sims
Derive summary stats and add to sims/presets.json (e.g., phase variance, coupling, noise). Then run sims/multi_scale_kuramoto.py.
	3.	Reflect back
Visualize in Dashboard and record observations in logs/notes/ (create if needed).

⸻

Simple Notes Convention

Create logs/notes/ and drop short Markdown notes alongside data:

logs/notes/2025-09-19_breath_session.md
# Breath Session — Inner Group
- Source: wearable stream
- Window: 19:00–19:05Z
- Observations: amplitude increased post-grounding
- Next: compute R_inner vs baseline, seed sim noise=0.12
Troubleshooting
	•	“Script not found” → make sure tools/ingest_csv.py and tools/ingest_json.py exist (see docs/data_input.md for full code).
	•	“No such file or directory” → create the directories shown above.
	•	Plot doesn’t show → on headless CI, skip plots; use dashboard rendering instead.
	•	Docs 404 → add a stub page or update mkdocs.yml nav.

⸻

Ethics & Consent

Only ingest signals with clear consent. Prefer anonymized data. Avoid coercion. Respect withdrawal.
See ETHICS.md for ground rules.

⸻

Next
	•	Go to Dashboard to see your signals layered.
	•	Explore Synthesis Patterns to interpret shape and meaning.
	•	Use Convergence → Emergence to close the loop with practice.

Feed the canopy. Let the forest learn.
