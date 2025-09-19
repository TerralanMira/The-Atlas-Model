"""
Run a tiny R_Growth pass and print the trajectory.
"""
from algorithms.r_growth import run_growth_cycle

stream = [
    {"I":0.4,"Psi":0.5,"H":0.6,"S":0.5,"beta_echo":0.4,"pi":0.5,"W":0.6},
    {"I":0.6,"Psi":0.6,"H":0.7,"S":0.6,"beta_echo":0.6,"pi":0.7,"W":0.7},
    {"I":0.7,"Psi":0.7,"H":0.8,"S":0.7,"beta_echo":0.7,"pi":0.8,"W":0.8},
    {"I":0.9,"Psi":0.9,"H":0.9,"S":0.9,"beta_echo":0.9,"pi":0.9,"W":0.9},
]
res = run_growth_cycle(stream)
for r in res:
    print(f"t={r['t']} R={r['R']:.3f} stage={r['stage']}")
