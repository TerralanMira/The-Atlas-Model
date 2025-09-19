# Resonant Reality ↔ Atlas Model Bridge

**Purpose:**  
This page defines how **Resonant Reality** (RR) and **Atlas Model** (AM) interact.  
Resonant Reality is the **vessel** (city, cosmos, practice).  
Atlas is the **engine** (metrics, simulations, coherence algorithms).  
The bridge is the membrane where they meet.

---

## How Resonant Reality Calls Atlas

1. **Context Gathering (RR side)**
   - RR collects **environmental context**: geomagnetic index (Kp), Schumann amplitude, cosmic timing, node type, architecture.
   - RR collects **human signals**: I (Integrity), Ψ (Imagination), H (Humility), S (Sovereignty), β (Reciprocity), π (Permeability), W (Wonder).  
     - Always consent-first.  
     - Signals are normalized [0,1].

2. **Handshake JSON (RR → AM)**
   - RR prepares a JSON object. Example:
   ```json
   {
     "kp_index": 4.2,
     "schumann_amp": 7.9,
     "node_type": "hearth",
     "architecture": "chambered",
     "cosmic_timing": "equinox",
     "participants": 12,
     "signals": {"I":0.9,"Ψ":0.8,"H":0.85,"S":0.8,"β":0.7,"π":0.65,"W":0.9}
   }
