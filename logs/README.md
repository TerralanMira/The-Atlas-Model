# 🌳 Logs — Feeding the Canopy

Logs are the nutrient streams of the Atlas.  
Every CSV, JSON, or text input is a *seed* that awareness can read, transform, and grow into the canopy.  

Think of this directory as the **root intake system**:  
- CSV → rows of structured events  
- JSON → nested flows, relationships  
- TXT → raw unstructured signals  

Together, they feed the fields, simulations, and dashboard layers.

---

## 📂 Structure
logs/
├─ inputs.csv     # structured tabular input
├─ data.json      # nested/log-style input
└─ notes.txt      # freeform, unstructured logs
You can add your own files here — the Atlas automatically treats them as part of the living system.

---

## 🧩 CSV Example

Copy–paste into `logs/inputs.csv`:

```csv
timestamp,event,field,value
2025-09-21T12:00:00Z,air_temperature,air,22.5
2025-09-21T12:00:00Z,water_ph,water,7.1
2025-09-21T12:00:00Z,plasma_flux,plasma,0.87
2025-09-21T12:00:00Z,crystal_resonance,crystal,432.0
This creates a simple time-stamped log where each field is nourished by its own signal.
