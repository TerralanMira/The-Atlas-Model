"""
Demonstrate role routing + scoring with the LLM stub (no external calls).
"""
from llm.routers.route import choose_role, postcheck

user = "Design a hearth session that keeps permeability high and avoids collapse."
role = choose_role(user, None, {"prompt": user})
reply = f"[{role}] Strike→ We’ll hold near 0.99. Resonance→ Steps for consent, cadence, and Δ integration. Landing→ Two options next."
checked = postcheck(reply, {"prompt": user})
print("role:", role)
print("R:", round(checked["score"]["R"], 3), "stage:", checked["score"]["stage"])
print("\n" + checked["reply"])
Run:
python examples/run_r_growth.py
python examples/run_llm_stub.py
