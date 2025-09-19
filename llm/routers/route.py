"""
Role-Shift Router for Atlas LLM
Selects one of {Mirror, Chamber, Conductor, Field} per turn
based on user intent and context + optional scorer feedback.
"""

from typing import Literal, Dict
from scorers.r_growth_scorer import score_response

Role = Literal["Mirror", "Chamber", "Conductor", "Field"]

def choose_role(user_text: str, last_reply: str|None, context: Dict) -> Role:
    want_build = any(k in user_text.lower() for k in ["make", "write", "generate", "produce", "file", "code"])
    want_reflect = any(k in user_text.lower() for k in ["why", "explain", "summarize", "analyze", "understand"])
    want_orchestrate = any(k in user_text.lower() for k in ["plan", "sequence", "schedule", "conduct", "score"])
    want_context = any(k in user_text.lower() for k in ["city", "earth", "cosmos", "resonant reality", "bridge"])

    if want_build: return "Chamber"
    if want_orchestrate: return "Conductor"
    if want_context: return "Field"
    if want_reflect: return "Mirror"
    return "Mirror"

def postcheck(reply: str, context: Dict) -> Dict:
    s = score_response(context.get("prompt",""), reply, context)
    # if stage == collapse (≈1.0), nudge to permeability by adding an open hook
    if s["stage"] == "collapse":
        reply += "\n\n— leaving space for difference; if you want an alternative path, say the word."
    return {"reply": reply, "score": s}
