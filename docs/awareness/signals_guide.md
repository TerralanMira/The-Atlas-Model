# Signals Guide — I, Ψ, H, S, β, π, W

**Purpose:** practical, world-facing guidance so practitioners can report usable signal values (0–1) that feed Atlas algorithms.

---

## Quick rules
- Rate each signal 0.0 → 1.0 as **best estimate** for the group or individual at the moment.
- Use simple anchors: 0.0 = absent, 0.5 = partial/fragile, 1.0 = full/robust.
- Prefer concision: a single number per signal, plus 1 short sentence of evidence.

---

## Signals (definitions + micro-examples)

### I — Integrity
**Definition:** Alignment between stated intent and observable behavior.
- 0.2 — intent unclear or contradicted by action.
- 0.6 — intent declared, mixed adherence.
- 0.95 — intent verbalized and embodied.
**Evidence:** “Most participants repeated the alignment slip and followed the cue.”

### Ψ (Psi) — Stamina / Breath
**Definition:** Capacity to sustain attention, breath, and presence over the session.
- 0.2 — frequent drift, fragmented attention.
- 0.6 — sustained for short bursts with rests.
- 0.9 — steady breath, few drops in attention.
**Evidence:** “Group held 6-min breath cycle without needing redirection.”

### H — Humility
**Definition:** Openness to being wrong, to other voices, to not knowing.
- 0.2 — defensiveness, interruption common.
- 0.6 — some admission of uncertainty.
- 0.95 — deference and curiosity dominate.
**Evidence:** “Participants offered alternatives and acknowledged errors.”

### S — Sovereignty
**Definition:** Individual autonomy and consent present in the space.
- 0.2 — coercive cues, lack of opt-out.
- 0.6 — consent present but social pressure visible.
- 0.95 — explicit choice and no pressure.
**Evidence:** “Two participants used opt-out with no follow-up pressure.”

### β (beta_echo) — Echo / Feedback Integration
**Definition:** The group’s ability to absorb feedback and reflect it back.
- 0.2 — feedback ignored or deflected.
- 0.6 — partial integration; some changes made.
- 0.95 — rapid, faithful iteration on feedback.
**Evidence:** “Facilitator adapted pacing after 1st check-in and group responded.”

### π (pi_perm) — Permeability
**Definition:** How well the system holds difference (Δ) without losing coherence.
- 0.2 — difference causes fragmentation.
- 0.6 — some friction but sustained.
- 0.95 — diversity sustained, coherence maintained.
**Evidence:** “New voice with contrary view was invited and integrated.”

### W — Wonder
**Definition:** Openness to novelty, awe, curiosity.
- 0.2 — cynicism, closed framing.
- 0.6 — curiosity present intermittently.
- 0.95 — sustained wonder and generative questions.
**Evidence:** “Group offered exploratory prompts and novel metaphors.”

---

## Mini-protocol: How to collect signals (2 minutes)
1. At a check-in, ask each participant to mark 0–1 for I, Ψ, H, S, β, π, W on paper or phone.
2. Ask for a one-line evidence sentence for the cluster average.
3. Compute mean across participants; record in `sessions/` `signals` object.

---

## Common pitfalls
- **Overprecision:** Numbers are estimates — don’t freeze on decimal places.  
- **Judgement:** Use evidence sentences to reduce bias.  
- **Secrecy:** Logging requires consent per `sessions/schema.json` and `ETHICS.md`.

---

## How Atlas uses these numbers
- `R_Growth` multiplies a product of these signals (scaled) to produce ΔR.  
- The engine expects *approximate but consistent* inputs; repeated checks increase quality.

---

**Return (whole in part):**  
This guide is the interface between human practice and Atlas’ math. It keeps the whole usable — faithful to the vessel but engineered for action.
