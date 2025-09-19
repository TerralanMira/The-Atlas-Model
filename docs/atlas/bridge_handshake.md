# Bridge Handshake — Resonant Reality ↔ Atlas Model

**Purpose:**  
Define the **data interface** between Resonant Reality (RR) and Atlas Model (AM).  
This makes the bridge operational: RR provides field conditions, Atlas computes coherence metrics, and RR applies the outputs in practice.

---

## Inputs (Resonant Reality → Atlas)

RR gathers **field-level context** and sends it as JSON.

```json
{
  "kp_index": 3.5,                // geomagnetic activity (float)
  "schumann_amp": 7.8,            // dominant Schumann resonance amplitude (Hz)
  "node_type": "plaza",           // enum: plaza | hearth | garden | wild
  "architecture": "open",         // enum: open | chambered | hybrid
  "cosmic_timing": "solstice",    // enum: equinox | solstice | eclipse | none
  "participants": 25,             // number of people in the session
  "signals": {                    // optional human signal values (0–1)
    "I": 0.8,
    "Ψ": 0.7,
    "H": 0.9,
    "S": 0.85,
    "β": 0.6,
    "π": 0.75,
    "W": 0.95
  }
}
Outputs (Atlas → Resonant Reality)

Atlas computes coherence metrics and returns recommendations.
{
  "R_gain": 0.12,                  // projected gain in global coherence
  "RMSSD_gain": 14.3,              // projected gain in HRV (ms)
  "resilience_score": 0.82,        // 0–1 score of field resilience
  "recommended_K": [0.7, 1.1],     // coupling constant range to sustain R≈0.99
  "risk_flags": ["geomagnetic_high"], // optional alerts (strings)
  "notes": "Maintain permeability; reduce forcing; solstice anchor supports high W."
}
Flow
	1.	RR collects field context (geomagnetics, Schumann, participants, timing).
	2.	RR gathers signals (optional, see docs/awareness/signals_guide.md).
	3.	RR posts data → Atlas API (local or cloud service).
	4.	Atlas computes metrics (via algorithms/ and coherence_metrics.py).
	5.	Atlas returns JSON → used by RR Conductor to adjust sessions.
Example (Session Run)

Input (RR):
{ "kp_index": 4.2, "schumann_amp": 7.9, "node_type": "hearth",
  "architecture": "chambered", "cosmic_timing": "equinox", "participants": 12,
  "signals": {"I":0.9,"Ψ":0.8,"H":0.85,"S":0.8,"β":0.7,"π":0.65,"W":0.9} }
Output (AM):
{ "R_gain": 0.15, "RMSSD_gain": 11.2, "resilience_score": 0.79,
  "recommended_K": [0.8, 1.0], "risk_flags":[], 
  "notes":"High integrity + humility; chamber helps stability; equinox supports coupling." }
Notes
	•	Consent-first: signals collection is optional; RR must ensure participant consent.
	•	Minimal logging: only aggregated or anonymized data flows; personal data never required.
	•	Extensible: node types, architectures, cosmic timings are enums and can be extended.
	•	Test stubs: see examples/session_to_metrics.py and examples/dual_phase_with_anchor.py.
Return (whole in part):
This handshake keeps vessel and engine permeable but distinct.
RR brings context; Atlas returns resonance metrics.
Together they close the loop without collapsing difference.
