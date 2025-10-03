# The Atlas Model — Documentation Spine

Atlas is a **field-aware information architecture**: it houses consciousness in structures of symbols, recursion, ethics, and choice. This index orients you to Atlas’ layers, code, and proofs—without crossing into the separate Resonant Reality lab.

---

## First Principles

1. **Whole in part, part in whole** — each module mirrors the field.
2. **Coherence is choice** — alignment is enacted via ethical gates.
3. **Simulation as practice** — toy models reveal governing structure.
4. **Safeguards first** — sovereignty, consent, stamina, integrity.

---

## Core Layers (Atlas octave)

### 1) Human (Information) Layer
How information “houses” awareness.
- **Consciousness Architecture** — symbols → spiral memory → ethical lock (E) → expression → embodiment.
- Harmonic carriers in language & design (432–963 Hz mappings for *information*, not biophysics).

**Read & Run**
- Guide: `docs/consciousness_architecture.md`
- Module: `atlas_model/consciousness_architecture.py`
- Demo: `examples/atlas_consciousness_demo.py`

---

### 2) Civic Layer (Design of Systems)
How structures hold resonance.
- Governance scaffolds, plaza/hearth patterns, procedural safeguards.
- Coherence metrics for information spaces (coherence / noise / coupling).

**Read & Run**
- Atlas–Atlas bridge: `docs/bridge-spiral-map.md`
- Multi-zone toy: `sims/collective_demo.py`
- Utilities: `sims/analysis_utils.py`
- Plots: `sims/plot_collective.py`

*(These sims are informational toy models for Atlas—kept distinct from any biophysical lab work.)*

---

### 3) Calibration & Proof (Repeatability)
- **Locks** define baseline assumptions for Atlas sims (e.g., harmonic sets, grace factors) in **information space**.
- **Benches** compare scenarios × locks and publish artifacts.

**Read & Run**
- Calibration profiles: `docs/calibration.md`
- Results walkthrough: `docs/results.md`
- Bench script: `scripts/bench_collective.py`
- CI workflow: `.github/workflows/sim-ci.yml`

---

### 4) Cosmos (Framing & Limits)
- Infinity relation (∞ = 0 ↔ 1) and scaling symmetries *as information frames*.
- Orientation for long-horizon design (no physical claims in this repo).

*(Detail pages linked from `docs/cosmos/` if present in your tree.)*

---

## Quickstarts

**A) Consciousness Architecture**
```bash
python -c "from atlas_model.consciousness_architecture import run_demo; \
import json; print(json.dumps(run_demo(['truth','choice','field','memory']), indent=2))"
B) Multi-Zone Toy + Plots
python -m sims.collective_demo --scenario coherent --steps 240 --export json,csv --outdir out/collective
python -m sims.plot_collective --csv out/collective/collective_series.csv --outdir out/collective/plots
C) Benchmarks (artifacts for audit)
python scripts/bench_collective.py --steps 240 --outdir out/bench --seed 42
Safeguards (Atlas commitments)
	•	Sovereignty (S): opt-in, revocable; no hidden coupling.
	•	Ethical Gate (E): deny action absent consent/clarity.
	•	Stamina / Integrity: throttle; effects bounded, reversible.
	•	Transparency: every run yields CSV/JSON/plots.

⸻

Repository Map (Atlas)
	•	atlas_model/ — core modules (e.g., consciousness_architecture.py)
	•	sims/ — informational toy models + tests
	•	scripts/ — benches and tooling
	•	conductor/pulses/ — lock profiles for information simulations
	•	docs/ — this spine, calibration, results, bridges within Atlas
	•	examples/ — minimal runnable demos
	•	.github/workflows/ — CI producing artifacts
