# Community Resonance

Communities are forests of memory.  
Within-group coherence grows trunks; between-group transfer weaves canopies.

This layer shows **how alignment in one group leaks into another** (resonance transfer), and how to tell **healthy coherence** from **brittle entrainment**.

---

## Model

We simulate G groups of oscillators:
- **Intra-group coupling (K_intra)**: how strongly each group self-aligns.
- **Cross-group coupling (K_cross)**: how much alignment leaks across groups.
- **Noise (σ)**: variability that keeps the system adaptive.
- **Natural frequencies (ω)**: diversity of intrinsic tempos.

Outputs:
- **R_groups(t)**: coherence inside each group.
- **R_global(t)**: whole-field coherence.
- **gap(t)**: mean phase gap between group means (lower is tighter braiding).

---

## Run

```bash
python -c "from sims.resonance_transfer import simulate,TransferConfig; print(simulate(TransferConfig())['summary'])"
Or import in Python and plot with the dashboard tools
Interpret
	•	Healthy coherence: R_groups↑ and R_global↑ while gap↓, and resource metrics (if layered in) stay stable.
	•	Brittle entrainment: R_global↑ but gap remains large or resource health drops.
	•	Isolated pockets: some R_groups↑ while R_global remains flat and gap stays wide.

Use A/B comparisons to validate interventions rather than narratives.

⸻

A/B Compare With Multilayer Runs
	1.	Baseline: multilayer_demo (no memory scaffolding).
	2.	Intervention: memory_demo (noise↓, K↑, bridge+).
	3.	Compare:
python dashboard/compare_presets.py --a multilayer_demo --b memory_demo
This shows whether local improvements actually lift the whole.

⸻

Extend
	•	Add resource dynamics (r(t)) to each group to couple coherence with health.
	•	Encode rituals (periodic revisiting) to model memory-driven stability.
	•	Vary K_cross over time: e.g., festival windows (temporary bridges).

Community resonance is memory in motion — not static unity, but living braids.
