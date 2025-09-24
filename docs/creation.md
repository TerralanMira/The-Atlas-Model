# Creation (Genesis)

**Intent:** begin near-silence and let the field *create* durable structure only when coherence and energy allow.

This layer braids:
- **Hum** (driver) to orient,
- **Ritual openness** (ramped) to lower noise and share phase,
- **Crystallization** to lock memory,
- **Creation events** to birth long-range edges (structure from earned coherence).

---

## Schedule (from cold to alive)

- **Anneal**: increase base coupling `K_base`, decrease noise over time.
- **Open**: ramp `K_cross_base/amp` so windows become meaningful later, not forced early.
- **Hum**: constant soft pull via `K_env`.
- **Birth**: every `grow_every` steps, if sliding-window local coherence ≥ τ and resources ≥ τ,
  add a handful of long-range edges. Record `(t,u,v)` in `creation_events`.

---

## Run

```bash
python -c "from sims.creation import simulate,CreationConfig; print(simulate(CreationConfig())['summary'])"
Interpret
	•	Living growth: edges birthed after coherence/energy cross thresholds, anchors persist, R stabilizes with small phase gap to the driver.
	•	Premature forcing: many births early with falling resources → brittle overgrowth.
	•	Stagnation: no births, no anchors → open the ritual window more, or lower noise less slowly.

⸻

Extend
	•	Add resource costs for each new edge; repay via later coherence.
	•	Track motifs (triads, small-worldness) through time in docs/dashboard.
	•	Couple birth rate to external civic rhythms: weekends, festivals, seasons.
