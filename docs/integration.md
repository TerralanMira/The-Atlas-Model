# Integration — Closing the Loop

Integration is the practiced art of folding the parts back into the whole.  
If Awareness is the lens, Coherence the pattern, and Field Layers the map — Integration is the ritual by which the map is lived, tested, and evolved.

---

## Purpose of this document
- Show how the repo’s pieces (docs, sims, algorithms, dashboards, tests) form a single living loop.  
- Make explicit the operational links (file names, headers, metric names).  
- Give practice-first paths so readers can run sims, read results, and apply corrections ethically.

---

## 1. The Loop (practical)
1. **Tuning (Awareness):** apply practices from `docs/awareness.md`. Morning hum, breath cycles, short daily calibration.  
2. **Measure (Coherence):** run simulations or recordings; compute `R_total`, `R_inner`, `R_outer`, `C_cross`, `Delta`, `Phi`. See `algorithms/coherence_metrics.py`.  
3. **Read (Dashboard):** summarize with `dashboard/overlay_loader.py` or `dashboard/dashboard.py`. Look for “gentle lift” vs “watch clamp.”  
4. **Act (Applications):** choose interventions from `docs/applications.md` (lower K_cross, add breath/noise, shift ritual cadence).  
5. **Log (Sessions):** save session with schema in `sessions/schema.json` for consented experiments.  
6. **Reflect (Integration):** update docs/parameters if interventions changed behavior, add tests if new invariants arise, commit and repeat.

---

## 2. Files ↔ Truths (explicit mapping)
- `algorithms/coherence_metrics.py` → canonical metrics API: returns `R`, `C_cross`, `drift`, `C01`, `Delta`. Use these names in code and docs.  
- `sims/multi_scale_kuramoto.py` & `sims/breath_cycle.py` → write CSV headers:  
  `step, t, R_total, R_inner, R_outer, C_cross, drift, Delta, Phi, choice_score`  
- `dashboard/overlay_loader.py` → one-line qualitative read; expects above headers.  
- Tests in `tests/` must assert presence & bounds of these metrics. Keep `C_cross` as the canonical cross-layer metric.  
- `docs/*.md` must reference these names verbatim (so readers find the real signals in logs).

---

## 3. Ethics & Safety in Looping
- Log and simulate only with **consent**. When simulations model people, keep parameters hypothetical and anonymized.  
- Interventions: prefer reversible, bounded nudges (small noise, reduced coupling). Never hard-lock fields.  
- Keep `ETHICS.md` visible and linked in top-level nav.

---

## 4. Operational Recipes (copy-paste)
- Quick sim + read:
```bash
python sims/multi_scale_kuramoto.py --seed 7 --steps 800 --save_csv logs/multi_scale.csv
python dashboard/overlay_loader.py logs/multi_scale.csv
	•	If dashboard shows watch clamp:
	•	Reduce K_cross by 10–30% OR add noise_std +0.002–0.006 in sim presets.
	•	Re-run sim and observe Delta (entropy) increase; Phi should remain high.

⸻

5. Tests as Practice
	•	Tests are not just CI—they are ritual checks that the field remains healthy.
	•	Example invariant to test: 0 <= C_cross <= 1, 0 <= Delta <= 1, R_total ∈ [0,1].
	•	Add test when you add a new sim or intervention.

⸻

6. Appendix: Quick glossary
	•	R_total — global order parameter (0..1).
	•	R_inner, R_outer — sub-layer order measures.
	•	C_cross — canonical cross-layer alignment (0..1).
	•	Delta — phase entropy normalized (0..1).
	•	Phi — lag-1 smoothness / gentleness (0..1).
	•	choice_score — computed signal for collapse risk (0..1).
