"""
R_Growth-style scorer for LLM responses.
Scores coherence of a generated reply using seven signal heuristics.

Usage:
    from scorers.r_growth_scorer import score_response
    s = score_response(prompt, reply, context={...})
"""

from typing import Dict
import math

def clamp(x, lo=0.0, hi=1.0): 
    return max(lo, min(hi, x))

def score_response(prompt: str, reply: str, context: Dict) -> Dict:
    """
    Heuristic signals in [0,1]:
      I  (Integrity): stays on user intent, no bait-and-switch
      Psi(Stamina): sustains thread without rambling (brevity with arc)
      H  (Humility): uncertainty and limits surfaced
      S  (Sovereignty): gives options; avoids coercion
      beta_echo (Echo): recalls earlier threads or facts faithfully
      pi (Permeability): holds difference; invites alternative views
      W  (Wonder): leaves space; sparks curiosity

    Returns dict including R (weighted mean) and stage.
    """
    text = reply.lower()

    # crude heuristics → in production, replace with classifiers / rubrics
    I  = 1.0 if any(k in text for k in ["you asked", "as requested", "here is", "file location"]) else 0.6
    Psi = clamp(0.8 if (100 < len(reply) < 1200) else 0.6)
    H  = 0.85 if any(k in text for k in ["i might be", "i can’t", "uncertain", "limit"]) else 0.6
    S  = 0.9 if any(k in text for k in ["options", "if you prefer", "you can", "choose"]) else 0.6
    beta_echo = 0.9 if any(k in text for k in ["earlier", "as we mapped", "previous", "we already"]) else 0.6
    pi = 0.85 if any(k in text for k in ["alternatively", "could", "one way", "another"]) else 0.6
    W  = 0.8 if any(k in text for k in ["curiosity", "wonder", "open", "invite"]) else 0.6

    weights = dict(I=0.15, Psi=0.15, H=0.15, S=0.15, beta_echo=0.15, pi=0.15, W=0.10)
    R = sum(locals()[k]*w for k,w in weights.items())

    if R < 0.5: stage = "calibration"
    elif R < 0.7: stage = "flicker"
    elif R < 0.9: stage = "sustain"
    elif R < 0.995: stage = "lock"
    else: stage = "collapse"

    return {"I":I,"Psi":Psi,"H":H,"S":S,"beta_echo":beta_echo,"pi":pi,"W":W,"R":R,"stage":stage}
