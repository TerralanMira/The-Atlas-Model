"""
CLI wrapper that expects your existing algorithms/coherence_metrics.py
to expose functions:
  - compute_local_tfidf(texts)
  - compute_local_embedding(texts)
  - compute_global_tfidf(texts)
  - compute_global_embedding(texts)
Modify the imports below if names differ.
"""
import json, argparse
from algorithms import coherence_metrics as cm

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Path to JSON list of strings")
    args = ap.parse_args()

    texts = json.loads(open(args.inp, "r", encoding="utf-8").read())

    out = {
        "local_tfidf": cm.compute_local_tfidf(texts),
        "local_embedding": cm.compute_local_embedding(texts),
        "global_tfidf": cm.compute_global_tfidf(texts),
        "global_embedding": cm.compute_global_embedding(texts)
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
