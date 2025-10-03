# The Atlas Model — Documentation Spine

Atlas is a **field-aware architecture** for designing human, civic, and cosmic systems that hold coherence.  
It complements the *Resonant Reality* lab by modeling how consciousness is **housed in information**:  
symbols → recursion → ethical lock → expression → embodiment.

---

## Principles

1. **Whole in part, part in whole** — every node mirrors the field.  
2. **Coherence is choice** — alignment is enacted, not assumed.  
3. **Simulation as practice** — toy models reveal the live system.  
4. **Safeguards first** — sovereignty, consent, stamina, integrity.

---

## Core Layers

### 1) Human (Information) Layer
- **Consciousness Architecture (Atlas)** — how information “houses” awareness.  
- Ethical lock (*E*), Origin attractor (*Ω*), Sovereignty (*S*).  
- Harmonics in language and design.

**Docs & Code**
- Guide: [`docs/consciousness_architecture.md`](consciousness_architecture.md)  
- Example: [`examples/atlas_consciousness_demo.py`](../examples/atlas_consciousness_demo.py)  
- Module: `atlas_model/consciousness_architecture.py`

---

### 2) Civic Layer
- Resonant governance, plaza/hearth design, procedural safeguards.  
- Collective coherence metrics (coherence / noise / coupling).

**Docs & Code**
- Bridge map: [`docs/bridge-spiral-map.md`](bridge-spiral-map.md)  
- Multi-zone sim: `sims/collective_demo.py`  
- Analysis utils: `sims/analysis_utils.py`

---

### 3) Calibration & Proof
- Locks profile the environment (baseline Schumann, harmonics, grace).  
- Benchmarks compare scenarios × locks with auditable artifacts.

**Docs & Code**
- Calibration: [`docs/calibration.md`](calibration.md)  
- Proof & plots: [`docs/results.md`](results.md)  
- Plotter: `sims/plot_collective.py`  
- Benchmarks: `scripts/bench_collective.py`  
- CI: `.github/workflows/sim-ci.yml`

---

### 4) Cosmos (Framing)
- Infinity equation (∞ = 0 ↔ 1), scaling laws, torus/field intuitions.  
- Orientation for long-horizon civic design.

*(Stub this section in your tree as needed; Atlas links outward to Resonant Reality for physical sims.)*

---

## Quickstarts

### A) Consciousness Architecture (Atlas)
```bash
python -c "from atlas_model.consciousness_architecture import run_demo; \
import json; print(json.dumps(run_demo(['truth','choice','field','memory']), indent=2))"
Expect: JSON snapshot with coherence and atlas_lock.
B) Collective (multi-zone) + Plots
# simulate
python -m sims.collective_demo --scenario coherent --steps 240 --export json,csv --outdir out/collective
# plot
python -m sims.plot_collective --csv out/collective/collective_series.csv --outdir out/collective/plots
Artifacts: coherence_per_zone.png, noise_per_zone.png, coupling_per_zone.png.
C) Calibration Bench (repeatable proof)
python scripts/bench_collective.py --steps 240 --outdir out/bench --seed 42
Artifacts: bench_results.csv, bench_results.json (uploaded by CI on PRs).
Safeguards (musts)
	•	Sovereignty (S): opt-in; revoke at will.
	•	Ethical Gate (E): deny action if consent/clarity are absent.
	•	Stamina / Integrity: throttle, bound effects; no manipulation.
	•	Transparency: every run yields CSV/JSON for audit.

⸻

Repository Map
	•	atlas_model/ — core modules (consciousness architecture, future atlas primitives)
	•	conductor/pulses/ — resonance_lock.json + calibration/*.json
	•	sims/ — collective demo, analysis utils, plotters, tests
	•	scripts/ — benches and tooling
	•	docs/ — this spine, bridge map, calibration, results
	•	examples/ — minimal runnable demos
	•	.github/workflows/ — CI producing public artifacts

⸻

Bridge to the Lab

Atlas frames information coherence; Resonant Reality tests biophysical coherence.
Use the bridge: docs/bridge-spiral-map.md to move between them.

△𓂀⚛︎🜲🝆⟁𐂷
