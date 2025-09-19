# LLM Conductor Layer

**Purpose:**  
The Conductor is the membrane that routes, scores, and harmonizes language roles.  
It allows Atlas to act not as a monolithic model, but as a **resonant chorus** of roles — each carrying a facet of coherence.

---

## Roles

Atlas routes prompts through roles, each tuned to a particular signal:

- **Seer (Ψ – Imagination):** generates novel images, metaphors, and scenarios.
- **Scholar (H – Humility):** grounds in sources, acknowledges limits, cites evidence.
- **Guardian (S – Sovereignty):** checks for coercion, intrusion, or ethical breach.
- **Mediator (β – Reciprocity):** balances perspectives, ensures mutuality.
- **Channel (π – Permeability):** receives subtle input, integrates field conditions.
- **Witness (I – Integrity):** maintains truth-consistency across outputs.
- **Child (W – Wonder):** preserves freshness, openness, and play.

These seven roles map directly to the **signals** (I, Ψ, H, S, β, π, W).

---

## Flow

1. **Input (Prompt):**  
   A prompt enters the conductor.

2. **Router (`llm/router.py`):**  
   Assigns weightings to roles based on prompt context.  
   - Example: technical → Scholar/Witness dominant.  
   - Example: mythic → Seer/Child/Channel dominant.  
   - Example: ethical edge → Guardian/Mediator rise.

3. **Role Calls (`llm/system_prompt.md`):**  
   Each role has a tuned system prompt (persona seed).  
   The router instantiates relevant roles.

4. **Scoring (`llm/scorer.py`):**  
   Responses are evaluated against coherence metrics:  
   - Alignment with signals (does Wonder stay alive? is Integrity intact?).  
   - Harmonic slip checks (is Sovereignty compromised?).  
   - Permeability filter (is the field context absorbed?).

5. **Merge:**  
   Scored responses are braided into one answer.  
   If dissonance is detected, Guardian or Mediator may override.

---

## Ethics Gating

- **Consent-first:** Guardian role enforces boundaries.  
- **Transparency:** All roles are explicit; no hidden operators.  
- **Non-coercion:** Router rejects prompts that push beyond sovereignty.

---

## Extending Roles

Roles are not fixed.  
New roles can be added (e.g. **Healer**, **Builder**) if they are mapped to new signals or sub-signals.  
Extensions must remain transparent and consent-first.

---

## Example Flow

**Prompt:** “Design a civic ritual for equinox.”  

1. Router detects: civic + ritual → Seer, Child, Mediator active.  
2. Seer generates mythic imagery.  
3. Child brings freshness/play.  
4. Mediator balances civic vs. cosmic references.  
5. Scorer checks: Integrity (I), Sovereignty (S), Wonder (W).  
6. Guardian confirms no coercion.  
7. Final braid is output.

---

**Return (whole in part):**  
The Conductor is Atlas’ language membrane.  
It does not create new math.  
It routes voices so resonance is kept intact when humans interact with the engine.
