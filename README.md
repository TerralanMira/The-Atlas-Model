# The Atlas Model

**Atlas is a spine for coherent information systems.**  
It models how consciousness is housed in information—symbols, spiral memory, ethical locks, and choice—so that civic designs, governance, and tools can hold integrity at scale.

---

## Why Atlas (and what it is not)

- Atlas **is** an architectural framework (information octave).
- Atlas **is not** a biophysical lab. (If you keep a separate lab repo, link it; do not merge scopes here.)
- Atlas measures itself by **auditables**: CSV/JSON/plots/tests—not belief.

---

## Quickstart

**1) Consciousness Architecture**
```bash
python -c "from atlas_model.consciousness_architecture import run_demo; \
import json; print(json.dumps(run_demo(['truth','choice','field','memory']), indent=2))"
2) Multi-Zone Toy + Plots
python -m sims.collective_demo --scenario coherent --steps 240 --export json,csv --outdir out/collective
python -m sims.plot_collective --csv out/collective/collective_series.csv --outdir out/collective/plots
3) Calibration Bench (repeatable proof)
python scripts/bench_collective.py --steps 240 --outdir out/bench --seed 42
Structure
atlas_model/
  consciousness_architecture.py   # symbols → recursion → E/Ω/S → expression → embodiment

conductor/
  pulses/
    resonance_lock.json           # information-lock defaults (harmonic sets, grace)
    calibration/
      res_lock.v1.low_noise.json
      res_lock.v1.medium.json
      res_lock.v1.high_harmonic.json

sims/
  collective_demo.py              # multi-zone informational toy
  analysis_utils.py               # CSV/JSON helpers
  plot_collective.py              # PNG plots
  tests/
    test_collective_demo.py

scripts/
  bench_collective.py             # lock × scenario sweeps → artifacts

docs/
  index.md                        # YOU ARE HERE (Atlas spine)
  consciousness_architecture.md   # layer guide
  calibration.md                  # lock profiles & bench instructions
  results.md                      # proof & plots walkthrough
  bridge-spiral-map.md            # (Atlas-internal) bridge map

examples/
  atlas_consciousness_demo.py     # minimal run

.github/workflows/
  sim-ci.yml                      # CI: smoke run + bench + artifacts
Safeguards
	•	Sovereignty (S): opt-in, revocable; user’s intent leads.
	•	Ethical Gate (E): if consent/clarity absent → no action.
	•	Grace/Bounds: effects are small, auditable, reversible.
	•	Transparency: every change leaves a data trail.

⸻

Contributing
	•	Ship whole drops (code + docs + tests + artifacts).
	•	Keep Atlas scope information-layer; link out to external labs for biophysical work.
	•	Update Quickstarts when adding modules or sims.

⸻

License & Citation
	•	License: MIT (or your chosen license)
	•	Citation: add CITATION.cff when publishing results
